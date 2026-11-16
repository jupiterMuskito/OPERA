from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from . import storage

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

SOURCE_TEMPLATE_DEFAULTS = {
    "DCS": ("plant-performance", "process-performance"),
    "Lab": ("plant-performance", "quality-compliance"),
    "Field": ("condition-monitoring", "reliability"),
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


def field_mappings_path(bu: str):
    """Persist only Admin overrides; deterministic defaults cover every field."""
    return storage.bu_dir(bu) / "field_mappings.json"


def load_field_mapping_overrides(bu: str) -> dict[str, dict[str, list[str]]]:
    value = storage.json_setting(field_mappings_path(bu), {})
    return value if isinstance(value, dict) else {}


def _field_number(field_id: str) -> int:
    digits = "".join(character for character in str(field_id) if character.isdigit())
    return max(1, int(digits or "1"))


def _equipment_keywords(record: dict[str, Any] | pd.Series) -> list[str]:
    text = " ".join(str(dict(record).get(key, "")) for key in ("equipment_type", "equipment_name")).lower()
    keywords: list[str] = []
    for equipment_key, values in EQUIPMENT_FIELD_KEYWORDS.items():
        if equipment_key in text:
            keywords.extend(values)
    return list(dict.fromkeys(keywords))


def default_field_mapping(
    field_id: str,
    source: str,
    field_name: str,
    equipment: pd.DataFrame,
) -> dict[str, list[str]]:
    """Return a stable equipment/template mapping for any input or placeholder field.

    Semantic equipment matches are preferred. A deterministic equipment fallback and
    round-robin template fallback guarantee that all DP/L/F/TA–TG placeholders have
    at least one equipment and one of the five operational dashboard templates.
    """
    usable = equipment.copy()
    if not usable.empty:
        if "active" in usable:
            active = usable["active"].astype(str).str.lower() == "true"
            usable = usable[active]
        if "placeholder" in usable:
            named = usable[usable["placeholder"].astype(str).str.lower() != "true"]
            usable = named if not named.empty else usable
    equipment_ids = usable.get("equipment_id", pd.Series(dtype=str)).astype(str).tolist()
    field_text = str(field_name).lower()
    semantic_ids = [] if "placeholder" in field_text else [
        str(row.equipment_id)
        for row in usable.itertuples()
        if any(keyword in field_text for keyword in _equipment_keywords(row._asdict()))
    ]
    if semantic_ids:
        mapped_equipment = semantic_ids
    elif equipment_ids:
        mapped_equipment = [equipment_ids[(_field_number(field_id) - 1) % len(equipment_ids)]]
    else:
        mapped_equipment = []

    template_ids = list(SOURCE_TEMPLATE_DEFAULTS.get(str(source), ()))
    if not template_ids:
        canonical = list(MAPPING_TEMPLATES)
        template_ids = [canonical[(_field_number(field_id) - 1) % len(canonical)]]
    return {"equipment_ids": mapped_equipment, "template_ids": template_ids}


def field_mapping(
    bu: str,
    field_id: str,
    source: str | None = None,
    field_name: str | None = None,
    equipment: pd.DataFrame | None = None,
) -> dict[str, list[str]]:
    registry = storage.registry(bu)
    match = registry[registry["field_id"].astype(str) == str(field_id)] if not registry.empty else pd.DataFrame()
    if source is None:
        source = str(match.iloc[0].get("source", "")) if not match.empty else ""
    if field_name is None:
        field_name = str(match.iloc[0].get("field_name", field_id)) if not match.empty else str(field_id)
    default = default_field_mapping(str(field_id), str(source), str(field_name), storage.equipment(bu) if equipment is None else equipment)
    override = load_field_mapping_overrides(bu).get(str(field_id), {})
    mapped_equipment = override.get("equipment_ids", default["equipment_ids"])
    mapped_templates = override.get("template_ids", default["template_ids"])
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
    equipment = storage.equipment(bu)
    overrides = load_field_mapping_overrides(bu)
    selected: set[str] = set()
    for row in registry.itertuples():
        field_id = str(row.field_id)
        mapping = default_field_mapping(field_id, str(getattr(row, "source", "")), str(getattr(row, "field_name", field_id)), equipment)
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
    overrides = load_field_mapping_overrides(bu)
    overrides[str(field_id)] = {
        "equipment_ids": list(dict.fromkeys(str(item) for item in equipment_ids if str(item))),
        "template_ids": list(dict.fromkeys(str(item) for item in template_ids if str(item))),
    }
    storage.save_json(field_mappings_path(bu), overrides)


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
