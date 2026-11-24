# OPERA-X v3.10.1 build notes

## Version-banner correction

- Made the repository-root `VERSION` file the single source of truth and set it to `3.10.1`.
- Removed the duplicate hardcoded package version from `opera/__init__.py`; `opera.__version__` is now derived from `VERSION` through `opera/version.py`.
- Removed the banner's imported `APP_VERSION` value. The top ribbon now calls `version_badge_html()` on every render, and that helper reads `VERSION` rather than retaining a hardcoded or process-cached banner value.
- Added a regression test that checks the `VERSION` file, package version, badge HTML and the banner integration in `app.py` together. A second test proves that changing the authoritative file changes the generated badge without a Python-module reload.
- The code-only update includes `VERSION`, `opera/__init__.py`, `opera/version.py`, `app.py` and the new test, so GitHub, Streamlit Community Cloud and the DDF server receive the complete version path.

## Field Catalogue/template-mapping correction

- Reproduced the defect with current v3.10.0 application code pointed at a persistent data directory containing a pre-v3.9 `field_mappings.xlsx` without `Template IDs`.
- Added an in-place schema upgrade that runs before the workbook is cached or used to prepare a download. It inserts `Template IDs` and `Dashboard Templates` beside `Equipment IDs` in both backend mapping sheets and fills them from any legacy Template Mappings sheet, legacy JSON override or the current engineering defaults.
- The migration preserves existing equipment mappings, administrator metadata, extra columns and extra worksheets. It invalidates only the derived runtime cache, which is rebuilt automatically.
- The in-app Field Catalogue always contains `Dashboard Template ID` and `Dashboard Template` beside `Equipment ID` and `Equipment`. Multiple templates use multiple included rows, matching the equipment relationship model.
- The Dashboard Template ID uses a controlled dropdown backed by the five packaged templates: Plant Performance, Condition Monitoring, Process Performance, Quality and Compliance, and Reliability.
- The backend Excel Mapping Database now shows both semicolon-separated Template IDs and human-readable Dashboard Templates per field.
- Bulk upload reads all included Field Catalogue rows, de-duplicates multiple template relationships, rejects unknown template IDs with the worksheet row number, and writes validated relationships to the backend workbook.
- The Admin page now clears any previously prepared workbook before building a fresh download. A schema/generation error therefore cannot leave an older pre-upgrade workbook available for download.

## Retained v3.10.0 changes

- Restored the authenticated top navigation to the v3.8 presentation: plain page labels, no category names in navigation labels, no category legend, no category icons and no category colour formatting.
- Renamed only the user-facing module previously called **Operational Data** to **Operational Data Pipeline**. The Home card, navigation, module heading, export names and displayed Admin audit labels use the new name.
- Preserved compatibility-sensitive identifiers such as `page_operational_data`, `operational_data_view`, `data_input_saved`, `bulk_upload`, source keys, CSV names and live-data paths. The Admin audit view translates the two retained stored action values for display instead of rewriting historical audit rows.
- Kept the Home category/group name **Operational Data**. It contains Plant Overview, Equipment Overview, Operations Dashboard, Operating Parameters, Operational Data Pipeline and Process Optimization.
- Placed Job Risk Assessment under **Operational Knowledge** with Event Log and Lesson Bank.
- Removed the Admin / Super Admin card from Home. Admin / Super Admin remains available to authorized users from the top navigation.
- Rebuilt the supplied Vision 2030 artwork as transparent PNG assets and removed the obsolete JPEG renditions.
- Stacked **Change BU** above **Sign Out**. The compact transparent Vision 2030 mark sits beside the button stack, aligned from the top and spanning the level of the two controls without increasing the ribbon beyond the compact two-row navigation layout.
- Removed the unused v3.9 category formatting functions, mappings and CSS.

## Header and branding layout

The first ribbon remains the compact OPERA-X brand/version ribbon. Directly below it, the navigation uses unprefixed page names. Business-unit/user context remains at the upper left, notifications remain between navigation and actions, Change BU is above Sign Out, and Vision 2030 is positioned to the right of that stack. The logo has a real alpha channel and no white rectangle, so the application background shows through.

Visual captures are included under `verification/` and summarized in `VISUAL_VERIFICATION_v3.10.0.md`.

## Deployment and data safety

- The full ZIP is for fresh/test deployment and includes the v3.9 runtime data unchanged.
- The code-only ZIP is the correct GitHub/DDF update and excludes `data/`, `registers/` and `reference_sources/`.
- No CSV, JSON or Excel runtime file changed versus v3.9.0.
- No manual change is required under live `~/opera_data`. On first mapping access, the app automatically upgrades an old `field_mappings.xlsx` in place and regenerates its derived runtime cache; existing mapping data is retained.
- Keep `OPERA_DATA_DIR=~/opera_data` (or `OPERAX_DATA_DIR=~/opera_data`) when restarting the DDF service.
- Local brand assets are embedded as data URIs, so both Streamlit Community Cloud and the nginx `/operationaldashboard/` deployment remain supported.

## Verification

- `pytest -q`: **64 passed**.
- `python -m py_compile app.py opera/*.py scripts/*.py`: passed.
- Playwright/Chromium rendered the sign-in page, Home/header and Operational Data Pipeline page at 1600×1000 with no Streamlit exception panels.
- The browser check confirmed the corrected Home groups, absence of the Admin Home card, transparent Vision 2030 mark, stacked actions and working Operational Data Pipeline route.
