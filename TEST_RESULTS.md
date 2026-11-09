# OPERA v3.1.0 — Test Results

Tested on 2026-11-09 with Python 3.12.

## Automated Suite

```text
..............                                                           [100%]
14 passed
```

Coverage:

1. Safe formula functions, ordered calculated fields and unsafe-code rejection.
2. High/Low target interpretation.
3. Locked atomic CSV append and spreadsheet-formula-injection protection.
4. Placeholder TA entry, validation, calculation and Excel round-trip (the same shared path is used by TB–TG).
5. PBKDF2 password verification and role/business-unit access controls.
6. Cement v8 schema/load checks: required sheets, expected row counts and zero warnings.
7. P23 Cement risk generation and valid PDF bytes.
8. Cement hierarchy provenance and three-plant cloning: 67 Okpella, 67 Obajana and 67 Ibese named records, plus 500 unchanged spares.
9. Obajana and Ibese named equipment are cloned records and do not use `CEM-SPARE-*` identifiers.
10. NASCON business-unit ID, display name, data folder and access lists.
11. Dashboard template schema for Plant Overview, Equipment Overview and Operations Dashboard, including chart fields, table fields and chart type.
12. Editable equipment validation lists covering Plant, Unit / Section and Equipment Type.
13. Event Log Field Data update columns and optional Lesson Bank event reference.
14. Streamlit login → Business Unit → OPERA Home startup.

## Additional Checks

- Reproducible `scripts/seed_data.py` run: passed.
- `python -m compileall app.py opera scripts tests`: passed.
- Streamlit launch: passed.
- `/_stcore/health`: returned `ok`.
- Page-logic smoke test: OPERA Home, Plant Overview, Equipment Overview, Operations Dashboard, Data Input, Event Log, Data Analysis, Data Output, Operating Parameters, Risk Assessment, Lesson Bank, and Admin / Super Admin all completed without application exceptions.
- Static UI scan: no user-facing reference to the removed implementation-style label.
- Static naming scan: the corrected NASCON business-unit name is used throughout application data and documentation.
- Generated active-business-unit data per BU: 120 DCS rows, 30 Lab rows, 120 Field rows, zero TA–TG sample rows, 60 active input fields and eight calculated fields.
- Cement equipment package: 201 named plant records (67 per plant) plus 500 spares.

## Dependency Note

The host sandbox has an unrelated preinstalled NumPy/PyArrow binary mismatch. Deployment requirements explicitly pin a compatible pair (`numpy>=1.26,<2`, `pyarrow>=17,<18`) with Streamlit 1.53+. The route smoke test therefore bypassed only the host's broken dataframe serializer while exercising all OPERA page logic; the automated suite, application compilation and Streamlit health check ran normally.
