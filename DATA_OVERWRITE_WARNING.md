# OPERA-X v3.8.0 — Runtime Data Overwrite Warning

No runtime data file changed between v3.7.0 and v3.8.0, and **nothing must be updated in live `~/opera_data`**.

The full deployment nevertheless contains the unchanged seeded runtime tree under `data/`. Do not overlay it on `~/opera_data`. Files in that tree can replace state entered through the running app, including users/passwords, audit logs, readings, flags, events, lessons, notifications, field/equipment metadata, formulas, mappings, templates, constants, presets and DCS settings.

Use `OPERA-X_Code_Only_Update_v3.8.0.zip` for GitHub and the live server. It excludes the complete `data/`, `registers/` and `reference_sources/` trees.

Required sequence:

```bash
cd ~/OPERA
git pull
source .venv/bin/activate
export OPERA_DATA_DIR=~/opera_data
~/OPERA/start_opera.sh
```

There is no v3.8 migration script to run. See `LIVE_DATA_UPDATE_v3.8.0.md`.
