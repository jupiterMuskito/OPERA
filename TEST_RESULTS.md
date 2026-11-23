# OPERA-X v3.10.1 test results

## Automated suite

```text
pytest -q
64 passed
```

The complete retained suite passed, including authentication, permissions, BU selection, formulas, storage validation, hierarchy/equipment administration, configurable dashboards, mapping persistence, Admin propagation, Home exports and every authenticated route.

## New v3.10.1 coverage

1. The package version and repository-root `VERSION` file both resolve to `3.10.1`.
2. The top banner uses `version_badge_html()` rather than a separate `APP_VERSION` constant or literal.
3. The generated badge is exactly `<div class="version">v3.10.1</div>`.
4. Repointing the helper to an updated temporary `VERSION` file changes the badge immediately, proving that the banner helper does not retain a cached version literal.
5. A pre-v3.9 live `field_mappings.xlsx` without template columns is upgraded before the in-app mapping template is built; unrelated legacy columns and worksheets remain intact.
6. The generated Field Catalogue contains the equipment/template columns, all five dashboard-template names and the controlled Template ID validation range.
7. A Field Catalogue upload can replace one field with two dashboard-template relationships and the backend database exposes both IDs and names.
8. An unknown Dashboard Template ID is rejected with a clear validation error.

## Retained v3.10 coverage

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
