# OPERA-X v3.4.0 vs OPERA v3.3.0 — Repository Change Manifest

This manifest compares the v3.4.0 deployment package against `OPERA_Streamlit_Deployment_v3.3.0.zip` by relative path and SHA-256 content hash.

## Summary

- Changed: 14 files (including this release's regenerated checksum inventory)
- Added: 3 files
- Deleted: 2 files
- Runtime data/CSV files changed: **0**

## Changed files

```text
/BUILD_NOTES.md
/README.md
/SHA256SUMS.txt
/TEST_RESULTS.md
/VERSION
/app.py
/opera/__init__.py
/opera/auth.py
/opera/dashboard.py
/opera/exports.py
/opera/risk_store.py
/opera/storage.py
/scripts/seed_data.py
/tests/test_cement_register.py
```

## Added files

```text
/CHANGE_MANIFEST_v3.4.0_vs_v3.3.0.md
/assets/opera_x_icon.png
/tests/test_v340_features.py
```

## Deleted files

```text
/CHANGE_MANIFEST_v3.3.0_vs_v3.2.0.md
/assets/opera_icon.png
```

The code-only update ZIP contains `_DELETE_THESE_FILES.txt` so repository-only upgrades can remove these obsolete files explicitly.

## Data overwrite warning

**No file under `/data/` and no CSV file changed between v3.3.0 and v3.4.0.** Applying the code-only update therefore does not overwrite data entered through the running application.

`scripts/seed_data.py` is changed only to seed OPERA-X branding in a fresh environment. Do **not** run the seed script against an existing production data directory: seeding is destructive by design and can replace runtime CSVs.

The new mapping system does not ship generated `field_mappings.json` files. Deterministic defaults cover every field in code; only future Admin overrides are persisted at runtime. This avoids replacing user-maintained mappings during upgrades.

## Recommended repository-only upgrade

1. Back up the repository and persistent `OPERAX_DATA_DIR`/legacy `OPERA_DATA_DIR`.
2. Extract the code-only update ZIP at the repository root, preserving paths.
3. Delete the two paths listed in `_DELETE_THESE_FILES.txt`.
4. Keep all existing `/data/` files unchanged.
5. Install `requirements.txt` if the environment is new.
6. Run `python3 -m py_compile app.py opera/*.py scripts/seed_data.py`.
7. Run `pytest -q` and confirm 30 passing tests.
8. Redeploy/restart Streamlit.
