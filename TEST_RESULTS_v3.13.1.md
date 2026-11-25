# OPERA-X v3.13.1 Test Results

## Automated regression suite

Commands:

```bash
python3 -m compileall -q app.py opera scripts
pytest -q
```

Result: **90 passed, 1 skipped, 0 failed** (91 collected).

The skipped test is the existing opt-in real-browser marker, which runs only when `OPERAX_RUN_BROWSER_TESTS=1` is set. The same browser verifier was run directly for this build.

## New v3.13.1 coverage

- Complete role/action permission matrix.
- Super Admin receives every declared capability and every BU even with a legacy role alias or missing wildcard assignment.
- Secrets roles remain authoritative across reruns.
- Automatic migration and de-duplication of per-BU v3.13.0 pipeline configuration.
- Global pipeline configuration remains unchanged when a different active BU is viewed.
- Scheduler cycles without any user session import Live Excel files 1, 2 and 3 into Refinery, Cement and Fertilizer respectively.
- Multi-BU Live Excel rows route by each row's `Business unit` value and validate equipment in that target BU.
- Fixed-target sources import valid rows while rejecting rows for disallowed BUs.
- Non-Super-Admin pipeline health is filtered to permitted BU data.
- The removed developer-information phrases cannot regress into the app source.

## Real browser verifier

Command:

```bash
python3 scripts/verify_header_browser.py --check-only
```

Result: **PASS — 52 Chrome/Edge checks across root and `/operationaldashboard/`**.

Coverage includes 1920, 1536, 1366, 1280, 1272 and 1099 px widths; 1.5 device scale factor; scrollbar gutter; one-row navigation; all authenticated routes; content-control borders; visible exceptions; and nginx sub-path behavior.
