# Public source research — Water Monitor — 2026-09-05

## Result

This report covers a bounded public-source batch: Xiaomi Robot Vacuum H50 Pro / regional PL and UK pages, Roborock Qrevo, ECOVACS DEEBOT X8/OZMO, and the already-frozen Home Assistant source-contract fixture. It reduces known unresolved capability and setting questions, but does not make a worldwide or 356-protocol retail claim. The MIoT inventory remains `356` protocol IDs, `retail_denominator=unknown`, and `global_inventory_complete=false`.

The structured evidence ledger is [public-source-evidence-2026-09-05.json](public-source-evidence-2026-09-05.json). It records URL, access date, source authority, source hash status, normalized claim hash slot, evidence class, claim limitations and per-action `ready|blocked|complete` dispositions.

## Evidence findings

Xiaomi’s Polish and global product pages establish a public regional product identity for H50 Pro and manufacturer-declared mop/dock capability: clean and dirty tanks, mop hardware, automatic mop washing and drying. Xiaomi’s Polish/UK FAQ further states 4 L clean and dirty tanks, up to 32 mop-pad cleanings, first docking wash at 180 ml, and mid-task wash at 120 ml per cleaning. The FAQ describes the default mid-task trigger as 8 m² or 8 minutes, adjustable to 5/8/10, and mop lift of 10 mm.

These numbers are manufacturer declarations only. They are not measured physical millilitres, do not prove an HA completion counter, do not prove firmware stability, and cannot create an approved profile. They may be retained as declaration evidence with the stated conditions; they must not be used as a rate or as a completed-action event.

Roborock’s official Qrevo page documents adjustable water flow and dock mop washing with dynamic speed/water flow. ECOVACS’ official X8 pages document OZMO ROLLER fresh-water renewal, 16 nozzles, 200 washing actions per minute, mop washing, product-family reservoir/capability details, and selectable cleaning modes. These establish capability/settings applicability at product-family declaration level, not SKU/firmware-specific integration bindings, completion identities or ml rates.

The pinned HA fixture remains useful source semantics: six Roborock and three ECOVACS capability-dependent bindings. Its null model/SKU/firmware fields prevent exact-device approval. Existing source hashes and frozen MIoT hashes are retained; no frozen fixture or bundle was edited.

## Per-action remaining work

| Action | Remaining work | Evidence-backed disposition |
|---|---|---|
| `wash_mop` | Exact completion counter/terminal event and physical-ml stream for scoped model/SKU/firmware | `blocked` |
| `tray_clean` | Public terminal completion identity; process instructions alone are insufficient | `blocked` |
| `flush` | Exact station event/counter and measured quantity | `blocked` |
| `refill` | Completed refill identity plus physical supply measurement; preserve external supply edge | `blocked` |
| `detergent_dose` | Verified concentration/density and measured dose, otherwise not applicable | `blocked` |
| H50 Pro / Qrevo / X8 bounded retail+mop batch | Public regional/product-family evidence recorded; not a global inventory resolution | `complete` for this bounded research step |

## Evidence intake and resume conditions

To resume any blocked action, intake must include the exact public source URL or sanitized device trace, source access date and reproducible source hash where raw bytes are available; model ID, retail SKU, firmware, integration version, domain/key/unit and exact entity identity; and a completion counter increment or documented terminal event. For quantities, add timestamped physical-ml provenance, baseline/reservoir state, setting fingerprint, uninterrupted cycle boundaries and independent repeat/holdout information. A command acknowledgement, return-to-dock state, phase disappearance, tank capacity, marketed area or elapsed time is not completion evidence.

If device evidence is required, the resume condition is a user-provided sanitized intake from the exact device and a measurement protocol; this lane does not control HA or inspect private data.

## Constraints and non-actions

No schema, runtime, test, app-repository, frozen receipt, bundle or fixture was changed. No source declaration was promoted to `measured`, `approved` or `hardware_verified`; no rate was fabricated. No release, push or tag was performed. Any future import/code work requires a separate frozen implement handoff by the coordinator; this research lane does not implement it.

## Source ledger

See the structured JSON for all URLs, dates, hash status and claims. The raw bytes of browser-rendered manufacturer pages were not locally retrievable in this environment, so their `source_sha256` values are explicitly `null` with reason `raw_source_unavailable_from_browser_capture`; no empty or invented digest is used. Existing frozen local hashes are copied only for the already-read MIoT inventory and HA source-contract fixture.
