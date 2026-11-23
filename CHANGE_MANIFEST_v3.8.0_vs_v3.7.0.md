# OPERA-X v3.8.0 — Change Manifest vs v3.7.0

## Summary

v3.8.0 implements the six requested UI, Super Admin data-access, chart, Operations Dashboard and Excel mapping-template changes while retaining the v3.7 performance architecture and both deployment targets.

## Changed files

- `VERSION` — updated to `3.8.0`.
- `app.py` — banner version badge; full-width Sign Out control; clickable Home data cards with Super Admin authorization, data tables and Excel downloads; source-grouped Readings workbook; mixed-source Operations Dashboard data alignment; mixed-source Operations template administration.
- `opera/__init__.py` — package version updated to `3.8.0`.
- `opera/dashboard.py` — 231 px chart height (30% below 330 px); mixed Digital Data/Raw Field Data/QAQC/Calculated Operations catalog and defaults; safe recognition of exact v3.7 calculated-only defaults; equipment-aware Field Catalogue with dropdown validation and bulk-update support.
- `tests/test_app_smoke.py` — Home smoke assertion updated from passive metrics to the five requested data buttons.
- `README.md` — v3.8 feature and deployment guidance.
- `BUILD_NOTES.md` — v3.8 implementation and verification summary.
- `DATA_OVERWRITE_WARNING.md` — v3.8 code-only deployment and no-live-data-update guidance.
- `TEST_RESULTS.md` — 50-test v3.8 verification result.
- `SHA256SUMS.txt` — regenerated package-tree hashes.

## Added files

- `tests/test_v380_features.py` — version/banner, Home Excel grouping, Operations source coverage, chart sizing, and Field Catalogue equipment-dropdown/update tests.
- `LIVE_DATA_UPDATE_v3.8.0.md` — exact server and `~/opera_data` instructions.
- `CHANGE_MANIFEST_v3.8.0_vs_v3.7.0.md` — this manifest.
- `CODE_ONLY_DELETE_INSTRUCTIONS_v3.8.0.txt` — code-only overlay guidance.

## Deleted files

None.

## Runtime data impact

No file under `data/`, `registers/` or `reference_sources/` was changed versus v3.7.0. In particular, no CSV, JSON, XLSX, attachment, audit, event, lesson, notification, user, field, equipment, formula, mapping, template, preset or reading file is part of the code change.

The full deployment ZIP still contains the unchanged v3.7 seeded `data/` tree for fresh/test deployments. Do not overlay that tree on live runtime data. The code-only ZIP excludes `data/`, `registers/` and `reference_sources/`.

## Live `~/opera_data` requirement

**No file in `~/opera_data` must be added, replaced or edited for v3.8.0.** The exact legacy v3.7 calculated-only Operations defaults are expanded in memory to the new mixed-source defaults. Existing genuinely customized templates are preserved. The mapping workbook is not rewritten by this release merely to expose the new Field Catalogue template layout; the new layout is generated on demand from Admin / Super Admin.
