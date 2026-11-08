# OPERA v3.0.0 — Build Notes

## Final-review objectives included

- BU → Plant → Unit/Section → Equipment hierarchy.
- Selectable dashboard templates on Equipment Overview and Operations Dashboard.
- Excel, CSV and PDF export preparation with audit entries.
- Event picture attachments, data-table/report formats, notifications and automatic user/time capture.
- JSON preset save/download/upload.
- No-code BU cloning, placeholder activation and configuration.
- Login, configuration, input/upload, risk and export audit coverage.
- Lesson Bank linked to Event Log IDs.
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
- Butamer 6-hourly Field model and Field vs DCS Monitor/Critical comparison logic; shutdown dates come from Event Log events tagged `Shutdown`.
- Operational Intelligence safe formula concepts, profiles, presets and report/export patterns.
- CPP ordered calculated fields, formula functions, On Hold behaviour, targets/direction, Current/Period/MTD/YTD views, KPI card semantics, sign-off fields, trend granularity, comparison, regression/forecast, and blue/red visual language. Plotly replaces Chart.js.
- Current portal BU configuration and no-code cloning concept, rewritten for locked CSV storage.

### Delete or exclude from deployment

- Old SQLite persistence and reconstructed generic demo pages.
- Old Digital Operator Rounds and SOP Knowledge Portal pages; relevant Butamer logic is integrated into Data Input, Data Analysis, Event Log and Lesson Bank instead.
- `ai_agent.py` and all Copilot Analyst AI UI/connectors.
- RA v5.3 test account, printed test password, built-in admin hash and separate admin password page.
- Packaging BU and separate Sugar/NASCON entries; NASCO now contains Salt and Sugar sections.
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

- Cement named equipment is real Okpella register data and supersedes the earlier general-knowledge assumption.
- Refinery, Fertilizer and NASCO named operational equipment remains an initial industry-based list and must be reviewed by each plant. Every BU retains 500 spare equipment records for controlled activation.
- NASCO has no approved risk workbook in the supplied sources; risk generation remains blocked until an approved Excel register is uploaded.
- Sample data is synthetic and is only for functional testing. Deliberate outliers are marked in each active BU's `flags.csv`.
- Streamlit's native immediate toast is combined with a persistent notification centre. Notification rows remain until read; native toast display duration is controlled by Streamlit rather than fixed at exactly 60 seconds.
- The DCS connector expects an HTTPS JSON array or `{ "data": [...] }` and requires the endpoint to emit OPERA column names. Production authentication tokens belong in Streamlit Secrets.
- Community Cloud storage is ephemeral. A server deployment should set `OPERA_DATA_DIR` to persistent storage; GitHub persistence is retained only for test-phase risk-register uploads.

## Data package summary

For each active BU: 10,000 registered input fields, 60 active named sample fields, eight named calculated fields, 30 days of data (DCS and Field four readings/day; Lab daily), 10 source CSVs, event/flag/lesson/notification/preset/audit registries, and 500 equipment placeholders. TA–TG contain no sample rows but are covered by automated entry, calculation and export tests.
