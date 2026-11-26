# OPERA-X v3.13.2 Visual Verification

All evidence below was captured from the real Streamlit application. The required production-proxy evidence uses Microsoft Edge at **1272 px width** under **`/operationaldashboard/`**.

## Required screenshots

| Area | Evidence |
|---|---|
| Manual Job Risk Assessment, live hazard-count strip, editable fields and print/download button | `verification/v3.13.2/edge/operationaldashboard/risk_manual_hazard_count_and_print_1272px.png` |
| Preset Job Risk Assessment, editable preset values and print/download button | `verification/v3.13.2/edge/operationaldashboard/risk_preset_editable_and_print_1272px.png` |
| Compact avatar-anchored account menu | `verification/v3.13.2/edge/operationaldashboard/account_menu_1272px.png` |
| Home cards with prominent counts and no hover-help overlay | `verification/v3.13.2/edge/operationaldashboard/home_cards_1272px.png` |
| Navigation bar, bell and avatar | `verification/v3.13.2/edge/operationaldashboard/navigation_bar_1272px.png` |

## Hazard-count presentation

The screenshots show the live Cement register result of **360 approved hazards available for assessment**. This number came from the active register's `hazard_count` property during the browser run. The code does not contain a hardcoded 360.

The information element:

- is inside the bounded assessment form;
- aligns with the form's left and right edges;
- uses a light information background and navy text;
- uses 14 px body text and a stronger 16 px count;
- shows the current BU register label; and
- is not an `h1`, `h2` or Streamlit caption.

## Page-heading audit

The real-browser audit covers Home, Plant Overview, Equipment Overview, Operations Dashboard, Operating Parameters, every Operational Data Pipeline view, Process Optimization, Event Log, Lesson Bank, Job Risk Assessment and every Admin route. It fails if an `h1`, `h2` or Streamlit caption is visible between the breadcrumb and the first control.

## Navigation hit-area audit

For every desktop nav item, the browser suite resets to a different page, clicks the target at 3 px from the top, at its centre, and 3 px from the bottom, then waits for the completed target-page marker. The same top/centre/bottom procedure opens and closes the notification panel and the account popover.

## Additional screenshots

Complete route and viewport captures are available under:

- `verification/v3.13.2/chrome/root/`
- `verification/v3.13.2/chrome/operationaldashboard/`
- `verification/v3.13.2/edge/root/`
- `verification/v3.13.2/edge/operationaldashboard/`

These include 1920, 1536, 1366, 1280, 1272 and 1099 px captures plus 1280 px at a 1.5 device scale factor.
