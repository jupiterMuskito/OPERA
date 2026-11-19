# OPERA-X v3.8.0 — Build Notes

## Requested changes

- The top brand ribbon now carries a compact `v3.8.0` badge at its lower-right edge; the mobile layout moves it left with the tagline.
- Readings, Open Flags, Events, Lessons and Notifications are now Home buttons. Super Admins can open the complete underlying tables and download Excel; other roles receive a clear least-privilege message.
- Readings Excel exports use separate DCS, Field, QAQC and TA–TG worksheets instead of flattening unlike sources together.
- The Sign Out column and button now preserve the complete `Sign Out` label without shrinking or wrapping.
- Plotly chart height changed from 330 px to 231 px, an exact 30% reduction.
- Operations Dashboard data and Admin field setup now accept active DCS, Field and Lab/QAQC fields together with Calculated fields.
- Exact untouched v3.7 calculated-only Operations defaults are upgraded in memory; genuine Admin customizations are retained.
- The Excel Mapping Update Template's Field Catalogue now shows one row per field/equipment relationship, includes equipment names and supplies controlled Field ID, Equipment ID and Include dropdowns. Bulk upload accepts edits made there while retaining v3.7 Equipment Mappings compatibility.

## Performance and deployment compatibility

- v3.7 selective reads, caches, 300-point trace cap, four-panel pagination, atomic writes and external data-root support are retained.
- `OPERAX_DATA_DIR` and legacy `OPERA_DATA_DIR` remain supported.
- Internal server port/address and nginx subpath are unchanged.
- Streamlit Community Cloud remains supported.
- Use the code-only ZIP for the live server. No `~/opera_data` migration is required.

## Verification

- 45 retained tests passed.
- 5 new v3.8 tests passed.
- Python compilation passed for `app.py`, `opera/`, `scripts/` and `tests/`.
- The production Cement mapping template was generated and opened successfully with its equipment-aware Field Catalogue.
