"""Portable v2 contracts for app import and synthetic accounting replay.

These contracts deliberately live beside dataset-v1 records: v1 remains a
portable evidence bundle, while v2 makes complete-action accounting explicit.
"""
import copy
import hashlib
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator

from tools.validate import ROOT, canonical

RESERVOIRS = ("dock_clean", "dock_dirty", "robot_clean", "robot_dirty", "detergent")
COMPLETION_EVIDENCE = ("counter_increment", "terminal_event")
MAX_LIVE_AGE_MS = 120_000
MAX_CLOCK_SKEW_MS = 5_000
SCOPE_KEYS = ("model_id", "sku", "firmware", "integration_id", "integration_version", "domain", "key", "unit")


def _schema(name):
    return json.loads((ROOT / "schemas" / name).read_text())


def _validate(schema_name, value):
    try:
        Draft202012Validator(_schema(schema_name)).validate(value)
    except Exception as error:
        raise ValueError(str(error)) from error


def validate_source_contracts(source):
    _validate("source-contract-v2.schema.json", source)
    names = set()
    for binding in source["bindings"]:
        if set(binding) != {"id", "integration", "role", "key", "state", "scope", "source"}:
            raise ValueError("malformed source binding")
        if binding["id"] in names:
            raise ValueError("duplicate binding")
        names.add(binding["id"])
        if binding["scope"]["integration_id"] != binding["integration"] or binding["scope"]["key"] != binding["key"]:
            raise ValueError("binding identity/scope mismatch")
        if set(binding["scope"]) != set(SCOPE_KEYS):
            raise ValueError("incomplete source scope")
    for setting in source["settings"]:
        if set(setting) != {"name", "state", "scope"} or set(setting["scope"]) != set(SCOPE_KEYS):
            raise ValueError("malformed scoped setting")
    for action, disposition in source["action_completion"].items():
        if disposition["disposition"] == "complete" and disposition["evidence"] not in COMPLETION_EVIDENCE:
            raise ValueError(f"{action}: command/state is not completion evidence")
        if disposition["disposition"] != "complete" and disposition["evidence"] in COMPLETION_EVIDENCE:
            raise ValueError(f"{action}: completion evidence requires complete disposition")
    return source


def validate_replay(replay):
    _validate("accounting-replay-v2.schema.json", replay)
    if replay["fixture_class"] == "synthetic_accounting_replay" and replay["source_provenance"] != "synthetic":
        raise ValueError("synthetic fixture needs synthetic provenance")
    balances = dict(replay["initial_reservoirs"])
    completed, aborted = [], []
    last_end = replay["baseline_observed_at_ms"]
    segment_ids = set()
    for segment in replay["setting_segments"]:
        if segment["start_at_ms"] != last_end or segment["end_at_ms"] <= segment["start_at_ms"]:
            raise ValueError("setting segments must be contiguous nonempty epoch-ms intervals")
        if segment["id"] in segment_ids:
            raise ValueError("duplicate setting segment")
        segment_ids.add(segment["id"])
        last_end = segment["end_at_ms"]
    seen = set()
    supplied = 0
    last_sequence = 0
    last_timestamp = -1
    for event in replay["events"]:
        if event["id"] in seen:
            raise ValueError("duplicate event id")
        seen.add(event["id"])
        if event["sequence"] != last_sequence + 1 or event["observed_at_ms"] <= last_timestamp:
            raise ValueError("events require contiguous sequence and strictly increasing timestamps")
        if event["segment_id"] not in segment_ids:
            raise ValueError("unknown setting segment")
        segment = next(item for item in replay["setting_segments"] if item["id"] == event["segment_id"])
        if not segment["start_at_ms"] <= event["observed_at_ms"] < segment["end_at_ms"]:
            raise ValueError("event is outside its half-open setting segment")
        if event["observed_at_ms"] < replay["baseline_observed_at_ms"]:
            raise ValueError("event predates measured baseline")
        last_sequence, last_timestamp = event["sequence"], event["observed_at_ms"]
        if event["completed"] and event["aborted"]:
            raise ValueError("operation cannot be both completed and aborted")
        if event["completed"]:
            if event["completion_evidence"] not in COMPLETION_EVIDENCE:
                raise ValueError("command, phase disappearance, and return state do not complete an action")
            completed.append(event["id"])
        elif event["completion_evidence"] in COMPLETION_EVIDENCE:
            raise ValueError("aborted operation cannot claim completion evidence")
        if event["aborted"]:
            aborted.append(event["id"])
        for edge in event["edges"]:
            amount = edge["amount_ml"]
            origin, target = edge["from"], edge["to"]
            if isinstance(amount, bool) or not math.isfinite(amount) or amount <= 0:
                raise ValueError("transfer amount must be finite positive number")
            if origin == target:
                raise ValueError("self transfer is not a physical edge")
            if origin in balances:
                balances[origin] -= amount
            elif origin != "external_supply":
                raise ValueError("unknown transfer origin")
            else:
                supplied += amount
            if target in balances:
                balances[target] += amount
            elif target != "external_drain":
                raise ValueError("unknown transfer target")
            if any(value < 0 for value in balances.values()):
                raise ValueError("negative intermediate reservoir balance")
    if balances != replay["expected_final_reservoirs"]:
        raise ValueError("replay balance differs from hand-calculated result")
    return {"final_reservoirs": balances, "completed_actions": completed, "aborted_actions": aborted, "external_supply_ml": supplied}


