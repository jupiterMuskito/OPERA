from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from opera import dashboard


BUSINESS_UNITS = ["cement", "refinery", "fertilizer", "nascon", "bu5", "bu6", "bu7", "bu8", "bu9"]
SAMPLE_FIELDS = {
    "cement": ["DP1", "DP8", "L6", "F3", "CF6"],
    "refinery": ["DP2", "DP11", "L20", "F17", "CF6"],
    "fertilizer": ["DP9", "DP14", "L7", "F7", "CF5"],
    "nascon": ["DP8", "DP14", "L4", "F1", "CF8"],
}


def display_text(value: object) -> str:
    """Apply current data-type terminology to report narratives only."""
    return str(value).replace("DCS", "Digital Data")


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_None._"
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in frame.fillna("").astype(str).itertuples(index=False, name=None):
        lines.append("| " + " | ".join(value.replace("|", "\\|").replace("\n", " ") for value in row) + " |")
    return "\n".join(lines)


def build_report() -> str:
    tables: dict[str, pd.DataFrame] = {bu: dashboard.field_mapping_table(bu) for bu in BUSINESS_UNITS}
    all_counts: list[dict[str, object]] = []
    named_counts: list[dict[str, object]] = []
    review_rows: list[dict[str, str]] = []
    placeholder_rows: list[dict[str, object]] = []
    sample_rows: list[dict[str, str]] = []

    for bu, mappings in tables.items():
        for template_id, template_name in dashboard.MAPPING_TEMPLATES.items():
            all_counts.append(
                {
                    "Business unit": bu,
                    "Template": template_name,
                    "All mapped fields": int(mappings["_template_ids"].map(lambda values: template_id in values).sum()),
                }
            )
            named = mappings[mappings["Field Type"] != "Placeholder"]
            named_counts.append(
                {
                    "Business unit": bu,
                    "Template": template_name,
                    "Named fields": int(named["_template_ids"].map(lambda values: template_id in values).sum()),
                }
            )
        named_review = mappings[(mappings["Field Type"] != "Placeholder") & (mappings["Confidence"] == "Review")]
        for _, row in named_review.iterrows():
            review_rows.append(
                {
                    "Business unit": bu,
                    "Field ID": str(row["Field ID"]),
                    "Data field": str(row["Data Field"]),
                    "Equipment IDs": str(row["Equipment IDs"]),
                    "Mapping basis": display_text(row["Mapping Basis"]),
                }
            )
        placeholders = mappings[mappings["Field Type"] == "Placeholder"]
        for source, group in placeholders.groupby("Source", sort=False):
            placeholder_rows.append(
                {
                    "Business unit": bu,
                    "Source group": source,
                    "Review placeholders": len(group),
                    "Basis": "Default placeholder mapping – review when field is named.",
                }
            )
        for field_id in SAMPLE_FIELDS.get(bu, []):
            row = mappings[mappings["Field ID"] == field_id].iloc[0]
            sample_rows.append(
                {
                    "BU": bu,
                    "Field": f"{field_id} — {row['Data Field']}",
                    "Equipment": row["Equipment Names"],
                    "Templates": row["Dashboard Templates"],
                    "Reason": display_text(row["Mapping Basis"]),
                    "Confidence": row["Confidence"],
                }
            )

    all_count_frame = pd.DataFrame(all_counts).pivot(index="Business unit", columns="Template", values="All mapped fields").reset_index()
    named_count_frame = pd.DataFrame(named_counts).pivot(index="Business unit", columns="Template", values="Named fields").reset_index()
    review_frame = pd.DataFrame(review_rows)
    placeholder_frame = pd.DataFrame(placeholder_rows)
    sample_frame = pd.DataFrame(sample_rows)
    total_named = sum(int((frame["Field Type"] != "Placeholder").sum()) for frame in tables.values())
    total_placeholder = sum(int((frame["Field Type"] == "Placeholder").sum()) for frame in tables.values())

    return f"""# OPERA-X v3.9.0 — Engineering Mapping Quality Report

## Scope and method

The default mapping was rebuilt from field names, units, formulas, physical process context and the registered equipment inventory. Named DP, F and L fields use curated field-by-field engineering rules. Calculated fields inherit the union of equipment mapped to their formula inputs. Placeholder fields use a source-aware SPARE assignment and are explicitly marked for review when named. No named field uses round-robin, index-based or random assignment.

- Named/calculated fields reviewed: **{total_named:,}**
- Placeholder fields retained: **{total_placeholder:,}**
- Named fields marked **Review**: **{len(review_frame):,}**
- Placeholder fields marked **Review**: **{total_placeholder:,}** (grouped below because listing all IDs would add {total_placeholder:,} low-value rows)

## Mapping counts by BU and dashboard template

Counts are field-to-template relationships; a field is counted in each template where it genuinely serves more than one use.

### Named and calculated fields

{markdown_table(named_count_frame)}

### Complete database, including placeholders

{markdown_table(all_count_frame)}

## Named mappings marked Review

These are not silent guesses. Most indicate that the physically correct equipment or sample point is absent from the current register and the field has been assigned to a clearly identified SPARE record or a documented shared process scope.

{markdown_table(review_frame)}

## Placeholder Review summary

{markdown_table(placeholder_frame)}

## Twenty named mappings for spot-checking

{markdown_table(sample_frame)}

## Calculated-field check

The 32 packaged calculated fields were checked against their formulas. Misnamed or dimensionally inconsistent v3.5.0 defaults were corrected in the four configured BUs. Each calculated mapping now inherits equipment from its actual formula inputs, and its database basis records those input IDs and formula.

## Instrument Check pairs recorded

The Excel databases record the physically comparable Raw Field Data/Digital Data pairs for Refinery (Butamer feed flow, reactor temperatures and pressures), Fertilizer (urea-reactor pressure) and NASCON (salt-evaporator temperature and vacuum-pan pressure). Cement has no defensible same-point F/DP pair in the current 60-field sample, so none was fabricated.
"""


if __name__ == "__main__":
    target = ROOT / "MAPPING_QUALITY_REPORT.md"
    target.write_text(build_report(), encoding="utf-8")
    print(target)
