# OPERA-X — Operational Excellence and Reliability Assistant

OPERA-X is a role-based Streamlit application for operational dashboards, validated plant data, event and lesson management, calculated KPIs, operating parameters, process optimization, and register-backed Job Risk Assessments.

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

For persistent server storage, set `OPERAX_DATA_DIR`. Existing deployments that define `OPERA_DATA_DIR=~/opera_data` remain fully compatible. The application also remains compatible with Streamlit Community Cloud and with the DDF nginx reverse-proxy deployment at `/operationaldashboard/` because the packaged brand images are local and are rendered without root-relative URLs.

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

The fixed first ribbon carries OPERA-X branding. The fixed navigation bar retains the compact v3.8-style page labels and directly contains navigation, business-unit/user context and notifications. **Change BU** is stacked above **Sign Out**, with a transparent Vision 2030 mark beside the button stack. The rounded blue page-title/subtitle hero remains removed from authenticated modules.

Modules:

- **Operational Data:** Plant Overview, Equipment Overview, Operations Dashboard, Operating Parameters, Process Optimization, and **Operational Data Pipeline**.
- **Operational Data Pipeline:** the user-facing name for the retained Manual Entry, Bulk Upload, Derived Data and Analyze Data workspace. Internal route, file and storage identifiers remain unchanged.
- **Operational Knowledge:** Event Log, Lesson Bank, and Job Risk Assessment.
- **Process Optimization:** bounded-response decision support grouped under Operational Data; no duplicate Optimization tab remains in Operational Data Pipeline.
- **Job Risk Assessment:** deterministic, register-backed job hazard assessment grouped under Operational Knowledge, with Job Risk Assessment PDF and Excel/CSV export labels.
- Plant Overview, Equipment Overview and Operations Dashboard provide configurable templates, KPI fields, chart fields, table fields, and chart type. Operations setup accepts Digital Data, Raw Field Data, QAQC and Calculated fields in one catalog.
- CPP-style charts: 12 configurable template fields, rendered four panels at a time in a two-column grid for responsive loading, or in one combined same-axis chart. v3.8 uses a compact 231 px chart height.
- Operational Data Pipeline uses one lazy-loaded ribbon: **Manual Entry**, **Bulk Upload**, **Derived Data**, and **Analyze Data**; only the selected area executes. Analyze Data contains comparisons, statistics, forecasts and Instrument Check.
- Digital Data endpoint setup and manual pipeline execution are under **Admin / Super Admin → Digital Data Connector**.
- Event Log supports report, table, or picture events; notifications; and optional mapped Raw Field Data updates.
- Lesson Bank supports event links, attachments, read counts, and OPERA-X PDF downloads.

## Data-field mapping

Every input field, placeholder (`DP`, `L`, `F`, and `TA`–`TG`), and calculated field is stored in each BU's `field_mappings.xlsx` runtime database with:

- at least one equipment record; and
- at least one of **Plant Performance**, **Condition Monitoring**, **Process Performance**, **Quality and Compliance**, or **Reliability**.
- a plain-language **Mapping Basis** and **Confidence** (`High`, `Medium`, or `Review`); and
- any same-point Digital Data/Raw Field Data **Instrument Check Pair IDs**.

The named defaults are field-by-field process-engineering assignments, not round-robin/index/random mappings. Cement covers Okpella, Obajana and Ibese equipment; Refinery covers the Butamer process train; Fertilizer covers reforming, ammonia, urea and granulation; NASCON covers Salt and Sugar. Calculated fields inherit equipment from their formula inputs. Unnamed placeholders use source-aware SPARE equipment and are clearly labelled **Default placeholder mapping – review when field is named**.

When equipment or a dashboard template is selected, related data-field dropdowns are automatically filtered by the applicable map. This applies to Plant Overview, Equipment Overview, Manual Entry, Bulk Upload, Event Log field updates, and Operating Parameters. Operations Dashboard KPI and chart controls remain filtered by the chosen Operations template.

To download the controlled mapping workbook, use **Admin / Super Admin → Data Field Mapping → Excel mapping database and bulk update → Prepare Excel Mapping Update Template → Download Excel Update Template**. In **Field Catalogue**, the Dashboard Template ID/Template columns sit beside the Equipment ID/Equipment columns. Add another included row for each additional equipment or dashboard-template relationship. The five Dashboard Template IDs are controlled by an Excel dropdown and are listed with their names in **Template Catalogue**.

