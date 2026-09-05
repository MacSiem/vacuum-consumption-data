# Public source inventory v2 — Water Monitor — 2026-09-05

## Scope

Ten manufacturer source families were fetched once and recorded for reuse. The frozen MIoT inventory contains **356 unresolved records in 43 exact namespace groups**; no worldwide retail denominator is claimed. H50/Qrevo/X8 were excluded as already covered by v1.

## Grouping and evidence

Groups are `namespace:<literal first protocol-id segment>`. Every `record_id` is listed exactly once in the JSON and receives the group disposition/blocker. Candidate aliases are lexical only; no cross-namespace merge or inheritance of SKU, mopping capability, rates or hardware status is allowed. JSON records each source URL/date, separate claim hash and explicit null raw-source hash because browser raw bytes were unavailable locally.

## Group coverage

| Group | Records | Disposition | Next |
|---|---:|---|---|
| `namespace:dreame` | 48 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:roborock` | 46 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:xiaomi` | 43 | `unknown_exact_mapping_after_family_source` | ready |
| `namespace:narwa` | 36 | `unknown_exact_mapping_after_family_source` | ready |
| `namespace:viomi` | 33 | `unknown_exact_mapping_after_family_source` | ready |
| `namespace:eco` | 32 | `unknown_exact_mapping_after_family_source` | ready |
| `namespace:yeedi` | 16 | `unknown_exact_mapping_after_family_source` | ready |
| `namespace:ijai` | 12 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:zhimi` | 12 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:deerma` | 11 | `unknown_exact_mapping_after_family_source` | ready |
| `namespace:xtl` | 8 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:roidmi` | 7 | `unknown_exact_mapping_after_family_source` | ready |
| `namespace:mijia` | 6 | `unknown_exact_mapping_after_family_source` | ready |
| `namespace:jdyw` | 5 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:miot` | 4 | `unknown_exact_mapping_after_family_source` | ready |
| `namespace:chuangmi` | 3 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:gdyimu` | 3 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:girt` | 2 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:hanyi` | 2 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:meijin` | 2 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:szkj` | 2 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:yonsz` | 2 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:360sdj` | 1 | `unknown_exact_mapping_after_family_source` | ready |
| `namespace:beem` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:cgzn` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:dji` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:doit` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:ghome` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:homend` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:ilife` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:iot` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:lambot` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:onej` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:orvibo` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:puppy` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:rockrobo` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:scinan` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:swhome` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:tab` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:tuya` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:xzh` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:yuerzj` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |
| `namespace:zigma` | 1 | `blocked_no_identifiable_primary_source_after_group_search` | blocked |

## Mechanical consistency and handoff

The JSON coverage block and groups permit checks for input/output counts, unique IDs, source references and group sums. `remaining_ready_group_order` contains all groups with candidate family sources (not resolved crosswalks); other groups are concrete blockers after documented search. Every record still needs exact retail SKU/region, protocol/model crosswalk, mopping capability and active-firmware applicability. Rates and action completion remain blocked pending measured/device evidence.

## Non-actions

No schema, runtime, tests, fixtures, frozen bundle, app repo, private HA data, release, push, tag, model, service, mode or child was changed. No approved profile or rate was created. Full 356-record ledger: `reports/public-source-inventory-v2.json`.
