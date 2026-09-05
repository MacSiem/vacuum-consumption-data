# Measurement protocol v1 (provisional acceptance policy)

Record one reservoir and one identifiable scope at a time: floor_only, wash_only, or whole_cycle. Record water use in ml with instrument resolution. Mass-to-volume conversion needs known fluid density; detergent grams are not water millilitres.

Start/end levels must use the same reference, or measure refill to that reference. Record robot internal refill and transfers where needed to avoid counting dock water twice. Dirty return differs from clean withdrawal because of water left on surfaces, pads and plumbing. Distinguish pre-wetting, intermediate wash, final wash and tray cleaning.

Keep model, SKU, dock, firmware, integration version and settings constant throughout a sample. Record mode, intensity, route, passes, wash mode/frequency/temperature, adaptive mode and detergent setting. A mid-cycle change requires segments; if its timing cannot be observed, do not fit an individual-mode rate from that sample. Exclude interrupted/ambiguous samples from fitting while keeping them locally for investigation.

For a single exposure axis, record observed_ml and exposure in m2, min, action or cycle. Time is active mopping time, not whole mission duration; area must correspond to mopping, not vacuum-only coverage. A whole-cycle refill cannot independently identify floor and wash coefficients. Multiple wash settings require separate contexts. Adaptive modes require observed influencing inputs or a separately evaluated aggregate model.

The first implementation fits the median of per-sample ratios for one axis. At least three distinct training cycles are required. It never marks the result runtime eligible. Promotion to a shared empirical profile additionally requires five holdout cycles, at least three contributing device series overall, no device-series overlap between training and holdout, identical context/scope, and recomputed error metrics. These are minimum organizational checks, not proof of statistical significance or 95% confidence.

Provisional validation policy: every holdout error must be <= max(10% observed_ml, 2 * instrument_resolution_ml). Report actual absolute and relative maxima. A maintainer must assess whether measurement resolution, sample diversity and error are adequate for the claimed use; no approved real profiles currently exist. This threshold must be reviewed before first production promotion.

Keep private device IDs and absolute timestamps locally. Public samples use random series/cycle IDs, public product identity and explicit publication consent. A GitHub contribution is voluntary; do not initiate robot actions merely to collect data, and do not automatically upload Home Assistant history.
