# OPERA-X v3.9.0 live-data update

## Required change in `~/opera_data`

**None. Do not copy, replace, rename or edit any file in `~/opera_data` for this release.**

The names Digital Data and Raw Field Data are presentation labels. OPERA-X continues to read and write the existing internal source keys and files:

| User-facing name | Stable internal source key | Stable field IDs | Stable input file |
|---|---|---|---|
| Digital Data | `DCS` | `DP1`… | `inputs/dcs.csv` |
| Raw Field Data | `Field` | `F1`… | `inputs/field.csv` |

Existing `field_mappings.xlsx` files do not need a new column. The expanded Field Catalogue is generated on demand when a Super Admin prepares an Excel Mapping Update Template. New combined equipment/template edits are written back into the existing authoritative mapping schema.

Job Risk Assessment is also a presentation rename. Keep these live identifiers unchanged:

- `business_units/<bu>/risk_assessments.csv`
- `registers/` and its uploaded/history contents
- configured approved register filenames
- existing historical audit rows

New audit rows use `job_risk_assessment_generated`, `job_risk_assessment_exported`, and `job_risk_assessment_register_activated`. The Admin audit view translates matching older labels for display without rewriting the CSV.

## Safe DDF update

1. Apply `OPERA-X_Code_Only_Update_v3.9.0_vs_v3.8.0.zip` to the GitHub repository.
2. On the DDF server, pull the commit in the existing OPERA-X checkout.
3. Keep `OPERA_DATA_DIR=~/opera_data` (or the newer `OPERAX_DATA_DIR`) set in the start script.
4. Restart the Streamlit process on `172.20.130.228:8089`.
5. Do not copy the full ZIP's `data/` directory over `~/opera_data`.

The code is compatible with both Streamlit Community Cloud and the nginx reverse proxy at `/operationaldashboard/`.
