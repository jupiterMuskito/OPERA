# OPERA v3.3.0 — Build Notes

## v3.3.0 update

- Renamed the legacy Field/DCS comparison workflow to **Instrument Check**. Its source controls are deliberately limited to one Field reading and one DCS reading.
- Rebuilt the application header as three ordered ribbons: OPERA name/tagline, Business Unit/user context, then a fixed responsive navigation grid.
- Aligned OPERA Home module panels with fixed card geometry and consistent action placement.
- Increased KPI-card internal spacing and aligned title/value/target/status content. Each Operations Dashboard KPI card now has a selectable card-name/data-field control.
- Added 1-hour, 6-hour and 12-hour trend granularity while retaining daily, weekly, monthly and yearly options.
- Added semantic equipment-to-parameter ranking. Equipment Overview derives key parameters from the selected equipment name/type, uses an exact Admin override when present, and exposes the DCS / Field / QAQC / Others selection tool.
- Added selectable chart headers to Plant and Equipment Overview, selectable combined-chart legend fields, and table-field selectors. The CPP-style two-column chart grid remains the default split layout.
- Extended Admin dashboard templates with Operations KPI fields and clarified per-equipment key-parameter override controls. Plant Overview, Equipment Overview and Operations Dashboard remain configurable.
- Replaced the 30-day single-site sample with a trailing 365-day dataset (16 November 2025 through 15 November 2026) for every active BU. DCS and Field readings are six-hourly; QAQC/Lab readings are daily. Cement covers Okpella, Obajana and Ibese and rotates readings across all 201 named equipment records.
- Fixed the calculated-data QAQC/Lab join to retain Plant in the daily merge, preventing cross-plant duplication once the three Cement plants have same-date samples.
- Added v3.3 regression tests for terminology, trend intervals, equipment mapping/overrides, configurable KPI fields, complete active-field population, one-year date coverage and all Cement plants/equipment.

## v3.2.0 baseline retained

- Replaced the left sidebar with a responsive top navigation bar and added a dedicated OPERA PNG app icon.
- Applied the tagline **One Platform for All Plant Operational Data**, removed the Home operating-flow panel and technical login credential caption, aligned the Business Unit selector/action, and made Home module cards actionable.
- Consolidated Data Input, Data Output and Data Analysis into **Operational Data**, ordered as **Input Data**, **Derived Data**, **Analyze Data**.
- Added selective bulk templates: the user chooses a source and exact active fields before downloading a template; uploads are checked against that selection.
- Standardized selector groups as DCS=`DP`, Field=`F`, QAQC=`L` (Laboratory), Others=`TA`–`TG`.
- Added bounded linear-response optimization with maximize, minimize and target-matching goals, configurable bounds, model-fit reporting and audit logging.
- Added target-aware red highlighting to generated UI tables and Excel/PDF exports. Wide PDF exports are split into readable wrapped column groups to prevent overlap.
- Fixed Equipment Overview aggregation by using explicit named aggregations rather than assigning a fixed list to a version-dependent grouped result.
- Expanded Lesson Bank with titles, equipment/unit/most-read filters, an explicit saved-lesson view action, read counts, Word/text/image/PDF/video supporting files, previews/downloads and lesson PDF generation.
- Operating Parameters now lists every active configured equipment record and exposes all four field groups.
- Equipment Overview templates now support per-equipment chart/table field overrides with template defaults as fallback.
- Added in-app calculated-formula guidance and corrected Cement `CF2` to **Kiln Speed** (`[DP2]`) and `CF3` to **Kiln Inlet Oxygen** (`[DP3]`); the remaining Cement calculated-field names were checked against their linked formulas.
- **Baseline constants decision:** retained because `calculated_data()` passes them into the safe ordered formula engine, allowing reusable numeric assumptions in formulas. The technical JSON editor was removed and replaced with a plain-language explanation plus a validated name/value table.
- Removed superseded navigation and Home-flow code while retaining the Operational Intelligence visual language and CPP-style chart grid.

## Update objectives included

- Operational Intelligence visual language applied across sign-in, navigation, page headers, cards, forms, tables and charts.
- Consistent chart cards with a two-column individual-axis grid, plus an explicit same-axis option for every chart type.
- Admin-managed Plant Overview, Equipment Overview and Operations Dashboard templates: template name, chart fields, table fields and chart type.
- Plant Overview charts shown before the data table.
- Fixed, editable Plant, Unit / Section and Equipment Type validation lists; equipment editing uses dropdowns from those lists.
- Event Log can send an update for any active Field Data (`F`) field for later Instrument Check analysis.
- Lesson Bank entries are independent; linking to an Event Log entry is optional.
- Obajana Cement Plant and Ibese Cement Plant added by cloning all 67 named Okpella equipment records without consuming spares.
- NASCON naming applied to the business-unit ID, display name, access lists, data records and reproducible seed script.
- Change-Business-Unit and Sign-Out controls use permanently visible text/icons; Operations KPI cards have fixed aligned dimensions.
- Excel, CSV and PDF export preparation with audit entries remains available.
- OPERA branding; no Analyst AI, old rounds page or SOP portal page.
- Excel-register-backed Risk Assessment with optional GitHub persistence during Community Cloud testing.

## Keep / port / delete-or-exclude review

