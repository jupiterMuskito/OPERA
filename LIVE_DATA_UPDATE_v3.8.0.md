# OPERA-X v3.8.0 — Live `~/opera_data` Update

## Required live-data change

**None. Do not copy or merge any packaged data file into `~/opera_data`.**

v3.8.0 is a code-only functional update. No CSV, JSON, XLSX, attachment or other runtime-state file changed versus v3.7.0.

## Server sequence

```bash
cd ~/OPERA
git pull
source .venv/bin/activate
export OPERA_DATA_DIR=~/opera_data

# No v3.8 data migration command is required.
~/OPERA/start_opera.sh
```

The existing reverse-proxy URL remains `https://172.20.130.228/operationaldashboard/`; the app continues to run internally on port 8089 and remains compatible with Streamlit Community Cloud.

## Automatic compatibility behavior

- If an Operations Dashboard template still has the exact v3.7 default `CF1`–`CF12` chart/table set and `CF1`–`CF8` KPI set, v3.8 presents the mixed DCS, Field, QAQC and Calculated default in memory.
- A genuinely customized Operations template is not replaced.
- The runtime mapping database remains authoritative and unchanged.
- The new equipment-aware Field Catalogue is generated only when a Super Admin prepares a new Excel Mapping Update Template.

## Full ZIP overwrite risk

The full ZIP includes the unchanged seeded `data/` tree for fresh or isolated test deployments. Every file under that directory must be treated as live-state overwrite risk, including users/passwords, audit logs, readings, flags, events, lessons, notifications, field/equipment metadata, formulas, mappings, templates, constants, presets and DCS connector settings.

Use `OPERA-X_Code_Only_Update_v3.8.0.zip` for the server/GitHub update. It excludes `data/`, `registers/` and `reference_sources/`.
