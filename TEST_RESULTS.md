# OPERA-X v3.10.0 test results

## Automated suite

```text
pytest -q
59 passed
```

The complete retained suite passed, including authentication, permissions, BU selection, formulas, storage validation, hierarchy/equipment administration, configurable dashboards, mapping persistence, Admin propagation, Home exports and every authenticated route.

## New v3.10 coverage

1. The Home category remains **Operational Data** and includes Operational Data Pipeline plus Process Optimization.
2. Operational Knowledge includes Event Log, Lesson Bank and Job Risk Assessment.
3. Operational Data Pipeline is used in navigation, Home, the module heading, export names and displayed audit labels.
4. The rejected longer rename does not appear in application source.
5. Navigation contains no v3.9 category prefixes, legend, category style mapping or category colour CSS.
6. Admin / Super Admin is absent from Home and remains in the authorized top navigation route.
7. Change BU precedes Sign Out in one vertical stack, with Vision 2030 in the adjacent column.
8. Full and compact Vision 2030 PNGs have real transparent and opaque pixels; obsolete JPEG files are absent.

## Compile check

```text
python -m py_compile app.py opera/*.py scripts/*.py
passed
```

## Visual check

Headless Chromium rendered the sign-in page, Home/header and Operational Data Pipeline page at 1600×1000. All required labels and controls were found and no Streamlit exception panel was visible. See `VISUAL_VERIFICATION_v3.10.0.md` and `verification/`.
