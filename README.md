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

`Login → Business Unit → fixed OPERA-X brand ribbon → fixed merged navigation → module content`

The fixed first ribbon carries OPERA-X branding. The fixed navigation bar directly contains navigation, business-unit/user context, notifications, **Change BU**, and **Sign Out**. The rounded blue page-title/subtitle hero has been removed from every authenticated module and was not replaced by another coloured banner.

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

Every input field, placeholder (`DP`, `L`, `F`, and `TA`–`TG`), and calculated field is stored in each BU's `field_mappings.xlsx` runtime database with:

- at least one equipment record; and
- at least one of **Plant Performance**, **Condition Monitoring**, **Process Performance**, **Quality and Compliance**, or **Reliability**.
- a plain-language **Mapping Basis** and **Confidence** (`High`, `Medium`, or `Review`); and
- any same-point DCS/Field **Instrument Check Pair IDs**.

The named defaults are field-by-field process-engineering assignments, not round-robin/index/random mappings. Cement covers Okpella, Obajana and Ibese equipment; Refinery covers the Butamer process train; Fertilizer covers reforming, ammonia, urea and granulation; NASCON covers Salt and Sugar. Calculated fields inherit equipment from their formula inputs. Unnamed placeholders use source-aware SPARE equipment and are clearly labelled **Default placeholder mapping – review when field is named**.

When equipment or a dashboard template is selected, related data-field dropdowns are automatically filtered by the applicable map. This applies to Plant Overview, Equipment Overview, Manual Entry, Bulk Upload, Event Log field updates, and Operating Parameters. Operations Dashboard KPI and chart controls remain filtered by the chosen Operations template.

**Admin / Super Admin → Field Mappings** shows the complete effective mapping—not only overrides—with business-unit, plant, unit, equipment, dashboard-template, source and status filters plus Field ID/name search. It includes field, reverse-equipment and reverse-template views. Administrators can edit or reset any active, placeholder or calculated field. Saves are written to the audit log and persisted directly in `field_mappings.xlsx`; the `Default Mappings` sheet supplies the reset baseline.

The page provides three Excel workflows:

- **Excel Mapping Update Template** — editable equipment/template relationships plus Field Review metadata; controlled dropdown validation for Field ID, Equipment ID, Dashboard Template ID, Apply Update, Include and Confidence.
- **Bulk upload** — validates IDs, required sheets, non-empty relationships, confidence values and DCS/Field pair integrity before atomically updating the mapping database and audit log.
- **Excel Mapping Database / Complete Mapping Workbook** — backend database review plus human-readable field, equipment and template views.

Instrument Check reads recorded DCS/Field pairs from the mapping database and selects the appropriate same-point pair by default. See `MAPPING_QUALITY_REPORT.md` for counts by BU/template, all named `Review` items, grouped placeholder reviews, calculated-field checks, and 20 sample mappings with their reasoning.

## Data and persistence

Each BU has one CSV per source: DCS (`DP1–DP1000`), Lab (`L1–L1000`), Field (`F1–F1000`), and placeholders `TA1–TG1000`. Manual and bulk rows use ISO dates and 24-hour time. Values are checked for numeric format, configured range, and abnormal jumps. CSV values are protected from spreadsheet-formula injection.

Community Cloud local file changes can be lost after a restart. For testing, use built-in backup/download functions. For production, use persistent storage through `OPERAX_DATA_DIR`.

For an existing deployment, apply `OPERA-X_Code_Only_Update_v3.6.0.zip`. It excludes runtime CSV/XLSX files. On first use, v3.6.0 creates `field_mappings.xlsx` from the engineering baseline and migrates any legacy `field_mappings.json` overrides as `Review` items. Do not copy the full deployment package over a live `data/` directory: it contains seed/runtime files that can replace readings, equipment, calculated fields and mappings entered through the app. See `DATA_OVERWRITE_WARNING.md` for the exact inventory.

## Risk registers

Bundled approved Excel workbooks remain unchanged:

- Cement: `registers/OKPELLA_Master_Workbook_v8.xlsx`
- Refinery: `registers/DANGOTE_REFINERY_Master_Workbook_v1.xlsx`
- Fertilizer: `registers/DANGOTE_FERTILISER_Master_Workbook_v1.xlsx`

NASCON and new BUs require an approved register upload before risk assessments can be generated.

## Tests

```bash
pytest -q
python -m py_compile app.py opera/*.py scripts/*.py
```

The 40-test suite covers the formula engine, roles and password hashes, locked CSV storage, upload validation, Excel round-trip, engineering mapping assignments, placeholder SPARE rules, calculated-field inheritance, Instrument Check pairs, controlled mapping workbooks, partial bulk updates, field-mapping filtering, export branding metadata, dashboard configuration, Cement hierarchy/register behavior, risk/PDF generation, and every authenticated Streamlit route.

See `BUILD_NOTES.md`, `TEST_RESULTS.md`, `CHANGE_MANIFEST_v3.6.0_vs_v3.5.0.md`, `MAPPING_QUALITY_REPORT.md`, and `DATA_OVERWRITE_WARNING.md`.
