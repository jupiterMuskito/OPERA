from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.workbook.defined_name import DefinedName

from . import engineering_mapping, storage

BLUE = "#1857C9"
RED = "#CF3430"
CHART_COLORS = [BLUE, "#2F7DE1", "#6B8FD8", "#E8964A", RED, "#3B9B7A", "#7A5AF8", "#2AA5A0"]
CHART_TYPES = ["Line", "Area", "Bar", "Scatter", "Box Plot"]
AXIS_MODES = ["Split Into Individual Axes", "Place on the Same Axis"]
TREND_RULES = {
    "1 Hour": "1h",
    "6 Hours": "6h",
    "12 Hours": "12h",
    "Daily": "1D",
    "Weekly": "1W",
    "Monthly": "ME",
    "Yearly": "YE",
}

EQUIPMENT_FIELD_KEYWORDS = {
    "pump": ["flow", "pressure", "vibration", "bearing", "seal", "current", "power"],
    "heater": ["temperature", "pressure", "flow", "fuel", "oxygen", "tube skin"],
    "furnace": ["temperature", "pressure", "flow", "fuel", "oxygen", "tube skin"],
    "reformer": ["temperature", "pressure", "flow", "fuel", "tube skin"],
    "reactor": ["temperature", "pressure", "level", "flow", "ratio", "differential"],
    "compressor": ["pressure", "vibration", "bearing", "flow", "speed", "temperature"],
    "fan": ["pressure", "vibration", "bearing", "flow", "speed", "temperature"],
    "mill": ["feed", "power", "vibration", "bearing", "differential", "outlet", "speed"],
    "crusher": ["feed", "power", "vibration", "bearing", "current", "speed"],
    "cooler": ["temperature", "fan", "grate", "pressure", "vibration"],
    "dryer": ["temperature", "moisture", "differential", "pressure", "vibration"],
    "column": ["temperature", "pressure", "level", "reflux", "flow"],
    "stripper": ["temperature", "pressure", "level", "flow", "vibration"],
    "centrifuge": ["speed", "vibration", "bearing", "temperature"],
    "granulator": ["temperature", "feed", "vibration", "size"],
    "packing": ["packing", "rate", "air pressure", "dust"],
    "bagging": ["bagging", "rate", "air pressure", "dust"],
    "evaporator": ["temperature", "vacuum", "pressure", "brix", "flow"],
    "conveyor": ["belt", "drift", "bearing", "temperature"],
    "elevator": ["bearing", "temperature", "boot"],
    "silo": ["level", "dust", "temperature"],
    "kiln": ["feed", "speed", "oxygen", "temperature", "pressure", "vibration", "shell"],
    "filter": ["dust", "pressure", "differential", "flow", "temperature"],
    "tower": ["temperature", "pressure", "oxygen", "flow", "differential"],
}

MAPPING_TEMPLATES = {
    "plant-performance": "Plant Performance",
    "condition-monitoring": "Condition Monitoring",
    "process-performance": "Process Performance",
    "quality-compliance": "Quality and Compliance",
    "reliability": "Reliability",
}

SOURCE_GROUPS = {
    "DCS": "DCS",
    "Field": "Field",
    "Lab": "QAQC",
    "TA": "Others",
    "TB": "Others",
    "TC": "Others",
    "TD": "Others",
    "TE": "Others",
    "TF": "Others",
    "TG": "Others",
    "Calculated": "Calculated",
}


def default_templates() -> dict[str, list[dict[str, Any]]]:
    return {
        "Plant Overview": [
            {
                "id": "plant-performance",
                "name": "Plant Performance",
                "chart_fields": ["DP1", "DP5", "L6", "F1"],
                "table_fields": ["DP1", "DP5", "DP8", "L6", "L17", "F1"],
                "chart_type": "Line",
                "period_mode": "Selected Period",
            }
        ],
        "Equipment Overview": [
            {"id": "condition-monitoring", "name": "Condition Monitoring", "chart_fields": ["F1", "F3", "F4", "DP2"], "table_fields": ["F1", "F3", "F4", "DP2"], "equipment_fields": {}, "chart_type": "Line", "period_mode": "Selected Period"},
            {"id": "process-performance", "name": "Process Performance", "chart_fields": ["DP1", "DP2", "DP5", "DP20"], "table_fields": ["DP1", "DP2", "DP5", "DP20"], "equipment_fields": {}, "chart_type": "Area", "period_mode": "Selected Period"},
            {"id": "quality-compliance", "name": "Quality and Compliance", "chart_fields": ["L1", "L6", "L12", "L17"], "table_fields": ["L1", "L6", "L12", "L17"], "equipment_fields": {}, "chart_type": "Box Plot", "period_mode": "Selected Period"},
            {"id": "reliability", "name": "Reliability", "chart_fields": ["F3", "F4", "F5", "F7"], "table_fields": ["F3", "F4", "F5", "F7"], "equipment_fields": {}, "chart_type": "Scatter", "period_mode": "Selected Period"},
        ],
        "Operations Dashboard": [
            {"id": "current", "name": "Current", "kpi_fields": ["CF1", "CF2", "CF3", "CF4"], "chart_fields": ["CF1", "CF2", "CF3", "CF4"], "table_fields": ["CF1", "CF2", "CF3", "CF4", "CF5", "CF6"], "chart_type": "Line", "period_mode": "Current"},
            {"id": "period-total", "name": "Period Total", "kpi_fields": ["CF1", "CF2", "CF3", "CF4", "CF5", "CF6", "CF7", "CF8"], "chart_fields": ["CF1", "CF4", "CF6", "CF8"], "table_fields": ["CF1", "CF2", "CF3", "CF4", "CF5", "CF6", "CF7", "CF8"], "chart_type": "Bar", "period_mode": "Period Total"},
            {"id": "month-to-date", "name": "Month-to-Date", "kpi_fields": ["CF1", "CF2", "CF4", "CF5", "CF8"], "chart_fields": ["CF1", "CF2", "CF4", "CF8"], "table_fields": ["CF1", "CF2", "CF4", "CF5", "CF8"], "chart_type": "Area", "period_mode": "Month-to-Date"},
            {"id": "year-to-date", "name": "Year-to-Date", "kpi_fields": ["CF1", "CF2", "CF4", "CF5", "CF8"], "chart_fields": ["CF1", "CF2", "CF4", "CF8"], "table_fields": ["CF1", "CF2", "CF4", "CF5", "CF8"], "chart_type": "Line", "period_mode": "Year-to-Date"},
            {"id": "quality", "name": "Quality", "kpi_fields": ["CF4", "CF7"], "chart_fields": ["CF4", "CF7"], "table_fields": ["CF4", "CF7"], "chart_type": "Box Plot", "period_mode": "Selected Period"},
            {"id": "reliability", "name": "Reliability", "kpi_fields": ["CF5", "CF6"], "chart_fields": ["CF5", "CF6"], "table_fields": ["CF5", "CF6"], "chart_type": "Scatter", "period_mode": "Selected Period"},
        ],
    }


