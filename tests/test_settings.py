import copy
import unittest
from tools.settings import check_settings

class SettingsTests(unittest.TestCase):
    def catalog(self):
        return {'dimensions':[{'name':'cleaning_mode','options':['vacuum','mop','vacuum_mop']},{'name':'water_level','options':['off','low','high']}],'rules':[{'id':'vacuum_water_off','when':{'cleaning_mode':'vacuum'},'allowed':{'water_level':['off']}}],'relationships_complete':True}
    def test_forbidden_cross_product(self):
        result=check_settings(self.catalog(),{'cleaning_mode':'vacuum','water_level':'high'})
        self.assertFalse(result['compatible']);self.assertIn('incompatible_settings:vacuum_water_off',result['reason_codes'])
    def test_separate_mop_and_combined(self):
        for mode in ['mop','vacuum_mop']:
            self.assertTrue(check_settings(self.catalog(),{'cleaning_mode':mode,'water_level':'high'})['compatible'])
    def test_incomplete_relationships_not_proven(self):
        c=self.catalog();c['relationships_complete']=False
        self.assertFalse(check_settings(c,{'cleaning_mode':'mop','water_level':'high'})['compatible'])
    def test_unknown_option_and_missing_setting(self):
        self.assertFalse(check_settings(self.catalog(),{'cleaning_mode':'new_firmware_mode'})['compatible'])
