# OPERA-X — Operational Excellence and Reliability Assistant

OPERA-X is a role-based Streamlit application for operational dashboards, validated plant data, event and lesson management, calculated KPIs, operating parameters, and register-backed risk assessments.

## Deployment

1. Unzip the deployment package without changing its folder structure.
2. Create or update the Streamlit app and use `app.py` as the entry point.
3. Use Python 3.12 (`runtime.txt`) and install `requirements.txt`.
4. Optional: copy `.streamlit/secrets.example.toml` into Streamlit Cloud **App settings → Secrets**, replace all placeholders, and never commit a real `secrets.toml`.
5. Start locally with:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

For persistent server storage, set `OPERAX_DATA_DIR`. Existing deployments that still define `OPERA_DATA_DIR` remain compatible, but should migrate to the new variable name.

## Seeded test logins

All seeded accounts use the temporary password `ChangeMe!2026`.

| Username | Role | Business-unit access |
|---|---|---|
| `superadmin` | Super Admin | All; forced password change on first login |
| `buadmin` | BU Admin | Cement, Refinery, Fertilizer, NASCON |
| `operator` | Operator | Cement, Refinery, Fertilizer, NASCON |
| `viewer` | Viewer | Cement, Refinery, Fertilizer, NASCON |

Change or disable every seeded account before production. Passwords are PBKDF2-SHA256 hashes; five failed attempts lock an account for 15 minutes. Matching users can be overridden through Streamlit Secrets.

## Main application flow

`Login → Business Unit → OPERA-X Home → module`

The fixed first ribbon carries OPERA-X branding. The fixed navigation bar directly contains navigation, notifications, **Change BU**, and **Sign Out**. The previous separate context/control ribbon has been removed.

Modules:

- Plant Overview, Equipment Overview and Operations Dashboard with configurable templates, KPI fields, chart fields, table fields, and chart type.
- CPP-style charts: two-column individual-axis grids or combined same-axis charts.
- Operational Data uses one ribbon: **Manual Entry**, **Bulk Upload**, **Derived Data**, and **Analyze Data**.
- DCS endpoint setup and manual pipeline execution are under **Admin / Super Admin → DCS Connector**.
- Event Log supports report, table, or picture events; notifications; and optional mapped Field Data updates.
- Analyze Data supports grouped comparisons, statistics, forecast, bounded optimization, and Instrument Check.
- Risk Assessment produces deterministic, register-backed OPERA-X PDF reports.
- Lesson Bank supports event links, attachments, read counts, and OPERA-X PDF downloads.

## Data-field mapping

Every input field and placeholder (`DP`, `L`, `F`, and `TA`–`TG`) receives a deterministic default mapping to:

- at least one equipment record; and
- at least one of **Plant Performance**, **Condition Monitoring**, **Process Performance**, **Quality and Compliance**, or **Reliability**.

When equipment or a dashboard template is selected, related data-field dropdowns are automatically filtered by the applicable map. This applies to Plant Overview, Equipment Overview, Manual Entry, Bulk Upload, Event Log field updates, and Operating Parameters. Operations Dashboard KPI and chart controls remain filtered by the chosen Operations template.

Administrators can update any active or placeholder field under **Admin / Super Admin → Field Mappings**. Only Admin overrides are persisted to `field_mappings.json`; defaults remain code-driven, so an upgrade does not need to replace production data files.

## Data and persistence

Each BU has one CSV per source: DCS (`DP1–DP1000`), Lab (`L1–L1000`), Field (`F1–F1000`), and placeholders `TA1–TG1000`. Manual and bulk rows use ISO dates and 24-hour time. Values are checked for numeric format, configured range, and abnormal jumps. CSV values are protected from spreadsheet-formula injection.

Community Cloud local file changes can be lost after a restart. For testing, use built-in backup/download functions. For production, use persistent storage through `OPERAX_DATA_DIR`.

## Risk registers

Bundled approved Excel workbooks remain unchanged:

- Cement: `registers/OKPELLA_Master_Workbook_v8.xlsx`
- Refinery: `registers/DANGOTE_REFINERY_Master_Workbook_v1.xlsx`
- Fertilizer: `registers/DANGOTE_FERTILISER_Master_Workbook_v1.xlsx`

NASCON and new BUs require an approved register upload before risk assessments can be generated.

## Tests

```bash
pytest -q
python -m py_compile app.py opera/*.py scripts/seed_data.py
```

The suite covers the formula engine, roles and password hashes, locked CSV storage, upload validation, Excel round-trip, field-mapping coverage and filtering, export branding metadata, dashboard configuration, Cement hierarchy/register behavior, risk/PDF generation, and Streamlit startup.

See `BUILD_NOTES.md`, `TEST_RESULTS.md`, and `CHANGE_MANIFEST_v3.4.0_vs_v3.3.0.md`.