def templates_path(bu: str):
    return storage.bu_dir(bu) / "dashboard_templates.json"


def load_templates(bu: str) -> dict[str, list[dict[str, Any]]]:
    defaults = default_templates()
    saved = storage.json_setting(templates_path(bu), {})
    if not isinstance(saved, dict):
        return defaults
    result: dict[str, list[dict[str, Any]]] = {}
    for module, module_defaults in defaults.items():
        value = saved.get(module)
        result[module] = value if isinstance(value, list) and value else module_defaults
        for template in result[module]:
            if template.get("id") == "quality-compliance":
                template["name"] = "Quality and Compliance"
    return result


def save_templates(bu: str, templates: dict[str, list[dict[str, Any]]]) -> None:
    storage.save_json(templates_path(bu), templates)


MAPPING_COLUMNS = [
    "Field ID",
    "Data Field",
    "Source",
    "Status",
    "Field Type",
    "Equipment IDs",
    "Template IDs",
    "Instrument Check Pair IDs",
    "Mapping Basis",
    "Confidence",
    "Mapping Type",
]


def field_mappings_path(bu: str):
    """Return the Excel mapping database used by OPERA-X at runtime."""
    return storage.bu_dir(bu) / "field_mappings.xlsx"


def _legacy_field_mappings_path(bu: str):
    """Return the pre-v3.6 JSON override path, used only during migration."""
    return storage.bu_dir(bu) / "field_mappings.json"


def _split_mapping_ids(value: Any) -> list[str]:
    return list(dict.fromkeys(item.strip() for item in str(value or "").replace(",", ";").split(";") if item.strip()))


def _mapping_record(
    equipment_ids: list[str],
    template_ids: list[str],
    mapping_type: str = "Computed Default",
    mapping_basis: str = "",
    confidence: str = "Review",
    instrument_check_pairs: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "equipment_ids": list(dict.fromkeys(str(item).strip() for item in equipment_ids if str(item).strip())),
        "template_ids": list(dict.fromkeys(str(item).strip() for item in template_ids if str(item).strip())),
        "instrument_check_pairs": list(dict.fromkeys(str(item).strip() for item in (instrument_check_pairs or []) if str(item).strip())),
        "mapping_basis": str(mapping_basis).strip(),
        "confidence": str(confidence).strip().title() if str(confidence).strip().title() in {"High", "Medium", "Review"} else "Review",
        "mapping_type": "Admin Override" if str(mapping_type) == "Admin Override" else "Computed Default",
    }


def _records_from_mapping_frame(frame: pd.DataFrame) -> dict[str, dict[str, Any]]:
    required = {"Field ID", "Equipment IDs", "Template IDs"}
    if not required.issubset(frame.columns):
        raise ValueError("The mapping database is missing required columns: Field ID, Equipment IDs and Template IDs.")
    records: dict[str, dict[str, Any]] = {}
    for row in frame.fillna("").to_dict("records"):
        field_id = str(row.get("Field ID", "")).strip()
        if not field_id:
            continue
        equipment_ids = _split_mapping_ids(row.get("Equipment IDs", ""))
        template_ids = _split_mapping_ids(row.get("Template IDs", ""))
        if not equipment_ids or not template_ids:
            raise ValueError(f"Field {field_id} must have at least one Equipment ID and one Template ID in the mapping database.")
        records[field_id] = _mapping_record(
            equipment_ids,
            template_ids,
            str(row.get("Mapping Type", "Computed Default")),
            str(row.get("Mapping Basis", "")),
            str(row.get("Confidence", "Review")),
            _split_mapping_ids(row.get("Instrument Check Pair IDs", "")),
        )
    return records


