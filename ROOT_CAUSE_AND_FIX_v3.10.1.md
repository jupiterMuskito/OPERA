# OPERA-X v3.10.1 banner and Field Catalogue root causes and fixes

## 1. Top banner version

### Root cause

v3.10.0 maintained the release version in two independent places:

- `VERSION` contained `3.10.0`.
- `opera/__init__.py` separately hardcoded `__version__ = "3.10.0"`.

`app.py` imported the package value once as `APP_VERSION` and rendered that imported value in the top banner. Streamlit reruns `app.py`, but an already imported `opera` module can remain in the server process, so current v3.10.0 application code could coexist with an older in-memory package version. Updating `VERSION` did not affect the banner at all. The separate hardcoded values also allowed the package and release file to drift, and the existing source-level check verified only that the banner referenced `APP_VERSION`, not that all three values agreed.

### Fix

`VERSION` is now the only persisted release version. `opera/version.py` validates and reads it, `opera.__version__` is initialized from it, and the top banner calls `version_badge_html()` on each render. There is no version number in `app.py` or `opera/__init__.py`.

`tests/test_version_consistency.py` fails if:

- the `VERSION` file is not `3.10.1`;
- the package version differs from the file;
- the badge HTML differs from the file;
- `app.py` stops using the shared badge helper; or
- a cached `APP_VERSION` is reintroduced.

The code-only ZIP contains the complete dependency chain: `VERSION`, `opera/version.py`, `opera/__init__.py`, `app.py`, and the regression test.

## 2. Field Catalogue template columns

### Root cause reproduced against a pre-v3.9 live data directory

The v3.10.0 in-app download path did not begin with a schema migration. `mapping_update_template_bytes()` first called `load_effective_field_mappings()`, whose workbook parser required `Template IDs` in the existing `~/opera_data/.../field_mappings.xlsx`. A workbook created before v3.9 did not have that column, so the parser failed before the newer Field Catalogue builder reached the code that appends Dashboard Template ID and Dashboard Template.

The Admin page also retained an already prepared workbook in Streamlit session state. If fresh generation failed on the old schema, the old downloadable bytes were not cleared. That combination explains the live symptom with confirmed current v3.10.0 code: the server reached the new code path, the live old-schema workbook stopped fresh generation, and the page could continue offering the prior template that had no template-mapping columns. This was not a stale Git checkout.

### Fix

- Before any cache/read/export path uses `field_mappings.xlsx`, the app checks both `Field Mappings` and `Default Mappings` for `Template IDs` and `Dashboard Templates`.
- Missing columns are inserted in place beside `Equipment IDs`. Values come from any retained standalone Template Mappings sheet, legacy JSON override, or the current engineering default for the field.
- Existing cells, equipment mappings, administrator metadata, extra columns and extra worksheets are preserved. Only the derived runtime cache is invalidated and rebuilt.
- The generated Field Catalogue carries Equipment ID/Equipment followed by Dashboard Template ID/Dashboard Template/Include. Repeated included rows support multiple equipment and multiple template relationships per field.
- Dashboard Template ID has a controlled Excel validation list for `plant-performance`, `condition-monitoring`, `process-performance`, `quality-compliance` and `reliability`; the adjacent catalogue lists the corresponding names.
- The backend Excel Mapping Database now includes both Template IDs and human-readable Dashboard Templates per field.
- Bulk upload reads all Field Catalogue template relationships, applies multiple templates, and reports unknown IDs as validation errors.
- The Admin prepare action clears any prior session workbook before generation, so a failed build can no longer expose a stale template.

### Exact in-app download path

**Admin / Super Admin → Data Field Mapping → Excel mapping database and bulk update → Prepare Excel Mapping Update Template → Download Excel Update Template**

No manual update is required in `~/opera_data`. On first access, an old mapping workbook is upgraded automatically in place without replacing live data.

## Live-server confirmation after deployment

From the existing repository checkout on the DDF server:

```bash
git pull
cat VERSION
python -c "import opera; print(opera.__version__)"
grep -n "version_badge_html" app.py
```

The first two commands must both print `3.10.1`, and the grep must show that `app.py` imports and calls `version_badge_html`.

Then restart the Streamlit process using the existing service/start script with `OPERA_DATA_DIR=~/opera_data`, port `8089`, and address `172.20.130.228`. Open `https://172.20.130.228/operationaldashboard/`, sign in, and confirm the top-right banner badge reads `v3.10.1`. If a browser tab was already open, perform a hard refresh after the restart.

Finally, follow the exact Admin menu path above. Open the downloaded workbook and confirm **Field Catalogue** contains Dashboard Template ID and Dashboard Template beside Equipment ID and Equipment. Use **Prepare Excel Mapping Database → Download Excel Mapping Database** to confirm the backend **Field Mappings** sheet contains Template IDs and Dashboard Templates.