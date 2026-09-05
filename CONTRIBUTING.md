# Contributing

Submit a new model, a measurement, or a correction using the corresponding issue form. A factual declaration needs a manufacturer/integration source URL and access date. An empirical sample needs explicit publication consent and the measurement fields in the schema.

1. Use a new immutable observation ID. To correct an existing observation, explain the old ID and the correction in the PR; preserve the original pending review.
2. Specify the exact model/SKU/dock, firmware, integration version, reservoir, action and all known settings. Unknown is null; use `not_applicable` only with evidence that the setting is absent for this device/action.
3. Follow the calibration protocol. Never infer usage from tank capacity or convert unitless intensity to ml.
4. Submit only data you can share. Do not attach raw Diagnostics or maps. Review an export locally before submission. Relative sample IDs must not contain household/device identifiers.
5. Run the validators and tests. Include the coverage change in your PR. A declaration or experimental fit cannot be promoted simply by changing its confidence.

Maintainers verify source meaning, regional and firmware applicability, signal/action observation and independent validation. Require a separate reviewer for approved profiles. The automated checks detect inconsistency, not fabricated measurements; manual review and independent replication remain necessary. If a profile is contradicted, mark it revoked and keep its evidence available for review.

Code contributions use MIT. Contributor-owned measurements/database contributions use CC BY 4.0 as described in LICENSE-DATA.md. Linked third-party works retain their rights.
