# OPERA-X v3.10.0 live-data update

## Required change in `~/opera_data`

**None. Do not copy, replace, rename or edit any file in `~/opera_data` for this release.**

The release changes user-facing labels, Home grouping, navigation/header layout and packaged brand assets only. Internal data compatibility is preserved:

- Operational Data Pipeline continues to use the existing internal route and storage logic.
- `data_input_saved` and `bulk_upload` remain the stored audit action values; Admin translates them to Operational Data Pipeline labels for display.
- Digital Data and Raw Field Data continue to use stable internal keys `DCS` and `Field` and files `inputs/dcs.csv` and `inputs/field.csv`.
- Existing `field_mappings.xlsx`, `risk_assessments.csv`, register workbooks, uploads, events, lessons, users and audit history remain compatible.

## Safe DDF update

1. Apply `OPERA-X_Code_Only_Update_v3.10.0_vs_v3.9.0.zip` at the repository root.
2. Delete the two obsolete Vision 2030 JPEG assets listed in `CODE_ONLY_DELETE_INSTRUCTIONS_v3.10.0.txt` (recommended cleanup; the app no longer references them).
3. Commit the code-only update and deletions to GitHub.
4. Test the commit on Streamlit Community Cloud.
5. On the DDF server, run `git pull` in the existing checkout.
6. Keep `OPERA_DATA_DIR=~/opera_data` (or `OPERAX_DATA_DIR`) in the startup environment.
7. Restart Streamlit on port 8089/address 172.20.130.228.
8. Do not copy the full ZIP's `data/` directory over `~/opera_data`.

The local images are embedded as data URIs, so both Streamlit Community Cloud and the nginx reverse proxy at `/operationaldashboard/` remain supported.
