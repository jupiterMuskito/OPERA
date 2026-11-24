# OPERA-X v3.11.1 visual verification

## Method

The real authenticated `app.py` was started by `scripts/verify_header_browser.py` with a temporary copy of packaged data. Chromium rendered the application at device scale factor 1 and 100% page zoom in two independent deployments:

- root path: `/`;
- reverse-proxy-equivalent path: `/operationaldashboard/` using Streamlit `server.baseUrlPath`.

The BU Admin test account opened Cement and exercised three real routes: Home, Equipment Overview and Admin / Super Admin. This was not a static HTML mockup or a separate header harness.

## Viewports and results

For each route and deployment path, screenshots were captured at **1920, 1560, 1536, 1366, 1280 and 1279 CSS px**. The resulting 36 screenshots are in:

- `verification/v3.11.1/root/`
- `verification/v3.11.1/operationaldashboard/`

All 30 cases at 1280px or wider showed the complete flat menu in one row. Both 1536px cases represent the usable CSS width of a 1920px display at 125% Windows scaling. All six 1279px cases showed the compact left-aligned ☰ control.

## Automated assertions

`verification/v3.11.1/header_measurements.json` records every assertion:

- navigation bar: exactly 52px;
- flat-menu labels: all 11 visible and one row at 1280px and wider;
- packed label row: maximum 947.66px, not equal-width columns;
- compact menu: at most 42px wide and left aligned at 1279px;
- breadcrumb: 41px outer box including its border, with the full 40px content box inside it;
- first page heading: below the breadcrumb bottom edge;
- popover chevrons: no visible `expand_more` icon beside the bell or avatar;
- document: no horizontal overflow;
- application: no visible Streamlit exception.

## Comparison sheets

- `verification/v3.11.1/comparison_collapsed_before_vs_final_1560.png`
- `verification/v3.11.1/comparison_flat_before_vs_final_1536.png`

Each sheet places the user's reported v3.11.0 screenshot beside the approved mockup's measured criteria and the final v3.11.1 real-app rendering. They make the responsive, spacing, control and breadcrumb corrections visible without relying only on numeric checks.

## Representative screenshots

| Deployment | Route | 1920 | 1560 | 1536 | 1366 | 1280 | 1279 |
|---|---|---|---|---|---|---|---|
| Root | Home | `root/home_1920px.png` | `root/home_1560px.png` | `root/home_1536px.png` | `root/home_1366px.png` | `root/home_1280px.png` | `root/home_1279px.png` |
| Root | Equipment | `root/equipment_1920px.png` | `root/equipment_1560px.png` | `root/equipment_1536px.png` | `root/equipment_1366px.png` | `root/equipment_1280px.png` | `root/equipment_1279px.png` |
| Root | Admin | `root/admin_1920px.png` | `root/admin_1560px.png` | `root/admin_1536px.png` | `root/admin_1366px.png` | `root/admin_1280px.png` | `root/admin_1279px.png` |
| Base path | Home | `operationaldashboard/home_1920px.png` | `operationaldashboard/home_1560px.png` | `operationaldashboard/home_1536px.png` | `operationaldashboard/home_1366px.png` | `operationaldashboard/home_1280px.png` | `operationaldashboard/home_1279px.png` |
| Base path | Equipment | `operationaldashboard/equipment_1920px.png` | `operationaldashboard/equipment_1560px.png` | `operationaldashboard/equipment_1536px.png` | `operationaldashboard/equipment_1366px.png` | `operationaldashboard/equipment_1280px.png` | `operationaldashboard/equipment_1279px.png` |
| Base path | Admin | `operationaldashboard/admin_1920px.png` | `operationaldashboard/admin_1560px.png` | `operationaldashboard/admin_1536px.png` | `operationaldashboard/admin_1366px.png` | `operationaldashboard/admin_1280px.png` | `operationaldashboard/admin_1279px.png` |

## Deployment reminder

After applying the code-only update, fully restart with `~/OPERA/start_opera.sh` and hard-refresh with **Ctrl+F5**. Do not modify `~/opera_data`.
