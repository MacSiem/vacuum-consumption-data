# Frozen Water dataset receipt — 2026-09-05

Input handoff SHA-256: `3589049c8f1c391146589970e6c7c9e911fbb30314bafd31b997c478b964474a`.

The source inventory contains 356 MIoT protocol IDs. Each is emitted in `reports/miot-inventory-dispositions.json` with the source URL, source SHA-256, retail SKU (currently `unknown` where not verified), disposition, owner and next step. No disposition is `goalPASS`; a protocol specification is not retail or mopping proof.

Source fixture `fixtures/source-contracts-2026-09-05.json` preserves exactly six Roborock and three Ecovacs pinned, capability-dependent source contracts, thirteen scoped setting states, and five scoped action-completion dispositions. It is source-documented but hardware-unverified. Completion is 0/5 verified: commands/states are deliberately not promoted to completion evidence.

Portable schema v2 is specified in `protocols/portable-schema-v2.md`, `schemas/source-contract-v2.schema.json` and `schemas/accounting-replay-v2.schema.json`. `fixtures/synthetic-replay-v2.json` is synthetic-only and exercises five reservoirs, setting segments, restart, partial/aborted operation, transfer edges and plumbed supply. Its hand-calculated final balance is dock clean 1260 ml, dock dirty 100 ml, robot clean 90 ml, robot dirty 50 ml and detergent 50 ml; external supply is 300 ml. It is not a measured profile.

Proposed application-ledger integration (application repo remains read-only here): consume only schema-v2 envelopes accepted by `validate_import`; retain v1 evidence as non-runtime evidence; bind live action completion only to a hardware-verified scoped counter/terminal-event identity; replay contiguous timestamped event IDs per installation+vacuum identity; show every unknown denominator rather than a coverage percentage.

Remaining blockers: regional retail/SKU and mopping verification for 356 IDs; real sanitized registry fixtures by model/firmware; source-backed completion counters/events; physical measured cycles for all rate claims; independent holdout devices before any approved profile. Owner: manufacturer/region researcher, device reporter, and measurement contributor respectively.
