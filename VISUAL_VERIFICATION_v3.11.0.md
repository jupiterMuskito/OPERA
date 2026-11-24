# OPERA-X v3.11.0 visual verification

The authenticated header was rendered with the pinned Streamlit 1.66.1 runtime through a local `/operationaldashboard/` base path, matching the DDF nginx sub-path. The test account was a Super Admin in Cement and the active route was Equipment Overview.

## Required width captures

| Viewport | Capture | Result |
|---:|---|---|
| 1920 px | `verification/v3.11.0/header_1920px.png` | Flat menu in one row; no label overflow; active Equipment underline visible |
| 1560 px | `verification/v3.11.0/header_1560px.png` | Flat menu in one row; no label overflow |
| 1366 px | `verification/v3.11.0/header_1366px.png` | Flat menu in one row; no label overflow |
| 1280 px | `verification/v3.11.0/header_1280px.png` | Flat menu in one row; no label overflow |

An additional breakpoint capture, `verification/v3.11.0/header_1279px.png`, verifies that the desktop page menu is hidden and the native **☰ Menu** control is shown below 1280 px.

## Automated browser measurements

`verification/v3.11.0/header_measurements.json` records the following checks for every required width:

- brand content height: 68 px;
- one visible desktop button row at 1920, 1560, 1366, and 1280 px;
- zero overflowing navigation labels;
- Equipment is the single active item;
- no horizontal document overflow;
- no browser console or page errors.

The Streamlit container around the 52 px navy bar contributes its normal vertical layout gap, while the visible header remains compact and replaces the former multi-row header. The white brand bar, navy flat menu, breadcrumb, Vision 2030/version placement, notification badge, and avatar were visually inspected in all captures.

## Deployment reminder

Apply the complete v3.11.0 code-only update to the verified v3.10.1 codebase; do not skip releases or copy only selected files. After `git pull`, fully restart the DDF app with:

```bash
~/OPERA/start_opera.sh
```

Do not rely on Streamlit hot reload for this release, and do not change anything manually in `~/opera_data`.
