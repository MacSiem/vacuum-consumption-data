# Estimate consumer contract (bundle schema v2)

Consumers read `kind: "estimate"` records only from a schema-v2 bundle. A v1 bundle may be deterministically repackaged with `tools.build_bundle.migrate_v1_bundle`; that migration adds no estimates or approvals.

Use `tools.resolve_estimate.resolve_estimate(records, context)`. It returns `labeled_estimate` only for a matching named model/action and all non-null scope fields. Display its label, source type, confidence category, method, basis IDs and limitations. Otherwise render `unknown`. Never convert it to a measured/approved profile, add it to a completion counter, or infer consumption from a reservoir capacity.

Schema v2 is backward-readable by `verify`; schema-v1 consumers must migrate or reject it explicitly. The bundle hash verifies bytes, not physical truth.

## Source research and current VWM import boundary

The full schema-v2 bundle contains all `load_records()` model, integration, observation, settings and estimate records, with only approved profile records retained. As of the November update, its four estimates comprise two existing H50 `labeled_runtime_estimate` records and two Concept `calibration_only` records. The latter remain research data: `resolve_estimate` returns unknown for their contexts.

The current VWM `compile_snapshot` rejects a bundle containing a non-runtime estimate. Do not import the full bundle, change Concept readiness, loosen the importer, or turn review claims into profiles to avoid that rejection. Build and verify an explicit consumer projection that excludes exactly `concept_vr4050_wash_standard_labeled` and `concept_vr4050_wash_deep_labeled`; preserve both H50 estimates unchanged. Record the full and projection payload/file hashes, excluded IDs and source revision in the handoff manifest. Both bundles retain all model/settings/observation records; the application snapshot itself retains only eligible estimates and profiles.

Canonical research quantities and limitations remain in [model provenance](../data/models), [settings](../data/settings), [observations](../data/observations), [Concept estimates](../data/estimates), and the [November inventory](../data/inventory/research-2026-11-04.json). The inventory includes ranges, source dates, short quotes and unqualified catalog gaps; it is outside `load_records()` and is not exported in the bundle or snapshot. A hash establishes lineage and integrity, never physical accuracy.

A reproducible projection uses the unchanged data builder:

```python
from tools.build_bundle import build, verify
from tools.validate import load_records

excluded = {
    "concept_vr4050_wash_standard_labeled",
    "concept_vr4050_wash_deep_labeled",
}
records = load_records()
full = build(records, source_revision=source_revision)
projection = build(
    [record for record in records if record["id"] not in excluded],
    source_revision=source_revision,
)
verify(full)
verify(projection)
```

`source_revision` must be the exact clean committed dataset revision. Assert the excluded records exist, remain `calibration_only`, and are the only difference between the full and projected record lists. Compile the snapshot with the consumer's actual importer at its own exact source pin without writing the application checkout. Keep the full bundle, projection, snapshot, generation command and manifest together for review.
