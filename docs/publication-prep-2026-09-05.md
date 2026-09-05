# Public publication candidate — 2026-09-05

This is a local, reviewable candidate for the proposed repository slug `MacSiem/vacuum-consumption-data`. No remote exists today; this document does not claim a public URL, and no push, tag, release or remote creation occurred.

## Public layout and evidence boundary

- `README.md`, `CONTRIBUTING.md` and `.github/ISSUE_TEMPLATE/evidence-intake.yml` are the public starting point for issue reporters.
- `data/` contains public identities, source references, declarations, settings and two explicitly labeled estimates. It contains **zero approved profiles**. An estimate has a separate source type and readiness, retains basis/unit/method/scope/limitations, and is never a measurement or completion-counter proof.
- `reports/public-source-inventory-v2.json` and its Markdown companion preserve the bounded 356-ID research result: retail/SKU/firmware crosswalks remain unknown or blocked; no rate/action completion is inferred.
- `reports/coverage.json`, frozen bundle records and v1/v2/v3 protocol documents expose known denominators and unknowns. A public source link is attribution, not a redistribution license for its content.
- Private physical notes stay local. A public contribution may contain consented, schema-complete measurements with non-identifying IDs and relative time/order/duration, never raw Diagnostics or household identifiers.

## Candidate exclusions and audit

The candidate excludes `.venv/**`, `work/**`, `dist/**`, `**/__pycache__/**`, `*.log` and `*.trace`. The deterministic audit records tracked, modified and untracked candidate files plus a SHA-256 per file in `reports/publication-audit-2026-09-05.json`. It reports only `{path, rule, lines, redacted:true}` for a possible private path, credential pattern or private-key marker; it never serializes a matched value. It also checks every JSON record under `data/` for `provenance`, `source`, or migration source metadata.

`LICENSE` remains MIT for code. `LICENSE-DATA.md` retains CC BY 4.0 attribution rules for original data organization/contributions and explicitly leaves linked manufacturer/integration/API material under its own terms. No third-party license was added or inferred.

## Freeze and authorized later commands

The schema-v2 labeled-estimate bundle is frozen in `reports/frozen-bundle-v4-tiers-2026-09-05.json`: payload SHA-256 `5444b736ceb6e84e5b16b7bc0716dac65211970ba1e68ac9e914f296dd84880e`, file SHA-256 `6959f1f5965884f1ede71128534905bd403878f2416cd426bf67c180befe6cff`, 168 records, two labeled estimates and zero approved profiles. Review the audit manifest and every diff first. In a separate `ALLOW_RELEASE=1` turn, after a fresh audit/readback, the exact sequence is:

```sh
git diff --check
python -m tools.publication_audit --output reports/publication-audit-2026-09-05.json
python -m unittest discover -s tests
python -m tools.check_public_data
python -m tools.validate
python -m tools.report_coverage
python -m tools.build_bundle
git add -- $(jq -r '.candidate_files.tracked[], .candidate_files.modified[], .candidate_files.untracked[]' reports/publication-audit-2026-09-05.json)
git commit -m "Prepare public vacuum consumption dataset"
gh repo create MacSiem/vacuum-consumption-data --public --source=. --remote=origin
git push -u origin main
```

Do not run the last three commands until the authorized release turn and a fresh audit/readback. Only after `gh repo view MacSiem/vacuum-consumption-data` succeeds may the app replace its `DATASET_URL` placeholder or issue reporters receive a public dataset link.
