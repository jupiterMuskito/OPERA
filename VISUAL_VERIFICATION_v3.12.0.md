# OPERA-X v3.12.0 visual verification

## Real browsers and real application

`scripts/verify_header_browser.py` starts the authenticated Streamlit application, not a static header harness. It runs both the root path and `--server.baseUrlPath=operationaldashboard` in:

- bundled Chromium (Chrome-equivalent engine); and
- installed Microsoft Edge (`microsoft-edge`, Chromium).

A 17 px gutter is applied to reproduce the user's 1272 px Edge viewport with approximately 1255 px usable width after the vertical scrollbar.

## Required viewport matrix

For both browsers and both paths:

- 1920 px;
- 1536 px;
- 1366 px;
- 1280 px;
- 1272 px with the scrollbar gutter; and
- 1099 px compact-menu boundary.

An additional 1280 CSS px context uses `deviceScaleFactor=1.5` to emulate a 1920 px physical laptop at 150% Windows scaling.

## Results

- **52 checks passed** across Chrome, Edge, root path and `/operationaldashboard/`.
- At 1272 px in both browsers, all eleven labels, the bell and avatar are visible on one row.
- The measured compact desktop menu row is 829.52 px at 1272 px; usable application width is 1255 px.
- At 1099 px, only the left-aligned ☰ trigger is shown.
- At 1280 CSS px and device scale factor 1.5, the full menu remains visible.
- The nav text computes to 14 px or larger.
- The header remains 68 px brand bar + 52 px navigation + 40 px breadcrumb.
- User, notification and compact-menu triggers were opened and their lazy panels verified in both browsers.
- No horizontal overflow or visible Streamlit exception was found.

## All-page review

At 1366 px, both browsers captured and checked all authenticated pages:

1. Home
2. Plant Overview
3. Equipment Overview
4. Operations Dashboard (`KPI's` in the flat menu)
5. Operating Parameters
6. Operational Data Pipeline
7. Process Optimization
8. Event Log
9. Lesson Bank
10. Job Risk Assessment
11. Admin / Super Admin

The checker validates current React-Aria/BaseWeb field borders where controls are present, plus upload and expander borders. It also asserts that the three v3.11.1 leftover H1 page headings are absent.

## Edge evidence

Primary target screenshots:

- `verification/v3.12.0/edge/root/home_1272px.png`
- `verification/v3.12.0/edge/operationaldashboard/home_1272px.png`
- `verification/v3.12.0/edge/root/home_1099px.png`
- `verification/v3.12.0/edge/root/home_1280px_dsf1.5.png`

Every-page Edge captures are under `verification/v3.12.0/edge/root/page_*_1366px.png`.

Chrome equivalents are under `verification/v3.12.0/chrome/`.

Machine-readable measurements are in `verification/v3.12.0/browser_measurements.json`.
