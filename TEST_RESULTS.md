# OPERA-X v3.11.1 test results

## Automated Python suite

Command:

```bash
python -m compileall -q app.py opera scripts tests
OPERAX_RUN_BROWSER_TESTS=1 pytest -q
```

Result: **71 passed**.

The opt-in browser test starts the real authenticated Streamlit application at both `/` and `/operationaldashboard/`; it is not a static HTML test or separate header harness.

## Browser verification

Command:

```bash
python scripts/verify_header_browser.py
```

Result: **36 real-app header checks passed** across:

- paths: root and `/operationaldashboard/`;
- pages: Home, Equipment Overview and Admin / Super Admin;
- CSS viewports at 100% zoom: 1920, 1560, 1536, 1366, 1280 and 1279 px.

Assertions covered:

- all 11 flat-menu labels visible in one row at 1280px and wider;
- compact left-aligned ☰ at 1279px;
- 52px nav height;
- packed content-width labels (maximum label-row width 947.66px);
- no visible popover chevrons beside the bell or avatar;
- fully visible 40px breadcrumb content within its bordered strip;
- first page heading below the breadcrumb;
- no horizontal document overflow;
- no visible Streamlit exception.

See `VISUAL_VERIFICATION_v3.11.1.md`, `verification/v3.11.1/header_measurements.json`, the 36 PNG captures and the two comparison sheets.

## Live-data boundary

The target `data/` tree was restored byte-for-byte from v3.11.0 after testing. No update is required in `~/opera_data`.
