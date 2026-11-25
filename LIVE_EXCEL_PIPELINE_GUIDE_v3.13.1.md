# OPERA-X v3.13.1 — DDF Server-Folder Live Excel Guide

## Design

Live Excel pipelines use a folder on the DDF server and run from the background scheduler without any signed-in user session. The global pipeline configuration is stored under the persistent OPERA data root and is independent of the business unit selected in the application header.

Default watched location:

```text
~/opera_inbox/live_excel/
```

The location is outside `~/OPERA`, so `git pull`, a code-only deployment or repository replacement cannot overwrite uploaded workbooks. Each pipeline can use the shared folder or an explicit `.xlsx` file.

## Default files and targets

| Pipeline | Default filename | Default target BU | Example equipment and fields |
|---|---|---|---|
| Live Excel files 1 | `live_excel_1.xlsx` | Refinery | `REF-BUT-RX-01`, DP1–DP5 |
| Live Excel files 2 | `live_excel_2.xlsx` | Cement | `EQ04`, DP1–DP5 |
| Live Excel files 3 | `live_excel_3.xlsx` | Fertilizer | `FER-UREA-RX-01`, DP7–DP10 |

The packaged sample workbooks contain **Live Data** and **How to use** sheets. Example values are demonstration data, not production measurements.

## Upload the files

```bash
mkdir -p ~/opera_inbox/live_excel ~/opera_logs
cd ~/opera_inbox/live_excel
mv OPERA-X_Live_Excel_1_Refinery_Sample.xlsx live_excel_1.xlsx
mv OPERA-X_Live_Excel_2_Cement_Sample.xlsx live_excel_2.xlsx
mv OPERA-X_Live_Excel_3_Fertilizer_Sample.xlsx live_excel_3.xlsx
ls -lh
```

The scheduler creates the watched folder if it does not exist.

## Configure pipelines globally

1. Sign in as Super Admin and open **Admin → Configure Data Pipeline** from any selected BU.
2. Select each Live Excel pipeline from the global list.
3. Set **Target Business Unit** to Refinery, Cement or Fertilizer as shown above.
4. Set **Watched Folder or Excel File** to `~/opera_inbox/live_excel/`.
5. Enable and save each source.

The setting is global; do not switch the header BU between edits. BU Admin and Manager see only pipelines assigned to their permitted BU scope.

For a workbook that intentionally contains multiple BUs, choose **Route by Business unit column** and select the allowed business units. Each valid row is routed to the BU named in that row, validated against that BU's equipment and field registries, and written to that BU's Digital Data. Unknown or disallowed BU rows are rejected individually without blocking valid rows for allowed BUs.

## Start or restart the scheduler

After a new installation:

```bash
cd ~/OPERA
chmod +x scripts/start_pipeline_scheduler.sh scripts/stop_pipeline_scheduler.sh
export OPERA_DATA_DIR=~/opera_data
scripts/start_pipeline_scheduler.sh
```

After upgrading from v3.13.0 to v3.13.1, a scheduler restart is required:

```bash
~/OPERA/scripts/stop_pipeline_scheduler.sh
~/OPERA/scripts/start_pipeline_scheduler.sh
```

The process runs under `nohup`, records its PID under `~/opera_logs`, prevents duplicate processes and writes to:

```text
~/opera_logs/pipeline_scheduler.log
```

To start it during a full OPERA restart, retain this idempotent line in `~/OPERA/start_opera.sh`:

```bash
"$HOME/OPERA/scripts/start_pipeline_scheduler.sh"
```

## Automatic migration

On first load, v3.13.1 scans existing per-BU `pipeline_configurations.json` files, de-duplicates each pipeline and keeps settings from its intended target BU. It creates:

```text
~/opera_data/shared/pipeline_configurations.json
~/opera_data/shared/pipeline_state.json
```

No manual `~/opera_data` edit is required. Legacy per-BU files are retained.

## Import behavior

- A changed workbook must retain the same size and modification time for two scheduler cycles before reading.
- Required identifiers and active Digital Data fields are validated per row's target BU.
- Equipment is checked against the target BU's equipment list, not the BU selected by an administrator.
- Unchanged rows are skipped.
- Changed values for the same Date, Time, BU, Plant, Unit/Section and Equipment update the matching row.
- New identifier combinations append rows.
- Valid rows continue when another row names an unknown or disallowed BU.
- Writes remain atomic and file-locked.
- Every target-BU run is recorded in `~/opera_data/business_units/<bu>/pipeline_runs.csv` with pipeline name and target BU.
- Health and target-BU state are recorded globally and filtered by role/BU in **Data Pipeline → Automatic Upload**.

## Verify

```bash
cat ~/opera_logs/pipeline_scheduler.pid
ps -fp "$(cat ~/opera_logs/pipeline_scheduler.pid)"
tail -f ~/opera_logs/pipeline_scheduler.log
```

Scheduler lines show the pipeline name and target BU. Also verify:

```bash
tail -20 ~/opera_data/business_units/refinery/pipeline_runs.csv
tail -10 ~/opera_data/business_units/refinery/inputs/dcs.csv
```

The first pass after an upload waits for file stability; the next unchanged cycle imports it.
