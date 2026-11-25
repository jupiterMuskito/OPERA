# OPERA-X v3.13.0 Test Results

## Automated regression suite

Command:

```bash
python3 -m compileall -q app.py opera scripts
pytest -q
```

Result: **83 passed, 1 skipped, 0 failed** (84 collected).

The skipped test is the existing opt-in browser marker used only when `OPERAX_RUN_BROWSER_TESTS=1` is set during pytest. The real browser verifier was run separately in this build.

## Real browser verifier

Command:

```bash
python3 scripts/verify_header_browser.py --check-only
```

Result: **PASS — 52 Chrome/Edge checks across root and `/operationaldashboard/`**.

## Live Excel sample execution

The packaged refinery sample was run against a temporary OPERA data root:

1. first cycle detected a changed/new workbook and waited for stability;
2. second cycle validated and imported three rows;
3. third cycle imported zero rows because the rows were unchanged duplicates;
4. state and run-log files showed successful health reporting.

## Workbook validation

All three sample `.xlsx` files were reopened with openpyxl and verified for:

- `Live Data` and `How to use` sheets;
- exact required identifier headers;
- intended DP-field headers;
- three realistic sample data rows;
- workbook readability after save.
