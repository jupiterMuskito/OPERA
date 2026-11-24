# OPERA-X v3.11.0 build notes

## Approved header/navigation redesign

- Replaced the old radio-button header with the approved Option B flat menu.
- Added a 68 px white brand bar with the Dangote mark, navy/red OPERA-X wordmark, tagline, and Vision 2030 mark. The version is read from the repository-root `VERSION` file and appears directly under Vision 2030.
- Added a 52 px navy navigation bar with this order: Home | Plant · Equipment · Dashboards · Parameters · Data Pipeline · Optimization | Event Log · Lessons · Risk Assessment | Admin.
- Kept full route and page-title names. For example, Dashboards opens Operations Dashboard and Risk Assessment opens Job Risk Assessment.
- Added light group dividers, non-wrapping labels, and a red active-page underline.
- Kept Admin conditional on the existing `configure` permission.
- Replaced the notification toggle with a native notification popover and red unread-count badge.
- Replaced the separate Change BU/Sign Out controls and Help icon with a native avatar popover containing user name, role, business unit, Change Business Unit, Help, Sign Out, and version.
- Added a 40 px breadcrumb strip with the business-unit pill, category, and full page name.
- Added a native mobile menu below 1280 px. The desktop menu is hidden rather than wrapped.

All clickable navigation and account actions are Streamlit controls. No HTML `<a href>` navigation is used, so page selection remains in the authenticated Streamlit session.

## Compatibility and maintenance

- Pinned Streamlit to `streamlit==1.66.1`. The custom header CSS depends on the tested DOM/classes and must be visually regression-tested before that version is changed.
- Brand images remain packaged and embedded as data URIs, preserving Community Cloud and nginx `/operationaldashboard/` sub-path compatibility.
- Removed dead authenticated-header code and CSS for the radio group, old blue ribbon, context row, stacked action buttons, and legacy Vision navigation wrapper.
- Preserved the v3.9–v3.10.1 fixes: Digital Data/Raw Field Data labels, Field Catalogue equipment/template mapping columns and auto-upgrade, Job Risk Assessment display name, Operational Data Pipeline display name, and `VERSION` as the single source of truth.

## Deployment

Apply the full code-only ZIP to the verified v3.10.1 repository; do not cherry-pick a subset and do not skip versions. After `git pull`, fully restart with `~/OPERA/start_opera.sh`. No file under `~/opera_data` requires a manual update.

See `VISUAL_VERIFICATION_v3.11.0.md`, `LIVE_DATA_UPDATE_v3.11.0.md`, `TEST_RESULTS.md`, and `CHANGE_MANIFEST_v3.11.0_vs_v3.10.1.md`.
