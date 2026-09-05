import copy
import unittest

from tools.build_bundle import build, migrate_v1_bundle, verify
from tools.resolve_estimate import resolve_estimate
from tools.validate import load_records, validate_dataset


class EstimateContractTests(unittest.TestCase):
    def setUp(self):
        self.records = load_records()
        self.estimate = next(r for r in self.records if r["kind"] == "estimate")

    def test_declared_quantity_is_a_labeled_estimate_not_a_measurement_or_profile(self):
        result = resolve_estimate(self.records, self.estimate["context"])
        self.assertEqual(result["status"], "labeled_estimate")
        self.assertEqual(result["source_type"], "manufacturer_declaration")
        self.assertEqual(result["quantity"]["unit"], "ml/action")
        self.assertFalse(any(r["kind"] == "profile" and r["review"]["status"] == "approved" for r in self.records))

    def test_wrong_model_and_incomplete_basis_are_unknown(self):
        wrong = copy.deepcopy(self.estimate["context"])
        wrong["model_id"] = "xiaomi_h50"
        self.assertEqual(resolve_estimate(self.records, wrong)["status"], "unknown")
        invalid = copy.deepcopy(self.records)
        next(r for r in invalid if r["kind"] == "estimate")["basis_ids"] = []
        with self.assertRaisesRegex(ValueError, "basis"):
            validate_dataset(invalid)

    def test_capacity_and_family_are_not_runtime_estimate_bases(self):
        invalid = copy.deepcopy(self.records)
        estimate = next(r for r in invalid if r["kind"] == "estimate")
        estimate["basis_kind"] = "tank_capacity"
        with self.assertRaisesRegex(ValueError, "capacity"):
            validate_dataset(invalid)
        invalid = copy.deepcopy(self.records)
        estimate = next(r for r in invalid if r["kind"] == "estimate")
        estimate["applicability"]["model_scope"] = "family"
        with self.assertRaisesRegex(ValueError, "family"):
            validate_dataset(invalid)

    def test_v2_bundle_contains_labeled_estimates_and_migrates_v1(self):
        bundle = build(self.records)
        self.assertEqual(bundle["manifest"]["schema_version"], 2)
        self.assertTrue(any(r["kind"] == "estimate" for r in verify(bundle)["records"]))
        v1 = build([r for r in self.records if r["kind"] != "estimate"], schema_version=1)
        self.assertEqual(migrate_v1_bundle(v1)["manifest"]["schema_version"], 2)
