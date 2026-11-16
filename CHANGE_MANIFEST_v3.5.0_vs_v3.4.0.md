# OPERA-X v3.5.0 vs v3.4.0 — Change Manifest

## Summary

This release removes the shared blue page-title hero from every authenticated module and replaces the override-only Field Mappings screen with a complete mapping administration workspace.

## Modified files

| File | Change |
|---|---|
| `app.py` | Deleted the shared `hero()` renderer and `.opera-hero` CSS; removed every module-page hero call; added complete mapping filters, field/equipment/template views, mapping editor/reset, cross-BU selection, Excel download, and audit actions. |
| `opera/dashboard.py` | Added the complete field catalog (input, placeholder and calculated), effective mapping table, reverse equipment/template views, mapping workbook sheets, source grouping, and override reset support. |
| `opera/__init__.py` | Updated package version to 3.5.0. |
| `README.md` | Updated the UI flow, mapping administration, workbook export, persistence, and deployment warning. |
| `BUILD_NOTES.md` | Replaced with v3.5.0 implementation and user test notes. |
| `TEST_RESULTS.md` | Updated for the 34-test suite and all-page render verification. |
| `VERSION` | Updated from 3.4.0 to 3.5.0. |
| `SHA256SUMS.txt` | Regenerated after packaging preparation. |

## Added files

| File | Purpose |
|---|---|
| `tests/test_v350_features.py` | Tests removal of the blue hero, complete mapping coverage, reverse views, edit/reset persistence, Excel export, and rendering of every authenticated page. |
| `CHANGE_MANIFEST_v3.5.0_vs_v3.4.0.md` | This comparison. |
| `DATA_OVERWRITE_WARNING.md` | Exact inventory of packaged CSV files that must not replace live runtime data during a code-only update. |

## Deleted files

None.

## Runtime data changes versus v3.4.0

None. No file under `data/`, `registers/`, or `reference_sources/` changed versus the supplied v3.4.0 build.

## Deployment choice

- **Existing deployment with user-entered data:** use `OPERA-X_Code_Only_Update_v3.5.0.zip`. It contains no runtime CSVs and preserves live data.
- **Fresh deployment:** use `OPERA-X_Streamlit_Deployment_v3.5.0.zip`.
- **Do not copy the full deployment package over a live data directory** unless the live `data/` directory has been backed up and deliberately excluded from replacement. The full package contains 174 seed/runtime CSVs; see `DATA_OVERWRITE_WARNING.md`.
