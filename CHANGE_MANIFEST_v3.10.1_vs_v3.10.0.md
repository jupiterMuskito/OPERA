# OPERA-X v3.10.1 vs v3.10.0 change manifest

## Summary

| Result | Count |
|---|---:|
| Modified | 13 |
| Added | 7 |
| Deleted | 0 |
| Unchanged | 295 |
| v3.10.0 files | 308 |
| v3.10.1 files | 315 |

Counts use SHA-256 file comparison, exclude directories/caches, and include `SHA256SUMS.txt` as modified plus this manifest as added.

## Modified files

```text
BUILD_NOTES.md
DATA_OVERWRITE_WARNING.md
MAPPING_QUALITY_REPORT.md
README.md
SHA256SUMS.txt
TEST_RESULTS.md
VERSION
app.py
opera/__init__.py
opera/dashboard.py
scripts/build_mapping_quality_report.py
tests/test_v380_features.py
tests/test_v390_features.py
```

## Added files

```text
CHANGE_MANIFEST_v3.10.1_vs_v3.10.0.md
CODE_ONLY_DELETE_INSTRUCTIONS_v3.10.1.txt
LIVE_DATA_UPDATE_v3.10.1.md
ROOT_CAUSE_AND_FIX_v3.10.1.md
opera/version.py
tests/test_v3101_mapping_regressions.py
tests/test_version_consistency.py
```

## Deleted files

```text
None
```

## Root cause 1 — top banner version

v3.10.0 maintained the version independently in `VERSION` and `opera/__init__.py`. `app.py` imported the package value once as `APP_VERSION`, so the banner did not read the release file and could retain an old module value inside a long-running Streamlit process even while the current application source was present. The prior test checked the presence of the `APP_VERSION` interpolation rather than verifying the displayed/package/file values together.

v3.10.1 makes `VERSION` the only persisted source. `opera/version.py` validates and reads it, `opera.__version__` derives from it, and the top ribbon calls `version_badge_html()` on every render. The regression test checks the file, package value, badge HTML and `app.py` integration and proves the badge follows an updated version file without a module reload.

## Root cause 2 — missing template mapping in Field Catalogue

The v3.10.0 in-app workbook generator called `load_effective_field_mappings()` before building Field Catalogue. A pre-v3.9 live `field_mappings.xlsx` lacked the required `Template IDs` column, so parsing failed before the newer builder could append Dashboard Template ID and Dashboard Template. The Admin page did not clear an already prepared workbook before trying a fresh build, so a prior pre-upgrade workbook could remain downloadable after that failure. This reproduces the reported behavior with current v3.10.0 code and an old persistent data directory; it is not a stale deployment.

v3.10.1 upgrades an old backend workbook in place before caching or export. It inserts `Template IDs` and `Dashboard Templates` beside `Equipment IDs` in both backend sheets, recovers values from retained/current mappings, preserves existing cells/extra columns/extra sheets, and rebuilds only the derived runtime cache. The prepare action also clears old session bytes before generating a fresh workbook.

## Field Catalogue and bulk-upload behavior

- Field Catalogue columns are `Equipment ID`, `Equipment`, `Dashboard Template ID`, `Dashboard Template`, and `Include`.
- Dashboard Template ID uses a controlled dropdown backed by Plant Performance, Condition Monitoring, Process Performance, Quality and Compliance, and Reliability.
- Multiple equipment and multiple template mappings use multiple included rows and are de-duplicated during upload.
- Invalid Field IDs, Equipment IDs, Dashboard Template IDs and Include values are rejected with a worksheet row error.
- The backend Excel Mapping Database shows semicolon-separated Template IDs and human-readable Dashboard Templates for every field.

Exact download path:

**Admin / Super Admin → Data Field Mapping → Excel mapping database and bulk update → Prepare Excel Mapping Update Template → Download Excel Update Template**

## Runtime-data and overwrite impact

Every packaged file under `data/`, `registers/` and `reference_sources/` is byte-for-byte unchanged from v3.10.0.

**No manual change is required in live `~/opera_data`.** If a live `field_mappings.xlsx` has the old schema, v3.10.1 performs a one-time in-place upgrade on first mapping access and regenerates `field_mappings.runtime.json.gz`. Existing mappings, administrator metadata and unrelated workbook content are retained. Do not overlay the full ZIP's seeded `data/` directory on the live data folder.

## Verification

- 64 automated tests passed, including five v3.10.1 regression tests.
- Python compilation passed for `app.py`, `opera/*.py` and `scripts/*.py`.
- Both defects were reproduced/tested against an isolated data directory whose mapping workbook mimicked a pre-v3.9 live schema.
- The generated Field Catalogue was opened with openpyxl and verified for column order, all five templates and validation ranges.
- A two-template upload updated the effective mapping and backend workbook; an invalid template ID produced the expected validation error.

## Recommended deployment

1. Overlay `OPERA-X_Code_Only_Update_v3.10.1_vs_v3.10.0.zip` at the repository root and commit every included file.
2. Test the commit on Streamlit Community Cloud.
3. On the DDF server, run `git pull` in the existing checkout.
4. Confirm `cat VERSION` and `python -c "import opera; print(opera.__version__)"` both print `3.10.1`.
5. Restart the Streamlit process with the existing `OPERA_DATA_DIR=~/opera_data`, port `8089` and address `172.20.130.228` configuration.
6. Open `https://172.20.130.228/operationaldashboard/`, sign in, hard-refresh if necessary, and confirm the banner reads `v3.10.1`.
7. Follow the exact Admin path above and confirm Field Catalogue contains the template columns.
8. Do not copy the full package's `data/` tree into `~/opera_data`.
