# OPERA-X v3.13.0 Browser Verification

Automated real-app verification completed successfully with installed Chromium/Chrome and Microsoft Edge executables.

## Coverage

- 52 checks across both browsers.
- Root path and `/operationaldashboard/` Streamlit base path.
- Widths: 1920, 1536, 1366, 1280, 1272 and 1099 CSS pixels.
- Device scale factor 1.5 check.
- Persistent 17 px scrollbar-gutter simulation at the user's 1272 px Edge case.
- All eleven authenticated routes checked for visible Streamlit exceptions, field/control borders and leftover H1 page titles.
- Header notification, user and compact-menu actions checked.

## 1272 px result

In both Chrome and Edge:

- desktop menu visible: yes;
- usable app width after simulated scrollbar: 1255 px;
- packed eleven-item menu width: 829.52 px;
- menu remained on one row.

At 1099 px, the compact menu appeared as intended. Measurements are in `verification/v3.13.0/browser_measurements.json`.

The checker ran in assertion-only mode, so it did not generate a second set of screenshots. v3.12.0 screenshot assets remain in the full build as historical evidence; v3.13.0's modified surfaces are covered by DOM/layout assertions and the unchanged responsive-header contract.
