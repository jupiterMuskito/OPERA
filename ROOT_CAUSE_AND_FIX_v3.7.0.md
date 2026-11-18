# OPERA-X v3.7.0 — Root Cause and Fix

## Reported failure

An Admin could rename/activate a placeholder field, map it to Plant Performance or Process Performance, and still not see a chart.

## Root cause

The mapping and the chart-panel configuration were two separate paths:

1. `field_mappings.xlsx` controlled whether a field was eligible for a selected equipment/template context.
2. `dashboard_templates.json` separately supplied only 2–4 default `chart_fields` in v3.6.0.
3. The chart renderer created controls only for fields already present in the filtered long-form data.
4. A newly activated placeholder often had no source values yet. Even when it was mapped correctly, it was outside the template's short panel list or removed before the selector was built.
5. Wide source files (1,008 columns) were re-read on each rerun, and the 10,000-row Excel mapping database was repeatedly materialised, making Admin-to-dashboard verification slow.

The mapping save itself was not lost. The dashboard consumption path did not fully expose the new mapping and could not distinguish “mapped but no readings” from “not configured.”

## Fix

- Every dashboard template now has 12 default chart fields and 12 default table fields.
- Split-axis dashboards retain all 12 configured panels and render four at a time in a two-column panel set; each panel's field remains user-selectable.
- Plant and Equipment chart selectors are built from the current mapping catalogue, not only fields that already have values.
- A mapped field with no values now produces an explicit “mapped but no readings in the selected period” panel instead of disappearing.
- A field with saved values appears immediately after the Admin field, mapping and template saves; no process restart is required.
- Newly created/activated fields missing from an existing mapping workbook are reconciled into the Excel database automatically, preserving existing Admin overrides.
- CSV and JSON reads are signature-cached by path, modification time and size. Atomic writes invalidate caches, so Admin changes remain immediate.
- The authoritative Excel mapping database now has a compressed derived runtime cache. Any workbook replacement or Admin save changes the signature and rebuilds the cache.

## Verified end-to-end case

The automated test performs the reported sequence in one process:

1. Rename and activate placeholder `DP2` with UOM, range and target.
2. Map `DP2` to equipment `EQ1` and Plant/Process Performance.
3. Put `DP2` into the Plant Performance chart-panel defaults.
4. Save a validated DCS value.
5. Verify the registry metadata, mapping, template, source value and 12-panel defaults immediately, without restarting Streamlit.

Result: PASS.