@lru_cache(maxsize=32)
def _read_mapping_database_cached(path_text: str, modified_ns: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    del modified_ns  # The modification time is part of the cache key.
    sheets = pd.read_excel(path_text, sheet_name=["Field Mappings", "Default Mappings"], dtype=str, keep_default_na=False)
    return sheets["Field Mappings"], sheets["Default Mappings"]


def _read_mapping_database(bu: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    path = ensure_mapping_database(bu)
    try:
        effective, defaults = _read_mapping_database_cached(str(path), path.stat().st_mtime_ns)
    except Exception as exc:
        raise ValueError(f"The Excel mapping database for {bu} could not be read: {exc}") from exc
    return effective.copy(), defaults.copy()


def _style_mapping_workbook(workbook: Workbook) -> None:
    workbook.properties.creator = "OPERA-X"
    workbook.properties.lastModifiedBy = "OPERA-X"
    normal = workbook._named_styles["Normal"]
    normal.font = Font(name="Arial", size=10)
    header_fill = PatternFill("solid", fgColor="D9E8FB")
    body_font = Font(name="Arial", size=10)
    for sheet in workbook.worksheets:
        sheet.freeze_panes = "A2" if sheet.max_row > 1 else None
        if sheet.max_row and sheet.max_column:
            sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.font = Font(name="Arial", size=10, bold=True, color="123A73")
            cell.fill = header_fill
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.font = body_font
        for column in sheet.columns:
            letter = column[0].column_letter
            sample = list(column[:200])
            sheet.column_dimensions[letter].width = min(42, max(12, max((len(str(cell.value or "")) for cell in sample), default=10) + 2))


def _mapping_database_frames(
    bu: str,
    effective: dict[str, dict[str, Any]],
    defaults: dict[str, dict[str, Any]],
) -> dict[str, pd.DataFrame]:
    catalog = field_catalog(bu)

    def make_rows(records: dict[str, dict[str, Any]]) -> pd.DataFrame:
        rows: list[dict[str, Any]] = []
        for field in catalog.itertuples(index=False):
            field_id = str(field.field_id)
            record = records.get(field_id)
            if not record:
                continue
            rows.append(
                {
                    "Field ID": field_id,
                    "Data Field": str(field.field_name),
                    "Source": str(field.source),
                    "Status": str(field.status),
                    "Field Type": str(field.field_type),
                    "Equipment IDs": "; ".join(record["equipment_ids"]),
                    "Template IDs": "; ".join(record["template_ids"]),
                    "Instrument Check Pair IDs": "; ".join(record.get("instrument_check_pairs", [])),
                    "Mapping Basis": str(record.get("mapping_basis", "")),
                    "Confidence": str(record.get("confidence", "Review")),
                    "Mapping Type": str(record.get("mapping_type", "Computed Default")),
                }
            )
        return pd.DataFrame(rows, columns=MAPPING_COLUMNS)

    equipment = _usable_mapping_equipment(bu)
    equipment_columns = [column for column in ["equipment_id", "equipment_name", "plant", "unit_section", "equipment_type", "active"] if column in equipment]
    template_list = pd.DataFrame(
        [{"Template ID": template_id, "Dashboard Template": name} for template_id, name in MAPPING_TEMPLATES.items()]
    )
    guide = pd.DataFrame(
        [
            {"Item": "Runtime source", "Explanation": "OPERA-X reads effective equipment and dashboard-template mappings from the Field Mappings sheet in this Excel database."},
            {"Item": "Controlled updates", "Explanation": "Use the Admin page's Excel update template and bulk upload. Do not directly replace this runtime file while the app is running."},
            {"Item": "Computed Default", "Explanation": "The baseline mapping stored in the Default Mappings sheet and restored by Reset to Computed Default."},
            {"Item": "Admin Override", "Explanation": "A mapping saved in the Admin UI or applied by an audited bulk upload."},
            {"Item": "Multiple values", "Explanation": "Equipment IDs and Template IDs are separated with semicolons."},
            {"Item": "Mapping Basis", "Explanation": "Plain-language engineering reason for the equipment and dashboard-template assignment."},
            {"Item": "Confidence", "Explanation": "High, Medium or Review. Filter Review first; it normally indicates missing equipment-register detail or an unconfirmed sample point."},
            {"Item": "Instrument Check Pair IDs", "Explanation": "A same-point DCS/Field pair that Instrument Check uses as its default comparison."},
        ]
    )
    return {
        "Field Mappings": make_rows(effective),
        "Default Mappings": make_rows(defaults),
        "Equipment List": equipment[equipment_columns].copy() if equipment_columns else pd.DataFrame(),
        "Template List": template_list,
        "Guide": guide,
    }


def _mapping_workbook_bytes(frames: dict[str, pd.DataFrame]) -> bytes:
    workbook = Workbook()
    workbook.remove(workbook.active)
    for name, frame in frames.items():
        sheet = workbook.create_sheet(name[:31])
        sheet.append(list(frame.columns))
        for row in frame.itertuples(index=False, name=None):
            sheet.append(list(row))
    _style_mapping_workbook(workbook)
    out = BytesIO()
    workbook.save(out)
    return out.getvalue()


def _write_mapping_database(
    bu: str,
    effective: dict[str, dict[str, Any]],
    defaults: dict[str, dict[str, Any]],
) -> None:
    storage.atomic_write_bytes(field_mappings_path(bu), _mapping_workbook_bytes(_mapping_database_frames(bu, effective, defaults)))
    _read_mapping_database_cached.cache_clear()


def _seed_field_mapping_records(bu: str) -> dict[str, dict[str, Any]]:
    """Build the one-time engineering baseline that is then persisted in Excel."""
    catalog = field_catalog(bu)
    equipment = storage.equipment(bu)
    calculated = storage.read_csv(storage.bu_dir(bu) / "calculated_fields.csv")
    return engineering_mapping.build_engineering_defaults(bu, catalog, equipment, calculated)


def ensure_mapping_database(bu: str):
    """Create the Excel database once, migrating any legacy JSON overrides."""
    path = field_mappings_path(bu)
    if path.exists() and path.stat().st_size:
        return path
    defaults = _seed_field_mapping_records(bu)
    effective = {field_id: _mapping_record(**record) for field_id, record in defaults.items()}
    legacy = storage.json_setting(_legacy_field_mappings_path(bu), {})
    if isinstance(legacy, dict):
        for field_id, record in legacy.items():
            if field_id in effective and isinstance(record, dict):
                equipment_ids = record.get("equipment_ids", effective[field_id]["equipment_ids"])
                template_ids = record.get("template_ids", effective[field_id]["template_ids"])
                if equipment_ids and template_ids:
                    baseline = effective[field_id]
                    effective[field_id] = _mapping_record(
                        equipment_ids,
                        template_ids,
                        "Admin Override",
                        "Migrated administrator override from the pre-v3.6 JSON mapping store; engineering basis requires review.",
                        "Review",
                        baseline.get("instrument_check_pairs", []),
                    )
    _write_mapping_database(bu, effective, defaults)
    return path


def load_effective_field_mappings(bu: str) -> dict[str, dict[str, Any]]:
    effective, _ = _read_mapping_database(bu)
    return _records_from_mapping_frame(effective)


def load_default_field_mappings(bu: str) -> dict[str, dict[str, Any]]:
    _, defaults = _read_mapping_database(bu)
    return _records_from_mapping_frame(defaults)


def load_field_mapping_overrides(bu: str) -> dict[str, dict[str, list[str]]]:
    """Return Admin overrides from the Excel database for compatibility callers."""
    return {
        field_id: {"equipment_ids": record["equipment_ids"], "template_ids": record["template_ids"]}
        for field_id, record in load_effective_field_mappings(bu).items()
        if record.get("mapping_type") == "Admin Override"
    }


def field_mapping(
    bu: str,
    field_id: str,
    source: str | None = None,
    field_name: str | None = None,
    equipment: pd.DataFrame | None = None,
) -> dict[str, list[str]]:
    del source, field_name, equipment
    record = load_effective_field_mappings(bu).get(str(field_id), {})
    mapped_equipment = record.get("equipment_ids", [])
    mapped_templates = record.get("template_ids", [])
    return {
        "equipment_ids": list(dict.fromkeys(str(item) for item in mapped_equipment if str(item))),
        "template_ids": list(dict.fromkeys(str(item) for item in mapped_templates if str(item))),
    }


def mapped_field_ids(
    bu: str,
    registry: pd.DataFrame,
    equipment_id: str | None = None,
    template_id: str | None = None,
) -> set[str]:
    """Filter a supplied field catalog by the current equipment/template context."""
    if registry.empty or (not equipment_id and not template_id):
        return set(registry.get("field_id", pd.Series(dtype=str)).astype(str))
    effective = load_effective_field_mappings(bu)
    # Preserve the public override hook used by integrations and older tests.
    # Runtime values still originate from the Excel database by default.
    overrides = load_field_mapping_overrides(bu)
    selected: set[str] = set()
    for row in registry.itertuples():
        field_id = str(row.field_id)
        mapping = effective.get(field_id, {"equipment_ids": [], "template_ids": []})
        override = overrides.get(field_id, {})
        equipment_ids = override.get("equipment_ids", mapping["equipment_ids"])
        template_ids = override.get("template_ids", mapping["template_ids"])
        if equipment_id and str(equipment_id) not in {str(item) for item in equipment_ids}:
            continue
        if template_id and str(template_id) not in {str(item) for item in template_ids}:
            continue
        selected.add(field_id)
    return selected


def save_field_mapping(bu: str, field_id: str, equipment_ids: list[str], template_ids: list[str]) -> None:
    if not equipment_ids or not template_ids:
        raise ValueError("Every data field must map to at least one equipment and one dashboard template.")
    effective = load_effective_field_mappings(bu)
    defaults = load_default_field_mappings(bu)
    if str(field_id) not in effective:
        raise ValueError(f"Unknown Field ID: {field_id}")
    current = effective[str(field_id)]
    effective[str(field_id)] = _mapping_record(
        equipment_ids,
        template_ids,
        "Admin Override",
        "Administrator override saved in OPERA-X; review against the engineering default and plant tag register.",
        "Review",
        current.get("instrument_check_pairs", []),
    )
    _write_mapping_database(bu, effective, defaults)


def reset_field_mapping(bu: str, field_id: str) -> bool:
    """Restore a field from the default sheet in the Excel mapping database."""
    effective = load_effective_field_mappings(bu)
    defaults = load_default_field_mappings(bu)
    current = effective.get(str(field_id))
    baseline = defaults.get(str(field_id))
    existed = bool(current and current.get("mapping_type") == "Admin Override")
    if existed and baseline:
        effective[str(field_id)] = _mapping_record(**baseline)
        _write_mapping_database(bu, effective, defaults)
    return existed


def field_catalog(bu: str) -> pd.DataFrame:
    """Return every input, placeholder and calculated field in one catalog."""
    inputs = storage.registry(bu).copy()
    if inputs.empty:
        inputs = pd.DataFrame(columns=["field_id", "field_name", "source", "active"])
    for column in ("field_id", "field_name", "source", "active"):
        if column not in inputs:
            inputs[column] = ""
    input_catalog = pd.DataFrame(
        {
            "field_id": inputs["field_id"].astype(str),
            "field_name": inputs["field_name"].astype(str),
            "source_key": inputs["source"].astype(str),
            "source": inputs["source"].astype(str).map(lambda value: SOURCE_GROUPS.get(value, "Others")),
            "status": inputs["active"].astype(str).str.lower().map(
                lambda value: "Active" if value == "true" else "Placeholder / Inactive"
            ),
            "field_type": inputs["active"].astype(str).str.lower().map(
                lambda value: "Input" if value == "true" else "Placeholder"
            ),
        }
    )

    calculated = storage.read_csv(storage.bu_dir(bu) / "calculated_fields.csv")
    if calculated.empty:
        calculated_catalog = pd.DataFrame(columns=input_catalog.columns)
    else:
        for column in ("field_id", "field_name", "status"):
            if column not in calculated:
                calculated[column] = ""
        calculated_catalog = pd.DataFrame(
            {
                "field_id": calculated["field_id"].astype(str),
                "field_name": calculated["field_name"].astype(str),
                "source_key": "Calculated",
                "source": "Calculated",
                "status": calculated["status"].astype(str).map(
                    lambda value: value.strip().title() or "Inactive"
                ),
                "field_type": "Calculated",
            }
        )
    return pd.concat([input_catalog, calculated_catalog], ignore_index=True)


def _usable_mapping_equipment(bu: str) -> pd.DataFrame:
    """Return every active named or spare record that can receive a mapping."""
    equipment = storage.equipment(bu).copy()
    if equipment.empty:
        return equipment
    if "active" in equipment:
        active = equipment["active"].astype(str).str.lower() == "true"
        placeholder = equipment.get("placeholder", pd.Series(index=equipment.index, dtype=str)).astype(str).str.lower() == "true"
        equipment = equipment[active | placeholder]
    return equipment


def field_mapping_table(bu: str) -> pd.DataFrame:
    """Materialise the complete effective mapping from the Excel database.

    Tuple-valued private columns (prefixed with ``_``) support exact UI filtering;
    the public columns are readable and ready for display or Excel export.
    """
    catalog = field_catalog(bu)
    equipment = _usable_mapping_equipment(bu)
    effective = load_effective_field_mappings(bu)
    equipment_by_id = (
        equipment.assign(equipment_id=equipment.get("equipment_id", pd.Series(dtype=str)).astype(str))
        .drop_duplicates("equipment_id")
        .set_index("equipment_id")
        if not equipment.empty and "equipment_id" in equipment
        else pd.DataFrame()
    )
    rows: list[dict[str, Any]] = []
    for field in catalog.itertuples(index=False):
        field_id = str(field.field_id)
        record = effective.get(field_id, {"equipment_ids": [], "template_ids": [], "mapping_type": "Computed Default"})
        equipment_ids = tuple(dict.fromkeys(str(item) for item in record.get("equipment_ids", []) if str(item)))
        template_ids = tuple(dict.fromkeys(str(item) for item in record.get("template_ids", []) if str(item)))
        equipment_names: list[str] = []
        plants: list[str] = []
        units: list[str] = []
        for equipment_id in equipment_ids:
            if equipment_by_id.empty or equipment_id not in equipment_by_id.index:
                equipment_names.append(equipment_id)
                continue
            equipment_record = equipment_by_id.loc[equipment_id]
            equipment_names.append(str(equipment_record.get("equipment_name", equipment_id)))
            plants.append(str(equipment_record.get("plant", "")))
            units.append(str(equipment_record.get("unit_section", "")))
        plants_tuple = tuple(dict.fromkeys(item for item in plants if item))
        units_tuple = tuple(dict.fromkeys(item for item in units if item))
        template_names = tuple(MAPPING_TEMPLATES.get(item, item) for item in template_ids)
        rows.append(
            {
                "Business Unit": bu,
                "Field ID": field_id,
                "Data Field": str(field.field_name),
                "Source": str(field.source),
                "Source Code": str(field.source_key),
                "Status": str(field.status),
                "Field Type": str(field.field_type),
                "Mapping Type": str(record.get("mapping_type", "Computed Default")),
                "Equipment IDs": "; ".join(equipment_ids),
                "Equipment Names": "; ".join(equipment_names),
                "Plants": "; ".join(plants_tuple),
                "Units / Sections": "; ".join(units_tuple),
                "Template IDs": "; ".join(template_ids),
                "Dashboard Templates": "; ".join(template_names),
                "Instrument Check Pair IDs": "; ".join(record.get("instrument_check_pairs", [])),
                "Mapping Basis": str(record.get("mapping_basis", "")),
                "Confidence": str(record.get("confidence", "Review")),
                "_equipment_ids": equipment_ids,
                "_plants": plants_tuple,
                "_units": units_tuple,
                "_template_ids": template_ids,
            }
        )
    return pd.DataFrame(rows)


def mapping_reverse_views(bu: str, mappings: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return field-per-equipment and field-per-template reverse mapping views."""
    mappings = field_mapping_table(bu) if mappings is None else mappings
    equipment = _usable_mapping_equipment(bu)
    equipment_lookup = (
        equipment.assign(equipment_id=equipment.get("equipment_id", pd.Series(dtype=str)).astype(str))
        .drop_duplicates("equipment_id")
        .set_index("equipment_id")
        if not equipment.empty and "equipment_id" in equipment
        else pd.DataFrame()
    )
    equipment_rows: list[dict[str, Any]] = []
    template_rows: list[dict[str, Any]] = []
    for row in mappings.itertuples(index=False, name=None):
        values = dict(zip(mappings.columns, row))
        common = {
            "Business Unit": values["Business Unit"],
            "Field ID": values["Field ID"],
            "Data Field": values["Data Field"],
            "Source": values["Source"],
            "Status": values["Status"],
            "Field Type": values["Field Type"],
            "Mapping Type": values["Mapping Type"],
        }
        for equipment_id in values["_equipment_ids"]:
            record = equipment_lookup.loc[equipment_id] if not equipment_lookup.empty and equipment_id in equipment_lookup.index else {}
            equipment_rows.append(
                {
                    "Business Unit": bu,
                    "Plant": str(record.get("plant", "")),
                    "Unit / Section": str(record.get("unit_section", "")),
                    "Equipment ID": equipment_id,
                    "Equipment": str(record.get("equipment_name", equipment_id)),
                    **{key: value for key, value in common.items() if key != "Business Unit"},
                    "Dashboard Templates": values["Dashboard Templates"],
                }
            )
        for template_id in values["_template_ids"]:
            template_rows.append(
                {
                    "Business Unit": bu,
                    "Template ID": template_id,
                    "Dashboard Template": MAPPING_TEMPLATES.get(template_id, template_id),
                    **{key: value for key, value in common.items() if key != "Business Unit"},
                    "Equipment IDs": values["Equipment IDs"],
                    "Equipment Names": values["Equipment Names"],
                }
            )
    return pd.DataFrame(equipment_rows), pd.DataFrame(template_rows)


def mapping_export_sheets(bu: str, mappings: pd.DataFrame | None = None) -> dict[str, pd.DataFrame]:
    """Build the complete review workbook sheets for one business unit."""
    mappings = field_mapping_table(bu) if mappings is None else mappings
    equipment_view, template_view = mapping_reverse_views(bu, mappings)
    public_mapping = mappings[[column for column in mappings.columns if not column.startswith("_")]].copy()
    guide = pd.DataFrame(
        [
            {
                "Item": "How mapping works",
                "Explanation": "Equipment and dashboard-template selections use this mapping to filter data-field dropdowns across OPERA-X.",
            },
            {
                "Item": "Computed Default",
                "Explanation": "The baseline mapping stored in the Default Mappings sheet of field_mappings.xlsx.",
            },
            {
                "Item": "Admin Override",
                "Explanation": "An administrator-saved mapping in field_mappings.xlsx; the change is also written to the audit log.",
            },
        ]
    )
    return {
        "Field Mappings": public_mapping,
        "By Equipment": equipment_view,
        "By Template": template_view,
        "Guide": guide,
    }


def mapping_database_bytes(bu: str) -> bytes:
    """Return the live Excel mapping database for Admin backend review."""
    return ensure_mapping_database(bu).read_bytes()


def instrument_check_pairs(bu: str) -> dict[str, list[str]]:
    """Return Field-to-DCS pairs recorded in the Excel mapping database."""
    catalog = field_catalog(bu).set_index("field_id")
    records = load_effective_field_mappings(bu)
    pairs: dict[str, list[str]] = {}
    for field_id, record in records.items():
        if field_id not in catalog.index or str(catalog.at[field_id, "source_key"]) != "Field":
            continue
        valid = [
            pair_id
            for pair_id in record.get("instrument_check_pairs", [])
            if pair_id in catalog.index and str(catalog.at[pair_id, "source_key"]) == "DCS"
        ]
        if valid:
            pairs[field_id] = valid
    return pairs


def _add_named_range(workbook: Workbook, name: str, sheet: str, column: str, last_row: int) -> None:
    workbook.defined_names.add(DefinedName(name, attr_text=f"'{sheet}'!${column}$2:${column}${max(2, last_row)}"))


def mapping_update_template_bytes(bu: str) -> bytes:
    """Build a controlled Excel template for audited bulk mapping updates."""
    effective = load_effective_field_mappings(bu)
    catalog = field_catalog(bu)
    equipment = _usable_mapping_equipment(bu)

    workbook = Workbook()
    workbook.remove(workbook.active)
    instructions = workbook.create_sheet("Instructions")
    instructions.append(["Item", "Guidance"])
    instruction_rows = [
        ("Purpose", "Update OPERA-X data-field mappings in bulk. Upload this .xlsx file from Admin / Super Admin > Field Mappings."),
        ("Editable sheets", "Edit Equipment Mappings, Template Mappings and Field Review. Set Apply Update to Yes in Field Review only for fields you want to change."),
        ("Controlled inputs", "Field IDs, Equipment IDs, Dashboard Template IDs and Include values use Excel dropdown validation lists."),
        ("Include", "Use Yes to include a relationship. Use No or delete the row to exclude it. Duplicate relationships are automatically de-duplicated."),
        ("Partial update", "Only Field IDs marked Apply Update = Yes in Field Review are applied. All other database mappings remain unchanged."),
        ("Example", "For DP1, use an Equipment Mappings row such as DP1 | EQ-001 | Yes and a Template Mappings row such as DP1 | plant-performance | Yes."),
        ("Safety", "Validate the business unit before applying. The app rejects unknown IDs, missing required sheets, empty mappings and invalid controlled values."),
    ]
    for row in instruction_rows:
        instructions.append(row)

    equipment_sheet = workbook.create_sheet("Equipment Mappings")
    equipment_sheet.append(["Field ID", "Equipment ID", "Include"])
    template_sheet = workbook.create_sheet("Template Mappings")
    template_sheet.append(["Field ID", "Dashboard Template ID", "Include"])
    review_sheet = workbook.create_sheet("Field Review")
    review_sheet.append(["Field ID", "Apply Update", "Mapping Basis", "Confidence", "Instrument Check Pair IDs"])
    for field_id in sorted(effective):
        record = effective[field_id]
        for equipment_id in record["equipment_ids"]:
            equipment_sheet.append([field_id, equipment_id, "Yes"])
        for template_id in record["template_ids"]:
            template_sheet.append([field_id, template_id, "Yes"])
        review_sheet.append(
            [
                field_id,
                "No",
                record.get("mapping_basis", ""),
                record.get("confidence", "Review"),
                "; ".join(record.get("instrument_check_pairs", [])),
            ]
        )

    catalogue = workbook.create_sheet("Field Catalogue")
    catalogue.append(["Field ID", "Data Field", "Source", "Status", "Field Type"])
    for field in catalog.itertuples(index=False):
        catalogue.append([str(field.field_id), str(field.field_name), str(field.source), str(field.status), str(field.field_type)])

    equipment_catalogue = workbook.create_sheet("Equipment Catalogue")
    equipment_catalogue.append(["Equipment ID", "Equipment", "Plant", "Unit / Section", "Equipment Type"])
    for row in equipment.itertuples():
        equipment_catalogue.append(
            [
                str(getattr(row, "equipment_id", "")),
                str(getattr(row, "equipment_name", "")),
                str(getattr(row, "plant", "")),
                str(getattr(row, "unit_section", "")),
                str(getattr(row, "equipment_type", "")),
            ]
        )

    template_catalogue = workbook.create_sheet("Template Catalogue")
    template_catalogue.append(["Dashboard Template ID", "Dashboard Template"])
    for template_id, name in MAPPING_TEMPLATES.items():
        template_catalogue.append([template_id, name])

    lists = workbook.create_sheet("Lists")
    lists.append(["Field IDs", "Equipment IDs", "Template IDs", "Include", "Confidence"])
    field_ids = catalog["field_id"].astype(str).tolist()
    equipment_ids = equipment.get("equipment_id", pd.Series(dtype=str)).astype(str).tolist()
    template_ids = list(MAPPING_TEMPLATES)
    include_values = ["Yes", "No"]
    confidence_values = ["High", "Medium", "Review"]
    for index in range(max(len(field_ids), len(equipment_ids), len(template_ids), len(include_values), len(confidence_values))):
        lists.append(
            [
                field_ids[index] if index < len(field_ids) else "",
                equipment_ids[index] if index < len(equipment_ids) else "",
                template_ids[index] if index < len(template_ids) else "",
                include_values[index] if index < len(include_values) else "",
                confidence_values[index] if index < len(confidence_values) else "",
            ]
        )
    _add_named_range(workbook, "MappingFieldIDs", "Lists", "A", len(field_ids) + 1)
    _add_named_range(workbook, "MappingEquipmentIDs", "Lists", "B", len(equipment_ids) + 1)
    _add_named_range(workbook, "MappingTemplateIDs", "Lists", "C", len(template_ids) + 1)
    _add_named_range(workbook, "MappingIncludeOptions", "Lists", "D", len(include_values) + 1)
    _add_named_range(workbook, "MappingConfidenceOptions", "Lists", "E", len(confidence_values) + 1)

    validation_specs = [
        (equipment_sheet, "A", "=MappingFieldIDs"),
        (equipment_sheet, "B", "=MappingEquipmentIDs"),
        (equipment_sheet, "C", "=MappingIncludeOptions"),
        (template_sheet, "A", "=MappingFieldIDs"),
        (template_sheet, "B", "=MappingTemplateIDs"),
        (template_sheet, "C", "=MappingIncludeOptions"),
        (review_sheet, "A", "=MappingFieldIDs"),
        (review_sheet, "B", "=MappingIncludeOptions"),
        (review_sheet, "D", "=MappingConfidenceOptions"),
    ]
    validation_last_row = max(50000, equipment_sheet.max_row + 5000, template_sheet.max_row + 5000)
    for sheet, column, formula in validation_specs:
        validation = DataValidation(type="list", formula1=formula, allow_blank=False)
        validation.error = "Select a value from the OPERA-X controlled list."
        validation.errorTitle = "Invalid mapping value"
        validation.prompt = "Choose a controlled value from the dropdown."
        validation.promptTitle = "OPERA-X mapping"
        validation.showErrorMessage = True
        validation.showInputMessage = True
        sheet.add_data_validation(validation)
        validation.add(f"{column}2:{column}{validation_last_row}")

    lists.sheet_state = "hidden"
    _style_mapping_workbook(workbook)
    out = BytesIO()
    workbook.save(out)
    return out.getvalue()


def bulk_update_field_mappings(bu: str, workbook_bytes: bytes) -> dict[str, int]:
    """Validate and apply a partial/full mapping update workbook to the Excel database."""
    if not workbook_bytes:
        raise ValueError("Choose a non-empty .xlsx mapping workbook.")
    if len(workbook_bytes) > 25 * 1024 * 1024:
        raise ValueError("The mapping workbook must not exceed 25 MB.")
    try:
        workbook = load_workbook(BytesIO(workbook_bytes), read_only=True, data_only=False)
        sheet_names = set(workbook.sheetnames)
        workbook.close()
    except Exception as exc:
        raise ValueError(f"The uploaded file is not a readable Excel workbook: {exc}") from exc
    required_sheets = {"Equipment Mappings", "Template Mappings", "Field Review"}
    if not required_sheets.issubset(sheet_names):
        missing = ", ".join(sorted(required_sheets - sheet_names))
        raise ValueError(f"The mapping workbook is missing required sheet(s): {missing}.")
    try:
        sheets = pd.read_excel(
            BytesIO(workbook_bytes),
            sheet_name=["Equipment Mappings", "Template Mappings", "Field Review"],
            dtype=str,
            keep_default_na=False,
        )
    except Exception as exc:
        raise ValueError(f"The mapping update sheets could not be read: {exc}") from exc

    equipment_frame = sheets["Equipment Mappings"]
    template_frame = sheets["Template Mappings"]
    review_frame = sheets["Field Review"]
    if not {"Field ID", "Equipment ID", "Include"}.issubset(equipment_frame.columns):
        raise ValueError("Equipment Mappings must contain Field ID, Equipment ID and Include columns.")
    if not {"Field ID", "Dashboard Template ID", "Include"}.issubset(template_frame.columns):
        raise ValueError("Template Mappings must contain Field ID, Dashboard Template ID and Include columns.")
    if not {"Field ID", "Apply Update", "Mapping Basis", "Confidence", "Instrument Check Pair IDs"}.issubset(review_frame.columns):
        raise ValueError("Field Review must contain Field ID, Apply Update, Mapping Basis, Confidence and Instrument Check Pair IDs columns.")

    catalog = field_catalog(bu)
    valid_fields = set(catalog["field_id"].astype(str))
    source_by_field = catalog.set_index("field_id")["source_key"].astype(str).to_dict()
    valid_equipment = set(_usable_mapping_equipment(bu).get("equipment_id", pd.Series(dtype=str)).astype(str))
    valid_templates = set(MAPPING_TEMPLATES)
    allowed_include = {"yes", "no"}

    def clean(frame: pd.DataFrame, value_column: str, valid_values: set[str]) -> tuple[dict[str, list[str]], set[str]]:
        values: dict[str, list[str]] = {}
        touched: set[str] = set()
        for row_number, row in enumerate(frame.fillna("").to_dict("records"), start=2):
            field_id = str(row.get("Field ID", "")).strip()
            value = str(row.get(value_column, "")).strip()
            include = str(row.get("Include", "")).strip().lower()
            if not field_id and not value and not include:
                continue
            if field_id not in valid_fields:
                raise ValueError(f"{frame.attrs.get('sheet_name', 'Mapping sheet')} row {row_number}: unknown Field ID '{field_id}'.")
            if include not in allowed_include:
                raise ValueError(f"Row {row_number}: Include must be Yes or No.")
            if value not in valid_values:
                raise ValueError(f"Row {row_number}: unknown {value_column} '{value}'.")
            touched.add(field_id)
            if include == "yes":
                values.setdefault(field_id, []).append(value)
        return {field_id: list(dict.fromkeys(items)) for field_id, items in values.items()}, touched

    equipment_frame.attrs["sheet_name"] = "Equipment Mappings"
    template_frame.attrs["sheet_name"] = "Template Mappings"
    equipment_values, _ = clean(equipment_frame, "Equipment ID", valid_equipment)
    template_values, _ = clean(template_frame, "Dashboard Template ID", valid_templates)

    review_values: dict[str, dict[str, Any]] = {}
    touched: set[str] = set()
    for row_number, row in enumerate(review_frame.fillna("").to_dict("records"), start=2):
        field_id = str(row.get("Field ID", "")).strip()
        if not field_id:
            continue
        if field_id not in valid_fields:
            raise ValueError(f"Field Review row {row_number}: unknown Field ID '{field_id}'.")
        apply_update = str(row.get("Apply Update", "")).strip().lower()
        if apply_update not in allowed_include:
            raise ValueError(f"Field Review row {row_number}: Apply Update must be Yes or No.")
        basis = str(row.get("Mapping Basis", "")).strip()
        confidence = str(row.get("Confidence", "")).strip().title()
        if confidence not in {"High", "Medium", "Review"}:
            raise ValueError(f"Field Review row {row_number}: Confidence must be High, Medium or Review.")
        if not basis:
            raise ValueError(f"Field Review row {row_number}: Mapping Basis must not be blank.")
        pairs = _split_mapping_ids(row.get("Instrument Check Pair IDs", ""))
        for pair_id in pairs:
            if pair_id not in valid_fields:
                raise ValueError(f"Field Review row {row_number}: unknown Instrument Check Pair ID '{pair_id}'.")
            source_pair = {source_by_field.get(field_id), source_by_field.get(pair_id)}
            if source_pair != {"DCS", "Field"}:
                raise ValueError(f"Field Review row {row_number}: Instrument Check pairs must link one Field reading and one DCS reading.")
        review_values[field_id] = {"mapping_basis": basis, "confidence": confidence, "instrument_check_pairs": pairs}
        if apply_update == "yes":
            touched.add(field_id)
    if not touched:
        raise ValueError("No fields are marked Apply Update = Yes in Field Review.")
    for field_id in sorted(touched):
        if not equipment_values.get(field_id):
            raise ValueError(f"Field {field_id} must include at least one Equipment ID.")
        if not template_values.get(field_id):
            raise ValueError(f"Field {field_id} must include at least one Dashboard Template ID.")
    missing_review = sorted(field_id for field_id in touched if field_id not in review_values)
    if missing_review:
        raise ValueError(f"Field Review is missing metadata for updated field(s): {', '.join(missing_review[:10])}.")

    effective = load_effective_field_mappings(bu)
    defaults = load_default_field_mappings(bu)
    for field_id in touched:
        metadata = review_values[field_id]
        effective[field_id] = _mapping_record(
            equipment_values[field_id],
            template_values[field_id],
            "Admin Override",
            metadata["mapping_basis"],
            metadata["confidence"],
            metadata["instrument_check_pairs"],
        )
    _write_mapping_database(bu, effective, defaults)
    return {
        "fields_updated": len(touched),
        "equipment_relationships": sum(len(equipment_values[field_id]) for field_id in touched),
        "template_relationships": sum(len(template_values[field_id]) for field_id in touched),
    }


def fields_for_equipment(template: dict[str, Any], equipment_id: str) -> tuple[list[str], list[str]]:
    """Return equipment-specific fields, falling back to template defaults."""
    overrides = template.get("equipment_fields", {})
    override = overrides.get(equipment_id, {}) if isinstance(overrides, dict) else {}
    chart_fields = override.get("chart_fields", template.get("chart_fields", []))
    table_fields = override.get("table_fields", template.get("table_fields", []))
    return list(chart_fields or []), list(table_fields or [])


def intelligent_equipment_fields(
    equipment_record: dict[str, Any] | pd.Series,
    registry: pd.DataFrame,
    available_ids: set[str] | None = None,
    limit: int = 6,
) -> list[str]:
    """Rank active fields against equipment name/type semantics for a useful default overview."""
    if registry.empty:
        return []
    record = dict(equipment_record)
    equipment_text = " ".join(str(record.get(key, "")) for key in ("equipment_type", "equipment_name")).lower()
    keywords: list[str] = []
    for equipment_key, field_keywords in EQUIPMENT_FIELD_KEYWORDS.items():
        if equipment_key in equipment_text:
            keywords.extend(field_keywords)
    if not keywords:
        keywords = ["temperature", "pressure", "flow", "vibration", "speed", "level", "power"]

    work = registry.copy()
    if "active" in work:
        work = work[work["active"].astype(str).str.lower() == "true"]
    if available_ids is not None:
        work = work[work["field_id"].astype(str).isin(available_ids)]
    if work.empty:
        return []

    source_priority = {"DCS": 3, "Field": 2, "Lab": 1}
    scored: list[tuple[int, int, str]] = []
    for position, row in enumerate(work.itertuples()):
        name = str(row.field_name).lower()
        score = sum(4 for keyword in keywords if keyword in name)
        score += source_priority.get(str(getattr(row, "source", "")), 0)
        scored.append((score, -position, str(row.field_id)))
    scored.sort(reverse=True)
    ranked = [field_id for score, _, field_id in scored if score > 0]
    return ranked[:limit]


def equipment_overview_fields(
    template: dict[str, Any],
    equipment_record: dict[str, Any] | pd.Series,
    registry: pd.DataFrame,
    available_ids: set[str],
    limit: int = 6,
) -> tuple[list[str], list[str]]:
    """Use an Admin override first, otherwise intelligently map key fields to equipment."""
    equipment_id = str(dict(equipment_record).get("equipment_id", ""))
    overrides = template.get("equipment_fields", {})
    if isinstance(overrides, dict) and equipment_id in overrides:
        charts, tables = fields_for_equipment(template, equipment_id)
        return ([field for field in charts if field in available_ids], [field for field in tables if field in available_ids])
    mapped = intelligent_equipment_fields(equipment_record, registry, available_ids, limit)
    if not mapped:
        mapped = [field for field in template.get("chart_fields", []) if field in available_ids][:limit]
    return mapped, mapped.copy()


def hierarchy_path(bu: str):
    return storage.bu_dir(bu) / "equipment_validation.json"


def hierarchy_options(bu: str) -> dict[str, list[str]]:
    equipment = storage.equipment(bu)
    derived = {
        "plants": sorted({str(x).strip() for x in equipment.get("plant", pd.Series(dtype=str)) if str(x).strip()}),
        "units": sorted({str(x).strip() for x in equipment.get("unit_section", pd.Series(dtype=str)) if str(x).strip() and str(x).strip() != "Unassigned"}),
        "equipment_types": sorted({str(x).strip() for x in equipment.get("equipment_type", pd.Series(dtype=str)) if str(x).strip() and str(x).strip() != "Placeholder"}),
    }
    saved = storage.json_setting(hierarchy_path(bu), {})
    for key in derived:
        if isinstance(saved, dict) and isinstance(saved.get(key), list):
            derived[key] = sorted(set(derived[key]) | {str(x).strip() for x in saved[key] if str(x).strip()})
    return derived


def save_hierarchy_options(bu: str, options: dict[str, list[str]]) -> None:
    clean = {key: sorted({str(x).strip() for x in values if str(x).strip()}) for key, values in options.items()}
    storage.save_json(hierarchy_path(bu), clean)


def field_label_map(registry: pd.DataFrame) -> dict[str, str]:
    if registry.empty:
        return {}
    return {str(row.field_id): f"{row.field_id} — {row.field_name} ({row.uom})" for row in registry.itertuples()}


def normalise_long(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    work = frame.copy()
    work["Timestamp"] = pd.to_datetime(work["Timestamp"], errors="coerce")
    work["value"] = pd.to_numeric(work["value"], errors="coerce")
    return work.dropna(subset=["Timestamp", "value"])


def _figure(view: pd.DataFrame, chart_type: str, combined: bool, title: str):
    color = "field_name" if combined and view["field_name"].nunique() > 1 else None
    common = {"color_discrete_sequence": CHART_COLORS}
    if chart_type == "Area":
        fig = px.area(view, x="Timestamp", y="value", color=color, title=title, **common)
    elif chart_type == "Bar":
        fig = px.bar(view, x="Timestamp", y="value", color=color, title=title, barmode="group", **common)
    elif chart_type == "Scatter":
        fig = px.scatter(view, x="Timestamp", y="value", color=color, title=title, **common)
    elif chart_type == "Box Plot":
        fig = px.box(view, x="field_name" if combined else None, y="value", color=color, title=title, points="outliers", **common)
    else:
        fig = px.line(view, x="Timestamp", y="value", color=color, title=title, markers=False, **common)
    units = [x for x in view.get("uom", pd.Series(dtype=str)).dropna().astype(str).unique() if x]
    y_title = units[0] if len(units) == 1 else "Value (mixed units)"
    fig.update_layout(
        template="plotly_white",
        height=330,
        hovermode="x unified" if chart_type in {"Line", "Area"} else "closest",
        legend_title_text="",
        margin=dict(l=48, r=20, t=58, b=42),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="IBM Plex Sans, Arial, sans-serif", color="#152238"),
        title_font=dict(size=15),
        xaxis=dict(showgrid=False, linecolor="#C9D8EC"),
        yaxis=dict(title=y_title, gridcolor="#E8EEF7", zerolinecolor="#C9D8EC"),
    )
    return fig


def render_chart_grid(frame: pd.DataFrame, field_ids: list[str], chart_type: str, axis_mode: str, key: str) -> None:
    view = normalise_long(frame)
    if field_ids:
        view = view[view["field_id"].astype(str).isin(field_ids)]
    if view.empty:
        st.info("No chart data is available for the selected fields and period.")
        return
    if axis_mode == "Place on the Same Axis" or view["field_id"].nunique() == 1:
        st.plotly_chart(_figure(view, chart_type, True, "Selected Data Fields"), width="stretch", key=f"{key}_combined")
        return
    fields = list(dict.fromkeys(view["field_id"].astype(str).tolist()))
    for start in range(0, len(fields), 2):
        columns = st.columns(2, gap="large")
        for column, field_id in zip(columns, fields[start:start + 2]):
            part = view[view["field_id"].astype(str) == field_id]
            name = str(part["field_name"].iloc[0])
            with column:
                with st.container(border=True):
                    st.plotly_chart(_figure(part, chart_type, False, name), width="stretch", key=f"{key}_{field_id}")


def render_selectable_chart_grid(
    frame: pd.DataFrame,
    field_ids: list[str],
    chart_type: str,
    axis_mode: str,
    key: str,
) -> list[str]:
    """Render a CPP-style grid whose headers (or combined legend selector) change displayed fields."""
    view = normalise_long(frame)
    if view.empty:
        st.info("No chart data is available for the selected fields and period.")
        return []
    metadata = (
        view[["field_id", "field_name", "uom"]]
        .drop_duplicates("field_id")
        .assign(field_id=lambda x: x["field_id"].astype(str))
        .set_index("field_id")
    )
    available = metadata.index.tolist()
    defaults = [str(field) for field in field_ids if str(field) in metadata.index] or available[: min(6, len(available))]
    labels = {field: f"{metadata.at[field, 'field_name']} ({metadata.at[field, 'uom']})" for field in available}
    reverse = {label: field for field, label in labels.items()}

    if axis_mode == "Place on the Same Axis":
        chosen_labels = st.multiselect(
            "Chart Legend / Data Fields",
            list(reverse),
            default=[labels[field] for field in defaults],
            key=f"{key}_legend_fields",
            help="Select the chart legend fields to add or remove series.",
        )
        chosen = [reverse[label] for label in chosen_labels]
        if chosen:
            part = view[view["field_id"].astype(str).isin(chosen)]
            st.plotly_chart(_figure(part, chart_type, True, "Selected Data Fields"), width="stretch", key=f"{key}_combined")
        else:
            st.info("Select at least one chart field.")
        return chosen

    chosen: list[str] = []
    for start in range(0, len(defaults), 2):
        columns = st.columns(2, gap="large")
        for offset, (column, default) in enumerate(zip(columns, defaults[start:start + 2])):
            slot = start + offset
            with column:
                with st.container(border=True):
                    selected_label = st.selectbox(
                        "Chart Header / Data Field",
                        list(reverse),
                        index=list(reverse).index(labels[default]),
                        key=f"{key}_header_{slot}",
                        help="Choose this chart header to change the data field shown in the chart.",
                    )
                    field_id = reverse[selected_label]
                    chosen.append(field_id)
                    part = view[view["field_id"].astype(str) == field_id]
                    st.plotly_chart(_figure(part, chart_type, False, str(metadata.at[field_id, "field_name"])), width="stretch", key=f"{key}_slot_{slot}_{field_id}")
    return chosen