This list was prepared before excluding obsolete material. Source files in OneDrive were not deleted; excluded items are simply absent from the deployment package.

### Keep unchanged

- `OKPELLA_Master_Workbook_v8.xlsx` — approved Cement risk register; unmodified.
- `DANGOTE_REFINERY_Master_Workbook_v1.xlsx` — Refinery risk register; unmodified.
- `DANGOTE_FERTILISER_Master_Workbook_v1.xlsx` — Fertilizer risk register; unmodified.
- `Data_butamer.xlsx` — retained in `reference_sources/` for traceability.
- `OCL_Captive_Coal_Power_Plant_Operations_Dashboard_1.10.html` — retained in `reference_sources/` as the calculated-field/dashboard design reference.
- Streamlit deployment assets: `app.py`, `requirements.txt`, `runtime.txt`, `.streamlit/config.toml` and secrets example.

### Port into OPERA

- RA v5.3 deterministic loader/hazard engine and ReportLab risk PDF implementation.
- RA register activation/history pattern and optional GitHub-commit persistence, with hard-coded test/admin credentials removed.
- Butamer 6-hourly Field model and Instrument Check Monitor/Critical comparison logic; shutdown dates come from Event Log events tagged `Shutdown`.
- Operational Intelligence safe formula concepts, profiles, presets and report/export patterns.
- Ordered calculated fields, formula functions, On Hold behaviour, targets/direction, Current/Period/MTD/YTD views, KPI card semantics, sign-off fields, trend granularity, comparison, regression/forecast, and the approved blue/red visual language. Plotly is used for Streamlit-native interactive charts.
- Current portal BU configuration and no-code cloning concept, rewritten for locked CSV storage.

### Delete or exclude from deployment

- Old SQLite persistence and reconstructed generic demo pages.
- Old Digital Operator Rounds and SOP Knowledge Portal pages; relevant Butamer logic is integrated into Data Input, Data Analysis, Event Log and Lesson Bank instead.
- `ai_agent.py` and all Copilot Analyst AI UI/connectors.
- RA v5.3 test account, printed test password, built-in admin hash and separate admin password page.
- Packaging BU and the separate Sugar entry; NASCON contains the Salt and Sugar sections.
- RA default-register source generators; approved Excel workbooks are used directly.
- Duplicate `__init__` files, download stubs, old generated packages, caches and local secrets.

## Cement register verification

`OKPELLA_Master_Workbook_v8.xlsx` was opened read-only and checked against the RA v5.3 loader.

- Sheet order found: ReadMe, Lists, Locations, JobTags, EquipmentTypes, Equipment, ActivityHazards, EquipmentHazards, TaskPresets, ToolRecognition, InferenceRules, ReportTemplate, AgentText.
- Required sheets all present: JobTags, EquipmentTypes, Equipment, ActivityHazards and EquipmentHazards.
- Loader-used optional sheets present: Lists, Locations, TaskPresets, ToolRecognition and InferenceRules.
- `Settings` and `Synonyms` are absent, but optional. The loader uses its documented defaults and does not alter the workbook.
- ReportTemplate and AgentText are retained in the workbook and intentionally ignored by the Streamlit engine.
- Loaded counts: 46 locations, 166 job tags, 28 equipment types, 67 equipment items, 259 activity hazards, 101 equipment hazards, 87 presets, 66 tool rules and 20 inference rules.
- Loader warnings: zero. Fingerprint at build time: `A0E4BE03`.
- P23 `Kiln refractory brick lining` generated 22 applicable hazards in the automated test.

No schema mismatch required a loader workaround. The workbook is copied as-is. Cement hierarchy/equipment is generated from its `Equipment`, `LocationScope` and `LocationArea1–10` data. An item's first listed area is used as its primary OPERA Unit/Section; plant-wide scopes are labelled accordingly.

## Assumptions and review items

- Cement named equipment is real Okpella register data and supersedes the earlier general-knowledge assumption. Obajana and Ibese are configuration clones of that hierarchy and should be checked against each plant's approved master data.
- Refinery, Fertilizer and NASCON named operational equipment remains an initial industry-based list and must be reviewed by each plant. Every BU retains 500 spare equipment records for controlled activation.
- NASCON has no approved risk workbook in the supplied sources; risk generation remains blocked until an approved Excel register is uploaded.
- Sample data is synthetic and is only for functional testing. Deliberate outliers are marked in each active BU's `flags.csv`.
- Streamlit's native immediate toast is combined with a persistent notification centre. Notification rows remain until read; native toast display duration is controlled by Streamlit rather than fixed at exactly 60 seconds.
- The DCS connector expects an HTTPS JSON array or `{ "data": [...] }` and requires the endpoint to emit OPERA column names. Production authentication tokens belong in Streamlit Secrets.
- Community Cloud storage is ephemeral. A server deployment should set `OPERA_DATA_DIR` to persistent storage; GitHub persistence is retained only for test-phase risk-register uploads.

## Data package summary

For each active BU: 10,000 registered input fields, 60 active named sample fields, eight named calculated fields, 365 days of data (DCS and Field four readings/day; Lab daily), 10 source CSVs, event/flag/lesson/notification/preset/audit registries, and 500 equipment placeholders. Cement's three plants each have the full year and rotate readings across all 67 named plant equipment records. TA–TG contain no sample rows but are covered by automated entry, calculation and export tests.
