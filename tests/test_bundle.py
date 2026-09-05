import copy
import unittest
from tools.build_bundle import build,verify
from tools.validate import load_records,canonical
from tools.report_coverage import report

class BundleTests(unittest.TestCase):
    def test_reproducible_and_roundtrip(self):
        records=load_records()
        a=build(records);b=build(list(reversed(records)))
        self.assertEqual(canonical(a),canonical(b));self.assertEqual(len(verify(a)['records']),len(records))
    def test_corruption_rejected(self):
        b=build(load_records());b['payload']['records'][0]['name']='tampered'
        with self.assertRaises(ValueError):verify(b)
    def test_future_schema_rejected(self):
        b=build(load_records());b['manifest']['schema_version']=2
        with self.assertRaises(ValueError):verify(b)
    def test_partial_inventory_never_complete(self):
        r=report(load_records());self.assertFalse(r['goal_complete']);self.assertEqual(sum(m['approved_profiles'] for m in r['models']),0)

    def test_experimental_and_revoked_profiles_excluded(self):
        from test_calibration import sample_dataset
        for status in ['experimental','revoked']:
            records=sample_dataset();records[-1]['review']['status']=status
            bundle=build(records)
            self.assertFalse(any(r['kind']=='profile' for r in verify(bundle)['records']))
