# OPERA-X v3.13.1 Build Notes

Base: `OPERA-X_Streamlit_Deployment_v3.13.0_Final.zip`

## Summary

v3.13.1 preserves the v3.9–v3.13.0 mapping, dashboard, nginx base-path, Community Cloud, responsive-header, Live Excel and scheduler functionality while fixing three production issues:

1. developer and implementation notes were visible in the application;
2. Super Admin could be resolved as view-only on action pages; and
3. automatic pipeline configuration and execution were incorrectly tied to the business unit selected in the UI.

## 1. User-facing technical notes

### Root cause

The Automatic Upload panel contained a hard-coded engineering explanation about 100 ms polling, CSV lock contention and implementation defaults. Similar implementation wording appeared in Admin help, mapping text, connector status, source-path help, register persistence and saved-view controls.

### Fix

- Removed the 100 ms information box in full.
- Audited every application page and the Admin area.
- Replaced implementation explanations with short task-focused help only where a user needs guidance.
- Removed or renamed user-facing references to polling, CSV locks, Python scripts, Streamlit Secrets, environment-variable/path resolution, backend/runtime databases, fingerprints, simulated connectors and GitHub persistence.
- Kept the underlying functionality and moved implementation detail to documentation and build notes.
- Added a source-level regression test for the removed phrases.

## 2. Hierarchical permissions and Super Admin fail-safe

### Root causes

Three permission paths could disagree:

1. grants were assembled independently for each role, so a new lower-role capability could be omitted from Super Admin;
2. role checks depended on exact display strings or direct `user.role == "Super Admin"` comparisons, so legacy values such as `super_admin`, separator/casing variants or an inconsistent persisted record could fall back to Viewer; and
3. after a Secrets login, the next rerun reloaded a same-named CSV account and could replace the authoritative Secrets role. BU access also depended on a literal `*` assignment instead of the Super Admin role itself.

### Fix

- Added canonical role handling for supported legacy casing and separator variants.
- Built grants by inheritance: Viewer → Patroller → Operator → Manager/BU Admin → Super Admin.
- Super Admin is the union of every lower-role grant plus global user, business-unit and all-BU administration. A test iterates every declared action and fails if Super Admin is denied any one.
- Super Admin can access every current or future BU even if a persisted `business_units` value is missing or malformed.
- Secrets accounts remain authoritative on rerun and are no longer replaced by same-named CSV rows.
- Replaced direct page checks with capabilities for manual entry, bulk upload, event input, lesson input, risk assessment, exports, Home drill-downs, Admin sections and pipeline configuration.
- Enforced one-BU scope at runtime for Manager, Operator and Patroller, including legacy records that contain multiple BU values; the first assigned BU remains effective until a Super Admin updates the account.
- Restricted global **Business Units** and **Users & Roles** sections to Super Admin. BU Admin and Manager retain BU-scoped configuration sections.

## Permission matrix

A check means the action is available within the role's permitted BU scope.

| Role | View data | Manual entry | Bulk upload | Event input | Lesson input | Risk assessment | Exports | Home drill-downs | BU configuration and pipelines | Users and global BU administration | BU scope |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Super Admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Every BU |
| BU Admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | Assigned BU(s) |
| Manager | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | Exactly one assigned BU |
| Operator | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | Exactly one assigned BU |
| Patroller | ✓ | ✓ | — | — | — | — | — | — | — | — | Exactly one assigned BU |
| Viewer | ✓ | — | — | — | — | — | — | — | — | — | Assigned BU(s) |

## 3. Global automatic pipelines

### Root cause

v3.13.0 stored `pipeline_configurations.json` and `pipeline_state.json` inside each BU folder. Admin saved settings to the currently selected BU, and the scheduler looped through BUs and called Live Excel sync with that loop BU. Live Excel validation then required every row's `Business unit` value and equipment to match the loop BU. Enabling files 1 and 3 while Cement was selected therefore ran them as `cement/live_excel_1` and `cement/live_excel_3`, producing the observed “Must be cement” and “Equipment is not registered” errors.

### Fix

