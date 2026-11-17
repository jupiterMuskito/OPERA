# OPERA-X v3.6.0 — Runtime Data Overwrite Warning

**Use the code-only update ZIP for an existing deployment.** The full deployment ZIP contains the 174 CSV files listed below plus nine runtime `field_mappings.xlsx` databases. Copying it over a live deployment can replace passwords/users, entered readings, Excel mappings, events, flags, lessons, notifications, risk-assessment history, audit history, equipment configuration, calculated fields, and field metadata.

The code-only ZIP contains no `data/` files. On first use it creates `field_mappings.xlsx` from the engineering baseline and migrates any existing `field_mappings.json` overrides without replacing other runtime files.

The full v3.6.0 package deliberately changes 13 CSVs versus v3.5.0: all nine BU `equipment.csv` files activate SPARE records for placeholder mapping, and the four configured `calculated_fields.csv` files correct formula/name/target mismatches. It also adds the nine mapping databases below. Preserve any legacy `field_mappings.json` until the first v3.6.0 migration has completed successfully.

## Added Excel mapping databases (9 files)

- `data/business_units/bu5/field_mappings.xlsx`
- `data/business_units/bu6/field_mappings.xlsx`
- `data/business_units/bu7/field_mappings.xlsx`
- `data/business_units/bu8/field_mappings.xlsx`
- `data/business_units/bu9/field_mappings.xlsx`
- `data/business_units/cement/field_mappings.xlsx`
- `data/business_units/fertilizer/field_mappings.xlsx`
- `data/business_units/nascon/field_mappings.xlsx`
- `data/business_units/refinery/field_mappings.xlsx`

These files are live runtime state after deployment. Do not overwrite them with the full package after Administrators have saved single-field or bulk updates.

## CSVs changed versus v3.5.0 (13 files)

- `data/business_units/bu5/equipment.csv`
- `data/business_units/bu6/equipment.csv`
- `data/business_units/bu7/equipment.csv`
- `data/business_units/bu8/equipment.csv`
- `data/business_units/bu9/equipment.csv`
- `data/business_units/cement/equipment.csv`
- `data/business_units/fertilizer/equipment.csv`
- `data/business_units/nascon/equipment.csv`
- `data/business_units/refinery/equipment.csv`
- `data/business_units/cement/calculated_fields.csv`
- `data/business_units/fertilizer/calculated_fields.csv`
- `data/business_units/nascon/calculated_fields.csv`
- `data/business_units/refinery/calculated_fields.csv`

## User and shared state (2 files)

- `data/shared/users.csv`
- `data/business_units/shared/audit_log.csv`

## Per-business-unit configuration and logs (82 files)

