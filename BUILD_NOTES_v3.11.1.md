# OPERA-X v3.11.1 build notes

## Purpose

v3.11.1 is the corrective release for the v3.11.0 authenticated header. It preserves all existing routes, permissions, data workflows, nginx deployment behavior and Streamlit Community Cloud compatibility while aligning the real Streamlit header with the approved flat-menu mockup.

## Root cause

The v3.11.0 CSS breakpoint itself was `1279px`, but the implementation consumed substantially more space than the mockup:

1. The flat menu was built with `st.columns`, so the page labels expanded across the full menu column instead of using their natural text widths. This made the menu sensitive to the usable Streamlit block width and laptop/browser scaling.
2. Both desktop and mobile navigation trees were rendered. When the mobile tree was hidden, its surrounding Streamlit layout wrapper still contributed a 16px vertical flex gap. Together with nav padding, that turned the intended 52px bar into an approximately 68px block.
3. Streamlit's top-level vertical container added another 16px gap between the brand, navigation and breadcrumb containers.
4. Native popover buttons retained Streamlit's `expand_more` affordance, so chevrons appeared next to the bell and initials.
5. The breadcrumb had a fixed outer height while its internal Streamlit wrapper retained its own sizing and the breadcrumb content used `overflow:hidden`, causing clipping.
6. The page block retained Streamlit's wide horizontal padding, reducing usable menu width on laptops.

## Fix

- Replaced the column-based page menu with a non-wrapping horizontal Streamlit container and content-width native buttons.
- Set 13px horizontal button padding and kept group dividers immediately beside Plant, Event Log and Admin.
- Kept the exact responsive contract: flat menu at every viewport of 1280 CSS px or wider; compact left-aligned ☰ button at 1279px and below.
- Removed residual Streamlit layout gaps between the brand, nav and breadcrumb while retaining normal spacing below the header.
- Fixed the visible nav bar at 52px and vertically centered its controls.
- Hid only the popover caret wrapper; retained the bell icon, attached badge and circular initials avatar.
- Made the breadcrumb a full-width, square-cornered 40px strip with visible overflow, centered content and no gap below the nav.
- Added explicit Home, Equipment Overview and Admin / Super Admin page headings so browser checks can prove the first heading starts below the complete breadcrumb.
- Corrected the existing static-dataframe fallback to use an imported `Styler` class instead of the lazily unavailable `pd.io.formats.style` attribute.

## Compatibility

- `streamlit==1.66.1` remains pinned.
- Local brand assets are still embedded as data URIs.
- No HTML links, JavaScript navigation or root-relative asset paths were introduced.
- Both root-path Streamlit/Community Cloud and nginx `/operationaldashboard/` deployments were rendered in the real application.
- `OPERA_DATA_DIR=~/opera_data` and `OPERAX_DATA_DIR=~/opera_data` remain supported.

## Verification

- 71 Python tests passed, including the opt-in real Chromium/Streamlit browser test.
- The actual authenticated app was rendered at 1920, 1560, 1536, 1366, 1280 and 1279 CSS px for Home, Equipment Overview and Admin / Super Admin at both `/` and `/operationaldashboard/`: 36 checks in total.
- Every 1280px-and-wider case displayed all 11 flat-menu labels in one row.
- Every 1279px case displayed a compact left-aligned ☰ control.
- Every navigation bar measured 52px.
- Every breadcrumb measured 41px including its 1px border; its 40px content box was fully visible and the first heading started below it.
- Maximum packed label-row width was 947.66px, leaving flexible space before the bell and avatar.
- No visible Streamlit exceptions or horizontal document overflow were detected.

See `VISUAL_VERIFICATION_v3.11.1.md` and `verification/v3.11.1/header_measurements.json`.

## Deployment

Apply the complete v3.11.1 code-only update to v3.11.0, install the pinned requirements, and fully restart:

```bash
cd ~/OPERA
git pull
source .venv/bin/activate
python -m pip install -r requirements.txt
~/OPERA/start_opera.sh
```

Then hard-refresh the browser with **Ctrl+F5**. A Streamlit hot reload is not sufficient for this header/CSS update.
