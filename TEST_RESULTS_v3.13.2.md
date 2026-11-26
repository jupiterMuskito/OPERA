# OPERA-X v3.13.2 Test Results

## Automated regression suite

Commands:

```bash
python3 -m compileall -q app.py opera scripts tests
pytest -q
```

Result: **95 passed, 1 skipped, 0 failed** (96 collected).

The one skip is the opt-in wrapper for the real-browser suite. The browser verifier was run directly and passed.

## New regression coverage

- Manual/no-preset Job Risk Assessment mode is always present.
- Preset fields remain editable.
- Every editable assessment field participates in stale-result signature detection.
- The PDF button is direct (no separate prepare step) and has an export-audit callback.
- Secrets and CSV Super Admin variants can open Readings, Open Flags, Events, Lessons and Notifications and create Excel output for every drill-down.
- Home cards, bell and avatar do not define the sticky help tooltips reported by users.
- Page-level Risk Assessment, Process Optimization, Analyze Data, Automatic Upload, Field Mapping and pipeline-administration introductions do not regress.

## Real Chrome and Edge verification

Command:

```bash
python3 scripts/verify_header_browser.py --check-only
```

Result: **PASS — 78 Chrome/Edge checks across `/` and `/operationaldashboard/`.**

Coverage:

- Microsoft Edge and Chromium/Chrome engines.
- Widths 1920, 1536, 1366, 1280, 1272 and 1099 px.
- 1.5 device scale factor (Windows 150% scaling equivalent).
- Persistent scrollbar gutter at 1272 px.
- Root and nginx `/operationaldashboard/` base paths.
- Every authenticated application route.
- No visible Streamlit exceptions.
- Control borders and responsive desktop/mobile navigation.
- No `h1`/`h2` or caption between the breadcrumb and first page control; the dedicated Risk Assessment hazard-count strip is required.
- Top, centre and bottom pointer clicks on every desktop navigation item, the notification bell and the account avatar.

## Screenshot run

Command:

```bash
python3 scripts/verify_header_browser.py
```

Result: **PASS — 76 Chrome/Edge capture checks across `/` and `/operationaldashboard/`.**

The capture run omits the duplicate hit-area stress loop but captures every route and all requested visual evidence. The separate `--check-only` run executes the full hit-area loop.
