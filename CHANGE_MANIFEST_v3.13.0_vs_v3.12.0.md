# OPERA-X v3.13.0 Change Manifest

Compared with `OPERA-X_Streamlit_Deployment_v3.12.0_Final.zip`.

**12 modified, 20 added, 0 deleted.**

## Modified files

- `README.md`
- `VERSION`
- `app.py`
- `opera/auth.py`
- `scripts/verify_header_browser.py`
- `tests/test_v3101_mapping_regressions.py`
- `tests/test_v310_features.py`
- `tests/test_v3110_header.py`
- `tests/test_v340_features.py`
- `tests/test_v380_features.py`
- `tests/test_v390_features.py`
- `tests/test_version_consistency.py`

## Added files

- `BUILD_NOTES_v3.13.0.md`
- `CHANGE_MANIFEST_v3.13.0_vs_v3.12.0.md`
- `CODE_ONLY_DELETE_INSTRUCTIONS_v3.13.0.txt`
- `LIVE_EXCEL_PIPELINE_GUIDE_v3.13.0.md`
- `SYSTEMD_OPERAX_LIVE_EXCEL_TEMPLATE.service`
- `SYSTEMD_OPERAX_LIVE_EXCEL_TEMPLATE.timer`
- `TEST_RESULTS_v3.13.0.md`
- `VISUAL_VERIFICATION_v3.13.0.md`
- `opera/pipelines.py`
- `reference_sources/OPERA-X_Live_Excel_1_Refinery_Sample.xlsx`
- `reference_sources/OPERA-X_Live_Excel_2_Cement_Sample.xlsx`
- `reference_sources/OPERA-X_Live_Excel_3_Fertilizer_Sample.xlsx`
- `scripts/create_live_excel_samples.py`
- `scripts/pipeline_scheduler.py`
- `scripts/start_pipeline_scheduler.sh`
- `scripts/stop_pipeline_scheduler.sh`
- `scripts/sync_live_excel.py`
- `scripts/update_pipeline_status.py`
- `tests/test_v3130_pipelines_roles.py`
- `verification/v3.13.0/browser_measurements.json`

## Deleted files

- None

## Live-data boundary

The code-only package excludes `data/`, `registers/`, and `reference_sources/`. No existing file in `~/opera_data` should be replaced manually. Runtime pipeline configuration/state/log files are created only when used; validated Live Excel runs atomically upsert `inputs/dcs.csv`.
