# OPERA-X v3.7.0 — Test Results

## Result

**PASS — 45 automated tests passed in four isolated groups.** Python compilation also passed for `app.py`, `opera/`, `scripts/` and `tests/`.

The suite was split to keep peak memory and execution time bounded:

- Admin E2E, app smoke and roles: 7 passed
- v3.5/v3.6 regression: 10 passed
- v3.2–v3.4 regression: 16 passed
- Cement, dashboard, storage, formula and register: 12 passed

## Reported Admin-to-chart scenario

PASS in one Python/Streamlit process, with no restart:

1. Rename and activate a placeholder field.
2. Set UOM, minimum, maximum and target.
3. Map it to one equipment and Plant/Process Performance.
4. Set it as a Plant Performance chart-panel default.
5. Save a validated DCS value.
6. Verify the updated registry, mapping, template, source value and 12-panel template immediately.

A mapped field without a reading is also retained in the selector and receives an explicit no-readings message instead of disappearing.

## Admin configuration propagation matrix

| Admin configuration | Immediate verification and affected areas |
|---|---|
| Business units | Clone and activation are visible to BU selection and all BU-scoped modules. |
| Users and roles | New user authenticates immediately; role/BU/active changes are reloaded on the next interaction and change navigation/capabilities without server restart. |
| Input fields | Name, active status, UOM, range and target are re-read by dashboards, Operational Data, Event field updates, Operating Parameters and validation. |
| Calculated fields/formulas | Formula definitions and evaluation order are re-read by Derived Data and Operations Dashboard. |
| Constants | Saved constants are used immediately by calculated formulas. |
| Equipment | Name/plant/unit/type/active changes are visible to Plant Overview, Equipment Overview, Operational Data, Event Log, Operating Parameters, Risk Assessment and Lesson Bank selectors. |
| Validation lists | New plant/unit/equipment-type options are immediately returned to Equipment Admin. |
| Field mappings | Single-field save/reset and mapped selectors are verified for equipment/template context. |
| Excel mapping template | Required sheets, named lists and dropdown validations are present. |
| Bulk mapping upload | Partial update validates and changes only fields marked `Apply Update = Yes`; effective mapping changes immediately. |
| Dashboard templates | Every packaged template has 12 chart and 12 table fields; Admin changes persist immediately. |
| DCS connector | Latest JSON settings are re-read; mocked DCS ingest validates and appends a row immediately. |
| Presets | Save/import/load is immediate and audited. |
| Risk register | Existing register parsing, preset/hazard resolution and PDF tests remain passing. |
| Events and lessons | Newly written records and equipment links are immediately readable. |
| Audit and notifications | Existing locked append/update behavior remains passing. |

## Cement clone data verification

For each of Okpella, Obajana and Ibese:

- 67 named equipment records have sample readings.
- DCS: 1,460 rows per plant; 20 active fields; no missing active-field values.
- Field: 1,460 rows per plant; 20 active fields; no missing active-field values.
- Lab/QAQC: 365 rows per plant; 20 active fields; no missing active-field values.

The non-destructive live-data migration was tested in dry-run and apply modes, and a second run reported no changes (idempotent). It adds only missing rows/definitions/defaults and backs up each modified file.

## Performance verification

Streamlit AppTest timings and lower-level data-path timings are recorded in `PERFORMANCE_REPORT_v3.7.0.md`, `PAGE_BENCHMARK_v3.7.0.json` and `PERFORMANCE_BENCHMARK_v3.7.0.json`. Heavy page reductions versus v3.6.0 ranged from 65.6% to 94.7% on the test host.
