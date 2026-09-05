import copy
import json
import unittest
from pathlib import Path

from tools.contracts_v2 import migrate_v1_payload, validate_import, validate_live_envelope, validate_replay, validate_source_contracts
from test_calibration import sample_dataset


ROOT = Path(__file__).resolve().parents[1]


def fixture(name):
    return json.loads((ROOT / "fixtures" / name).read_text())


class ContractV2Tests(unittest.TestCase):
    def test_source_contracts_preserve_unknown_completion(self):
        source = fixture("source-contracts-2026-09-05.json")
        validate_source_contracts(source)
        self.assertEqual(source["action_completion"]["wash_mop"]["disposition"], "unknown")
        self.assertEqual(len(source["bindings"]), 9)

    def test_replay_has_hand_calculated_five_reservoir_balance(self):
        replay = fixture("synthetic-replay-v2.json")
        result = validate_replay(replay)
        self.assertEqual(result["final_reservoirs"], replay["expected_final_reservoirs"])
        self.assertEqual(result["completed_actions"], ["wash-1"])
        self.assertEqual(result["aborted_actions"], ["wash-2"])
        self.assertEqual(result["external_supply_ml"], 300)

    def test_replay_rejects_counting_command_or_aborted_action_as_completion(self):
        replay = fixture("synthetic-replay-v2.json")
        replay["events"][0]["completion_evidence"] = "command"
        with self.assertRaises(ValueError):
            validate_replay(replay)
        replay = fixture("synthetic-replay-v2.json")
        replay["events"][2]["completed"] = True
        with self.assertRaises(ValueError):
            validate_replay(replay)

    def test_replay_rejects_unbalanced_transfer_and_overlapping_segments(self):
        replay = fixture("synthetic-replay-v2.json")
        replay["events"][0]["edges"][0]["amount_ml"] = 99
        with self.assertRaises(ValueError):
            validate_replay(replay)
        replay = fixture("synthetic-replay-v2.json")
        replay["setting_segments"][1]["start"] = 4
        with self.assertRaises(ValueError):
            validate_replay(replay)

    def test_import_gate_rejects_legacy_and_nonmeasured_profiles(self):
        rows = sample_dataset()
        profile = copy.deepcopy(rows[-1])
        profile.update(evidence_class="empirical", accounting_contract="v2")
        payload = {"schema_version": 2, "envelope_kind": "portable_import", "source_payload_sha256": "a" * 64, "records": rows[:-1] + [profile]}
        validate_import(payload)
        for bad in (
            {"schema_version": 1, "records": []},
            dict(payload, records=rows[:-1] + [dict(profile, confidence="synthetic", evidence_class="synthetic")]),
            dict(payload, records=rows[:-1] + [dict(profile, review={"status":"experimental", "reviewer":"fixture_reviewer"})]),
        ):
            with self.assertRaises(ValueError):
                validate_import(bad)

    def test_import_requires_a_versioned_envelope_and_complete_referenced_records(self):
        rows = sample_dataset()
        profile = copy.deepcopy(rows[-1])
        profile.update(evidence_class="empirical", accounting_contract="v2")
        payload = {"schema_version": 2, "envelope_kind": "portable_import", "source_payload_sha256": "a" * 64, "records": [profile]}
        with self.assertRaises(ValueError):
            validate_import(payload)
        payload["records"] = rows[:-1] + [profile]
        validate_import(payload)
        for field in ("id", "context", "coefficient", "unit", "evidence_ids", "validation"):
            malformed = copy.deepcopy(payload)
            malformed["records"][-1].pop(field)
            with self.assertRaises(ValueError, msg=field):
                validate_import(malformed)

    def test_import_rejects_invalid_envelope_and_boolean_schema_version(self):
        for payload in ({}, {"schema_version": True, "envelope_kind": "portable_import", "source_payload_sha256": "a" * 64, "records": []}, {"schema_version": 2, "envelope_kind": "portable_import", "source_payload_sha256": "bad", "records": []}):
            with self.assertRaises(ValueError):
                validate_import(payload)

    def test_v1_migration_never_fabricates_a_v2_profile(self):
        migrated = migrate_v1_payload({"schema_version": 1, "records": [{"kind": "profile", "review": {"status": "approved"}, "confidence": "validated"}]})
        self.assertEqual(migrated["schema_version"], 2)
        self.assertEqual(migrated["records"][0]["accounting_contract"], "missing")
        with self.assertRaises(ValueError):
            validate_import(migrated)

    def test_v1_evidence_only_migration_has_a_strict_v2_envelope(self):
        rows = sample_dataset()[:-1]
        migrated = migrate_v1_payload({"schema_version": 1, "records": rows})
        self.assertEqual(migrated["envelope_kind"], "portable_import")
        self.assertRegex(migrated["source_payload_sha256"], r"^[0-9a-f]{64}$")
        validate_import(migrated)

    def test_replay_rejects_completed_aborted_and_negative_intermediate_balance(self):
        replay = fixture("synthetic-replay-v2.json")
        replay["events"][0]["aborted"] = True
        with self.assertRaises(ValueError):
            validate_replay(replay)
        replay = fixture("synthetic-replay-v2.json")
        replay["events"][0]["edges"][0]["amount_ml"] = 101
        with self.assertRaises(ValueError):
            validate_replay(replay)

    def test_replay_rejects_bad_quantities_self_edges_and_unlive_synthetic_events(self):
        for amount in (True, float("inf"), -1):
            replay = fixture("synthetic-replay-v2.json")
            replay["events"][0]["edges"][0]["amount_ml"] = amount
            with self.assertRaises(ValueError):
                validate_replay(replay)
        replay = fixture("synthetic-replay-v2.json")
        replay["events"][0]["edges"][0]["to"] = "robot_clean"
        with self.assertRaises(ValueError):
            validate_replay(replay)
        with self.assertRaises(ValueError):
            validate_live_envelope(fixture("synthetic-replay-v2.json"), fixture("source-contracts-2026-09-05.json"), now_ms=1_007_000)

    def test_source_contracts_are_scoped_six_roborock_plus_three_ecovacs(self):
        source = fixture("source-contracts-2026-09-05.json")
        validate_source_contracts(source)
        self.assertEqual(sum(b["integration"] == "integration.roborock" for b in source["bindings"]), 6)
        self.assertEqual(sum(b["integration"] == "integration.ecovacs" for b in source["bindings"]), 3)
        self.assertIn("route", [b["role"] for b in source["bindings"]])
        self.assertTrue(all("scope" in row for row in source["bindings"] + source["settings"]))

    def test_replay_requires_event_membership_in_half_open_epoch_segments(self):
        replay = fixture("synthetic-replay-v2.json")
        replay["events"][0]["segment_id"] = "segment-high"
        with self.assertRaises(ValueError):
            validate_replay(replay)
        replay = fixture("synthetic-replay-v2.json")
        replay["events"][1]["observed_at_ms"] = replay["setting_segments"][0]["end_at_ms"]
        with self.assertRaises(ValueError):
            validate_replay(replay)
        replay = fixture("synthetic-replay-v2.json")
        replay["events"][0]["observed_at_ms"] = replay["baseline_observed_at_ms"] - 1
        with self.assertRaises(ValueError):
            validate_replay(replay)

    def test_replay_rejects_reverse_clock_order(self):
        replay = fixture("synthetic-replay-v2.json")
        replay["events"][2]["observed_at_ms"] = replay["events"][1]["observed_at_ms"]
        with self.assertRaises(ValueError):
            validate_replay(replay)

    def test_synthetic_live_contract_exercises_freshness_and_clock_skew(self):
        replay = fixture("synthetic-live-event-stream-v2.json")
        source = fixture("synthetic-live-source-contract-v2.json")
        validate_live_envelope(replay, source, now_ms=1_000_010)
        with self.assertRaises(ValueError):
            validate_live_envelope(replay, source, now_ms=1_200_006)
        with self.assertRaises(ValueError):
            validate_live_envelope(replay, source, now_ms=990_000)

    def test_live_hardware_flag_without_evidence_or_exact_scope_is_rejected(self):
        replay = fixture("synthetic-live-event-stream-v2.json")
        replay.update(fixture_class="physical_event_stream", source_provenance="physical_ml")
        replay["events"][0]["quantity_provenance"] = "physical_ml"
        source = fixture("synthetic-live-source-contract-v2.json")
        source.update(fixture_class="source_contract", hardware_verified=True, verification={"status": "hardware_verified", "evidence": []})
        with self.assertRaises(ValueError):
            validate_live_envelope(replay, source, now_ms=1_000_010)
        source["verification"]["evidence"] = [{"kind": "registry_fixture", "source": "https://example.org/proof", "recorded_at_ms": 1_000_000}]
        source["bindings"][0]["scope"]["firmware"] = "other"
        with self.assertRaises(ValueError):
            validate_live_envelope(replay, source, now_ms=1_000_010)
