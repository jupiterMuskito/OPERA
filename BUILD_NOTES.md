# OPERA-X v3.9.0 build notes

## Requested changes completed

- Renamed user-facing data types **DCS → Digital Data** and **Field → Raw Field Data** across source selectors, grouped field pickers, Instrument Check, event updates, notifications, Home reading exports, Operations messaging, Admin filters, the Digital Data connector, generated Excel mapping workbooks and current documentation.
- Preserved the persisted source keys `DCS` and `Field` and field-ID prefixes `DP` and `F`. Existing CSV filenames, source records and mappings therefore remain compatible.
- Expanded the Excel Mapping Update Template's **Field Catalogue** so one row carries both **Equipment ID** and **Dashboard Template ID**, their readable names, and **Include**. Both ID columns have controlled dropdown validation. The uploader de-duplicates both relationships and reconciles edits with the retained compatibility sheets.
- Added the supplied **Dangote Group** and **Vision 2030** artwork as optimized local assets. The sign-in brand panel places the Dangote Group logo before OPERA-X; the sign-in heading places Vision 2030 to the right of Sign In; a compact Vision 2030 rendition sits beneath Change BU and Sign Out without materially increasing the fixed header.
- Increased the sign-in solution tagline to 1.2 rem, high-contrast bold text.
- Added colour-coded **Operational Data**, **Operational Knowledge**, **Process Optimization**, and **Job Risk Assessment** categories on Home and in navigation. Existing Operational Data capture/derived/analysis features remain available under Operational Data.
- Moved bounded response optimization to the standalone **Process Optimization** module and removed the duplicate Optimization tab from Operational Data → Analyze Data.
- Renamed the module **Risk Assessment → Job Risk Assessment** in navigation, Home, category and page labels, buttons, PDF/Excel/CSV export titles and filenames, Admin labels, generated PDF metadata/form titles, new audit action values, README and current docs.

## Job Risk Assessment compatibility decision

Only user-facing labels and future audit action values were renamed. The following stable live-data/code identifiers were deliberately not renamed: `risk_assessments.csv`, `registers/`, packaged register workbook filenames, `risk_store.py`, `risk_engine.py`, `risk_pdf.py`, and existing risk-related function/session-state identifiers. The Admin audit view displays historical `risk_assessment_*` actions with the new `job_risk_assessment_*` labels, while preserving the stored historical rows.

## Branding placement decision

The user's proposed placements were retained. A separately cropped compact Vision 2030 asset is used in the fixed navigation because the full artwork's long strapline would make the sticky header much taller. The complete supplied artwork is used on the sign-in panel. All images use intrinsic aspect ratios and `object-fit: contain`; none is stretched.

## Deployment and data safety

- The full ZIP is for fresh/test deployment and includes the unchanged v3.8 seeded `data/` tree.
- The code-only ZIP is the correct GitHub/DDF update and excludes `data/`, `registers/`, and `reference_sources/`.
- No CSV, JSON or XLSX runtime file changed versus v3.8.0.
- Nothing must be copied into or edited under live `~/opera_data` for v3.9.0.
- Keep `OPERA_DATA_DIR=~/opera_data` (or `OPERAX_DATA_DIR=~/opera_data`) when restarting the DDF service.
- The embedded local branding works both at Streamlit Cloud root and behind the nginx `/operationaldashboard/` path.

## Verification

- `pytest -q`: **54 passed**.
- `python -m py_compile app.py opera/*.py scripts/*.py`: passed.
- Every authenticated page, including Process Optimization and Job Risk Assessment, is covered by the retained Streamlit AppTest route smoke test.
- Production Cement mapping template generation was verified with the combined equipment/template Field Catalogue and all four controlled validation lists.
