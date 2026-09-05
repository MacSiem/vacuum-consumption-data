"""Strict public-data contracts; observations never become executable profiles implicitly."""
import ipaddress
import json
import math
from pathlib import Path
from urllib.parse import urlsplit
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
KINDS=('model','integration','observation','profile','settings_catalog','estimate')

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def validate_record(record):
    try:
        canonical(record)
        kind=record['kind']
        if kind not in KINDS:raise ValueError('Unknown record kind')
        schema=json.loads((ROOT/'schemas'/f'{kind}.schema.json').read_text())
        Draft202012Validator(schema,format_checker=FormatChecker()).validate(record)
        for source in record['provenance']:
            url=urlsplit(source['url']);host=url.hostname or ''
            if url.username or url.password or '.' not in host or host.endswith(('.local','.internal')):
                raise ValueError('Private or credential-bearing source URL')
            try: address=ipaddress.ip_address(host)
            except ValueError: address=None
            if address is not None and not address.is_global:raise ValueError('Private source address')
        if kind=='observation':
            empirical=record['source_class']=='empirical'
            if empirical != (record['measurement'] is not None):raise ValueError('Empirical measurement contract mismatch')
            if empirical and (record['sample_count']!=1 or record['confidence']!='measured' or not any(s['type']=='empirical' for s in record['provenance'])):
                raise ValueError('One empirical record represents one measured cycle/action')
            if empirical:
                m=record['measurement']
                axis={'floor_only':('m2','min'),'wash_only':('action',),'whole_cycle':('cycle',)}
                if m['exposure_unit'] not in axis[m['scope']]:raise ValueError('Scope/exposure mismatch')
                if record['quantity']['unit'] != 'ml/'+m['exposure_unit'] or not math.isclose(record['quantity']['value'],m['observed_ml']/m['exposure'],rel_tol=1e-9):raise ValueError('Reported quantity contradicts measurement')
            if not empirical and record['sample_count']!=0:raise ValueError('Declaration is not a measurement sample')
        if kind=='profile':
            expected={'area':'ml/m2','time':'ml/min','action':'ml/action','whole_cycle':'ml/cycle'}
            allowed={'floor_only':('area','time'),'wash_only':('action',),'whole_cycle':('whole_cycle',)}
            if record['exposure_domain']['min']>record['exposure_domain']['max']:raise ValueError('Inverted exposure domain')
            if record['method'] not in allowed[record['scope']]:raise ValueError('Profile scope/method mismatch')
            if record['unit']!=expected[record['method']]:raise ValueError('Method/unit mismatch')
        if kind=='estimate':
            if record['estimate_readiness']=='labeled_runtime_estimate' and record['source_type']=='unknown':raise ValueError('Unknown source cannot be runtime estimate')
            if record['basis_kind']=='tank_capacity':raise ValueError('Tank capacity is not a consumption basis')
            if record['applicability']['model_scope']!='named_model':raise ValueError('Family scope cannot prove a runtime estimate')
            if record['applicability']['sku_scope']=='exact' and record['context']['sku'] is None:raise ValueError('Exact SKU scope needs SKU')
            if record['applicability']['firmware_scope']=='exact' and record['context']['firmware'] is None:raise ValueError('Exact firmware scope needs firmware')
    except Exception as error:
        raise ValueError(f"Invalid {record.get('id','record')}: {error}") from error

def complete_context(context):
    return all(v is not None for k,v in context.items() if k!='settings') and all(v is not None for v in context['settings'].values())

def validate_dataset(records):
    by_id={}
    for record in records:
        validate_record(record)
        if record['id'] in by_id:raise ValueError('Duplicate record ID: '+record['id'])
        by_id[record['id']]=record
    for r in records:
        if r['kind']=='settings_catalog':
            if by_id.get(r['model_id'],{}).get('kind')!='model':raise ValueError('Missing settings model')
            dimensions={d['name']:d for d in r['dimensions']}
            if len(dimensions)!=len(r['dimensions']):raise ValueError('Duplicate setting dimension')
            for rule in r['rules']:
                for key,value in rule['when'].items():
                    if key not in dimensions or value not in dimensions[key]['options']:raise ValueError('Unknown rule condition')
                for key,values in rule['allowed'].items():
                    if key not in dimensions or not set(values)<=set(dimensions[key]['options']):raise ValueError('Unknown rule options')
        if r['kind'] not in ('observation','profile','estimate'):continue
        context=r['context']
        if by_id.get(context['model_id'],{}).get('kind')!='model':raise ValueError('Missing model reference')
        integration=context['integration_id']
        if integration is not None and by_id.get(integration,{}).get('kind')!='integration':raise ValueError('Missing integration reference')
        if r['kind']=='estimate':
            refs=r['basis_ids']
            if not refs:raise ValueError('Estimate needs source-backed basis')
            if len(refs)!=len(set(refs)):raise ValueError('Duplicate estimate basis IDs')
            bases=[by_id.get(key,{}) for key in refs]
            if any(base.get('kind')!='observation' for base in bases):raise ValueError('Missing estimate basis observation')
            if any(base['context']!=context for base in bases):raise ValueError('Estimate basis from another context')
            if r['source_type']=='manufacturer_declaration' and any(base['source_class']!='manufacturer_declaration' for base in bases):raise ValueError('Manufacturer estimate needs manufacturer declaration basis')
            if r['source_type']=='user_measurement' and any(base['source_class']!='empirical' for base in bases):raise ValueError('Measurement estimate needs empirical basis')
            if any(base['quantity']!=r['quantity'] for base in bases) and r['basis_kind']=='manufacturer_declared_quantity':raise ValueError('Declared estimate quantity contradicts basis')
            continue
        if r['kind']!='profile':continue
        refs=r['evidence_ids']
        if len(refs)!=len(set(refs)):raise ValueError('Duplicate evidence IDs')
        for key in refs:
            observation=by_id.get(key,{})
            if observation.get('kind')!='observation':raise ValueError('Missing observation reference')
            if observation['context']!=context:raise ValueError('Evidence from another context')
        if r['review']['status']=='approved':validate_approved(r,by_id)
    return by_id

