# OPERA-X v3.9.0 vs v3.8.0 change manifest

## Summary

| Result | Count |
|---|---:|
| Modified | 26 |
| Added | 7 |
| Deleted | 0 |
| Unchanged | 267 |
| v3.8.0 files | 293 |
| v3.9.0 files | 300 |

Counts use SHA-256 file comparison, exclude directories/caches, and include `SHA256SUMS.txt` as modified plus this manifest and the no-delete instruction file as added.

## Modified files

```text
BUILD_NOTES.md
CHANGE_MANIFEST_v3.8.0_vs_v3.7.0.md
DATA_OVERWRITE_WARNING.md
LIVE_DATA_UPDATE_v3.7.0.md
LIVE_DATA_UPDATE_v3.8.0.md
MAPPING_QUALITY_REPORT.md
PERFORMANCE_REPORT_v3.7.0.md
README.md
ROOT_CAUSE_AND_FIX_v3.7.0.md
SHA256SUMS.txt
TEST_RESULTS.md
VERSION
app.py
opera/__init__.py
opera/dashboard.py
opera/dcs_connector.py
opera/engineering_mapping.py
opera/operational.py
opera/risk_engine.py
opera/risk_pdf.py
opera/risk_store.py
opera/storage.py
scripts/build_mapping_quality_report.py
tests/test_v320_features.py
tests/test_v350_features.py
tests/test_v380_features.py
```

The retained historical release/benchmark documents were changed only to apply the current user-facing Digital Data, Raw Field Data and Job Risk Assessment terminology; their measured values and historical behavior descriptions were not otherwise changed.

## Added files

```text
CHANGE_MANIFEST_v3.9.0_vs_v3.8.0.md
CODE_ONLY_DELETE_INSTRUCTIONS_v3.9.0.txt
LIVE_DATA_UPDATE_v3.9.0.md
assets/dangote_group_logo.webp
assets/dangote_vision_2030.jpg
assets/dangote_vision_2030_compact.jpg
tests/test_v390_features.py
```

## Deleted files

None.

## Runtime-data and overwrite impact

No file under `data/`, `registers/` or `reference_sources/` changed. The full ZIP therefore contains the exact same seeded runtime data, CSV/JSON/XLSX files and approved register workbooks as v3.8.0.

**No file in live `~/opera_data` must be added, replaced, renamed or edited.** The labels Digital Data and Raw Field Data are presented by code while the stable internal keys `DCS` and `Field`, field IDs `DP` and `F`, and `inputs/dcs.csv` / `inputs/field.csv` remain unchanged. The new Field Catalogue columns are generated on demand and write back to the existing mapping schema.

The Job Risk Assessment rename is also presentation-safe. Keep `risk_assessments.csv`, `registers/`, approved workbook filenames and existing historical audit rows unchanged.

## Recommended GitHub/DDF deployment

Use `OPERA-X_Code_Only_Update_v3.9.0_vs_v3.8.0.zip`. It contains every modified or added file above except `SHA256SUMS.txt` and excludes `data/`, `registers/` and `reference_sources/`.

1. Overlay the code-only ZIP at the repository root and commit all files.
2. No deletion step is required.
3. On the DDF server, run `git pull` in the existing checkout.
4. Keep `OPERA_DATA_DIR=~/opera_data` (or `OPERAX_DATA_DIR`) in the startup script.
5. Restart Streamlit on port 8089/address 172.20.130.228.
6. Do not copy the full ZIP's `data/` folder into `~/opera_data`.

Streamlit Community Cloud continues to work from the same GitHub repository. Local embedded brand assets are safe at both the root URL and nginx `/operationaldashboard/` path.

## Verification

- 54 automated tests passed.
- Python compilation passed for `app.py`, `opera/*.py` and `scripts/*.py`.
- Production Cement mapping template: 11,293 Field Catalogue rows, 10 columns, and controlled Field ID, Equipment ID, Dashboard Template ID and Include validations.
- Runtime `data/`, `registers/` and `reference_sources/` hashes are identical to v3.8.0.