- `data/business_units/bu5/audit_log.csv`
- `data/business_units/bu5/calculated_fields.csv`
- `data/business_units/bu5/equipment.csv`
- `data/business_units/bu5/events.csv`
- `data/business_units/bu5/fields.csv`
- `data/business_units/bu5/flags.csv`
- `data/business_units/bu5/lessons.csv`
- `data/business_units/bu5/notifications.csv`
- `data/business_units/bu5/risk_assessments.csv`
- `data/business_units/bu6/audit_log.csv`
- `data/business_units/bu6/calculated_fields.csv`
- `data/business_units/bu6/equipment.csv`
- `data/business_units/bu6/events.csv`
- `data/business_units/bu6/fields.csv`
- `data/business_units/bu6/flags.csv`
- `data/business_units/bu6/lessons.csv`
- `data/business_units/bu6/notifications.csv`
- `data/business_units/bu6/risk_assessments.csv`
- `data/business_units/bu7/audit_log.csv`
- `data/business_units/bu7/calculated_fields.csv`
- `data/business_units/bu7/equipment.csv`
- `data/business_units/bu7/events.csv`
- `data/business_units/bu7/fields.csv`
- `data/business_units/bu7/flags.csv`
- `data/business_units/bu7/lessons.csv`
- `data/business_units/bu7/notifications.csv`
- `data/business_units/bu7/risk_assessments.csv`
- `data/business_units/bu8/audit_log.csv`
- `data/business_units/bu8/calculated_fields.csv`
- `data/business_units/bu8/equipment.csv`
- `data/business_units/bu8/events.csv`
- `data/business_units/bu8/fields.csv`
- `data/business_units/bu8/flags.csv`
- `data/business_units/bu8/lessons.csv`
- `data/business_units/bu8/notifications.csv`
- `data/business_units/bu8/risk_assessments.csv`
- `data/business_units/bu9/audit_log.csv`
- `data/business_units/bu9/calculated_fields.csv`
- `data/business_units/bu9/equipment.csv`
- `data/business_units/bu9/events.csv`
- `data/business_units/bu9/fields.csv`
- `data/business_units/bu9/flags.csv`
- `data/business_units/bu9/lessons.csv`
- `data/business_units/bu9/notifications.csv`
- `data/business_units/bu9/risk_assessments.csv`
- `data/business_units/cement/audit_log.csv`
- `data/business_units/cement/calculated_fields.csv`
- `data/business_units/cement/equipment.csv`
- `data/business_units/cement/events.csv`
- `data/business_units/cement/fields.csv`
- `data/business_units/cement/flags.csv`
- `data/business_units/cement/lessons.csv`
- `data/business_units/cement/notifications.csv`
- `data/business_units/cement/risk_assessments.csv`
- `data/business_units/fertilizer/audit_log.csv`
- `data/business_units/fertilizer/calculated_fields.csv`
- `data/business_units/fertilizer/equipment.csv`
- `data/business_units/fertilizer/events.csv`
- `data/business_units/fertilizer/fields.csv`
- `data/business_units/fertilizer/flags.csv`
- `data/business_units/fertilizer/lessons.csv`
- `data/business_units/fertilizer/notifications.csv`
- `data/business_units/fertilizer/risk_assessments.csv`
- `data/business_units/nascon/audit_log.csv`
- `data/business_units/nascon/calculated_fields.csv`
- `data/business_units/nascon/equipment.csv`
- `data/business_units/nascon/events.csv`
- `data/business_units/nascon/fields.csv`
- `data/business_units/nascon/flags.csv`
- `data/business_units/nascon/lessons.csv`
- `data/business_units/nascon/notifications.csv`
- `data/business_units/nascon/risk_assessments.csv`
- `data/business_units/refinery/audit_log.csv`
- `data/business_units/refinery/calculated_fields.csv`
- `data/business_units/refinery/equipment.csv`
- `data/business_units/refinery/events.csv`
- `data/business_units/refinery/fields.csv`
- `data/business_units/refinery/flags.csv`
- `data/business_units/refinery/lessons.csv`
- `data/business_units/refinery/notifications.csv`
- `data/business_units/refinery/risk_assessments.csv`
- `data/shared/business_units.csv`

## Operational input data (90 files)

