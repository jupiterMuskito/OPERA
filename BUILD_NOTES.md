# OPERA-X v3.10.0 build notes

## Requested changes completed

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
- Nothing must be copied into or edited under live `~/opera_data` for v3.10.0.
- Keep `OPERA_DATA_DIR=~/opera_data` (or `OPERAX_DATA_DIR=~/opera_data`) when restarting the DDF service.
- Local brand assets are embedded as data URIs, so both Streamlit Community Cloud and the nginx `/operationaldashboard/` deployment remain supported.

## Verification

- `pytest -q`: **59 passed**.
- `python -m py_compile app.py opera/*.py scripts/*.py`: passed.
- Playwright/Chromium rendered the sign-in page, Home/header and Operational Data Pipeline page at 1600×1000 with no Streamlit exception panels.
- The browser check confirmed the corrected Home groups, absence of the Admin Home card, transparent Vision 2030 mark, stacked actions and working Operational Data Pipeline route.