def validate_import(payload):
    _validate("portable-import-v2.schema.json", payload)
    projected = []
    for record in payload["records"]:
        if not isinstance(record, dict):
            raise ValueError("record must be object")
        projected_record = copy.deepcopy(record)
        projected_record.pop("evidence_class", None)
        projected_record.pop("accounting_contract", None)
        projected.append(projected_record)
    from tools.validate import validate_dataset
    validate_dataset(projected)
    for record in payload["records"]:
        if record.get("kind") != "profile":
            continue
        if record.get("review", {}).get("status") != "approved":
            raise ValueError("unapproved profile")
        if record.get("confidence") != "validated" or record.get("evidence_class") != "empirical":
            raise ValueError("declaration or synthetic profile cannot be imported")
        if record.get("accounting_contract") != "v2":
            raise ValueError("profile lacks a v2 complete-action accounting contract")
    return payload


def validate_live_envelope(replay, source_contracts, *, now_ms):
    validate_source_contracts(source_contracts)
    if isinstance(now_ms, bool) or not isinstance(now_ms, int) or now_ms < 0:
        raise ValueError("now_ms must be an epoch-millisecond integer")
    synthetic_test = replay.get("fixture_class") == "synthetic_live_event_stream_test_only"
    physical = replay.get("fixture_class") == "physical_event_stream"
    if not (physical or synthetic_test):
        raise ValueError("synthetic/declarative replay cannot be treated as a live stream")
    if physical and replay.get("source_provenance") != "physical_ml":
        raise ValueError("physical stream requires physical-ml provenance")
    if synthetic_test and replay.get("source_provenance") != "synthetic_physical_ml_test_only":
        raise ValueError("synthetic live test requires explicit test-only provenance")
    validate_replay(replay)
    verification = source_contracts.get("verification", {})
    if physical:
        if source_contracts.get("fixture_class") != "source_contract" or not source_contracts["hardware_verified"] or verification.get("status") != "hardware_verified":
            raise ValueError("live source requires hardware verification, not a flag alone")
        evidence = verification.get("evidence", [])
        if not evidence or not all(isinstance(item, dict) and item.get("kind") in {"registry_fixture", "terminal_counter", "physical_measurement"} and isinstance(item.get("source"), str) for item in evidence):
            raise ValueError("live source lacks verification evidence")
    elif source_contracts.get("fixture_class") != "synthetic_live_contract_test_only" or verification.get("status") != "synthetic_test_only":
        raise ValueError("synthetic live stream requires paired test-only source contract")
    bindings = {binding["id"]: binding for binding in source_contracts["bindings"]}
    for event in replay["events"]:
        binding = bindings.get(event["source_contract_id"])
        if binding is None:
            raise ValueError("unknown source contract id")
        for key in ("model_id", "sku", "firmware", "integration_id", "integration_version"):
            scoped = binding["scope"][key]
            if scoped is not None and scoped != replay["device_identity"][key]:
                raise ValueError("source scope does not match device identity")
        if event["quantity_provenance"] != "physical_ml":
            if not (synthetic_test and event["quantity_provenance"] == "synthetic"):
                raise ValueError("live transfer needs physical ml provenance")
    latest = replay["events"][-1]["observed_at_ms"]
    if latest > now_ms + MAX_CLOCK_SKEW_MS or replay["baseline_observed_at_ms"] > now_ms + MAX_CLOCK_SKEW_MS:
        raise ValueError("future baseline/event exceeds clock-skew allowance")
    if now_ms - latest > MAX_LIVE_AGE_MS:
        raise ValueError("live stream is stale")
    return replay


def migrate_v1_payload(payload):
    """Losslessly wrap v1 evidence; never fabricate a v2 accounting profile."""
    if payload.get("schema_version") != 1:
        raise ValueError("only v1 payloads may be migrated")
    records = []
    for record in payload.get("records", []):
        migrated = dict(record)
        if record.get("kind") == "observation":
            migrated["evidence_class"] = record["source_class"]
        if record.get("kind") == "profile":
            migrated["accounting_contract"] = "missing"
        records.append(migrated)
    return {"schema_version": 2, "envelope_kind": "portable_import", "source_payload_sha256": hashlib.sha256(canonical(payload)).hexdigest(), "records": records}
