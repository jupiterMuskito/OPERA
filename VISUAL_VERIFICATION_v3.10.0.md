# OPERA-X v3.10.0 visual verification

The application was rendered locally with Streamlit and headless Chromium at a 1600×1000 viewport.

## Sign-in page

- Dangote Group remains to the left of OPERA-X in the blue brand panel.
- The transparent Vision 2030 artwork appears to the right of Sign In with no opaque white rectangle.
- Username/password controls and Sign In remain aligned and readable.

Screenshot: `verification/sign_in_v3.10.0.png`

## Home and fixed header

- The OPERA-X/version ribbon remains compact.
- The navigation uses plain v3.8-style page names, with no category prefixes, legend or category colours.
- Change BU is stacked above Sign Out.
- The compact transparent Vision 2030 mark sits beside the button stack and is aligned from the top, spanning the level of the two controls.
- The Home group remains Operational Data and contains Plant Overview, Equipment Overview, Operations Dashboard, Operating Parameters, Operational Data Pipeline and Process Optimization.
- Operational Knowledge contains Event Log, Lesson Bank and Job Risk Assessment.
- No Admin / Super Admin card appears on Home.

Screenshot: `verification/home_and_header_v3.10.0.png`

## Operational Data Pipeline route

- The renamed navigation item opens successfully.
- The page heading reads Operational Data Pipeline.
- Manual Entry, Bulk Upload, Derived Data and Analyze Data remain present.

Screenshot: `verification/operational_data_pipeline_v3.10.0.png`

No Streamlit exception panel was visible in any captured page.
