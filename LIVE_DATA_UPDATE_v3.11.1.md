# OPERA-X v3.11.1 live-data update

## Required change in `~/opera_data`

**None. Do not copy, replace, rename or edit any file under `~/opera_data` for v3.11.1.**

This release changes application code, tests, release documentation and visual-verification evidence only. Existing users, readings, uploads, events, lessons, mapping workbooks, runtime caches, connector settings, presets, audit history and risk assessments remain compatible.

## Safe deployment from v3.11.0

1. Apply every file in `OPERA-X_Code_Only_Update_v3.11.1_vs_v3.11.0.zip` to the verified v3.11.0 repository.
2. Commit and test on Streamlit Community Cloud.
3. On the DDF server, run:

```bash
cd ~/OPERA
git pull
source .venv/bin/activate
python -m pip install -r requirements.txt
~/OPERA/start_opera.sh
```

4. Keep `OPERA_DATA_DIR=~/opera_data` (or `OPERAX_DATA_DIR=~/opera_data`).
5. Confirm `cat VERSION` and `python -c "import opera; print(opera.__version__)"` both print `3.11.1`.
6. Open `https://172.20.130.228/operationaldashboard/` and hard-refresh with **Ctrl+F5**.
7. Verify the flat menu at normal browser zoom, the attached bell badge, the clean circular avatar and the complete breadcrumb.

Do not rely on Streamlit hot reload for this update, and do not copy the full deployment ZIP's `data/` folder over the live data directory.
