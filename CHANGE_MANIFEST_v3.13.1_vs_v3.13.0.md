# OPERA-X v3.13.1 Change Manifest

Compared with `OPERA-X_Streamlit_Deployment_v3.13.0_Final.zip`.

**18 modified, 8 added, 0 deleted.**

## Modified files

- `BUILD_NOTES.md`
- `README.md`
- `SHA256SUMS.txt`
- `TEST_RESULTS.md`
- `VERSION`
- `app.py`
- `opera/auth.py`
- `opera/pipelines.py`
- `scripts/pipeline_scheduler.py`
- `scripts/sync_live_excel.py`
- `scripts/update_pipeline_status.py`
- `scripts/verify_header_browser.py`
- `tests/test_v3101_mapping_regressions.py`
- `tests/test_v3110_header.py`
- `tests/test_v3130_pipelines_roles.py`
- `tests/test_v380_features.py`
- `tests/test_v390_features.py`
- `tests/test_version_consistency.py`

## Added files

- `BUILD_NOTES_v3.13.1.md`
- `CHANGE_MANIFEST_v3.13.1_vs_v3.13.0.md`
- `CODE_ONLY_DELETE_INSTRUCTIONS_v3.13.1.txt`
- `LIVE_EXCEL_PIPELINE_GUIDE_v3.13.1.md`
- `TEST_RESULTS_v3.13.1.md`
- `VISUAL_VERIFICATION_v3.13.1.md`
- `tests/test_v3131_permissions_global_pipelines.py`
- `verification/v3.13.1/browser_measurements.json`

## Deleted files

- None.

## Live-data boundary

The code-only package excludes the complete `data/`, `registers/` and `reference_sources/` trees. It does not contain or overwrite `~/opera_data`.

No manual live-data edit is required. On first load, v3.13.1 reads existing per-BU pipeline configuration/state, de-duplicates by pipeline ID using the intended target BU, and writes global files under `~/opera_data/shared/`. Existing per-BU files are retained.

After deployment, restart the scheduler with `stop_pipeline_scheduler.sh` followed by `start_pipeline_scheduler.sh`, fully restart OPERA-X with `~/OPERA/start_opera.sh`, and hard-refresh with Ctrl+F5.
