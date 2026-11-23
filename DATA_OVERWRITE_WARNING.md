# Runtime data overwrite warning

The recommended v3.10.1 code-only update contains no `data/`, `registers/` or `reference_sources/` tree and cannot overwrite live app state.

The full deployment ZIP contains the unchanged seeded runtime tree under `data/` for fresh/test deployment. Do not overlay it on `~/opera_data`. It can replace users/passwords, audit logs, Digital Data and Raw Field Data readings, flags, events, lessons, notifications, field/equipment metadata, formulas, mappings, templates, constants, presets and Digital Data connector settings.

No file in `~/opera_data` needs a manual edit or replacement for v3.10.1. When an existing pre-v3.9 `field_mappings.xlsx` is loaded, the app performs a one-time in-place schema upgrade that adds the missing template columns and fills them from existing/current mappings while preserving all workbook data. Its derived runtime cache is then regenerated automatically. See `LIVE_DATA_UPDATE_v3.10.1.md`.
