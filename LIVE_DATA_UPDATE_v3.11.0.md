# OPERA-X v3.11.0 live-data update

## Required manual change in `~/opera_data`

**None. Do not manually copy, replace, rename, or edit any file in `~/opera_data` for this release.**

v3.11.0 changes application code, tests, documentation, and the pinned Streamlit dependency only. All live CSV files, Excel mapping databases, runtime mapping caches, users, readings, uploads, registers, events, lessons, audit history, and connector settings remain compatible.

## Safe GitHub, Community Cloud, and DDF update

1. Start from the verified v3.10.1 repository state and overlay every file in `OPERA-X_Code_Only_Update_v3.11.0_vs_v3.10.1.zip`. Do not skip versions or copy only selected files.
2. Commit all files from the code-only package, including `VERSION`, `requirements.txt`, `app.py`, tests, and release documentation.
3. Push and test on Streamlit Community Cloud. The exact `streamlit==1.66.1` pin is required because the custom header CSS targets that tested Streamlit structure.
4. On the DDF server, run `git pull` in `~/OPERA`.
5. Keep `OPERA_DATA_DIR=~/opera_data` (or the supported `OPERAX_DATA_DIR=~/opera_data`) in the startup environment.
6. Fully restart the process with `~/OPERA/start_opera.sh`. A Streamlit hot reload is not sufficient after dependency or imported-module changes.
7. Confirm `cat VERSION` and `python -c "import opera; print(opera.__version__)"` both print `3.11.0`.
8. Open `https://172.20.130.228/operationaldashboard/`, hard-refresh, sign in, and verify the brand bar, flat navigation, notifications, avatar menu, and breadcrumb.
9. Do not copy the full deployment ZIP's `data/` directory over `~/opera_data`.

The header uses embedded local image data URIs and Streamlit-native controls, so it remains compatible with both Community Cloud and the nginx `/operationaldashboard/` sub-path. No root-relative navigation links were added.
