# OPERA-X v3.10.1 live-data update

## Required manual change in `~/opera_data`

**None. Do not manually copy, replace, rename or edit any file in `~/opera_data` for this release.**

If a business unit's existing `field_mappings.xlsx` predates v3.9 and lacks template columns, the app automatically performs a one-time in-place schema upgrade when Data Field Mapping is loaded. It adds `Template IDs` and `Dashboard Templates`, recovers values from existing/current mappings, retains equipment relationships, administrator metadata, extra columns and extra worksheets, and regenerates only the derived `field_mappings.runtime.json.gz` cache. No administrator spreadsheet edit is needed.

All CSVs, registers, uploads, users, audit history, events, lessons and connector settings remain compatible.

## Safe GitHub, Community Cloud and DDF update

1. Overlay `OPERA-X_Code_Only_Update_v3.10.1_vs_v3.10.0.zip` at the repository root.
2. Commit all files from the package, including `VERSION` and the new `opera/version.py`.
3. Push and test the commit on Streamlit Community Cloud.
4. On the DDF server, run `git pull` in the existing checkout.
5. Confirm `cat VERSION` and `python -c "import opera; print(opera.__version__)"` both print `3.10.1`.
6. Keep `OPERA_DATA_DIR=~/opera_data` (or `OPERAX_DATA_DIR`) in the startup environment.
7. Restart Streamlit on port `8089` and address `172.20.130.228` using the existing service/start script.
8. Open `https://172.20.130.228/operationaldashboard/`, sign in, hard-refresh if needed, and confirm the top banner reads `v3.10.1`.
9. Open **Admin / Super Admin → Data Field Mapping → Excel mapping database and bulk update**. Select **Prepare Excel Mapping Update Template**, then **Download Excel Update Template**. Confirm **Field Catalogue** contains Dashboard Template ID and Dashboard Template beside the equipment columns.
10. Optionally prepare/download the Excel Mapping Database and confirm **Field Mappings** shows Template IDs and Dashboard Templates for each field.
11. Do not copy the full ZIP's `data/` directory over `~/opera_data`.

The version fix uses ordinary local Python and the packaged root `VERSION` file; it does not depend on proxy routing or writable local storage, so it remains compatible with both Streamlit Community Cloud and the nginx `/operationaldashboard/` deployment.