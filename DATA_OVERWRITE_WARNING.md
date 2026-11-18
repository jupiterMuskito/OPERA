# OPERA-X v3.7.0 — Runtime Data Overwrite Warning

The full deployment contains **228 runtime files** under `data/`:

- 174 CSV files
- 36 JSON files
- 9 authoritative `field_mappings.xlsx` workbooks
- 9 derived `field_mappings.runtime.json.gz` caches

Do not overlay this tree on the live `~/opera_data` folder. Any of these files can replace state entered through the running app. The highest-risk items are users/passwords, audit logs, operational readings, events, lessons, field/equipment metadata, calculated formulas, mappings, templates, constants, presets and DCS settings.

Use `OPERA-X_Code_Only_Update_v3.7.0.zip` for GitHub and the live server. It excludes the complete `data/`, `registers/` and `reference_sources/` trees.

The only supported live-data update for v3.7.0 is the non-destructive migration documented in `LIVE_DATA_UPDATE_v3.7.0.md`:

```bash
python scripts/upgrade_v370_live_data.py --data-dir ~/opera_data --package-data ./data
python scripts/upgrade_v370_live_data.py --data-dir ~/opera_data --package-data ./data --apply
```

The first command is a dry run. The apply command backs up every file it changes and never replaces an existing reading.
