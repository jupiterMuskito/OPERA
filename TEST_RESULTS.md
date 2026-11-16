# OPERA v3.3.0 — Test Results

Tested on 16 November 2026.

## Automated verification

```text
python3 -m py_compile app.py opera/*.py scripts/seed_data.py
Result: PASS

pytest -q
Result: PASS — 26 tests
```

The suite covers:

- login, Business Unit selection and Home startup;
- roles, password hashing and locked CSV storage;
- formulas, ordered calculations and target status;
- selective bulk templates and placeholder-source input;
- Cement hierarchy and approved risk-register loading/PDF generation;
- dashboard-template configuration and equipment overrides;
- DCS / Field / QAQC / Others grouping;
- Instrument Check terminology and Field/DCS source restriction;
- 1-hour, 6-hour and 12-hour trend rules;
- intelligent equipment-to-parameter mapping and exact-equipment Admin overrides;
- configurable Operations KPI fields;
- 365-day sample coverage, all active source fields, all active BUs, all three Cement plants and all 201 named Cement equipment records;
- export and target-highlighting behavior.

## Streamlit changed-page smoke test

A scripted BU Admin session signed in, selected Cement and opened each changed area without an application exception:

```text
Plant Overview        PASS
Equipment Overview    PASS
Operations Dashboard  PASS
Operational Data      PASS
Admin / Super Admin   PASS
```

The test host had a preinstalled NumPy/PyArrow mismatch outside the package requirements. OPERA's new safe table renderer was exercised and kept all pages available through a static preview. A normal deployment should install the versions declared in `requirements.txt`, which retain interactive dataframes/editors.

## Independent sample-data verification

A separate validation read the packaged DCS, Field and Lab CSVs for Cement, Refinery, Fertilizer and NASCON and confirmed:

- 365 distinct dates: 16 November 2025 through 15 November 2026;
- every one of the 20 active fields in each source is populated on every sample row;
- Cement contains Okpella, Obajana and Ibese in every active source file;
- Cement sample rows cover all 201 named equipment records;
- DCS and Field use 00:00, 06:00, 12:00 and 18:00 readings; Lab uses one daily reading.

## Result

**PASS.** The v3.3.0 deployment package is ready for Streamlit deployment and repository review, subject to the CSV overwrite warnings in `CHANGE_MANIFEST_v3.3.0_vs_v3.2.0.md`.
