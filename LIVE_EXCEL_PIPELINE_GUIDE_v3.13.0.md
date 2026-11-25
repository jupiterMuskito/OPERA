# OPERA-X v3.13.0 — DDF Server-Folder Live Excel Guide

## Decision implemented

The Live Excel pipelines use a **folder on the DDF server**. They do not use OneDrive, Microsoft Graph, an Azure/Entra app registration, or credentials for cloud file access.

Default watched location:

```text
~/opera_inbox/live_excel/
```

The location is outside `~/OPERA`, so `git pull`, a code-only deployment, or replacing the application repository cannot overwrite the uploaded workbooks. Each pipeline can use a different folder or an explicit `.xlsx` file in **Admin → Configure Data Pipeline**.

## Standalone sample workbooks

| Pipeline | Upload filename expected by the default folder | Example mapping |
|---|---|---|
| Live Excel files 1 | `live_excel_1.xlsx` | `refinery`, `REF-BUT-RX-01` (Butamer Reactor 1), DP1–DP5 |
| Live Excel files 2 | `live_excel_2.xlsx` | `cement`, `EQ04` (Rotary Kiln), DP1–DP5 |
| Live Excel files 3 | `live_excel_3.xlsx` | `fertilizer`, `FER-UREA-RX-01` (Urea Reactor), DP7–DP10 |

Each workbook has:

- a **Live Data** sheet containing realistic sample rows;
- a **How to use** sheet with the BU, equipment, DP-field mapping, units, date/time formats, duplicate rule, and instructions for adding rows.

The example values are demonstration data, not production measurements.

## Upload from a laptop with the Jupyter file browser

1. Sign in to the DDF server's Jupyter environment.
2. In the Jupyter file browser, open the home folder, then open `opera_inbox` and `live_excel`.
3. If the folders are not visible yet, open a Jupyter terminal and run:

   ```bash
   mkdir -p ~/opera_inbox/live_excel ~/opera_logs
   ```

4. Use Jupyter's **Upload** button to upload each downloaded sample workbook.
5. Rename the uploaded files to the exact watched names:

   ```bash
   cd ~/opera_inbox/live_excel
   mv OPERA-X_Live_Excel_1_Refinery_Sample.xlsx live_excel_1.xlsx
   mv OPERA-X_Live_Excel_2_Cement_Sample.xlsx live_excel_2.xlsx
   mv OPERA-X_Live_Excel_3_Fertilizer_Sample.xlsx live_excel_3.xlsx
   ls -lh
   ```

The scheduler creates the folder automatically if it is missing. Uploading through Jupyter is the recommended route because WinSCP is unavailable to the user.

## Configure the three sample pipelines

1. Start OPERA-X and select the target BU.
2. Go to **Admin → Configure Data Pipeline**.
3. Select the pipeline, set **Enabled**, set **Watched Folder or Excel File** to `~/opera_inbox/live_excel/`, and save.
4. Use these sample pairings:
   - in BU `refinery`, enable **Live Excel files 1**;
   - in BU `cement`, enable **Live Excel files 2**;
   - in BU `fertilizer`, enable **Live Excel files 3**.
5. Keep the default **60-second** interval unless the source process requires a slower cadence.

A folder path makes the pipeline resolve its own file as `live_excel_1.xlsx`, `live_excel_2.xlsx`, or `live_excel_3.xlsx`. An administrator may instead enter an explicit workbook path.

## Start a scheduler that survives logout

After deploying the code:

```bash
cd ~/OPERA
chmod +x scripts/start_pipeline_scheduler.sh scripts/stop_pipeline_scheduler.sh
export OPERA_DATA_DIR=~/opera_data
scripts/start_pipeline_scheduler.sh
```

The start script uses `nohup`, records a PID under `~/opera_logs`, prevents duplicate scheduler processes, and writes output to:

```text
~/opera_logs/pipeline_scheduler.log
```

To make the scheduler restart whenever OPERA-X is fully restarted, add this line near the end of `~/OPERA/start_opera.sh`:

```bash
"$HOME/OPERA/scripts/start_pipeline_scheduler.sh"
```

The start command is idempotent, so calling it from `start_opera.sh` does not create duplicate schedulers. To stop it manually:

```bash
~/OPERA/scripts/stop_pipeline_scheduler.sh
```

Systemd service/timer templates are also included for installations that prefer OS-managed scheduling.

## How import, update and safety work

- The scheduler creates the watched folder if necessary.
- A changed workbook must retain the same file size and modification time for **two scheduler cycles** before it is opened. A file still being copied is logged as waiting and retried on the next cycle.
- Locked, incomplete or unreadable workbooks are not written to Digital Data; they are logged and retried.
- Required identifiers and active DP1–DP1000 fields are validated using the existing OPERA-X rules.
- An unchanged imported row is skipped.
- A row with the same Date, Time, BU, Plant, Unit/Section and Equipment but changed DP values updates the matching Digital Data row.
- A new identifier combination appends a new Digital Data row.
- CSV writes remain atomic and file-locked. A failed validation does not partially update the data file.
- Every run is recorded in `~/opera_data/business_units/<bu>/pipeline_runs.csv`.
- Current state and last-synced time are recorded in `pipeline_state.json` and shown in **Data Pipeline → Automatic Upload**.

## Check that it is working

```bash
cat ~/opera_logs/pipeline_scheduler.pid
ps -fp "$(cat ~/opera_logs/pipeline_scheduler.pid)"
tail -f ~/opera_logs/pipeline_scheduler.log
```

Then check:

1. **Data Pipeline → Automatic Upload** shows the pipeline as Healthy after a successful stable-file cycle.
2. The displayed **Last synced (UTC)** advances.
3. The run log contains success rows:

   ```bash
   tail -20 ~/opera_data/business_units/refinery/pipeline_runs.csv
   ```

4. Digital Data contains the new or updated DP fields:

   ```bash
   tail -10 ~/opera_data/business_units/refinery/inputs/dcs.csv
   ```

If a workbook is newly uploaded, the first pass intentionally says it is waiting for stability; the next unchanged cycle imports it.

## Interval recommendation

Do not use 100 ms. It would perform up to ten polls per second per pipeline, contend for CSV locks, repeatedly inspect files that normally change much more slowly, and waste CPU/I/O. v3.13.0 defaults are:

- Refinery DCS: **5 seconds**;
- Python/server and Live Excel pipelines: **60 seconds**;
- SAP API: **300 seconds**.

All intervals are configurable per BU and pipeline in Admin. The Streamlit UI does not run a background thread; the server scheduler owns automatic execution, so normal page navigation remains responsive.
