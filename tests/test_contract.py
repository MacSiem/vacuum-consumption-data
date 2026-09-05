import copy
import json
import unittest
from pathlib import Path
from tools.validate import validate_record, validate_dataset

ROOT=Path(__file__).resolve().parents[1]

def observation():
    return {'id':'example_wash','kind':'observation','provenance':[{'url':'https://example.org/manual','date':'2026-09-05','type':'manufacturer','claim':'Synthetic test only'}],'confidence':'declared','unknowns':['firmware'],'context':{'model_id':'example','sku':None,'dock_variant':None,'firmware':None,'integration_id':None,'integration_version':None,'reservoir':'dock_clean','action':'mid_wash','settings':{k:None for k in ['task_scope','suction_level','carpet_policy','cleaning_mode','mop_mode','water_level','route','passes','wash_mode','wash_frequency','wash_temperature','adaptive_mode','detergent_mode']}},'quantity':{'value':120,'unit':'ml/action'},'source_class':'manufacturer_declaration','sample_count':0,'measurement':None,'runtime_eligible':False}

class ContractTests(unittest.TestCase):
    def test_declaration_cannot_be_runtime(self):
        r=observation();validate_record(r)
        r['runtime_eligible']=True
        with self.assertRaises(ValueError):validate_record(r)
    def test_extra_private_field_rejected(self):
        r=observation();r['device_id']='private'
        with self.assertRaises(ValueError):validate_record(r)
    def test_nonfinite_and_wrong_unit(self):
        for value in [float('nan'),float('inf'),-1,0]:
            r=observation();r['quantity']['value']=value
            with self.assertRaises(ValueError):validate_record(r)
        r=observation();r['quantity']['unit']='percent'
        with self.assertRaises(ValueError):validate_record(r)
    def test_empirical_requires_measurement(self):
        r=observation();r['source_class']='empirical'
        with self.assertRaises(ValueError):validate_record(r)
    def test_private_provenance_url(self):
        for url in ['https://192.168.1.1/source','https://localhost/source','https://user:password@example.org/manual']:
            r=observation();r['provenance'][0]['url']=url
            with self.assertRaises(ValueError):validate_record(r)
    def test_missing_model_reference(self):
        with self.assertRaises(ValueError):validate_dataset([observation()])
    def test_invalid_date(self):
        r=observation();r['provenance'][0]['date']='2026-02-31'
        with self.assertRaises(ValueError):validate_record(r)
