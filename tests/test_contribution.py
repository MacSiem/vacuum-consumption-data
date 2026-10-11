"""Synthetic intake packets prove validation, never physical water rates."""
import json
import unittest
from copy import deepcopy
from tools import contribution as c

CATALOG = {'roborock_s8_maxv_ultra':{'integration_adapters':['roborock'],
             'reservoirs_ml':{'dock_clean':4000}}}


def sample():
    return {'id':'local.private.123', 'device_id':'vacuum.house_private', 'confirmed':True,
        'context':{'model_id':'roborock_s8_maxv_ultra','sku':'EU','dock_variant':'tank',
            'firmware':'2.39.60','integration_id':'roborock','integration_version':'2026.10.0',
            'reservoir':'dock_clean','action':'whole_cycle',
            'settings':{**dict.fromkeys(c.SETTINGS,'not_applicable'),
                'mop_mode':'standard','water_level':'medium','wash_mode':'standard',
                'wash_frequency':'15min','wash_temperature':'60_c','cleaning_mode':'vac_and_mop'}},
        'observed_ml':300,'resolution_ml':5,'area_m2':10,
        'instrument':'graduated_jug','purpose':'training','scope':'whole_cycle',
        'quality':dict(c.QUALITY)}


class ContributionTests(unittest.TestCase):
    def test_preview_is_not_consented_but_a_confirmed_packet_can_enter_review(self):
        preview = c.build_confirmed_contribution([sample()],public_catalog=CATALOG)
        self.assertFalse(preview['publication_consent'])
        self.assertFalse(c.validate_contribution(preview,public_catalog=CATALOG)['submission_eligible'])
        packet = c.build_confirmed_contribution([sample()],public_catalog=CATALOG,consent_cc_by_4_0=True)
        result = c.validate_contribution(packet,public_catalog=CATALOG)
        self.assertTrue(result['submission_eligible'])
        self.assertTrue(result['review_needed'])
        self.assertFalse(result['runtime_eligible'])

    def test_identifiers_dates_urls_and_unsupported_text_never_escape(self):
        s=sample();s.update(ts=123,token='secret',map='Kitchen',ip='192.168.1.9',account='private-account-value')
        s['context'].update(sku='my-house-id',firmware='192.168.1.9',account='private-account-value')
        s['context']['settings']['route']='Kitchen private room'
        packet=c.build_confirmed_contribution([s],public_catalog=CATALOG)
        text=json.dumps(packet)
        for forbidden in ('local.private','vacuum.house','my-house-id','Kitchen','192.168','secret','private-account-value'):
            self.assertNotIn(forbidden,text)
        ctx=packet['samples'][0]['context']
        self.assertIsNone(ctx['sku']);self.assertIsNone(ctx['firmware'])
        self.assertIsNone(ctx['settings']['route'])

    def test_unknown_context_is_intake_only_and_never_a_runtime_wildcard(self):
        s=sample();s['context']['sku']='unreviewed variant'
        p=c.build_confirmed_contribution([s],public_catalog=CATALOG,consent_cc_by_4_0=True)
        r=c.validate_contribution(p,public_catalog=CATALOG)
        self.assertTrue(r['submission_eligible'])
        self.assertFalse(r['runtime_eligible'])
        self.assertIn('context.sku',p['unknowns'])

    def test_unconfirmed_duplicate_bad_quality_and_impossible_quantities_rejected(self):
        for key,value in [('confirmed',False),('observed_ml',float('inf')),
                          ('observed_ml',True),('observed_ml',5000),('resolution_ml',300)]:
            s=sample();s[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                c.build_confirmed_contribution([s],public_catalog=CATALOG)
        s=sample();s['quality']['uninterrupted']=False
        with self.assertRaises(ValueError):c.build_confirmed_contribution([s],public_catalog=CATALOG)
        with self.assertRaises(ValueError):c.build_confirmed_contribution([sample(),sample()],public_catalog=CATALOG)

    def test_external_packets_cannot_smuggle_extra_fields_or_promote_themselves(self):
        p=c.build_confirmed_contribution([sample()],public_catalog=CATALOG,consent_cc_by_4_0=True)
        for mutate in (lambda x:x.update(runtime_eligible=True),
                       lambda x:x['samples'][0].update(ts=123),
                       lambda x:x['samples'][0]['context']['settings'].update(room='Kitchen')):
            changed=deepcopy(p);mutate(changed)
            self.assertFalse(c.validate_contribution(changed,public_catalog=CATALOG)['submission_eligible'])
