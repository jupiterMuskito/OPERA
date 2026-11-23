# OPERA-X v3.7.0 — Live `~/opera_data` Update

## Do not overwrite the live data folder

The full deployment ZIP contains seeded files under `data/`. Do **not** copy that folder over `~/opera_data`; doing so can replace users, passwords, audit history, readings, events, lessons, equipment, field metadata, mappings, formulas, constants, presets and connector settings entered through the running app.

The code-only update excludes the complete `data/`, `registers/` and `reference_sources/` trees.

## Required server sequence

From the server terminal:

```bash
cd ~/OPERA
git pull
source .venv/bin/activate
export OPERA_DATA_DIR=~/opera_data

# 1. Review only; this changes nothing.
python scripts/upgrade_v370_live_data.py \
  --data-dir ~/opera_data \
  --package-data ./data

# 2. If the dry-run list is correct, apply the non-destructive additions.
python scripts/upgrade_v370_live_data.py \
  --data-dir ~/opera_data \
  --package-data ./data \
  --apply

# 3. Restart through the existing server script.
~/OPERA/start_opera.sh
```

The reverse-proxy URL remains `https://172.20.130.228/operationaldashboard/`; the app still runs internally on port 8089 and supports Streamlit Community Cloud.

## What the migration can change

The script first creates a timestamped backup under `~/opera_data_backups/v3.7.0_<UTC timestamp>/`. It then:

1. Adds missing `CF9`–`CF12` definitions to configured BUs. Existing calculated-field IDs are never replaced.
2. Fills missing template panel defaults up to 12 chart fields and 12 table fields while preserving the existing configured order and other template properties.
3. Appends packaged Obajana/Ibese DCS, Lab and Field sample rows only when the exact `(Date, Time, Equipment)` key does not already exist in the live file.
4. Leaves every existing reading unchanged.
5. Makes no direct change to `users.csv`, audit/event/lesson/risk files, constants, presets, Digital Data connector settings or approved risk-register workbooks.

`field_mappings.xlsx` is reconciled automatically on first access after restart. Existing Admin overrides remain; missing records for the four new calculated fields are added. `field_mappings.runtime.json.gz` is a derived cache and may be deleted safely—the app rebuilds it from the Excel workbook.

## Expected result

- If the live data already contains the cloned-plant rows and v3.7 defaults, the script reports **No live-data changes are required**.
- If the live folder lacks Obajana/Ibese sample data, only missing clone rows are appended.
- Run the script again after apply: it should report no changes (idempotence check).

## Files in the full ZIP that would overwrite live data

Every file under `data/` is runtime state and must be treated as overwrite-risk, including:

- `data/shared/users.csv` and `business_units.csv`;
- all BU input CSVs;
- `fields.csv`, `equipment.csv`, `calculated_fields.csv`;
- `field_mappings.xlsx` and its derived runtime cache;
- dashboard templates, hierarchy lists, constants, connector settings and presets;
- events, flags, lessons, notifications, audit logs and risk-assessment history.

Use the code-only ZIP for GitHub/server updates. Use the full ZIP only for a fresh deployment or an isolated test copy.
