# Contributing

Submit a new model, a measurement, or a correction using the corresponding issue form. A factual declaration needs a manufacturer/integration source URL and access date. An empirical sample needs explicit publication consent and the measurement fields in the schema.

1. Use a new immutable observation ID. To correct an existing observation, explain the old ID and the correction in the PR; preserve the original pending review.
2. Specify the exact model/SKU/dock, firmware, integration version, reservoir, action and all known settings. Unknown is null; use `not_applicable` only with evidence that the setting is absent for this device/action.
3. Follow the calibration protocol. Never infer usage from tank capacity or convert unitless intensity to ml.
4. Submit only data you can share. Do not attach raw Diagnostics or maps. Review an export locally before submission. Relative sample IDs must not contain household/device identifiers.
5. Run the validators and tests. Include the coverage change in your PR. A declaration or experimental fit cannot be promoted simply by changing its confidence.

## Sanitized integration and replay evidence

For a binding, transition or missing-action report, use the public intake form and include: exact model/SKU and sales region; firmware; integration name and version; dock/robot reservoir; entity domain and canonical property or translation key; and the smallest relevant sanitized attribute/state-transition excerpt. Preserve only relative timestamps, event order and durations needed to replay the reported behavior. State which fields are unknown rather than guessing.

Do not post raw Diagnostics, access tokens, account or device IDs, serial numbers, unique IDs, MAC/IP addresses, room names, maps, geolocation, or absolute timestamps. Keep private physical measurement notes locally; publish only a consented, schema-complete measurement with non-identifying series/cycle IDs. A public manufacturer declaration is useful source evidence but is not a measured rate or runtime profile.

Maintainers verify source meaning, regional and firmware applicability, signal/action observation and independent validation. Require a separate reviewer for approved profiles. The automated checks detect inconsistency, not fabricated measurements; manual review and independent replication remain necessary. If a profile is contradicted, mark it revoked and keep its evidence available for review.

Code contributions use MIT. Contributor-owned measurements/database contributions use CC BY 4.0 as described in LICENSE-DATA.md. Linked third-party works retain their rights.

## Confirmed measurement packets from Vacuum Water Monitor

Sharing starts OFF. Save a confirmed physical measurement locally, select it, inspect the exact JSON preview, and explicitly accept CC BY 4.0 for that packet. Download the reviewed JSON and attach it to the maintained [measurement issue form](https://github.com/MacSiem/vacuum-consumption-data/issues/new?template=measurement.yml). The card does not send measurements automatically. Opening the blank GitHub form does not include data in its URL; submission is a separate action on GitHub.

Maintainers run `python3 -B tools/check_contribution.py downloaded-packet.json`. A successful result means eligible for manual review, never a runtime profile. The validator requires physical quantities, instrument resolution, quality confirmations, a reviewed model/integration/reservoir, explicit publication consent, and a strict field projection. Unknown technical fields may enter review as null; they cannot act as runtime wildcards. The export vocabulary constrains text for privacy and does not verify hardware capabilities or HA value mappings.

Review the source, measurement boundaries, instrument and context with the contributor. Assign public non-identifying observation/series/cycle IDs only after review; do not copy private IDs or timestamps. Convert accepted measurements to the existing observation contract with source provenance and consent. Keep whole-cycle ml separate from floor-only and wash-only evidence. The existing independent reviewer, verified binding/settings, identifiability and holdout gates remain required before adding an approved consumption profile. An experimental packet cannot approve itself.

Technical metadata and measured quantities may allow re-identification. GitHub exposes the submitting account. Submit only measurements you may publish. Request withdrawal in the repository; maintainers can revoke applicability and remove future distribution, but downloaded copies and public Git history may remain. No current household history is exported automatically.
