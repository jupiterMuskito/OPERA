# OPERA-X v3.13.2 Change Manifest

Comparison base: `OPERA-X_Streamlit_Deployment_v3.13.1_Final.zip`

- Modified: **12**
- Added: **85**
- Deleted: **0**

## Modified files

- `SHA256SUMS.txt`
- `VERSION`
- `app.py`
- `opera/auth.py`
- `scripts/verify_header_browser.py`
- `tests/test_v3101_mapping_regressions.py`
- `tests/test_v310_features.py`
- `tests/test_v3110_header.py`
- `tests/test_v3111_browser_contract.py`
- `tests/test_v380_features.py`
- `tests/test_v390_features.py`
- `tests/test_version_consistency.py`

## Added files

- `BUILD_NOTES_v3.13.2.md`
- `CHANGE_MANIFEST_v3.13.2_vs_v3.13.1.md`
- `CODE_ONLY_DELETE_INSTRUCTIONS_v3.13.2.txt`
- `TEST_RESULTS_v3.13.2.md`
- `VISUAL_VERIFICATION_v3.13.2.md`
- `tests/test_v3132_ui_permissions_risk.py`
- `verification/v3.13.2/browser_measurements.json`
- `verification/v3.13.2/browser_measurements_capture.json`
- `verification/v3.13.2/chrome/operationaldashboard/home_1099px.png`
- `verification/v3.13.2/chrome/operationaldashboard/home_1272px.png`
- `verification/v3.13.2/chrome/operationaldashboard/home_1280px.png`
- `verification/v3.13.2/chrome/operationaldashboard/home_1280px_dsf1.5.png`
- `verification/v3.13.2/chrome/operationaldashboard/home_1366px.png`
- `verification/v3.13.2/chrome/operationaldashboard/home_1536px.png`
- `verification/v3.13.2/chrome/operationaldashboard/home_1920px.png`
- `verification/v3.13.2/chrome/operationaldashboard/page_admin_1366px.png`
- `verification/v3.13.2/chrome/operationaldashboard/page_equipment_1366px.png`
- `verification/v3.13.2/chrome/operationaldashboard/page_events_1366px.png`
- `verification/v3.13.2/chrome/operationaldashboard/page_home_1366px.png`
- `verification/v3.13.2/chrome/operationaldashboard/page_kpis_1366px.png`
- `verification/v3.13.2/chrome/operationaldashboard/page_lessons_1366px.png`
- `verification/v3.13.2/chrome/operationaldashboard/page_optimization_1366px.png`
- `verification/v3.13.2/chrome/operationaldashboard/page_parameters_1366px.png`
- `verification/v3.13.2/chrome/operationaldashboard/page_pipeline_1366px.png`
- `verification/v3.13.2/chrome/operationaldashboard/page_plant_1366px.png`
- `verification/v3.13.2/chrome/operationaldashboard/page_risk_1366px.png`
- `verification/v3.13.2/chrome/root/home_1099px.png`
- `verification/v3.13.2/chrome/root/home_1272px.png`
- `verification/v3.13.2/chrome/root/home_1280px.png`
- `verification/v3.13.2/chrome/root/home_1280px_dsf1.5.png`
- `verification/v3.13.2/chrome/root/home_1366px.png`
- `verification/v3.13.2/chrome/root/home_1536px.png`
- `verification/v3.13.2/chrome/root/home_1920px.png`
- `verification/v3.13.2/chrome/root/page_admin_1366px.png`
- `verification/v3.13.2/chrome/root/page_equipment_1366px.png`
- `verification/v3.13.2/chrome/root/page_events_1366px.png`
- `verification/v3.13.2/chrome/root/page_home_1366px.png`
- `verification/v3.13.2/chrome/root/page_kpis_1366px.png`
- `verification/v3.13.2/chrome/root/page_lessons_1366px.png`
- `verification/v3.13.2/chrome/root/page_optimization_1366px.png`
- `verification/v3.13.2/chrome/root/page_parameters_1366px.png`
- `verification/v3.13.2/chrome/root/page_pipeline_1366px.png`
- `verification/v3.13.2/chrome/root/page_plant_1366px.png`
- `verification/v3.13.2/chrome/root/page_risk_1366px.png`
- `verification/v3.13.2/edge/operationaldashboard/account_menu_1272px.png`
- `verification/v3.13.2/edge/operationaldashboard/home_1099px.png`
- `verification/v3.13.2/edge/operationaldashboard/home_1272px.png`
- `verification/v3.13.2/edge/operationaldashboard/home_1280px.png`
- `verification/v3.13.2/edge/operationaldashboard/home_1280px_dsf1.5.png`
- `verification/v3.13.2/edge/operationaldashboard/home_1366px.png`
- `verification/v3.13.2/edge/operationaldashboard/home_1536px.png`
- `verification/v3.13.2/edge/operationaldashboard/home_1920px.png`
- `verification/v3.13.2/edge/operationaldashboard/home_cards_1272px.png`
- `verification/v3.13.2/edge/operationaldashboard/navigation_bar_1272px.png`
- `verification/v3.13.2/edge/operationaldashboard/page_admin_1366px.png`
- `verification/v3.13.2/edge/operationaldashboard/page_equipment_1366px.png`
- `verification/v3.13.2/edge/operationaldashboard/page_events_1366px.png`
- `verification/v3.13.2/edge/operationaldashboard/page_home_1366px.png`
- `verification/v3.13.2/edge/operationaldashboard/page_kpis_1366px.png`
- `verification/v3.13.2/edge/operationaldashboard/page_lessons_1366px.png`
- `verification/v3.13.2/edge/operationaldashboard/page_optimization_1366px.png`
- `verification/v3.13.2/edge/operationaldashboard/page_parameters_1366px.png`
- `verification/v3.13.2/edge/operationaldashboard/page_pipeline_1366px.png`
- `verification/v3.13.2/edge/operationaldashboard/page_plant_1366px.png`
- `verification/v3.13.2/edge/operationaldashboard/page_risk_1366px.png`
- `verification/v3.13.2/edge/operationaldashboard/risk_manual_hazard_count_and_print_1272px.png`
- `verification/v3.13.2/edge/operationaldashboard/risk_preset_editable_and_print_1272px.png`
- `verification/v3.13.2/edge/root/home_1099px.png`
- `verification/v3.13.2/edge/root/home_1272px.png`
- `verification/v3.13.2/edge/root/home_1280px.png`
- `verification/v3.13.2/edge/root/home_1280px_dsf1.5.png`
- `verification/v3.13.2/edge/root/home_1366px.png`
- `verification/v3.13.2/edge/root/home_1536px.png`
- `verification/v3.13.2/edge/root/home_1920px.png`
- `verification/v3.13.2/edge/root/page_admin_1366px.png`
- `verification/v3.13.2/edge/root/page_equipment_1366px.png`
- `verification/v3.13.2/edge/root/page_events_1366px.png`
- `verification/v3.13.2/edge/root/page_home_1366px.png`
- `verification/v3.13.2/edge/root/page_kpis_1366px.png`
- `verification/v3.13.2/edge/root/page_lessons_1366px.png`
- `verification/v3.13.2/edge/root/page_optimization_1366px.png`
- `verification/v3.13.2/edge/root/page_parameters_1366px.png`
- `verification/v3.13.2/edge/root/page_pipeline_1366px.png`
- `verification/v3.13.2/edge/root/page_plant_1366px.png`
- `verification/v3.13.2/edge/root/page_risk_1366px.png`

## Deleted files

- None

## Deployment impact

- `~/opera_data`: no manual or structural change is required; do not overwrite it with packaged sample data.
- Pipeline scheduler: no restart is required because no scheduler or pipeline-routing code changed.
- Streamlit application: a full restart with `~/OPERA/start_opera.sh` is required.
- Browsers: use `Ctrl+F5` in Edge and Chrome after deployment.
