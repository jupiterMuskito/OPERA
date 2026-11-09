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
            {"id": "condition-monitoring", "name": "Condition Monitoring", "chart_fields": ["F1", "F3", "F4", "DP2"], "table_fields": ["F1", "F3", "F4", "DP2"], "chart_type": "Line", "period_mode": "Selected Period"},
            {"id": "process-performance", "name": "Process Performance", "chart_fields": ["DP1", "DP2", "DP5", "DP20"], "table_fields": ["DP1", "DP2", "DP5", "DP20"], "chart_type": "Area", "period_mode": "Selected Period"},
            {"id": "quality-compliance", "name": "Quality & Compliance", "chart_fields": ["L1", "L6", "L12", "L17"], "table_fields": ["L1", "L6", "L12", "L17"], "chart_type": "Box Plot", "period_mode": "Selected Period"},
            {"id": "reliability", "name": "Reliability", "chart_fields": ["F3", "F4", "F5", "F7"], "table_fields": ["F3", "F4", "F5", "F7"], "chart_type": "Scatter", "period_mode": "Selected Period"},
        ],
        "Operations Dashboard": [
            {"id": "current", "name": "Current", "chart_fields": ["CF1", "CF2", "CF3", "CF4"], "table_fields": ["CF1", "CF2", "CF3", "CF4", "CF5", "CF6"], "chart_type": "Line", "period_mode": "Current"},
            {"id": "period-total", "name": "Period Total", "chart_fields": ["CF1", "CF4", "CF6", "CF8"], "table_fields": ["CF1", "CF2", "CF3", "CF4", "CF5", "CF6", "CF7", "CF8"], "chart_type": "Bar", "period_mode": "Period Total"},
            {"id": "month-to-date", "name": "Month-to-Date", "chart_fields": ["CF1", "CF2", "CF4", "CF8"], "table_fields": ["CF1", "CF2", "CF4", "CF5", "CF8"], "chart_type": "Area", "period_mode": "Month-to-Date"},
            {"id": "year-to-date", "name": "Year-to-Date", "chart_fields": ["CF1", "CF2", "CF4", "CF8"], "table_fields": ["CF1", "CF2", "CF4", "CF5", "CF8"], "chart_type": "Line", "period_mode": "Year-to-Date"},
            {"id": "quality", "name": "Quality", "chart_fields": ["CF4", "CF7"], "table_fields": ["CF4", "CF7"], "chart_type": "Box Plot", "period_mode": "Selected Period"},
            {"id": "reliability", "name": "Reliability", "chart_fields": ["CF5", "CF6"], "table_fields": ["CF5", "CF6"], "chart_type": "Scatter", "period_mode": "Selected Period"},
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
    return result


def save_templates(bu: str, templates: dict[str, list[dict[str, Any]]]) -> None:
    storage.save_json(templates_path(bu), templates)


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
