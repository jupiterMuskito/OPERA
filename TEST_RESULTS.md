# OPERA-X v3.8.0 — Test Results

## Result

**PASS — 50 automated tests passed in bounded groups.** Python compilation also passed for `app.py`, `opera/`, `scripts/` and `tests/`.

- Retained v3.7 and earlier smoke/regression/Admin E2E suite: **45 passed**.
- New v3.8 feature suite: **5 passed**.

The suite is intentionally split to keep peak memory bounded when Streamlit AppTest and large mapping workbooks run in the same container.

## New v3.8 coverage

1. Package and banner version are `3.8.0`; full Sign Out text and least-privilege Home response are present.
2. Readings export is separated into DCS, Field, QAQC and seven TA–TG Excel worksheets.
3. Operations field catalog contains DCS, Field, Lab/QAQC and Calculated fields; every new Operations default includes all four categories.
4. Chart height is exactly 231 px (30% below the v3.7 330 px value).
5. Field Catalogue lists mapped equipment, exposes controlled dropdown validations, and applies a changed equipment mapping through the bulk-update path.

## Retained regression coverage

The retained suite continues to cover authentication, BU selection, role grants, Admin-to-chart propagation, fields/UOM/ranges/targets, formulas/constants, equipment and hierarchy lists, mappings and legacy Excel bulk update, templates, DCS ingest, presets, events/lessons, exports, storage locking/caches, Cement hierarchy/data, risk-register parsing and PDFs.

## Additional verification

- `python -m compileall -q app.py opera scripts tests` passed.
- A production Cement Excel Mapping Update Template was generated and reopened successfully; its Field Catalogue contains the Equipment ID column and validation.
