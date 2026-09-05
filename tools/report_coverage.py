"""Report evidence coverage without treating declarations as calibrated profiles."""
import csv
import json
from pathlib import Path
from tools.validate import ROOT, load_records, validate_dataset

def report(records):
    validate_dataset(records)
    rows=[]
    for model in sorted((r for r in records if r['kind']=='model'),key=lambda r:r['id']):
        obs=[r for r in records if r['kind']=='observation' and r['context']['model_id']==model['id']]
        profiles=[r for r in records if r['kind']=='profile' and r['context']['model_id']==model['id']]
        catalogs=[r for r in records if r['kind']=='settings_catalog' and r['model_id']==model['id']]
        dimensions=[d for c in catalogs for d in c['dimensions']]
        rows.append({'known_setting_dimensions':len(dimensions),'known_option_values':sum(len(d['options']) for d in dimensions),'setting_relationships_verified':bool(catalogs) and all(c['relationships_complete'] for c in catalogs),'model_id':model['id'],'manufacturer':model['manufacturer'],'name':model['name'],'declared_quantities':sum(r['source_class']=='manufacturer_declaration' for r in obs),'measured_observations':sum(r['source_class']=='empirical' for r in obs),'approved_profiles':sum(r['review']['status']=='approved' for r in profiles),'mode_action_inventory':'unknown','automatic_consumption_complete':False})
    return {'schema_version':1,'goal_complete':False,'global_inventory_complete':False,'models':rows,'integrations':[{'id':r['id'],'version':r['version'],'hardware_verified':r['hardware_verified'],'documented_signal_contracts':len(r['signal_contracts']),'unknowns':r['unknowns']} for r in records if r['kind']=='integration'],'reason':'Retail inventory, achievable setting combinations and integration bindings remain incomplete.'}

if __name__=='__main__':
    data=report(load_records());folder=ROOT/'reports';folder.mkdir(exist_ok=True)
    (folder/'coverage.json').write_text(json.dumps(data,indent=2)+'\n')
    with (folder/'coverage.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(data['models'][0]));writer.writeheader();writer.writerows(data['models'])
    print(json.dumps({'models':len(data['models']),'goal_complete':False}))
