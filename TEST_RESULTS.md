# OPERA-X v3.6.0 — Test Results

## Result

**PASS — 40 tests passed.**

Commands completed successfully:

```bash
python3 -m py_compile app.py opera/*.py scripts/*.py
pytest -q
```

## UI route verification

Streamlit's application-test runtime signed in as the seeded BU Admin, selected Cement, and rendered all ten authenticated routes without an exception:

- OPERA-X Home
- Plant Overview
- Equipment Overview
- Operations Dashboard
- Operational Data
- Event Log
- Operating Parameters
- Risk Assessment
- Lesson Bank
- Admin / Super Admin

The fixed brand/navigation structure and CPP-style chart behavior remain covered. The deleted blue page-title hero remains absent.

## Engineering mapping verification

- Four configured BUs: 272 named/calculated fields reviewed.
- Nine packaged BUs: 90,032 total mappings (272 named/calculated plus 89,760 placeholders).
- Empty equipment mappings: 0.
- Empty template mappings: 0.
- Empty mapping-basis values: 0.
- Confidence values restricted to High, Medium or Review.
- Named fields use curated process/equipment assignments; no named field uses round-robin/index/random fallback.
- Every placeholder maps to SPARE equipment, the required source-aware template set, `Confidence = Review`, and the exact placeholder review basis.
- Cement kiln/cooler/mill/QAQC assignments are verified across Okpella, Obajana and Ibese.
- Refinery Butamer reactors, drier, heater, stabiliser and compressor assignments are verified.
- Fertilizer urea-reactor and granulator assignments are verified.
- NASCON Salt evaporator and Sugar centrifuge assignments are verified.
- Recorded Instrument Check pairs are verified for Refinery, Fertilizer and NASCON; Cement correctly records none.
- All 32 calculated fields inherit equipment from their actual formula inputs; corrected formula/name examples are asserted.

## Excel verification

- Every packaged BU has a readable `field_mappings.xlsx` with effective/default mappings, equipment/template lists and guide.
- The Admin update template contains the required mapping/review/catalog sheets and a hidden controlled-list sheet.
- Excel named ranges and dropdown validation are verified for Field IDs, Equipment IDs, Template IDs, Include, Apply Update and Confidence.
- A partial workbook upload updates only a Field ID marked `Apply Update = Yes`; untouched fields remain computed defaults.
- Bulk validation rejects missing sheets/columns, unknown IDs, invalid pair types, blank bases, invalid confidence and empty relationships.
- Workbooks contain no formulas, so no formula recalculation errors can be introduced.

## Data-safety verification

- The code-only package excludes the complete `data/` tree and therefore excludes runtime CSV/XLSX files.
- The full package deliberately adds nine mapping databases and changes the four configured calculated-field CSVs plus nine equipment CSVs (SPARE activation).
- No file under `registers/` or `reference_sources/` changed versus v3.5.0.
- `DATA_OVERWRITE_WARNING.md` inventories the runtime overwrite risk and directs existing deployments to the code-only package.
