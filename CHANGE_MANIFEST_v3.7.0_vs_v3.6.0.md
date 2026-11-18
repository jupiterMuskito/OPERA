# OPERA-X v3.7.0 vs v3.6.0 — Change Manifest

Comparison method: SHA-256 by relative file path against the pristine `OPERA-X_Streamlit_Deployment_v3.6.0.zip` supplied for this task. Generated deliverable checksum/manifest helper files are excluded from the comparison counts.

| Result | Count |
|---|---:|
| Modified | 37 |
| Added | 16 |
| Deleted | 0 |
| Unchanged | 234 |
| v3.6.0 files compared | 271 |
| v3.7.0 files compared | 287 |

## Code, test and documentation files modified

- `BUILD_NOTES.md`
- `DATA_OVERWRITE_WARNING.md`
- `MAPPING_QUALITY_REPORT.md`
- `README.md`
- `SHA256SUMS.txt`
- `TEST_RESULTS.md`
- `VERSION`
- `app.py`
- `opera/auth.py`
- `opera/dashboard.py`
- `opera/storage.py`
- `scripts/build_mapping_quality_report.py`
- `scripts/seed_data.py`
- `tests/test_v340_features.py`
- `tests/test_v350_features.py`

## Code, test and documentation files added

- `LIVE_DATA_UPDATE_v3.7.0.md`
- `PAGE_BENCHMARK_v3.7.0.json`
- `PERFORMANCE_BENCHMARK_v3.7.0.json`
- `PERFORMANCE_REPORT_v3.7.0.md`
- `ROOT_CAUSE_AND_FIX_v3.7.0.md`
- `scripts/upgrade_v370_live_data.py`
- `tests/test_v370_admin_e2e.py`

## Files deleted

- None

No v3.6.0 file must be deleted for this update. Generated `__pycache__`, `.pytest_cache`, `.pyc` and stale `.lock` files are intentionally absent from the release and should not be committed if they exist locally.

## Runtime data files modified in the full build — overwrite risk

- `data/business_units/bu5/dashboard_templates.json`
- `data/business_units/bu5/field_mappings.xlsx`
- `data/business_units/bu6/dashboard_templates.json`
- `data/business_units/bu6/field_mappings.xlsx`
- `data/business_units/bu7/dashboard_templates.json`
- `data/business_units/bu7/field_mappings.xlsx`
- `data/business_units/bu8/dashboard_templates.json`
- `data/business_units/bu8/field_mappings.xlsx`
- `data/business_units/bu9/dashboard_templates.json`
- `data/business_units/bu9/field_mappings.xlsx`
- `data/business_units/cement/calculated_fields.csv`
- `data/business_units/cement/dashboard_templates.json`
- `data/business_units/cement/field_mappings.xlsx`
- `data/business_units/fertilizer/calculated_fields.csv`
- `data/business_units/fertilizer/dashboard_templates.json`
- `data/business_units/fertilizer/field_mappings.xlsx`
- `data/business_units/nascon/calculated_fields.csv`
- `data/business_units/nascon/dashboard_templates.json`
- `data/business_units/nascon/field_mappings.xlsx`
- `data/business_units/refinery/calculated_fields.csv`
- `data/business_units/refinery/dashboard_templates.json`
- `data/business_units/refinery/field_mappings.xlsx`

## Runtime data files added in the full build — derived cache

- `data/business_units/bu5/field_mappings.runtime.json.gz`
- `data/business_units/bu6/field_mappings.runtime.json.gz`
- `data/business_units/bu7/field_mappings.runtime.json.gz`
- `data/business_units/bu8/field_mappings.runtime.json.gz`
- `data/business_units/bu9/field_mappings.runtime.json.gz`
- `data/business_units/cement/field_mappings.runtime.json.gz`
- `data/business_units/fertilizer/field_mappings.runtime.json.gz`
- `data/business_units/nascon/field_mappings.runtime.json.gz`
- `data/business_units/refinery/field_mappings.runtime.json.gz`

All files in the two sections above are excluded from the code-only ZIP. Do not upload them over `~/opera_data`. Use `scripts/upgrade_v370_live_data.py` as documented in `LIVE_DATA_UPDATE_v3.7.0.md`.

## Recommended GitHub/server update

1. Apply `OPERA-X_Code_Only_Update_v3.7.0.zip` to the repository.
2. Commit and push; Streamlit Community Cloud remains the test deployment.
3. On the company server, run `git pull`.
4. Run the live-data migration once without `--apply`; review the output.
5. Run again with `--apply` only if additions are listed.
6. Restart with `~/OPERA/start_opera.sh`.
7. Verify `https://172.20.130.228/operationaldashboard/`.

The code-only ZIP includes this manifest and a deletion-instructions file confirming there are no required repository deletions.
