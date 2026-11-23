# OPERA-X v3.9.0 test results

## Automated suite

```text
pytest -q
54 passed
```

The suite covers authentication, permissions, BU selection, formulas, storage validation, hierarchy/equipment administration, configurable dashboards, mapping persistence, Admin-to-chart propagation, responsive chart controls, Home data exports, and every authenticated route.

## New v3.9 coverage

1. Display labels are **Digital Data** and **Raw Field Data**, while persisted source keys remain `DCS` and `Field` and ID prefixes remain `DP` and `F`.
2. Home reading Excel exports use Digital Data and Raw Field Data worksheet/source labels.
3. The Field Catalogue contains Equipment ID/Equipment and Dashboard Template ID/Dashboard Template on the same row.
4. Field Catalogue Equipment ID and Dashboard Template ID cells use controlled named-range dropdowns; Include remains validated.
5. A single bulk upload updates both equipment and dashboard-template mappings and takes effect in the mapping database.
6. Process Optimization is a standalone route and no Optimization tab remains in Operational Data → Analyze Data.
7. Four module categories, all three brand placements and the enlarged sign-in tagline are packaged.
8. Job Risk Assessment is used in navigation, Home, page/buttons, export titles/filenames, Admin labels, PDF metadata and audit labels while `risk_assessments.csv` remains stable.

## Additional checks

```text
python -m py_compile app.py opera/*.py scripts/*.py
```

Passed with no syntax errors.
