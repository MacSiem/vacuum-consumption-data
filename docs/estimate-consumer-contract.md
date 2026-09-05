# Estimate consumer contract (bundle schema v2)

Consumers read `kind: "estimate"` records only from a schema-v2 bundle. A v1 bundle may be deterministically repackaged with `tools.build_bundle.migrate_v1_bundle`; that migration adds no estimates or approvals.

Use `tools.resolve_estimate.resolve_estimate(records, context)`. It returns `labeled_estimate` only for a matching named model/action and all non-null scope fields. Display its label, source type, confidence category, method, basis IDs and limitations. Otherwise render `unknown`. Never convert it to a measured/approved profile, add it to a completion counter, or infer consumption from a reservoir capacity.

Schema v2 is backward-readable by `verify`; schema-v1 consumers must migrate or reject it explicitly. The bundle hash verifies bytes, not physical truth.
