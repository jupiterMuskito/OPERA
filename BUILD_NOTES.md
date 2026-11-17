# OPERA-X v3.6.0 — Build Notes

## Excel-backed Admin mapping workflow

**Admin / Super Admin → Field Mappings** now uses `data/business_units/<bu>/field_mappings.xlsx` as the runtime source of truth. The workbook contains:

- `Field Mappings` — effective mapping used by OPERA-X;
- `Default Mappings` — engineering baseline used by Reset to Computed Default;
- `Equipment List` and `Template List` — backend reference values; and
- `Guide` — persistence, confidence, mapping-basis and Instrument Check guidance.

The Admin page retains the v3.5.0 filters, reverse views, single-field editor/reset, review workbook and audit actions, and adds:

- **Prepare / Download Excel Mapping Update Template**;
- controlled Excel dropdown validation for Field ID, Equipment ID, Dashboard Template ID, relationship inclusion, Apply Update and Confidence;
- a field-level **Mapping Basis**, **Confidence**, and **Instrument Check Pair IDs** review sheet;
- **Validate and Apply Bulk Mapping Update** with partial-update selection;
- validation of workbook structure, controlled IDs, required relationships, confidence and DCS/Field pair integrity;
- atomic Excel-database writes and an audit summary; and
- **Prepare / Download Excel Mapping Database** for backend review.

A pre-v3.6 `field_mappings.json` file is read only during first-time migration. Its saved overrides are migrated into the Excel database with `Confidence = Review`; runtime mapping no longer depends on the JSON file.

## Engineering default mapping

The former named-field round-robin/index fallback has been removed. The new baseline reads the field name, source, unit, formula and registered equipment context, then persists the reviewed result in Excel.

- **Cement:** all 60 named DP/L/F fields and eight calculated fields are mapped across corresponding Okpella, Obajana and Ibese equipment. Kiln, cooler, raw mill, coal mill, cement mill/separator, crusher, ID fan, storage, packing and QAQC assignments are separated physically.
- **Refinery:** Butamer feed/drying/heating, the two reactors, stabiliser and recycle-gas compressor are mapped explicitly. Product/feed laboratory results follow their process sample context.
- **Fertilizer:** primary reforming, synthesis-gas compression, urea synthesis/stripping, granulation and bagging are explicit. Missing registered items such as the secondary reformer, ammonia converter, CO2 compressor and utilities use identified SPARE records with `Confidence = Review` rather than a false equipment match.
- **NASCON:** Salt brine/evaporation/drying/packing and Sugar milling/evaporation/centrifuging/packing are explicit. Missing clarifier, vacuum pan, sugar dryer, boiler, warehouse and conveying items use identified SPARE records marked `Review`.
- **Placeholders:** every unnamed DP/F/L/TA–TG field maps to source-aware SPARE equipment and the required source template(s), with the exact basis `Default placeholder mapping – review when field is named.`
- **Dashboard meaning:** throughput and plant KPIs map to Plant Performance; process variables to Process Performance; equipment-health variables to Condition Monitoring; QAQC/emissions/specifications to Quality and Compliance; and failure/downtime/condition-risk variables to Reliability. Multi-template assignments are used only when the field has a real dual purpose.

The Excel database carries **Mapping Basis** and **Confidence** for every mapping. `MAPPING_QUALITY_REPORT.md` gives the BU/template counts, every named `Review` item, grouped placeholder reviews, and 20 spot-check samples.

## Instrument Check pairs

Same-point DCS/Field links are stored in `Instrument Check Pair IDs` and now drive the default Instrument Check selection:

- Refinery: Butamer feed flow, reactor inlet temperature and reactor pressure checks;
- Fertilizer: urea-reactor pressure; and
- NASCON: salt-evaporator temperature and vacuum-pan pressure.

No Cement pair was fabricated because the current 60-field sample has no defensible same-point F/DP pair.

## Calculated-field corrections

All 32 configured calculated fields were checked. Misnamed or dimensionally inconsistent v3.5.0 formulas were corrected, including:

- Cement calciner–preheater temperature difference and clinker/raw-meal indices;
- Refinery reactor temperature rise and product C4 composition;
- Fertilizer urea-pressure Field/DCS deviation and converter temperature rise; and
- NASCON evaporator-temperature deviation, mill extraction, sugar polarisation and average packing rate.

Calculated mappings inherit the union of equipment assigned to the actual formula inputs, and each database basis names those inputs and the formula.

## UI/UX and retained functionality

- The Operational Intelligence layout, fixed OPERA-X brand ribbon, merged navigation and CPP-style chart grid remain unchanged.
- The removed v3.5.0 blue authenticated page-title hero remains absent.
- All existing dashboard, operational-data, event, parameter, risk, lesson, export, authentication and DCS-connector workflows are retained.

## Plain-language Admin test

1. Sign in as BU Admin or Super Admin and open **Admin / Super Admin → Field Mappings**.
2. Select a BU and search a named field; confirm Equipment, Dashboard Templates, Mapping Basis and Confidence are visible.
3. Choose **Prepare Excel Mapping Update Template**, download it and confirm dropdown arrows appear in the editable sheets.
4. In `Equipment Mappings` / `Template Mappings`, change one field's relationships.
5. In `Field Review`, set that Field ID's **Apply Update** to `Yes`, update its basis/confidence if needed, and save the workbook.
6. Bulk-upload the workbook and choose **Validate and Apply Bulk Mapping Update**.
7. Confirm the success summary names one updated field and the mapping is immediately visible in Field View/reverse views.
8. Confirm a `field_mapping_bulk_updated` audit entry exists.
9. Use **Reset to Computed Default** to restore the engineering baseline if this was only a test.
10. Download the Excel Mapping Database and confirm both effective/default sheets plus basis, confidence and pair IDs.
11. Open **Analyze Data → Instrument Check** in Refinery, Fertilizer or NASCON and confirm a recorded pair is selected by default.

## Compatibility and data safety

- Use `OPERA-X_Code_Only_Update_v3.6.0.zip` on an existing deployment; it contains no runtime files under `data/`.
- The code-only build creates the Excel mapping database on first use and migrates legacy JSON overrides without replacing readings or other runtime CSVs.
- The full build includes 174 runtime CSVs, nine `field_mappings.xlsx` databases, and four corrected `calculated_fields.csv` files; it is for fresh deployment unless live data has been backed up and deliberately excluded.
- Spare equipment records are activated because placeholder fields now map to those records.
- See `DATA_OVERWRITE_WARNING.md` for the exact changed/runtime-risk inventory.
