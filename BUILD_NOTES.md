# OPERA-X v3.5.0 — Build Notes

## Blue page-title ribbon removed

- Deleted the shared `hero()` function from `app.py`.
- Deleted the `.opera-hero`, `.opera-hero h1`, and `.opera-hero p` CSS rules.
- Removed every call that rendered the rounded blue gradient page-title/subtitle box.
- Did **not** replace it with another coloured banner. Authenticated modules now begin directly with their page content below the fixed controls.
- Preserved the fixed top OPERA-X brand ribbon and the fixed white navigation bar containing business-unit/user context, notifications, **Change BU**, and **Sign Out**.
- Preserved the blue sign-in brand panel; it is part of the login screen, not an authenticated page ribbon.

### Pages rendered and checked

All ten authenticated routes were rendered through Streamlit's application test runtime and completed without an exception:

1. OPERA-X Home
2. Plant Overview
3. Equipment Overview
4. Operations Dashboard
5. Operational Data
6. Event Log
7. Operating Parameters
8. Risk Assessment
9. Lesson Bank
10. Admin / Super Admin

Static checks also confirm there is no `hero()` function, `hero(` call, or `.opera-hero` CSS left in the codebase. The only remaining blue gradients in `app.py` are the intended top brand ribbon and sign-in brand panel.

## Complete Admin field mapping

Admin / Super Admin → Field Mappings now materialises and shows the complete effective mapping, rather than only saved overrides:

- every active input field;
- every inactive/spare placeholder field;
- DCS, Field, QAQC (Lab), Others (TA–TG), and calculated fields;
- mapped equipment IDs and names;
- mapped plants and units/sections;
- mapped dashboard templates: Plant Performance, Condition Monitoring, Process Performance, Quality and Compliance, and Reliability;
- whether each row is a computed default or an Admin override.

The page includes:

- filters for business unit, source, status, plant, unit/section, equipment, and dashboard template;
- Field ID/name search;
- a full field view;
- an equipment reverse view showing each equipment/data-field relationship;
- a dashboard-template reverse view showing each template/data-field relationship;
- an editor for any active, placeholder, or calculated field;
- reset-to-computed-default;
- audit entries containing the old and new equipment/template values;
- a complete Excel workbook with `Field Mappings`, `By Equipment`, `By Template`, and `Guide` sheets.

For Cement, the verified full catalog contains 10,008 fields: 60 active input fields, 9,940 placeholders, and 8 calculated fields. All have at least one equipment and one canonical dashboard-template mapping. The reverse views cover all 201 named active Cement equipment records and all five canonical templates.

## Plain-language mapping test script

1. Sign in as a BU Admin or Super Admin and select a business unit.
2. Open **Admin / Super Admin → Field Mappings**.
3. In **Field View**, search for an active field and note its mapped equipment and dashboard template.
4. Open **Equipment Reverse View**, filter to that equipment, and confirm the field is listed.
5. Open **Template Reverse View**, filter to that dashboard template, and confirm the field is listed.
6. Open **Edit Mapping**, select the field, remove its current equipment, choose a different equipment, retain at least one template, and select **Save Data Field Mapping**.
7. Open **Equipment Overview**, select the new equipment and applicable dashboard template, then open **Data Field Selection Tool**. Confirm the field is available.
8. Return to **Admin / Super Admin → Field Mappings**, select the old equipment, and confirm the field is no longer listed there.
9. In **Audit & Backup**, confirm a `field_mapping_changed` entry was written with the previous and new values.
10. Return to **Edit Mapping** and choose **Reset to Computed Default** if the test override should not be retained.
11. Select **Prepare Complete Mapping Workbook**, then download the Excel file and review all four sheets.

## Compatibility and data safety

- No packaged file under `data/`, `registers/`, or `reference_sources/` changed versus v3.4.0.
- Saved mapping overrides remain in each BU's runtime `field_mappings.json` and continue to take precedence over computed defaults.
- Use the code-only update ZIP on an existing deployment. The full deployment ZIP contains 174 seed/runtime CSVs that can overwrite data entered through the running app. See `DATA_OVERWRITE_WARNING.md`.
- CPP-style chart grids, existing dashboard templates, operational workflows, risk registers, exports, authentication, and all other v3.4.0 features are retained.
