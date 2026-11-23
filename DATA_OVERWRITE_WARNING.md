# Runtime data overwrite warning

The recommended v3.10 code-only update contains no `data/`, `registers/` or `reference_sources/` tree and cannot overwrite live app state.

The full deployment ZIP contains the unchanged seeded runtime tree under `data/` for fresh/test deployment. Do not overlay it on `~/opera_data`. It can replace users/passwords, audit logs, Digital Data and Raw Field Data readings, flags, events, lessons, notifications, field/equipment metadata, formulas, mappings, templates, constants, presets and Digital Data connector settings.

No CSV, JSON or XLSX file must be updated in `~/opera_data` for v3.10.0. See `LIVE_DATA_UPDATE_v3.10.0.md`.
