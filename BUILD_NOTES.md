# OPERA-X v3.7.0 — Build Notes

## Correctness

- Fixed the Admin field → mapping → template → chart propagation gap described in `ROOT_CAUSE_AND_FIX_v3.7.0.md`.
- Mapped fields remain available to chart panel selectors even before readings exist; a no-readings panel explains the state.
- Existing mapping workbooks automatically reconcile newly added/activated field records while preserving overrides.
- User-role changes refresh on the next interaction; Super Admin can now edit existing role, BU access and active state.
- DCS settings, templates, fields, constants, presets, equipment and lists are signature-reloaded after atomic writes.

## Dashboard defaults and data

- Every Plant, Equipment and Operations template has 12 default chart fields and 12 default table fields.
- Operations Dashboard now has 12 realistic calculated fields (`CF1`–`CF12`) for Cement, Refinery, Fertilizer and NASCON.
- Okpella, Obajana and Ibese each have sample values for all 67 named equipment records and all 60 active DCS/Lab/Field fields.
- Placeholder fields remain without values until named/activated.

## Performance

- Selective-column CSV reads, modification-signature caching, early plant/equipment filtering and direct Home counts.
- Signature-checked compressed mapping runtime cache; Excel remains authoritative and Admin-viewable.
- Lazy Operational Data/Admin section execution.
- Latest-30-day default window, 300-point trace cap and four-at-a-time chart panel sets while retaining all 12 configured fields.
- See `PERFORMANCE_REPORT_v3.7.0.md` for before/after figures.

## Deployment compatibility

- `OPERAX_DATA_DIR` and legacy `OPERA_DATA_DIR` remain supported.
- Internal server command/port and nginx subpath deployment remain unchanged.
- Streamlit Community Cloud remains supported without secrets.
- Use the code-only ZIP on the live GitHub/server deployment.
- Run `scripts/upgrade_v370_live_data.py` against `~/opera_data` first as a dry run, then with `--apply` if additions are listed.
- Never overlay the full build's `data/` folder on `~/opera_data`.

## Verification

- 45 automated tests passed.
- All configured Admin categories have direct E2E or retained regression coverage.
- The migration passed dry-run, apply and idempotence checks.
- Full and code-only package hashes are listed in `DELIVERABLE_SHA256SUMS_v3.7.0.txt`.
