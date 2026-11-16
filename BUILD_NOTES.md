# OPERA-X v3.4.0 — Build Notes

## Branding

- Renamed the product to **OPERA-X** across the page title, login, header, Home route, user-facing messages, reports, PDF/Excel metadata, seed script, README, and build documentation.
- Added a new `assets/opera_x_icon.png` and removed the old icon.
- Added `OPERAX_DATA_DIR` as the preferred persistent-data environment variable while retaining `OPERA_DATA_DIR` as a compatibility fallback.

## Header and navigation

- Removed the standalone business-unit/user context ribbon.
- Merged primary navigation, notifications, Change BU, and Sign Out into one navigation bar.
- Made the OPERA-X brand ribbon and merged navigation bar sticky while scrolling.

## Operational Data and DCS

- Replaced nested Input/Derived/Analyze and Manual/Bulk ribbons with one ribbon: Manual Entry, Bulk Upload, Derived Data, Analyze Data.
- Removed DCS Pipeline from Operational Data.
- Consolidated DCS endpoint configuration and manual pipeline execution in Admin / Super Admin → DCS Connector.

## Data-field mapping

- Added complete deterministic mappings for every input and placeholder field.
- Guaranteed at least one equipment and one canonical dashboard template per field.
- Added equipment/template filtering to field selectors across relevant pages.
- Added Admin / Super Admin → Field Mappings for audited overrides.
- Retained equipment-specific template overrides and the CPP-style chart grid.

## Compatibility

- No production CSV data files are changed by this release.
- Existing dashboard JSON files are normalized in memory so `Quality & Compliance` displays as `Quality and Compliance` without overwriting runtime configuration.
- Legacy seeded `OPERA Super Admin` display text is normalized in memory to `OPERA-X Super Admin` without replacing `users.csv`.