- Pipeline configuration is now global at `~/opera_data/shared/pipeline_configurations.json`.
- Pipeline state is global at `~/opera_data/shared/pipeline_state.json`, with target-BU status details for access-filtered health reporting.
- Every pipeline has either a fixed **Target Business Unit** or **Route by Business unit column** with an explicit allowed-BU list.
- Default Live Excel targets are:
  - Live Excel files 1 → Refinery;
  - Live Excel files 2 → Cement;
  - Live Excel files 3 → Fertilizer.
- Admin → Configure Data Pipeline shows the global list to Super Admin. BU Admin and Manager see only pipelines intersecting their assigned BU scope. Editing does not depend on the BU selected in the header.
- Automatic Upload shows all target-BU health rows to Super Admin. Other users see only the current BU's pipeline health.
- Live Excel canonicalizes each row's `Business unit` value, groups rows by that target, validates fields and equipment against that BU's registries, and writes to that BU's `inputs/dcs.csv`.
- Unknown or disallowed BU rows are rejected individually. Valid rows for allowed BUs continue to import; the signed-in or header-selected BU is never used for routing.
- Pipeline run logs now include pipeline ID, pipeline name, target BU, imported rows, flags and rejected-row count.
- The background scheduler loads the global configuration once per cycle and runs every enabled pipeline by its own interval without any user session.
- Scheduler console lines show the pipeline name and target BU(s).

## Automatic migration of v3.13.0 settings

No manual edit is required.

On first global configuration load:

1. OPERA-X scans existing `business_units/<bu>/pipeline_configurations.json` files.
2. It de-duplicates each pipeline ID.
3. When the same pipeline was saved under multiple BUs, it keeps the settings from the pipeline's intended target BU (for example, Refinery for Live Excel files 1).
4. It writes the merged global configuration to `shared/pipeline_configurations.json`.
5. Matching legacy state is migrated to `shared/pipeline_state.json`.
6. Existing per-BU configuration and state files are retained for rollback/audit and are not deleted or edited.

## What must be updated in `~/opera_data`

**Nothing must be edited or copied manually. Do not overwrite `~/opera_data` with the package `data/` folder.**

The application automatically creates or updates only these items when used:

- `~/opera_data/shared/pipeline_configurations.json` — global configuration created by automatic migration or the Admin page;
- `~/opera_data/shared/pipeline_state.json` — global scheduler/health state;
- `~/opera_data/business_units/<bu>/pipeline_runs.csv` — gains pipeline-name, target-BU and rejected-row fields on the next appended run;
- `~/opera_data/business_units/<target-bu>/inputs/dcs.csv` — updated only with validated rows routed to that BU;
- existing per-BU pipeline configuration/state files remain untouched.

The watched workbook folder remains `~/opera_inbox/live_excel/`, outside both the repository and `~/opera_data`.

## Scheduler restart — required

**Yes. The scheduler must be restarted after deploying v3.13.1.** The existing process has the v3.13.0 per-BU loop loaded in memory; updating files alone does not replace that running process.

After applying the code, run exactly:

```bash
~/OPERA/scripts/stop_pipeline_scheduler.sh
~/OPERA/scripts/start_pipeline_scheduler.sh
```

Then fully restart the application and hard-refresh the browser:

```bash
~/OPERA/start_opera.sh
```

Press **Ctrl+F5** in both Chrome and Edge. Verify the normal URL and `/operationaldashboard/`, including the 1272 px Edge viewport.

## Testing

- `python3 -m compileall -q app.py opera scripts` — passed.
- `pytest -q` — **90 passed, 1 skipped, 0 failed** (91 collected). The skip is the existing opt-in browser marker.
- `python3 scripts/verify_header_browser.py --check-only` — **PASS: 52 Chrome/Edge checks across root and `/operationaldashboard/`**.
- New tests cover the complete permission matrix, Super Admin fail-safe, Secrets role precedence, automatic global migration/de-duplication, three-BU scheduler execution without a user session, row-routed multi-BU workbooks, fixed-target row rejection, active-BU independence and non-Super-Admin health visibility.
