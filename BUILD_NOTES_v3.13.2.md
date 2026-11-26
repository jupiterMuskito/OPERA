# OPERA-X v3.13.2 Build Notes

Base: `OPERA-X_Streamlit_Deployment_v3.13.1_Final.zip`

## Summary

v3.13.2 is a focused production repair release. It preserves the v3.9–v3.13.1 hierarchy, mapping, dashboard, nginx base-path, Streamlit Community Cloud, global pipeline and permission work while fixing the six reported UI/authorization regressions and removing leftover post-breadcrumb page introductions.

## 1. Job Risk Assessment manual and editable-preset workflow

### Root cause

The v3.13.1 integration rendered only the register's preset names whenever presets existed. Its fallback `Custom` entry was reachable only when a register had no presets, so an approved register with presets had no manual entry path. The controls were also rendered directly across the full page instead of inside a bounded form.

### Fix

- Added `Manual / no preset` as the first assessment mode for every register.
- Added editable Job Description, Job Type / Activities, Location, Equipment Type, Equipment, Equipment Motion and Equipment Status controls.
- Selecting a preset fills all controls from the active BU register; every filled value remains editable before generation.
- Switching back to manual mode clears the preset fields and starts a clean assessment.
- Added signature validation so edited inputs cannot export stale hazards.
- Put the controls in a bounded, bordered form consistent with the rest of OPERA-X.
- Removed the large page heading and other redundant introduction text.
- Kept the live register count as a compact, 14 px navy information strip at the top of the form. The value is read from `register.hazard_count`; it is not hardcoded.

## 2. Print / download PDF button and audit trail

### Root cause

v3.13.1 required a separate `Prepare Job Risk Assessment PDF` click before the download button existed. This made the print action appear missing after hazard generation and again after exclusions changed.

### Fix

- The `Print / Download Job Risk Assessment PDF` button now appears immediately after a valid assessment is generated.
- The PDF is rebuilt from the current review/exclusion selection on every rerun, so it remains correct after the assessor excludes or restores hazards.
- Every PDF download writes `job_risk_assessment_exported` to the BU audit log with serial number, format, included count and excluded count.
- Generation remains separately audited and recorded in `risk_assessments.csv`.

## 3. Compact account menu

### Root cause

The previous account panel was a normal page-flow container. Its buttons expanded across the panel and pushed content down. Streamlit `help` tooltips on the bell and avatar could float over the brand bar and Vision 2030 logo.

### Fix

- Replaced the page-flow panel with an avatar-anchored popover.
- The compact menu shows name, role and BU first; Change Business Unit and Help use compact rows; Sign Out is red; the version remains at the bottom.
- Removed the bell and avatar `help` tooltips, eliminating brand/logo overlap.

## 4. Home-card tooltip cleanup

### Root cause

Each Home metric card supplied Streamlit `help` text. In the affected browser/session combination those tooltip portals could remain visible after mouse-out and cover the breadcrumb.

### Fix

Removed the nonessential help tooltips. The five cards remain native full-card buttons, retain their bordered card styling and continue to show the count prominently.

## 5. Super Admin Home drill-down and Excel access

### Root cause

The hierarchical matrix added in v3.13.1 already granted `home_drilldown` and `export` to Super Admin, but canonical role handling did not recognize the deployed aliases `OPERA Super Admin` and `OPERA-X Super Admin`. An account carrying either role label fell through to Viewer even though its display name looked administrative.

### Fix

- Added both deployed aliases to canonical role handling.
- Added an explicit Super Admin fail-safe for every declared action capability.
- Added a regression test for a Secrets-authenticated Super Admin and a CSV Super Admin opening all five Home registers and producing an Excel workbook for each.

## 6. Full nav-item, bell and avatar hit areas

### Root cause

The sticky brand container sat above the navigation in z-order and the navigation used the existing `-16px` gap compensation. The transparent bottom of the brand container therefore intercepted pointer events over the upper part of the otherwise visible 52 px navigation controls.

### Fix

- Made the noninteractive brand ribbon pointer-transparent while preserving its visuals and sticky layout.
- Kept each radio option at the full visible 52 px height.
- Added a real-browser test that clicks the top, centre and bottom of every desktop nav item, the bell and the avatar, and confirms the expected page/menu action.

## 7. Post-breadcrumb heading cleanup

- Removed the Job Risk Assessment page heading and floating caption.
- Removed pre-control headings/captions from Process Optimization, Analyze Data tabs, Automatic Upload, Field Mappings and Configure Data Pipeline.
- Rechecked Home, Plant, Equipment, KPI's, Operating Parameters, Operational Data Pipeline tabs, Event Log, Lesson Bank, Job Risk Assessment and all Admin sections.
- The browser verifier fails if an `h1`/`h2` or Streamlit caption appears between the breadcrumb and the first page control. The Job Risk Assessment hazard-count strip is a dedicated information element and is explicitly required.

## Data and scheduler impact

### `~/opera_data`

**No manual or structural change is required. Do not overwrite `~/opera_data` with the package `data/` folder.**

The new code continues using the existing registers, risk assessment log, audit log, users, global pipeline configuration/state and all BU input files. Normal use will append risk-generation/export audit rows exactly as before.

### Pipeline scheduler

**The pipeline scheduler does not need to be restarted for v3.13.2.** No scheduler, pipeline configuration or routing code changed in this release. Leave the currently running global scheduler in place.

## Deployment

Apply the code-only update or replace the repository from the full package, then run:

```bash
cd ~/OPERA
git pull
~/OPERA/start_opera.sh
```

`start_opera.sh` must perform the normal full application restart on port 8089. Then open `https://172.20.130.228/operationaldashboard/` and press **Ctrl+F5** in both Edge and Chrome.