def validate_approved(profile,by_id):
    if not complete_context(profile['context']) or profile['unknowns'] or profile['confidence']!='validated' or not profile['review']['reviewer']:
        raise ValueError('Approved profile has incomplete applicability/review')
    from tools.settings import check_settings
    catalogs=[r for r in by_id.values() if r['kind']=='settings_catalog' and r['model_id']==profile['context']['model_id']]
    if len(catalogs)!=1 or not all(d['ha_value_mapping_verified'] for d in catalogs[0]['dimensions']) or not check_settings(catalogs[0],profile['context']['settings'])['compatible']:
        raise ValueError('Unverified setting combinations or HA mappings')
    integration=by_id[profile['context']['integration_id']]
    if not integration['hardware_verified'] or integration['version']!=profile['context']['integration_version'] or profile['context']['model_id'] not in integration['supported_model_ids']:
        raise ValueError('Unverified integration binding')
    v=profile['validation'];train=v['training_ids'];hold=v['validation_ids']
    if len(set(train))<3 or len(set(hold))<5 or set(train)&set(hold) or set(train+hold)!=set(profile['evidence_ids']):
        raise ValueError('Insufficient or overlapping validation evidence')
    records=[by_id[k] for k in train+hold]
    if any(r['source_class']!='empirical' or r['measurement'] is None for r in records):raise ValueError('Only measured evidence can validate an empirical profile')
    if any(r['measurement']['scope']!=profile['scope'] for r in records):raise ValueError('Measurement scope mismatch')
    units={'ml/m2':'m2','ml/min':'min','ml/action':'action','ml/cycle':'cycle'}
    if any(r['measurement']['exposure_unit']!=units[profile['unit']] for r in records):raise ValueError('Exposure unit mismatch')
    cycles=[(r['measurement']['series_id'],r['measurement']['cycle_id']) for r in records]
    if len(set(cycles))!=len(cycles):raise ValueError('Repeated cycle used as independent evidence')
    exposures=[r['measurement']['exposure'] for r in records]
    domain=profile['exposure_domain']
    if domain['min']<min(exposures) or domain['max']>max(exposures):raise ValueError('Profile extrapolates beyond observed exposure')
    if any(not domain['min']<=x<=domain['max'] for x in exposures):raise ValueError('Validation observation outside profile domain')
    train_devices={by_id[k]['measurement']['series_id'] for k in train}
    hold_devices={by_id[k]['measurement']['series_id'] for k in hold}
    if train_devices&hold_devices or len(train_devices|hold_devices)<3 or v['device_count']!=len(train_devices|hold_devices):raise ValueError('Community profile needs independent device holdout')
    for key in train:
        if by_id[key]['measurement']['split']!='train':raise ValueError('Wrong training split')
    errors=[];relative=[]
    for key in hold:
        m=by_id[key]['measurement']
        if m['split']!='validation':raise ValueError('Wrong validation split')
        error=abs(profile['coefficient']*m['exposure']-m['observed_ml'])
        if error>max(.10*m['observed_ml'],2*m['instrument_resolution_ml']):raise ValueError('Validation error exceeds provisional policy')
        errors.append(error);relative.append(error/m['observed_ml'])
    if v['max_error_ml'] is None or v['max_relative_error'] is None or not math.isclose(v['max_error_ml'],max(errors),abs_tol=1e-9) or not math.isclose(v['max_relative_error'],max(relative),abs_tol=1e-9):raise ValueError('Validation metrics do not match observations')

def load_records(root=ROOT):
    records=[]
    for folder in ('models','integrations','observations','estimates','consumption_profiles','settings'):
        for path in sorted((Path(root)/'data'/folder).glob('*.json')):records.append(json.loads(path.read_text()))
    return records

if __name__=='__main__':
    records=load_records();validate_dataset(records)
    print(json.dumps({'validation':'PASS','records':len(records),'approved_profiles':sum(r['kind']=='profile' and r['review']['status']=='approved' for r in records)}))
