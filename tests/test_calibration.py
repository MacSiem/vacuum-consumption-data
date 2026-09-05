import copy
import unittest
from tools.validate import validate_dataset
from tools.fit_profiles import fit_coefficient
from test_contract import observation


def sample_dataset():
    base=observation();ctx=base['context']
    for key in ('sku','dock_variant','firmware','integration_version'):ctx[key]='test1'
    ctx['integration_id']='integration.test'
    ctx['settings']={k:'test_value' for k in ctx['settings']}
    provenance=[dict(base['provenance'][0],type='empirical')]
    model={'id':'example','kind':'model','manufacturer':'Synthetic','name':'Test only','public_model_ids':[],'regional_skus':[],'integration_candidates':[],'reservoirs_ml':{k:None for k in ['dock_clean','dock_dirty','robot_clean','robot_dirty','detergent']},'inventory_status':'unknown','confidence':'synthetic','unknowns':[],'provenance':provenance}
    integration={'id':'integration.test','kind':'integration','version':'test1','official':False,'supported_model_ids':['example'],'signal_contracts':[],'hardware_verified':True,'confidence':'synthetic','unknowns':[],'provenance':provenance}
    observations=[]
    for i in range(8):
        r=copy.deepcopy(base);r.update(id='sample_'+str(i),source_class='empirical',sample_count=1,confidence='measured',unknowns=[],provenance=provenance)
        r['measurement']={'series_id':'test_device_'+str(i%2 if i<3 else 2),'cycle_id':'cycle_'+str(i),'instrument_resolution_ml':1,'scope':'wash_only','observed_ml':120,'exposure':1,'exposure_unit':'action','split':'train' if i<3 else 'validation','settings_constant':True,'interrupted':False,'publication_consent':True}
        observations.append(r)
    profile={'id':'test_profile','kind':'profile','context':copy.deepcopy(ctx),'method':'action','exposure_domain':{'min':1,'max':1},'coefficient':120,'unit':'ml/action','scope':'wash_only','evidence_ids':[r['id'] for r in observations],'review':{'status':'approved','reviewer':'fixture_reviewer'},'validation':{'training_ids':[r['id'] for r in observations[:3]],'validation_ids':[r['id'] for r in observations[3:]],'device_count':3,'max_error_ml':0,'max_relative_error':0},'confidence':'validated','unknowns':[],'provenance':provenance}
    catalog={'id':'settings.example','kind':'settings_catalog','model_id':'example','dimensions':[{'name':k,'options':[v],'ha_value_mapping_verified':True} for k,v in ctx['settings'].items()],'rules':[],'relationships_complete':True,'confidence':'synthetic','unknowns':[],'provenance':provenance}
    return [model,integration,*observations,catalog,profile]

class CalibrationTests(unittest.TestCase):
    def test_fit_and_independent_validation(self):
        rows=sample_dataset();self.assertEqual(fit_coefficient(rows[2:5])['coefficient'],120);validate_dataset(rows)
    def test_fit_rejects_holdout(self):
        with self.assertRaises(ValueError):fit_coefficient(sample_dataset()[5:8])
    def test_fit_rejects_mixed_mode(self):
        rows=sample_dataset()[2:5];rows[1]['context']['settings']['wash_mode']='different'
        with self.assertRaises(ValueError):fit_coefficient(rows)
    def test_cannot_decompose_whole_cycle(self):
        rows=sample_dataset()[2:5]
        for r in rows:r['measurement'].update(scope='whole_cycle',exposure_unit='m2')
        with self.assertRaises(ValueError):fit_coefficient(rows)
    def test_validation_rejects_unknown_context(self):
        rows=sample_dataset()
        for r in rows[2:]:
            if 'context' in r:r['context']['firmware']=None
        with self.assertRaises(ValueError):validate_dataset(rows)
    def test_validation_rejects_wrong_device_count(self):
        rows=sample_dataset();rows[-1]['validation']['device_count']=30
        with self.assertRaises(ValueError):validate_dataset(rows)
    def test_validation_rejects_shared_device(self):
        rows=sample_dataset();rows[5]['measurement']['series_id']='test_device_0'
        with self.assertRaises(ValueError):validate_dataset(rows)
    def test_validation_rejects_error_and_fake_metric(self):
        for coefficient in [125,200]:
            rows=sample_dataset();rows[-1]['coefficient']=coefficient
            with self.assertRaises(ValueError):validate_dataset(rows)
    def test_validation_rejects_duplicate_cycle(self):
        rows=sample_dataset();rows[6]['measurement']['cycle_id']=rows[5]['measurement']['cycle_id']
        with self.assertRaises(ValueError):validate_dataset(rows)
    def test_validation_rejects_wrong_unit(self):
        rows=sample_dataset();rows[5]['measurement']['exposure_unit']='min'
        with self.assertRaises(ValueError):validate_dataset(rows)

    def test_scope_axis_mismatch_rejected(self):
        rows=sample_dataset();rows[2]['measurement']['scope']='floor_only'
        with self.assertRaises(ValueError):validate_dataset(rows)

    def test_quantity_must_match_measurement(self):
        rows=sample_dataset();rows[2]['measurement']['observed_ml']=999
        with self.assertRaises(ValueError):validate_dataset(rows)

    def test_profile_needs_verified_setting_relationships(self):
        rows=sample_dataset();rows[-2]['relationships_complete']=False
        with self.assertRaises(ValueError):validate_dataset(rows)

    def test_unsupported_exposure_range_rejected(self):
        rows=sample_dataset();rows[-1]['exposure_domain']['max']=1000
        with self.assertRaises(ValueError):validate_dataset(rows)
