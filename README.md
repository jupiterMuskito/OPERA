# OPERA — Operational Excellence and Reliability Assistant

OPERA is a role-based Streamlit application for operational dashboards, validated plant data, event and lesson management, calculated KPIs, operating parameters, and register-backed risk assessments.

## Deployment

1. Unzip the package without changing its folder structure.
2. Create a new Streamlit Community Cloud app and select `app.py` as the entry point.
3. Use Python 3.12 (`runtime.txt`). Dependencies are in `requirements.txt`.
4. Optional: copy `.streamlit/secrets.example.toml` into Streamlit Cloud **App settings → Secrets**, replace every placeholder, and never commit a real `secrets.toml`.
5. Start locally with:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

For a later server deployment, set `OPERA_DATA_DIR` to persistent storage. The CSV persistence, locking, atomic replacement, attachments, audit, notifications and risk-register uploads are isolated in the shared storage services.

## Seeded test logins

All seeded accounts use the temporary password `ChangeMe!2026`.

| Username | Role | Business-unit access |
|---|---|---|
| `superadmin` | Super Admin | All; forced password change on first login |
| `buadmin` | BU Admin | Cement, Refinery, Fertilizer, NASCO |
| `operator` | Operator | Cement, Refinery, Fertilizer, NASCO |
| `viewer` | Viewer | Cement, Refinery, Fertilizer, NASCO |

Change or disable every seeded account before production. Passwords in `users.csv` are PBKDF2-SHA256 hashes; five failed attempts lock an account for 15 minutes. Matching users can be overridden through Streamlit Secrets.

## Business units and hierarchy

- Active: Cement, Refinery, Fertilizer and NASCO.
- NASCO contains Salt and Sugar sections.
- Refinery contains the Butamer unit.
- BU5–BU9 are inactive placeholders. A Super Admin can name and activate a placeholder or clone an existing BU without code.
- Equipment follows `Business unit → Plant → Unit/Section → Equipment`.
- Cement's 67 named equipment items and section assignments come from the unmodified `OKPELLA_Master_Workbook_v8.xlsx`; 500 `CEM-SPARE-*` placeholders are retained.

## Main application flow

`Login → Business Unit → OPERA Home → module`

`Data Input → Event Log → Data Analysis → Data Output`

Modules:

- Plant Overview, Equipment Overview and Operations Dashboard
- Data Input: manual, validated bulk upload and DCS JSON connector
- Event Log: report, table or picture events; stored notifications
- Data Analysis: multi-field comparison, statistics, forecast, and Field vs DCS Monitor/Critical checks with shutdown-day exclusion
- Data Output: calculated fields and input/calculated/merged Excel downloads
- Operating Parameters: Process and Quality
- Risk Assessment: deterministic, Excel-register-backed assessments and PDFs
- Lesson Bank: lessons linked to Event Log events
- Admin / Super Admin: BUs, users, fields, UOM, ranges, targets, formulas, constants, equipment, registers, DCS connector, presets, audit and backups

## Data and calculated fields

Each BU has one CSV per source: DCS (`DP1–DP1000`), Lab (`L1–L1000`), Field (`F1–F1000`), and placeholders `TA1–TG1000`. DCS, Lab and Field contain 20 realistic active sample fields for the four active BUs. The seven placeholder sources have no sample rows; activate their fields in **Admin → Fields & formulas** before use.

Manual and bulk rows use ISO dates and 24-hour time. Values are checked for numeric format, configured range and abnormal jumps. Flags are retained in `flags.csv`. CSV values are protected from spreadsheet-formula injection.

The ordered formula engine supports field references such as `[DP1]`, baseline constants, arithmetic, comparisons and `IF`, `MIN`, `MAX`, `ABS`, `MOD`, and `ROUND`. Active BUs include eight named sample calculated fields. KPI cards show value, target, variance and On/Off Target status. Current, Period Total, MTD and YTD templates use Daily/Period targets and configured aggregation.

## Risk registers

The deployment keeps approved registers as Excel workbooks and does not modify them:

- Cement: `registers/OKPELLA_Master_Workbook_v8.xlsx`
- Refinery: `registers/DANGOTE_REFINERY_Master_Workbook_v1.xlsx`
- Fertilizer: `registers/DANGOTE_FERTILISER_Master_Workbook_v1.xlsx`

NASCO and new BUs require an approved register upload before risk assessments can be generated. Register uploads are validated before activation. Optional GitHub commit persistence is available through `[github]` secrets for Community Cloud testing.

## Community Cloud persistence warning

Local file changes can be lost when a Community Cloud container restarts. For testing, use the built-in download/backup functions and optional GitHub persistence for risk registers. For production, mount persistent server storage and set `OPERA_DATA_DIR`.

## Tests

Run:

```bash
pytest
python -m py_compile app.py opera/*.py scripts/seed_data.py
```

The included suite covers the formula engine, secure roles and hashes, locked CSV storage, bulk/placeholder-source validation, Excel round-trip, Cement hierarchy provenance, Cement v8 register loading and P23 risk/PDF generation, and Streamlit startup.

See `BUILD_NOTES.md` and `TEST_RESULTS.md` for integration decisions and verification results.
