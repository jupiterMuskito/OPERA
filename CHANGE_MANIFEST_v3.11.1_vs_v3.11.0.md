# OPERA-X v3.11.1 vs v3.11.0 change manifest

Baseline: `OPERA-X_Streamlit_Deployment_v3.11.0_Final.zip`  
Target: OPERA-X v3.11.1

## Changed files (12)

- `BUILD_NOTES.md`
- `README.md`
- `SHA256SUMS.txt`
- `TEST_RESULTS.md`
- `VERSION`
- `app.py`
- `pytest.ini`
- `tests/test_v3101_mapping_regressions.py`
- `tests/test_v3110_header.py`
- `tests/test_v380_features.py`
- `tests/test_v390_features.py`
- `tests/test_version_consistency.py`

## Added files (45)

- `BUILD_NOTES_v3.11.1.md`
- `CHANGE_MANIFEST_v3.11.1_vs_v3.11.0.md`
- `LIVE_DATA_UPDATE_v3.11.1.md`
- `VISUAL_VERIFICATION_v3.11.1.md`
- `scripts/verify_header_browser.py`
- `tests/test_v3111_browser_contract.py`
- `verification/v3.11.1/comparison_collapsed_before_vs_final_1560.png`
- `verification/v3.11.1/comparison_flat_before_vs_final_1536.png`
- `verification/v3.11.1/header_measurements.json`
- `verification/v3.11.1/operationaldashboard/admin_1279px.png`
- `verification/v3.11.1/operationaldashboard/admin_1280px.png`
- `verification/v3.11.1/operationaldashboard/admin_1366px.png`
- `verification/v3.11.1/operationaldashboard/admin_1536px.png`
- `verification/v3.11.1/operationaldashboard/admin_1560px.png`
- `verification/v3.11.1/operationaldashboard/admin_1920px.png`
- `verification/v3.11.1/operationaldashboard/equipment_1279px.png`
- `verification/v3.11.1/operationaldashboard/equipment_1280px.png`
- `verification/v3.11.1/operationaldashboard/equipment_1366px.png`
- `verification/v3.11.1/operationaldashboard/equipment_1536px.png`
- `verification/v3.11.1/operationaldashboard/equipment_1560px.png`
- `verification/v3.11.1/operationaldashboard/equipment_1920px.png`
- `verification/v3.11.1/operationaldashboard/home_1279px.png`
- `verification/v3.11.1/operationaldashboard/home_1280px.png`
- `verification/v3.11.1/operationaldashboard/home_1366px.png`
- `verification/v3.11.1/operationaldashboard/home_1536px.png`
- `verification/v3.11.1/operationaldashboard/home_1560px.png`
- `verification/v3.11.1/operationaldashboard/home_1920px.png`
- `verification/v3.11.1/root/admin_1279px.png`
- `verification/v3.11.1/root/admin_1280px.png`
- `verification/v3.11.1/root/admin_1366px.png`
- `verification/v3.11.1/root/admin_1536px.png`
- `verification/v3.11.1/root/admin_1560px.png`
- `verification/v3.11.1/root/admin_1920px.png`
- `verification/v3.11.1/root/equipment_1279px.png`
- `verification/v3.11.1/root/equipment_1280px.png`
- `verification/v3.11.1/root/equipment_1366px.png`
- `verification/v3.11.1/root/equipment_1536px.png`
- `verification/v3.11.1/root/equipment_1560px.png`
- `verification/v3.11.1/root/equipment_1920px.png`
- `verification/v3.11.1/root/home_1279px.png`
- `verification/v3.11.1/root/home_1280px.png`
- `verification/v3.11.1/root/home_1366px.png`
- `verification/v3.11.1/root/home_1536px.png`
- `verification/v3.11.1/root/home_1560px.png`
- `verification/v3.11.1/root/home_1920px.png`

## Deleted files (0)

None.

## Live-data boundary

**No change is required in `~/opera_data`.** The full deployment package retains the v3.11.0 `data/` tree byte-for-byte. The code-only package excludes `data/`, `registers/` and `reference_sources/`.

## Deployment reminder

Apply the entire code-only package to v3.11.0, install `requirements.txt`, fully restart with `~/OPERA/start_opera.sh`, then hard-refresh with **Ctrl+F5**.