- `data/business_units/bu5/inputs/dcs.csv`
- `data/business_units/bu5/inputs/field.csv`
- `data/business_units/bu5/inputs/lab.csv`
- `data/business_units/bu5/inputs/ta.csv`
- `data/business_units/bu5/inputs/tb.csv`
- `data/business_units/bu5/inputs/tc.csv`
- `data/business_units/bu5/inputs/td.csv`
- `data/business_units/bu5/inputs/te.csv`
- `data/business_units/bu5/inputs/tf.csv`
- `data/business_units/bu5/inputs/tg.csv`
- `data/business_units/bu6/inputs/dcs.csv`
- `data/business_units/bu6/inputs/field.csv`
- `data/business_units/bu6/inputs/lab.csv`
- `data/business_units/bu6/inputs/ta.csv`
- `data/business_units/bu6/inputs/tb.csv`
- `data/business_units/bu6/inputs/tc.csv`
- `data/business_units/bu6/inputs/td.csv`
- `data/business_units/bu6/inputs/te.csv`
- `data/business_units/bu6/inputs/tf.csv`
- `data/business_units/bu6/inputs/tg.csv`
- `data/business_units/bu7/inputs/dcs.csv`
- `data/business_units/bu7/inputs/field.csv`
- `data/business_units/bu7/inputs/lab.csv`
- `data/business_units/bu7/inputs/ta.csv`
- `data/business_units/bu7/inputs/tb.csv`
- `data/business_units/bu7/inputs/tc.csv`
- `data/business_units/bu7/inputs/td.csv`
- `data/business_units/bu7/inputs/te.csv`
- `data/business_units/bu7/inputs/tf.csv`
- `data/business_units/bu7/inputs/tg.csv`
- `data/business_units/bu8/inputs/dcs.csv`
- `data/business_units/bu8/inputs/field.csv`
- `data/business_units/bu8/inputs/lab.csv`
- `data/business_units/bu8/inputs/ta.csv`
- `data/business_units/bu8/inputs/tb.csv`
- `data/business_units/bu8/inputs/tc.csv`
- `data/business_units/bu8/inputs/td.csv`
- `data/business_units/bu8/inputs/te.csv`
- `data/business_units/bu8/inputs/tf.csv`
- `data/business_units/bu8/inputs/tg.csv`
- `data/business_units/bu9/inputs/dcs.csv`
- `data/business_units/bu9/inputs/field.csv`
- `data/business_units/bu9/inputs/lab.csv`
- `data/business_units/bu9/inputs/ta.csv`
- `data/business_units/bu9/inputs/tb.csv`
- `data/business_units/bu9/inputs/tc.csv`
- `data/business_units/bu9/inputs/td.csv`
- `data/business_units/bu9/inputs/te.csv`
- `data/business_units/bu9/inputs/tf.csv`
- `data/business_units/bu9/inputs/tg.csv`
- `data/business_units/cement/inputs/dcs.csv`
- `data/business_units/cement/inputs/field.csv`
- `data/business_units/cement/inputs/lab.csv`
- `data/business_units/cement/inputs/ta.csv`
- `data/business_units/cement/inputs/tb.csv`
- `data/business_units/cement/inputs/tc.csv`
- `data/business_units/cement/inputs/td.csv`
- `data/business_units/cement/inputs/te.csv`
- `data/business_units/cement/inputs/tf.csv`
- `data/business_units/cement/inputs/tg.csv`
- `data/business_units/fertilizer/inputs/dcs.csv`
- `data/business_units/fertilizer/inputs/field.csv`
- `data/business_units/fertilizer/inputs/lab.csv`
- `data/business_units/fertilizer/inputs/ta.csv`
- `data/business_units/fertilizer/inputs/tb.csv`
- `data/business_units/fertilizer/inputs/tc.csv`
- `data/business_units/fertilizer/inputs/td.csv`
- `data/business_units/fertilizer/inputs/te.csv`
- `data/business_units/fertilizer/inputs/tf.csv`
- `data/business_units/fertilizer/inputs/tg.csv`
- `data/business_units/nascon/inputs/dcs.csv`
- `data/business_units/nascon/inputs/field.csv`
- `data/business_units/nascon/inputs/lab.csv`
- `data/business_units/nascon/inputs/ta.csv`
- `data/business_units/nascon/inputs/tb.csv`
- `data/business_units/nascon/inputs/tc.csv`
- `data/business_units/nascon/inputs/td.csv`
- `data/business_units/nascon/inputs/te.csv`
- `data/business_units/nascon/inputs/tf.csv`
- `data/business_units/nascon/inputs/tg.csv`
- `data/business_units/refinery/inputs/dcs.csv`
- `data/business_units/refinery/inputs/field.csv`
- `data/business_units/refinery/inputs/lab.csv`
- `data/business_units/refinery/inputs/ta.csv`
- `data/business_units/refinery/inputs/tb.csv`
- `data/business_units/refinery/inputs/tc.csv`
- `data/business_units/refinery/inputs/td.csv`
- `data/business_units/refinery/inputs/te.csv`
- `data/business_units/refinery/inputs/tf.csv`
- `data/business_units/refinery/inputs/tg.csv`
