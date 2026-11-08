# OPERA v3.0.0 — Test Results

Tested on 2026-11-08 with Python 3.12.

## Automated suite

```text
..........                                                               [100%]
10 passed in 8.12s
```

Coverage:

1. CPP-style safe formula functions and ordered calculated fields.
2. Unsafe formula/code rejection.
3. High/Low target interpretation.
4. Locked atomic CSV append and spreadsheet-formula-injection protection.
5. Placeholder TA entry, validation, calculation and Excel round-trip (same shared path used by TB–TG).
6. PBKDF2 password verification and role/BU access controls.
7. Cement v8 schema/load checks: required sheets, expected row counts and zero warnings.
8. P23 Cement risk generation and valid PDF bytes.
9. Cement equipment provenance: all 67 workbook equipment IDs plus 500 CEM-SPARE placeholders.
10. Streamlit login-page startup without an exception.

## Additional checks

- `python -m py_compile app.py opera/*.py scripts/seed_data.py`: passed.
- Local Streamlit launch: passed.
- `/_stcore/health`: returned `ok`.
- Generic PDF export: generated one readable page; text extraction verified title, subtitle and table values.
- Static credential scan: no old RA test password, `TEST_PASS`, Analyst AI, old rounds renderer or SOP renderer found.
- Static Python secret scan: no literal assigned password or token found.
- Cement P23 result: 22 applicable hazards.
- Generated active-BU data per BU: 120 DCS rows, 30 Lab rows, 120 Field rows, zero TA–TG sample rows, 60 active input fields and eight calculated fields.

## Dependency note

The host sandbox contains unrelated preinstalled packages with version conflicts. The deployment requirements explicitly constrain Streamlit and `protobuf<7`; a clean Streamlit Community Cloud environment resolves from this package's `requirements.txt`.
