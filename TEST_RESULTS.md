# OPERA-X v3.11.0 test results

## Automated checks

- `pytest -q`: **68 passed**.
- `python -m py_compile app.py opera/*.py scripts/*.py`: **passed**.
- Version consistency: repository `VERSION`, `opera.__version__`, the brand-bar version, and avatar-menu version all resolve to **3.11.0** through the single version helper.
- Existing regressions retained: Digital Data/Raw Field Data labels and IDs, Field Catalogue equipment/template columns and pre-v3.9 workbook upgrade, Operational Data Pipeline naming, Job Risk Assessment naming, role permissions, dashboards, formulas, storage, export, and Admin workflows.
- New header regressions: menu order and short labels, native session-preserving controls, no HTML anchor navigation, admin-only visibility, user initials, category/breadcrumb mapping, active underline, exact Streamlit pin, and responsive breakpoint CSS.

## Browser verification

The header was rendered through the `/operationaldashboard/` base path at **1920, 1560, 1366, and 1280 px**. Every required width had one desktop menu row, zero overflowing labels, no horizontal document overflow, the correct active underline, and no browser console/page errors. A 1279 px capture confirmed the native hamburger menu breakpoint.

See `VISUAL_VERIFICATION_v3.11.0.md`, `verification/v3.11.0/header_measurements.json`, and the five PNG captures in that directory.
