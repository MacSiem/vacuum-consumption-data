"""Report evidence coverage without treating declarations as calibrated profiles."""
import csv
import json
from pathlib import Path
from tools.validate import ROOT, load_records, validate_dataset
from tools.contracts_v2 import validate_source_contracts

def report(records):
    validate_dataset(records)
    rows=[]
    for model in sorted((r for r in records if r['kind']=='model'),key=lambda r:r['id']):
        obs=[r for r in records if r['kind']=='observation' and r['context']['model_id']==model['id']]
        estimates=[r for r in records if r['kind']=='estimate' and r['context']['model_id']==model['id']]
        profiles=[r for r in records if r['kind']=='profile' and r['context']['model_id']==model['id']]
        catalogs=[r for r in records if r['kind']=='settings_catalog' and r['model_id']==model['id']]
        dimensions=[d for c in catalogs for d in c['dimensions']]
        rows.append({'known_setting_dimensions':len(dimensions),'known_option_values':sum(len(d['options']) for d in dimensions),'setting_relationships_verified':bool(catalogs) and all(c['relationships_complete'] for c in catalogs),'model_id':model['id'],'manufacturer':model['manufacturer'],'name':model['name'],'declared_quantities':sum(r['source_class']=='manufacturer_declaration' for r in obs),'labeled_runtime_estimates':sum(r['estimate_readiness']=='labeled_runtime_estimate' for r in estimates),'measured_observations':sum(r['source_class']=='empirical' for r in obs),'approved_profiles':sum(r['review']['status']=='approved' for r in profiles),'mode_action_inventory':'unknown','automatic_consumption_complete':False})
    source_contract=json.loads((ROOT/'fixtures'/'source-contracts-2026-09-05.json').read_text())
    validate_source_contracts(source_contract)
    raw_inventory=json.loads((ROOT/'data'/'inventory'/'miot-specifications.json').read_text())
    return {'schema_version':3,'goal_complete':False,'global_inventory_complete':False,'models':rows,'integrations':[{'id':r['id'],'version':r['version'],'hardware_verified':r['hardware_verified'],'documented_signal_contracts':len(r['signal_contracts']),'unknowns':r['unknowns']} for r in records if r['kind']=='integration'],'coverage_denominators':{'dataset_models':len(rows),'miot_protocol_ids':len(raw_inventory['models']),'retail_models':'unknown','regions_unsearched':'unknown','firmware_model_pairs':'unknown','setting_dimensions_documented':13,'setting_combinations_verified':0,'action_completion_contracts':len(source_contract['action_completion']),'action_completion_complete':sum(v['disposition']=='complete' for v in source_contract['action_completion'].values()),'labeled_runtime_estimates':sum(r['kind']=='estimate' and r['estimate_readiness']=='labeled_runtime_estimate' for r in records),'measured_cycles':0,'approved_profiles':0},'reason':'Labeled estimates have source and scope but are not measured profiles. Retail inventory, completion evidence and integration bindings remain incomplete.'}

if __name__=='__main__':
    data=report(load_records());folder=ROOT/'reports';folder.mkdir(exist_ok=True)
    (folder/'coverage.json').write_text(json.dumps(data,indent=2)+'\n')
    with (folder/'coverage.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(data['models'][0]),lineterminator='\n');writer.writeheader();writer.writerows(data['models'])
    print(json.dumps({'models':len(data['models']),'goal_complete':False}))
