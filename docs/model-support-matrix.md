# Model support matrix

This is a scope matrix, not a compatibility promise. A protocol ID or entity alone does not mean full model support.

| Model/family | Integration detection | Available data | Runtime estimate | User calibration / unknown |
| --- | --- | --- | --- | --- |
| Roborock (six scoped source contracts) | Documented source-only signal contracts; hardware verification remains false | Best current integration-signal inventory, no public physical consumption cycle | Unknown; no rate or completion binding is inferred | Mop/mop-wash sessions, exact model/SKU/firmware and sanitized transitions needed |
| Xiaomi Robot Vacuum H50 Pro | No verified HA binding | Manufacturer declaration: 180 ml first wash; 120 ml mid-task wash | Labeled estimate for named action/model only; SKU, firmware and HA action mapping unknown | User measurement can calibrate and may replace limitations with evidence |
| Concept VR4050 | No verified HA binding | Manufacturer declarations: 130 ml standard / 215 ml deep mop wash | Unknown: source-limited `calibration_only` estimates are retained with observations; no runtime mapping is established | Need model/SKU/firmware, wash mode and sanitized action evidence |
| Roborock S7 MaxV Ultra / Qrevo 5AE / Q8 Max+ | No new hardware verification | Public reports: deep rinse about 250 ml / deep wash about 150–160 ml / high-water tank weighing about 0.4 ml/ft² | No new executable rate; reports remain model provenance and research findings | Instruments, resolution, exact scope, firmware applicability and independent holdout incomplete |
| Tapo RV50 Omni / Pro | Source settings only; model and firmware vary | Wash frequency/mode controls, with regional conflicts retained | No new rate or hot-wash capability inferred for non-Pro | Match exact variant and observable wet phase before use |
| Dreame / MOVA / Ecovacs roller research | Source-only controls and reservoir declarations | Adaptation, rewash/remop, transfer and continuous rinsing described | No new measured coefficient or shared profile | Unexposed decisions and wet-area semantics remain gaps |
| Other catalogued models/families | Candidate/source-only or unknown | Identity/inventory data may exist; consumption basis often unknown | Unknown | Partial processed sessions are useful; family data never proves a specific SKU |

All current estimates are visibly labeled and source-backed. None is a measurement, approved profile, or proof that a completion counter may increment.

The [November research inventory](../data/inventory/research-2026-11-04.json) records the model-specific sources and remaining catalog gaps. See the [consumer contract](estimate-consumer-contract.md) for the full-bundle versus VWM-projection boundary.
