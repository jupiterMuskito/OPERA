# OPERA-X v3.12.0 vs v3.11.1 change manifest

Baseline: `OPERA-X_Streamlit_Deployment_v3.11.1_Final.zip`  
Target: OPERA-X v3.12.0

## Summary

- Modified: **16**
- Added: **64**
- Deleted: **0**

## Modified files (16)

- `BUILD_NOTES.md`
- `README.md`
- `SHA256SUMS.txt`
- `TEST_RESULTS.md`
- `VERSION`
- `app.py`
- `opera/dashboard.py`
- `opera/storage.py`
- `scripts/verify_header_browser.py`
- `tests/test_v3101_mapping_regressions.py`
- `tests/test_v310_features.py`
- `tests/test_v3110_header.py`
- `tests/test_v3111_browser_contract.py`
- `tests/test_v380_features.py`
- `tests/test_v390_features.py`
- `tests/test_version_consistency.py`

## Added files (64)

- `BUILD_NOTES_v3.12.0.md`
- `CHANGE_MANIFEST_v3.12.0_vs_v3.11.1.md`
- `CODE_ONLY_DELETE_INSTRUCTIONS_v3.12.0.txt`
- `LIVE_DATA_UPDATE_v3.12.0.md`
- `PERFORMANCE_REPORT_v3.12.0.md`
- `VISUAL_VERIFICATION_v3.12.0.md`
- `assets/dangote_vision_2030.webp`
- `assets/dangote_vision_2030_compact.webp`
- `scripts/benchmark_page_navigation.py`
- `tests/test_v3120_feedback.py`
- `verification/v3.12.0/browser_measurements.json`
- `verification/v3.12.0/chrome/operationaldashboard/home_1099px.png`
- `verification/v3.12.0/chrome/operationaldashboard/home_1272px.png`
- `verification/v3.12.0/chrome/operationaldashboard/home_1280px.png`
- `verification/v3.12.0/chrome/operationaldashboard/home_1280px_dsf1.5.png`
- `verification/v3.12.0/chrome/operationaldashboard/home_1366px.png`
- `verification/v3.12.0/chrome/operationaldashboard/home_1536px.png`
- `verification/v3.12.0/chrome/operationaldashboard/home_1920px.png`
- `verification/v3.12.0/chrome/root/home_1099px.png`
- `verification/v3.12.0/chrome/root/home_1272px.png`
- `verification/v3.12.0/chrome/root/home_1280px.png`
- `verification/v3.12.0/chrome/root/home_1280px_dsf1.5.png`
- `verification/v3.12.0/chrome/root/home_1366px.png`
- `verification/v3.12.0/chrome/root/home_1536px.png`
- `verification/v3.12.0/chrome/root/home_1920px.png`
- `verification/v3.12.0/chrome/root/page_admin_1366px.png`
- `verification/v3.12.0/chrome/root/page_equipment_1366px.png`
- `verification/v3.12.0/chrome/root/page_events_1366px.png`
- `verification/v3.12.0/chrome/root/page_home_1366px.png`
- `verification/v3.12.0/chrome/root/page_kpis_1366px.png`
- `verification/v3.12.0/chrome/root/page_lessons_1366px.png`
- `verification/v3.12.0/chrome/root/page_optimization_1366px.png`
- `verification/v3.12.0/chrome/root/page_parameters_1366px.png`
- `verification/v3.12.0/chrome/root/page_pipeline_1366px.png`
- `verification/v3.12.0/chrome/root/page_plant_1366px.png`
- `verification/v3.12.0/chrome/root/page_risk_1366px.png`
- `verification/v3.12.0/edge/operationaldashboard/home_1099px.png`
- `verification/v3.12.0/edge/operationaldashboard/home_1272px.png`
- `verification/v3.12.0/edge/operationaldashboard/home_1280px.png`
- `verification/v3.12.0/edge/operationaldashboard/home_1280px_dsf1.5.png`
- `verification/v3.12.0/edge/operationaldashboard/home_1366px.png`
- `verification/v3.12.0/edge/operationaldashboard/home_1536px.png`
- `verification/v3.12.0/edge/operationaldashboard/home_1920px.png`
- `verification/v3.12.0/edge/root/home_1099px.png`
- `verification/v3.12.0/edge/root/home_1272px.png`
- `verification/v3.12.0/edge/root/home_1280px.png`
- `verification/v3.12.0/edge/root/home_1280px_dsf1.5.png`
- `verification/v3.12.0/edge/root/home_1366px.png`
- `verification/v3.12.0/edge/root/home_1536px.png`
- `verification/v3.12.0/edge/root/home_1920px.png`
- `verification/v3.12.0/edge/root/page_admin_1366px.png`
- `verification/v3.12.0/edge/root/page_equipment_1366px.png`
- `verification/v3.12.0/edge/root/page_events_1366px.png`
- `verification/v3.12.0/edge/root/page_home_1366px.png`
- `verification/v3.12.0/edge/root/page_kpis_1366px.png`
- `verification/v3.12.0/edge/root/page_lessons_1366px.png`
- `verification/v3.12.0/edge/root/page_optimization_1366px.png`
- `verification/v3.12.0/edge/root/page_parameters_1366px.png`
- `verification/v3.12.0/edge/root/page_pipeline_1366px.png`
- `verification/v3.12.0/edge/root/page_plant_1366px.png`
- `verification/v3.12.0/edge/root/page_risk_1366px.png`
- `verification/v3.12.0/performance_comparison_v3.10.1_v3.11.1_v3.12.0.json`
- `verification/v3.12.0/performance_v3.10.1_vs_v3.12.0.json`
- `verification/v3.12.0/performance_v3.11.1_vs_v3.12.0.json`

## Deleted files (0)

None.

## Live-data boundary

**No manual edit under `~/opera_data` is required.** On first lesson load per business unit, the app atomically adds `category` to legacy `lessons.csv`; existing rows with equipment become Equipment and rows without equipment become General. The full package retains the v3.11.1 seeded `data/` tree byte-for-byte. The code-only ZIP excludes `data/`, `registers/` and `reference_sources/`.

## Deployment reminder

Apply the complete code-only ZIP, install pinned requirements, fully restart with `~/OPERA/start_opera.sh`, then use **Ctrl+F5** in both Chrome and Edge.