**Admin / Super Admin → Field Mappings** shows the complete effective mapping—not only overrides—with business-unit, plant, unit, equipment, dashboard-template, source and status filters plus Field ID/name search. It includes field, reverse-equipment and reverse-template views. Administrators can edit or reset any active, placeholder or calculated field. Saves are written to the audit log and persisted directly in `field_mappings.xlsx`; the `Default Mappings` sheet supplies the reset baseline.

The page provides three Excel workflows. The Excel workbook remains authoritative; a derived compressed runtime cache is rebuilt automatically when the workbook changes, cutting repeated page reads without hiding Admin edits:

- **Excel Mapping Update Template** — a combined Field Catalogue where each editable row maps a field to both an Equipment ID and Dashboard Template ID, with dropdown validation for both columns plus Field ID and Include. Field Review retains controlled Apply Update and Confidence inputs. Separate equipment/template sheets remain for compatibility.
- **Bulk upload** — validates IDs, required sheets, non-empty relationships, confidence values and Digital Data/Raw Field Data pair integrity before atomically updating the mapping database and audit log.
- **Excel Mapping Database / Complete Mapping Workbook** — backend database review plus human-readable field, equipment and template views.

Pre-v3.9 live mapping workbooks are upgraded automatically when loaded. Missing `Template IDs` and `Dashboard Templates` columns are added in place from the retained mappings/current engineering defaults; existing equipment mappings, administrator metadata and other worksheets are preserved. No manual `~/opera_data` edit is required.

Instrument Check reads recorded Digital Data/Raw Field Data pairs from the mapping database and selects the appropriate same-point pair by default. See `MAPPING_QUALITY_REPORT.md` for counts by BU/template, all named `Review` items, grouped placeholder reviews, calculated-field checks, and 20 sample mappings with their reasoning.

## Data and persistence

Each BU has one CSV per source: Digital Data (`DP1–DP1000`, persisted internally as source key `DCS`), QAQC (`L1–L1000`), Raw Field Data (`F1–F1000`, persisted internally as source key `Field`), and placeholders `TA1–TG1000`. The internal source keys and DP/F field IDs are intentionally unchanged so existing CSVs, mappings and live readings continue to work. Manual and bulk rows use ISO dates and 24-hour time. Values are checked for numeric format, configured range, and abnormal jumps. CSV values are protected from spreadsheet-formula injection.

Community Cloud local file changes can be lost after a restart. For testing, use built-in backup/download functions. For production, use persistent storage through `OPERAX_DATA_DIR`.

For an existing v3.10.0 deployment, apply `OPERA-X_Code_Only_Update_v3.10.1_vs_v3.10.0.zip`. It excludes the complete `data/`, `registers/` and `reference_sources/` trees. Do not copy the full deployment package over a live `~/opera_data` directory: it contains seeded users, readings, mappings, formulas, events, lessons and other runtime files. v3.10.1 requires no live-data migration; see `LIVE_DATA_UPDATE_v3.10.1.md`.

## Risk registers

Bundled approved Excel workbooks remain unchanged:

- Cement: `registers/OKPELLA_Master_Workbook_v8.xlsx`
- Refinery: `registers/DANGOTE_REFINERY_Master_Workbook_v1.xlsx`
- Fertilizer: `registers/DANGOTE_FERTILISER_Master_Workbook_v1.xlsx`

NASCON and new BUs require an approved register upload before Job Risk Assessments can be generated. The packaged and live register filenames, `risk_assessments.csv`, `registers/` folder and risk-related Python identifiers remain unchanged for backward compatibility; only user-facing labels and new audit action values use “Job Risk Assessment”.

## Tests

```bash
pytest -q
python -m py_compile app.py opera/*.py scripts/*.py
```

The automated suite includes end-to-end page rendering and Admin propagation, source-label/backward-compatibility checks, combined equipment/template Field Catalogue upload, Operational Data Pipeline naming and grouping, transparent Vision 2030 assets, the stacked header layout, branding, Job Risk Assessment labels, Home drill-down/Excel grouping, the mixed-source Operations catalog, compact charts, fixed-navigation UI, and agreement between the banner, package version and authoritative `VERSION` file.

See `BUILD_NOTES.md`, `TEST_RESULTS.md`, `ROOT_CAUSE_AND_FIX_v3.10.1.md`, `LIVE_DATA_UPDATE_v3.10.1.md`, `CHANGE_MANIFEST_v3.10.1_vs_v3.10.0.md`, and the retained earlier release, root-cause and performance reports.
