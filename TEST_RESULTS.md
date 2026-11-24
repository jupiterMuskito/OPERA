# OPERA-X v3.12.0 test results

## Python compilation and suite

```bash
python -m py_compile app.py opera/*.py scripts/*.py
python -m pytest -q
```

Result: **78 passed, 1 browser-marker test skipped by default (79 collected), 0 failed**.

The opt-in pytest browser marker calls the same real-app verifier described below; it is skipped unless `OPERAX_RUN_BROWSER_TESTS=1`.

## Real Chrome and Microsoft Edge verification

```bash
python scripts/verify_header_browser.py
```

Result: **52 checks passed**.

Coverage:

- installed Microsoft Edge and bundled Chromium;
- root and `/operationaldashboard/` base paths;
- 1920, 1536, 1366, 1280, 1272 and 1099 CSS px;
- 1272 px with a 17 px scrollbar gutter (1255 px usable width);
- 1280 CSS px at `deviceScaleFactor=1.5`;
- all eleven authenticated pages at 1366 px in both browsers;
- all eleven menu labels on one row at 1272 px;
- compact ☰ only at 1099 px;
- 14 px minimum nav text;
- content field, file-uploader and expander borders where present;
- no leftover v3.11.1 H1 page title;
- bell, avatar and compact-menu lazy panels;
- no horizontal overflow or visible Streamlit exception.

See `VISUAL_VERIFICATION_v3.12.0.md` and `verification/v3.12.0/browser_measurements.json`.

## Performance verification

The release benchmark compared v3.10.1, original v3.11.1 and v3.12.0 using warm authenticated click-to-settled-page timings. v3.12.0 improved every measured page against v3.11.1 by 34.5%–74.2%; see `PERFORMANCE_REPORT_v3.12.0.md`.

## Package checks

Both final ZIPs are compiled after cache cleanup, then checked with `unzip -t`. SHA-256 hashes are recorded in `DELIVERABLE_SHA256SUMS_v3.12.0.txt`.
