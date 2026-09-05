# Vacuum Consumption Data

An open-data project for water and detergent consumption of mopping robots, independent of Home Assistant and usable by other applications.

**Pre-publication local dataset. Universal consumption coverage is incomplete.** The initial collection contains 134 researched model records, 23 integration inventory records and four manufacturer-declared wash quantities and five partial settings catalogues. There are no approved consumption profiles and no submitted empirical measurements. The 356 MIoT protocol specifications are an unresolved inventory, not 356 verified retail mopping robots.

## Data layers

- `data/models`: public identity, regional variants and separately identified reservoirs. Unknown capacities are null.
- `data/integrations`: protocol/integration provenance and binding status. Candidate association is not verified compatibility.
- `data/observations`: immutable manufacturer declarations or consented measurements. An observation is never a runtime profile.
- `data/settings`: known options and conditional compatibility rules. An unverified combination is not inferred from individual options.
- `data/consumption_profiles`: reviewed parameters with exact applicability and independently recomputed validation metrics. Currently empty.
- `data/inventory`: public protocol research and migration provenance, not executable profiles.
- `reports`: machine-readable coverage and CSV. Missing data remains visible.

Keys include model, SKU, dock, firmware, integration version, reservoir, action and settings. Null never means "any". Current profile contracts use exact version matching; range compatibility requires a future reviewed extension. A setting such as water level 3 is not a measured number of millilitres.

## Local validation

Use Python 3.11+ in a virtual environment, install `requirements.txt`, then run:

```sh
python -m unittest discover -s tests
python -m tools.validate
python -m tools.report_coverage
python -m tools.build_bundle
```

The bundle is sorted canonical JSON with schema/dataset versions and a SHA-256 payload digest. This establishes integrity and deterministic content, not publisher authenticity. Consumers must obtain an approved snapshot from a trusted revision; no executable code is included in the bundle.

`tools.fit_profiles.fit_coefficient` estimates a single exposure axis from measurements with identical context and scope. It does not solve a hybrid floor/wash model from whole-cycle refill data. Separate observations are required to identify separate processes. Multi-axis fitting, complete per-brand research and end-to-end app integration remain open work.

See [calibration protocol](protocols/calibration.md), [contribution rules](CONTRIBUTING.md) and [coverage](reports/coverage.csv). Data corrections must preserve earlier observation IDs; a disputed measurement is not silently replaced. Profiles can be experimental, approved or revoked. Approval requires a maintainer review in addition to schema/consistency checks; a submitted boolean cannot establish hardware truth.

## Licensing

Original project code is MIT licensed (LICENSE). Original database organization and contributed data are intended for CC BY 4.0 with retained source attribution; see LICENSE-DATA.md. Linked manufacturer documents and upstream code retain their own rights and are not relicensed. We store short factual descriptions and public protocol metadata, not copies of manuals or private Diagnostics.

## Check your robot and help improve coverage

Look up your model in [coverage.csv](reports/coverage.csv), inspect its sources and report missing or incorrect settings. Contributions for any model are welcome, including a single well-documented mode. See [LLM-assisted contribution guidance](protocols/llm-assisted-contribution.md). LLM-generated estimates remain proposals until independently verified.
