# OPERA v3.3.0 vs v3.2.0 — Repository Change Manifest

This manifest compares the deployment package file-by-file with `OPERA_Streamlit_Deployment_v3.2.0.zip` using SHA-256 content hashes.

## Recommended code-only repository update

Upload these modified non-data files:

```text
/BUILD_NOTES.md
/README.md
/SHA256SUMS.txt  (regenerate after the final repository contents are in place)
/TEST_RESULTS.md
/VERSION
/app.py
/opera/__init__.py
/opera/dashboard.py
/scripts/seed_data.py
```

Upload these newly added non-data files:

```text
/CHANGE_MANIFEST_v3.3.0_vs_v3.2.0.md
/tests/test_v330_features.py
```

No files were deleted in v3.3.0.

## Data/CSV files changed — overwrite warning

The following 12 files were deliberately replaced with the new 365-day synthetic test dataset:

```text
/data/business_units/cement/inputs/dcs.csv
/data/business_units/cement/inputs/field.csv
/data/business_units/cement/inputs/lab.csv
/data/business_units/fertilizer/inputs/dcs.csv
/data/business_units/fertilizer/inputs/field.csv
/data/business_units/fertilizer/inputs/lab.csv
/data/business_units/nascon/inputs/dcs.csv
/data/business_units/nascon/inputs/field.csv
/data/business_units/nascon/inputs/lab.csv
/data/business_units/refinery/inputs/dcs.csv
/data/business_units/refinery/inputs/field.csv
/data/business_units/refinery/inputs/lab.csv
```

**Do not upload these CSV files over a repository or deployment that contains readings entered through the running app.** Replacing them will overwrite those saved readings when the repository `data` directory is the active runtime store.

Use the packaged CSVs only for a fresh test deployment, an intentional test-data reset, or after backing up and merging production rows. If `OPERA_DATA_DIR` points to separate persistent storage, repository CSV replacement does not directly replace that external runtime data, but the persistent dataset should still be backed up before migration.

No other data, user, audit, event, lesson, flag, notification, equipment, field-registry, calculated-field, template, preset or risk-assessment file changed versus v3.2.0.

## Complete file-by-file comparison

### Added (2)

```text
/CHANGE_MANIFEST_v3.3.0_vs_v3.2.0.md
/tests/test_v330_features.py
```

### Modified (21)

```text
/BUILD_NOTES.md
/README.md
/SHA256SUMS.txt
/TEST_RESULTS.md
/VERSION
/app.py
/data/business_units/cement/inputs/dcs.csv
/data/business_units/cement/inputs/field.csv
/data/business_units/cement/inputs/lab.csv
/data/business_units/fertilizer/inputs/dcs.csv
/data/business_units/fertilizer/inputs/field.csv
/data/business_units/fertilizer/inputs/lab.csv
/data/business_units/nascon/inputs/dcs.csv
/data/business_units/nascon/inputs/field.csv
/data/business_units/nascon/inputs/lab.csv
/data/business_units/refinery/inputs/dcs.csv
/data/business_units/refinery/inputs/field.csv
/data/business_units/refinery/inputs/lab.csv
/opera/__init__.py
/opera/dashboard.py
/scripts/seed_data.py
```

### Deleted (0)

```text
None
```

## Safe update sequence

1. Back up the current repository and any external `OPERA_DATA_DIR`.
2. Upload the modified and added non-data files, excluding `SHA256SUMS.txt` until the end.
3. Do not replace the 12 input CSVs unless the explicit goal is to install/reset synthetic test data.
4. If sample data is required, merge it into a copy of the live dataset or use the CSVs only in a separate test environment.
5. Run `pytest -q` and `python3 -m py_compile app.py opera/*.py scripts/seed_data.py`.
6. Regenerate `SHA256SUMS.txt` from the final repository contents, especially when live CSVs are preserved.
