# OPERA-X v3.13.0 Build Notes

Base: `OPERA-X_Streamlit_Deployment_v3.12.0_Final.zip`

## Changes

### Breadcrumb-area headings

- Removed the remaining `Modules` heading on OPERA-X Home.
- Removed the remaining `Operational Data Pipeline` heading on Data Pipeline.
- Audited authenticated routes for duplicated page-title headings below the breadcrumb. Sign-in, BU selection and the forced-password-change screen keep their own headings because they do not render the authenticated breadcrumb.

### Automatic Upload

- Added **Automatic Upload** immediately after **Manual Entry**.
- Added the eleven requested default pipelines and displays for health, last sync, interval, enabled state and details.
- A pipeline is never marked Healthy merely because it appears in the catalogue. Disabled/unconfigured connectors show **Not connected**; configured production connectors without an implementation or a reported success show **Simulated / connector pending**; failed runs show **Error**; old success states show **Stale**.
- Reviewed the suggested 100 ms cadence and rejected it as unsafe for a CSV-backed Streamlit app. Defaults are 5 seconds for Refinery DCS, 60 seconds for script/Live Excel pipelines and 300 seconds for SAP API. Every interval is configurable.
- Background execution is external to Streamlit so page reruns do not create duplicate worker threads or slow navigation.

### Live Excel server-folder pipeline

- Implemented the user-selected DDF server-folder design. There is no OneDrive, Microsoft Graph or app-registration code.
- Default folder: `~/opera_inbox/live_excel/`, outside the git repository.
- Added a long-running scheduler, idempotent start/stop scripts, one-shot sync command, status-reporting command and optional systemd templates.
- The scripts create the watched folder if missing.
- File stability is confirmed across two scheduler cycles. Locked, half-written or incomplete files are logged and retried without corrupting Digital Data.
- Validated DP1–DP1000 rows are upserted by Date + Time + Business unit + Plant + Unit/Section + Equipment. Unchanged rows are skipped, changed readings update the matching row and new keys append.
- Each run is logged; pipeline health and last-synced time use the same persisted state.
- Added three standalone sample workbooks (also included in the full build), each with a **Live Data** and **How to use** sheet:
  - Live Excel 1: Refinery / Butamer Reactor 1 / DP1–DP5;
  - Live Excel 2: Cement / Okpella Rotary Kiln / DP1–DP5;
  - Live Excel 3: Fertilizer / Urea Reactor / DP7–DP10.

See `LIVE_EXCEL_PIPELINE_GUIDE_v3.13.0.md` for exact upload, configuration, scheduler and verification commands.

### Configure Data Pipeline

- Renamed **Digital Data Connector** to **Configure Data Pipeline**.
- Added per-BU configuration for all eleven catalogue pipelines: enabled state, source/endpoint/path, interval, secret name and notes.
- Preserved the existing Refinery DCS pull path and legacy `pipeline.json` compatibility.
- Added immediate Live Excel execution from Admin when a stable configured workbook is present.

### Roles

- Added **Manager**: same functional grants as BU Admin, restricted to exactly one BU.
- Existing **Operator** remains and is restricted to exactly one BU when created or edited.
- Added **Patroller**: viewer access for exactly one BU plus Manual Entry only; no bulk upload, configuration, event, lesson or risk-creation grants.
- Existing Super Admin, BU Admin, Operator and Viewer profiles and persisted accounts remain available.

### Blue UI consistency

- Standardized the main navigation ribbon, breadcrumb BU badge, wordmark, popover accents, focus accents and Home module-card accents on the same `#1857C9` brand-blue family.
- Retained red for the X, selected-navigation underline, alert states and the user avatar.

## DDF deployment

1. Back up the current code and data.
2. Apply the code-only v3.13.0 update over `~/OPERA` (or deploy the full build to a clean directory).
3. Activate the existing environment and install/confirm requirements:

   ```bash
   cd ~/OPERA
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

4. Create the persistent inbox/log folders:

   ```bash
   mkdir -p ~/opera_inbox/live_excel ~/opera_logs
   ```

5. Upload the standalone workbooks through the Jupyter file browser and rename them to `live_excel_1.xlsx`, `live_excel_2.xlsx` and `live_excel_3.xlsx`. Exact steps are in the Live Excel guide.
6. In each target BU, configure/enable the matching pipeline in **Admin → Configure Data Pipeline**.
7. Start the scheduler:

   ```bash
   export OPERA_DATA_DIR=~/opera_data
   ~/OPERA/scripts/start_pipeline_scheduler.sh
   ```

8. Add the following idempotent line to the end of `~/OPERA/start_opera.sh` so a full OPERA restart also starts the scheduler:

   ```bash
   "$HOME/OPERA/scripts/start_pipeline_scheduler.sh"
   ```

9. Fully restart the app:

   ```bash
   ~/OPERA/start_opera.sh
   ```

10. Hard-refresh with **Ctrl+F5** in both Chrome and Edge. Verify the normal URL and nginx sub-path, including the 1272 px Edge viewport at 150% Windows scaling.

## What must change in `~/opera_data`

No manual overwrite or migration of existing files in `~/opera_data` is required.

At runtime, v3.13.0 creates these files only when used:

- `business_units/<bu>/pipeline_configurations.json` when an admin saves pipeline settings;
- `business_units/<bu>/pipeline_state.json` when a connector runs;
- `business_units/<bu>/pipeline_runs.csv` for run history;
- existing `business_units/<bu>/inputs/dcs.csv` is atomically appended/updated only after a successful validated import;
- existing `pipeline.json` remains supported for the Refinery DCS connector.

Do not copy the package's `data/` directory over live `~/opera_data`. The watched Excel folder is `~/opera_inbox/live_excel/`, deliberately outside both the repository and `~/opera_data`.

## Testing

- Full pytest regression suite passes (one existing optional test remains skipped).
- New coverage verifies the eleven-pipeline catalogue, realistic intervals, truthful unconnected/simulated status, stable-file deferral, validation, append/update behaviour, deduplication, run logging, health, new role grants/BU scope, and removal of duplicated authenticated headings.
- The packaged refinery sample was exercised against a temporary OPERA data root: first cycle waited for stability, second imported three rows, and the third skipped duplicates.
- All three workbooks were reopened and checked for required sheet names, dimensions and headers.
