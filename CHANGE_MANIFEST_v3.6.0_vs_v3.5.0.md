# OPERA-X v3.6.0 vs v3.5.0 — Change Manifest

## Summary

This release replaces mechanically generated named-field defaults and JSON-only overrides with engineering-reviewed Excel mapping databases, controlled Admin templates, validated partial bulk upload, recorded Instrument Check pairs, and mapping-quality metadata/reporting. Existing Operational Intelligence UI/UX, CPP-style charts and all prior workflows remain in place.

## Modified application and documentation files

| File | Change |
|---|---|
| `app.py` | Added Excel template/database downloads, validated bulk mapping upload, audit summary, and Instrument Check defaults from recorded mapping pairs. |
| `opera/dashboard.py` | Replaced runtime/default JSON logic with Excel database persistence; added basis/confidence/pair metadata, controlled workbook generation, upload validation, partial update, database migration, and pair retrieval; removed dead round-robin default code. |
| `opera/__init__.py` | Updated package version to 3.6.0. |
| `scripts/seed_data.py` | Corrected calculated-field definitions/targets and activated SPARE equipment records required by placeholder mapping. |
| `tests/test_v340_features.py` | Updated placeholder assertions for source-aware SPARE mapping. |
| `tests/test_v350_features.py` | Updated reverse-view assertions for active named/SPARE equipment. |
| `README.md` | Documented Excel persistence, bulk update, engineering defaults, pairs and deployment safety. |
| `BUILD_NOTES.md` | Replaced with v3.6.0 implementation, compatibility and user-test notes. |
| `TEST_RESULTS.md` | Updated for the 40-test engineering mapping and workbook suite. |
| `DATA_OVERWRITE_WARNING.md` | Added the exact XLSX and changed-CSV runtime overwrite inventory. |
| `VERSION` | Updated from 3.5.0 to 3.6.0. |
| `SHA256SUMS.txt` | Regenerated after final package preparation. |

## Modified runtime data files

The nine files below activate their 500 SPARE records so placeholder mappings reference valid active equipment:

- `data/business_units/bu5/equipment.csv`
- `data/business_units/bu6/equipment.csv`
- `data/business_units/bu7/equipment.csv`
- `data/business_units/bu8/equipment.csv`
- `data/business_units/bu9/equipment.csv`
- `data/business_units/cement/equipment.csv`
- `data/business_units/fertilizer/equipment.csv`
- `data/business_units/nascon/equipment.csv`
- `data/business_units/refinery/equipment.csv`

The four files below correct calculated-field names, formulas and targets so each calculation matches its inputs:

- `data/business_units/cement/calculated_fields.csv`
- `data/business_units/refinery/calculated_fields.csv`
- `data/business_units/fertilizer/calculated_fields.csv`
- `data/business_units/nascon/calculated_fields.csv`

## Added files

| File | Purpose |
|---|---|
| `opera/engineering_mapping.py` | Curated field-by-field process-engineering seed knowledge, source-aware placeholder logic, calculated-field inheritance and confidence/basis generation. |
| `scripts/build_mapping_quality_report.py` | Rebuilds the mapping quality report from the Excel databases. |
| `tests/test_v360_features.py` | Tests physical mapping examples, SPARE rules, pair records, calculated inheritance, controlled workbooks, partial upload and report content. |
| `MAPPING_QUALITY_REPORT.md` | BU/template counts, named Review list, grouped placeholder reviews, 20 sample mappings, calculated checks and pair notes. |
| `CHANGE_MANIFEST_v3.6.0_vs_v3.5.0.md` | This comparison. |
| `data/business_units/bu5/field_mappings.xlsx` | BU5 Excel mapping database. |
| `data/business_units/bu6/field_mappings.xlsx` | BU6 Excel mapping database. |
| `data/business_units/bu7/field_mappings.xlsx` | BU7 Excel mapping database. |
| `data/business_units/bu8/field_mappings.xlsx` | BU8 Excel mapping database. |
| `data/business_units/bu9/field_mappings.xlsx` | BU9 Excel mapping database. |
| `data/business_units/cement/field_mappings.xlsx` | Cement Excel mapping database for Okpella, Obajana and Ibese. |
| `data/business_units/refinery/field_mappings.xlsx` | Refinery/Butamer Excel mapping database. |
| `data/business_units/fertilizer/field_mappings.xlsx` | Fertilizer Excel mapping database. |
| `data/business_units/nascon/field_mappings.xlsx` | NASCON Salt/Sugar Excel mapping database. |

## Deleted files

None.

## Runtime overwrite warning

- **Existing deployment with live data:** use `OPERA-X_Code_Only_Update_v3.6.0.zip`. It excludes the entire `data/` tree, so it will not overwrite live CSVs or mapping databases. On first use, it creates the Excel database and migrates legacy JSON overrides.
- **Fresh deployment:** use `OPERA-X_Streamlit_Deployment_v3.6.0.zip`.
- **Do not copy the full package over live `data/`.** It contains 174 CSVs and nine mapping databases. The 13 intentionally changed CSVs and nine added XLSX files are identified above and in `DATA_OVERWRITE_WARNING.md`.
