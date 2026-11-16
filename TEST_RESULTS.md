# OPERA-X v3.5.0 — Test Results

## Result

**PASS — 34 tests passed.**

Commands completed successfully:

```bash
python3 -m py_compile app.py opera/*.py scripts/seed_data.py
pytest -q
```

## UI route verification

Streamlit's application test runtime signed in as the seeded BU Admin, selected Cement, and rendered every authenticated route without an exception:

- OPERA-X Home
- Plant Overview
- Equipment Overview
- Operations Dashboard
- Operational Data
- Event Log
- Operating Parameters
- Risk Assessment
- Lesson Bank
- Admin / Super Admin

The test also confirms the shared `hero()` function, every `hero(` call, and `.opera-hero` CSS are absent. The fixed top brand ribbon and merged navigation remain.

## Mapping verification

- Complete Cement mapping: 10,008 fields.
- Field types: 60 active inputs, 9,940 placeholders, 8 calculated fields.
- Source groups: DCS, Field, QAQC, Others, Calculated.
- Empty equipment mappings: 0.
- Empty template mappings: 0.
- Equipment reverse view covers all 201 named active Cement equipment records.
- Template reverse view covers all five canonical dashboard templates.
- Admin override save, effective-map refresh, reset-to-default, and four-sheet Excel review workbook are tested.
- Existing equipment/template-aware dropdown filtering remains tested.

## Regression coverage

The suite retains formula, role, password, storage, upload, Excel round-trip, export metadata, dashboard configuration, CPP-style chart behavior, Cement hierarchy/register, risk/PDF, placeholder source, mapping, and Streamlit smoke coverage.

## Data-safety verification

Transient audit rows and lock files created by application rendering were removed or restored before packaging. A byte-level comparison confirms no packaged file under `data/`, `registers/`, or `reference_sources/` changed versus v3.4.0.
