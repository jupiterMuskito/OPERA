from __future__ import annotations

import io
import json
import uuid
import zipfile
from datetime import date, datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

from opera import auth, config, dashboard, dcs_connector, exports, formula, risk_store, storage
from opera.risk_engine import collect_hazards, make_serial, suggest_from_text
from opera.risk_pdf import build_pdf

st.set_page_config(page_title="OPERA", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")
PAGES = [
    "OPERA Home", "Plant Overview", "Equipment Overview", "Operations Dashboard", "Data Input",
    "Event Log", "Data Analysis", "Data Output", "Operating Parameters", "Risk Assessment",
    "Lesson Bank", "Admin / Super Admin",
]


def styles() -> None:
    st.markdown(
        """
<style>
:root{
  --blue:#1857C9;--blue-dark:#0F3F9C;--red:#CF3430;--text:#152238;--muted:#48597A;
  --bg:#EEF3FA;--panel:#FFFFFF;--panel-alt:#F7F9FD;--border:#C9D8EC;--border-soft:#DCE7F4;
}
html,body,[class*="css"]{font-family:"IBM Plex Sans","Segoe UI",Arial,sans-serif;color:var(--text)}
.stApp{background:var(--bg)}
[data-testid="stHeader"]{background:rgba(238,243,250,.90);backdrop-filter:blur(8px)}
[data-testid="stSidebar"]{background:var(--panel-alt);border-right:1px solid var(--border)}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,[data-testid="stSidebar"] span{color:var(--text)}
[data-testid="stSidebar"] .stButton button{
  color:var(--blue-dark)!important;background:#FFFFFF!important;border:1px solid var(--border)!important;
  font-weight:700;box-shadow:0 1px 2px rgba(15,63,156,.05)
}
[data-testid="stSidebar"] .stButton button:hover{border-color:var(--blue)!important;background:#EAF1FC!important;color:var(--blue-dark)!important}
[data-testid="stSidebar"] [data-testid="stSidebarNav"]{padding-top:.4rem}
.block-container{padding-top:2rem;padding-bottom:3rem;max-width:1500px}
.opera-hero{padding:1.3rem 1.55rem;border-radius:12px;background:linear-gradient(135deg,var(--blue-dark),var(--blue));color:#fff;margin-bottom:1rem;box-shadow:0 8px 24px rgba(15,63,156,.15)}
.opera-hero h1{margin:0;font-size:1.9rem;letter-spacing:-.02em}.opera-hero p{margin:.35rem 0 0;color:#E7F0FF;opacity:.94}
.login-brand{min-height:410px;border-radius:18px;padding:3.1rem;background:linear-gradient(145deg,#0F3F9C 0%,#1857C9 70%,#2F7DE1 100%);color:#fff;box-shadow:0 24px 64px rgba(15,63,156,.24);display:flex;flex-direction:column;justify-content:space-between}
.login-brand .mark{width:58px;height:58px;border-radius:15px;background:#fff;color:var(--blue);display:flex;align-items:center;justify-content:center;font-size:1.7rem;font-weight:800;box-shadow:0 10px 24px rgba(0,0,0,.12)}
.login-brand h1{font-size:3rem;line-height:1;margin:1rem 0 .6rem;letter-spacing:-.04em}.login-brand p{font-size:1.05rem;color:#DCE9FF;max-width:34rem}.login-brand .route{font-size:.82rem;color:#E7F0FF;border-top:1px solid rgba(255,255,255,.25);padding-top:1rem}
.login-heading{margin:.35rem 0 1.2rem}.login-heading h2{margin:0;color:var(--text);font-size:1.7rem}.login-heading p{color:var(--muted);margin:.35rem 0 0}
.flow,.panel-note{background:#fff;border:1px solid var(--border);border-radius:10px;padding:.75rem 1rem;color:#334E68}
.badge-good,.badge-bad,.badge-neutral{display:inline-block;padding:.18rem .55rem;border-radius:999px;font-weight:700;font-size:.75rem;margin-top:.35rem}.badge-good{background:#E4ECF9;color:var(--blue-dark)}.badge-bad{background:#FBE5E5;color:#9F1F2A}.badge-neutral{background:#EDF1F5;color:#44576B}
.small-note{color:#60758A;font-size:.82rem;margin-top:.2rem}
.stButton>button,.stDownloadButton>button{border-radius:8px;border:1px solid var(--blue);font-weight:650;min-height:2.45rem}
.stButton>button[kind="primary"]{background:var(--blue);color:#fff}.stButton>button[kind="primary"]:hover{background:var(--blue-dark);color:#fff}
div[data-testid="stForm"],div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-color:var(--border)!important;border-radius:12px}
div[data-testid="stMetric"]{background:#fff;border:1px solid var(--border);padding:.9rem;border-radius:10px;min-height:105px}
[data-testid="stDataFrame"]{background:#fff;border:1px solid var(--border-soft);border-radius:10px;overflow:hidden}
div[data-testid="stPlotlyChart"]{background:#fff;border:1px solid var(--border-soft);border-radius:10px;overflow:hidden;box-shadow:0 2px 8px rgba(21,34,56,.04)}
.metric-card{border:1px solid var(--border);border-top:4px solid var(--blue);background:#fff;border-radius:10px;padding:1rem;min-height:170px;height:170px;box-sizing:border-box;box-shadow:0 2px 8px rgba(21,34,56,.04);display:flex;flex-direction:column;justify-content:flex-start}
.metric-card.bad{border-top-color:var(--red)}.metric-value{font-size:1.65rem;font-weight:750;color:var(--blue-dark);line-height:1.15;margin:.45rem 0 .25rem}.metric-title{font-size:.82rem;color:var(--muted);font-weight:700;min-height:2.25rem}.metric-meta{font-size:.8rem;color:var(--muted)}
.module-card{background:#fff;border:1px solid var(--border);border-radius:10px;padding:1rem 1.1rem;min-height:105px;height:105px;box-sizing:border-box}.module-card strong{color:var(--blue-dark)}.module-card p{color:var(--muted);font-size:.87rem;margin:.35rem 0 0}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:.35rem}[data-testid="stTabs"] [data-baseweb="tab"]{border-radius:8px;padding:.45rem .8rem}
h1,h2,h3,h4{color:var(--text);letter-spacing:-.015em}
hr{border-color:var(--border-soft)}
@media(max-width:900px){.login-brand{min-height:260px;padding:2rem}.login-brand h1{font-size:2.2rem}.metric-card{height:auto;min-height:150px}}
</style>
""",
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="opera-hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def secret_users() -> dict[str, Any]:
    try:
        return dict(st.secrets.get("users", {}))
    except Exception:
        return {}


def do_login() -> None:
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    brand, sign_in = st.columns([1.08, .92], gap="large", vertical_alignment="center")
    with brand:
        st.markdown(
            """
<div class="login-brand">
  <div><div class="mark">O</div><h1>OPERA</h1><p>Operational Excellence and Reliability Assistant</p></div>
  <div class="route">Operational intelligence · Reliability · Continuous improvement</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with sign_in:
        with st.container(border=True):
            st.markdown('<div class="login-heading"><h2>Sign In</h2><p>Use your OPERA account to continue.</p></div>', unsafe_allow_html=True)
            with st.form("login"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In", type="primary", width="stretch")
            if submitted:
                user, message = auth.authenticate(username, password, secret_users())
                if not user:
                    st.error(message)
                else:
                    st.session_state.user = user
                    storage.audit("shared", user.username, "login", {"role": user.role})
                    st.rerun()
            st.caption("Testing credentials are documented in README.md. Change all seeded passwords before production.")
    st.stop()


def choose_bu(user: auth.User) -> None:
    bus = config.business_units(active_only=True)
    bus = bus[bus["id"].map(lambda value: auth.can_access_bu(user, value))]
    hero("Select Business Unit", f"Signed in as {user.display_name} · {user.role}")
    if bus.empty:
        st.error("No active business unit is assigned to this account.")
        st.stop()
    labels = {row["name"]: row["id"] for _, row in bus.iterrows()}
    left, right = st.columns([2, 1])
    selected = left.selectbox("Business Unit", labels)
    if right.button("Open OPERA", type="primary", width="stretch"):
        st.session_state.bu = labels[selected]
        st.rerun()
    st.stop()


def password_change_gate(user: auth.User) -> None:
    if not user.must_change_password:
        return
    hero("Password Change Required", "Replace the seeded Super Admin password before OPERA opens.")
    with st.form("force_password"):
        old = st.text_input("Current Password", type="password")
        new = st.text_input("New Password", type="password")
        confirm = st.text_input("Confirm New Password", type="password")
        go = st.form_submit_button("Change Password", type="primary")
    if go:
        if new != confirm:
            st.error("The new passwords do not match.")
        else:
            ok, message = auth.change_password(user.username, old, new)
            if ok:
                st.success(message + " Sign in again.")
                st.session_state.clear()
                st.rerun()
            st.error(message)
    st.stop()


def sidebar(user: auth.User, bu: str) -> str:
    bus = config.business_units()
    name = bus.loc[bus["id"] == bu, "name"].iloc[0] if (bus["id"] == bu).any() else bu
    st.sidebar.markdown("## ⚙️ OPERA")
    st.sidebar.caption(f"{name} · {user.role}")
    unread = storage.unread_notifications(bu, user.username)
    with st.sidebar.expander(f"Notifications ({len(unread)})", expanded=False):
        if unread.empty:
            st.caption("No unread notifications.")
        else:
            for _, row in unread.head(10).iterrows():
                (st.error if row["level"] == "error" else st.success)(row["message"])
            if st.button("Mark All as Read", width="stretch"):
                storage.mark_notifications_read(bu, user.username)
                st.rerun()
    available = [page for page in PAGES if page != "Admin / Super Admin" or auth.allowed(user, "configure")]
    page = st.sidebar.radio("Navigate", available)
    st.sidebar.divider()
    if st.sidebar.button("⇄  Change Business Unit", width="stretch"):
        st.session_state.pop("bu", None)
        st.rerun()
    if st.sidebar.button("↪  Sign Out", width="stretch"):
        storage.audit(bu, user.username, "logout")
        st.session_state.clear()
        st.rerun()
    st.sidebar.caption("Data Input → Event Log → Data Analysis → Data Output")
    return page


def source_frame(bu: str, source: str) -> pd.DataFrame:
    frame = storage.read_csv(storage.source_path(bu, source))
    if not frame.empty:
        frame["Timestamp"] = pd.to_datetime(frame["Date"] + " " + frame["Time"], errors="coerce")
    return frame


def active_registry(bu: str, source: str | None = None) -> pd.DataFrame:
    registry = storage.registry(bu)
    registry = registry[registry["active"].str.lower() == "true"]
    return registry if source is None else registry[registry["source"] == source]


def long_data(bu: str, sources: list[str] | None = None) -> pd.DataFrame:
    items: list[pd.DataFrame] = []
    registry = active_registry(bu).set_index("field_id")
    for source in sources or ["DCS", "Lab", "Field"]:
        frame = source_frame(bu, source)
        if frame.empty:
            continue
        fields = [column for column in frame.columns if column in registry.index]
        if not fields:
            continue
        identifiers = [column for column in storage.BASE_COLUMNS if column in frame.columns] + ["Timestamp"]
        view = frame.melt(id_vars=identifiers, value_vars=fields, var_name="field_id", value_name="value")
        view["value"] = pd.to_numeric(view["value"], errors="coerce")
        view["source"] = source
        view["field_name"] = view["field_id"].map(registry["field_name"])
        view["uom"] = view["field_id"].map(registry["uom"])
        view["target"] = pd.to_numeric(view["field_id"].map(registry["target"]), errors="coerce")
        items.append(view.dropna(subset=["value"]))
    return pd.concat(items, ignore_index=True) if items else pd.DataFrame()


def calculated_data(bu: str) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    dcs, field, lab = source_frame(bu, "DCS"), source_frame(bu, "Field"), source_frame(bu, "Lab")
    if dcs.empty:
        return pd.DataFrame(), pd.DataFrame(), []
    keys = [column for column in ["Date", "Time", "Business unit", "Plant", "Unit/Section", "Equipment", "Timestamp"] if column in dcs.columns]
    base = dcs.drop(columns=[column for column in ["Recorded by", "Recorded at"] if column in dcs.columns])
    if not field.empty:
        base = base.merge(field.drop(columns=[column for column in ["Recorded by", "Recorded at"] if column in field.columns]), on=keys, how="left")
    if not lab.empty:
        lab_daily = lab.drop(columns=[column for column in ["Time", "Plant", "Unit/Section", "Equipment", "Recorded by", "Recorded at", "Timestamp"] if column in lab.columns])
        base = base.merge(lab_daily, on=["Date", "Business unit"], how="left")
    definitions = storage.read_csv(storage.bu_dir(bu) / "calculated_fields.csv")
    constants = storage.json_setting(storage.bu_dir(bu) / "constants.json", {})
    out, errors = formula.apply_ordered(base, definitions.to_dict("records"), constants)
    return out, definitions, errors


def period_filter(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    if frame.empty or "Timestamp" not in frame.columns:
        return frame
    valid = frame["Timestamp"].dropna()
    if valid.empty:
        return frame
    low, high = valid.min().date(), valid.max().date()
    first, second = st.columns(2)
    start = first.date_input("Start Date", low, min_value=low, max_value=high, key=f"{key}_start")
    end = second.date_input("End Date", high, min_value=low, max_value=high, key=f"{key}_end")
    return frame[(frame["Timestamp"].dt.date >= start) & (frame["Timestamp"].dt.date <= end)]


def export_panel(frame: pd.DataFrame, title: str, bu: str, user: auth.User, key: str) -> None:
    with st.expander("Export", expanded=False):
        fmt = st.selectbox("Export Format", ["Excel", "CSV", "PDF"], key=f"{key}_fmt")
        if st.button("Prepare Export", key=f"{key}_prepare"):
            data, extension, mime = exports.build_export(fmt, title, frame, bu, user.username)
            st.session_state[f"{key}_export"] = (data, extension, mime, fmt)
            st.success("Export prepared and recorded in the audit log.")
        if f"{key}_export" in st.session_state:
            data, extension, mime, saved_fmt = st.session_state[f"{key}_export"]
            st.download_button(f"Download {saved_fmt}", data, f"{title.lower().replace(' ', '_')}.{extension}", mime, key=f"{key}_download")


def template_selector(bu: str, module: str, key: str) -> dict[str, Any]:
    templates = dashboard.load_templates(bu)[module]
    labels = [template["name"] for template in templates]
    selected = st.selectbox("Dashboard Template", labels, key=f"{key}_template")
    return next(template for template in templates if template["name"] == selected)


def chart_controls(default_chart: str, key: str) -> tuple[str, str]:
    first, second = st.columns(2)
    chart_type = first.selectbox("Chart Type", dashboard.CHART_TYPES, index=dashboard.CHART_TYPES.index(default_chart) if default_chart in dashboard.CHART_TYPES else 0, key=f"{key}_chart_type")
    axis_mode = second.selectbox("Axis Layout", dashboard.AXIS_MODES, key=f"{key}_axis_mode", help="Split uses one chart and y-axis per field. Same axis overlays fields for direct comparison.")
    return chart_type, axis_mode


def kpi_cards(frame: pd.DataFrame, definitions: pd.DataFrame, period: bool = False) -> None:
    if frame.empty or definitions.empty:
        st.info("No calculated KPI data is available.")
        return
    active = definitions[(definitions["status"].str.lower() != "disabled") & (definitions["dashboard"].str.lower() == "true")].head(8)
    records = list(active.iterrows())
    for start in range(0, len(records), 4):
        columns = st.columns(4, gap="medium")
        for column, (_, item) in zip(columns, records[start:start + 4]):
            method = item["aggregation"] if period else "Latest"
            value = formula.aggregate(frame[item["field_id"]], method) if item["field_id"] in frame else None
            target_key = "period_target" if period else "daily_target"
            target = pd.to_numeric(item[target_key], errors="coerce")
            status, variance = formula.target_status(value, None if pd.isna(target) else float(target), item["target_direction"])
            bad = status == "Off Target"
            with column:
                st.markdown(
                    f'<div class="metric-card {"bad" if bad else ""}"><div class="metric-title">{item["field_name"]}</div>'
                    f'<div class="metric-value">{"—" if value is None else f"{value:,.2f}"}</div>'
                    f'<div class="metric-meta">{item["uom"]} · Target {"—" if pd.isna(target) else f"{target:,.2f}"}</div>'
                    f'<span class="badge-{"bad" if bad else "good" if status == "On Target" else "neutral"}">{status}</span>'
                    f'<div class="small-note">Variance {"—" if variance is None else f"{variance:+,.2f}"}</div></div>',
                    unsafe_allow_html=True,
                )
        st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)


def page_home(bu: str, user: auth.User) -> None:
    hero("OPERA Home", "Operational intelligence · Reliability · Continuous improvement")
    data = long_data(bu)
    events = storage.read_csv(storage.bu_dir(bu) / "events.csv")
    flags = storage.read_csv(storage.bu_dir(bu) / "flags.csv")
    lessons = storage.read_csv(storage.bu_dir(bu) / "lessons.csv")
    columns = st.columns(5)
    values = [
        len(data), len(flags[flags.get("status", "") == "Open"]) if not flags.empty else 0,
        len(events), len(lessons), len(storage.unread_notifications(bu, user.username)),
    ]
    for column, label, value in zip(columns, ["Readings", "Open Flags", "Events", "Lessons", "Unread Notifications"], values):
        column.metric(label, f"{value:,}")
    st.markdown("### Operating Flow")
    st.markdown('<div class="flow"><b>Data Input</b> → validation and flags → <b>Event Log</b> → <b>Data Analysis</b> → <b>Data Output</b> → audited export</div>', unsafe_allow_html=True)
    st.markdown("### Modules")
    cards = [
        ("Plant Overview", "Plant-level trends, conditions and period reports"),
        ("Equipment Overview", "Equipment trends using configurable dashboard templates"),
        ("Operations Dashboard", "Aligned KPI cards, targets, period views and chart grids"),
        ("Risk Assessment", "Register-backed deterministic hazard assessment"),
        ("Lesson Bank", "Independent lessons with optional event references"),
        ("Admin", "No-code fields, charts, templates, equipment and validation lists"),
    ]
    for start in range(0, len(cards), 3):
        cols = st.columns(3, gap="medium")
        for col, (title, text) in zip(cols, cards[start:start + 3]):
            col.markdown(f'<div class="module-card"><strong>{title}</strong><p>{text}</p></div>', unsafe_allow_html=True)


def page_plant(bu: str, user: auth.User) -> None:
    hero("Plant Overview", "Select a plant, period and template to review operating conditions")
    data = long_data(bu)
    equipment = storage.equipment(bu)
    plants = sorted(equipment[equipment["placeholder"].str.lower() != "true"]["plant"].dropna().unique())
    if not plants:
        st.info("No plants are configured.")
        return
    plant = st.selectbox("Plant", plants)
    template = template_selector(bu, "Plant Overview", "plant")
    if data.empty:
        st.info("No operational data is available.")
        return
    view = period_filter(data[data["Plant"] == plant], "plant")
    if view.empty:
        st.info("This plant is configured, but it has no readings in the selected period.")
        return
    available = set(view["field_id"].astype(str))
    chart_fields = [field for field in template.get("chart_fields", []) if field in available]
    if not chart_fields:
        chart_fields = list(view.groupby("field_id")["value"].count().sort_values(ascending=False).head(6).index)
    chart_type, axis_mode = chart_controls(template.get("chart_type", "Line"), "plant")
    st.markdown("### Charts")
    dashboard.render_chart_grid(view, chart_fields, chart_type, axis_mode, "plant")
    table_fields = [field for field in template.get("table_fields", []) if field in available] or chart_fields
    summary = view[view["field_id"].isin(table_fields)].groupby(["field_id", "field_name", "uom"], as_index=False).agg(Average=("value", "mean"), Minimum=("value", "min"), Maximum=("value", "max"), Readings=("value", "count"))
    summary["Target"] = summary["field_id"].map(active_registry(bu).set_index("field_id")["target"])
    st.markdown("### Data Table")
    st.dataframe(summary, width="stretch", hide_index=True)
    export_panel(summary, f"{plant} Plant Overview", bu, user, "plant")


def page_equipment(bu: str, user: auth.User) -> None:
    hero("Equipment Overview", "Select equipment, period and a configurable dashboard template")
    data = long_data(bu)
    equipment = storage.equipment(bu)
    equipment = equipment[(equipment["active"].str.lower() == "true") & (equipment["placeholder"].str.lower() != "true")]
    if equipment.empty:
        st.info("No active equipment is configured.")
        return
    plant = st.selectbox("Plant", sorted(equipment["plant"].unique()), key="equipment_plant")
    section = st.selectbox("Unit / Section", sorted(equipment[equipment["plant"] == plant]["unit_section"].unique()), key="equipment_section")
    options = equipment[(equipment["plant"] == plant) & (equipment["unit_section"] == section)]
    label = st.selectbox("Equipment", options.apply(lambda row: f"{row['equipment_id']} — {row['equipment_name']}", axis=1))
    equipment_id = label.split(" — ", 1)[0]
    template = template_selector(bu, "Equipment Overview", "equipment")
    if data.empty:
        st.info("No operational data is available.")
        return
    view = period_filter(data[data["Equipment"] == equipment_id], "equipment")
    if view.empty:
        st.info("No readings are assigned to this equipment in the selected period.")
        return
    available = set(view["field_id"].astype(str))
    chart_fields = [field for field in template.get("chart_fields", []) if field in available]
    if not chart_fields:
        chart_fields = list(view.groupby("field_id")["value"].count().sort_values(ascending=False).head(6).index)
    chart_type, axis_mode = chart_controls(template.get("chart_type", "Line"), "equipment")
    st.markdown("### Charts")
    dashboard.render_chart_grid(view, chart_fields, chart_type, axis_mode, "equipment")
    table_fields = [field for field in template.get("table_fields", []) if field in available] or chart_fields
    summary = view[view["field_id"].isin(table_fields)].groupby(["field_id", "field_name", "uom"], as_index=False)["value"].agg(["mean", "min", "max", "std"]).reset_index()
    summary.columns = ["Field ID", "Data Field", "UOM", "Average", "Minimum", "Maximum", "Standard Deviation"]
    st.markdown("### Data Table")
    st.dataframe(summary, width="stretch", hide_index=True)
    export_panel(summary, f"{equipment_id} {template['name']}", bu, user, "equipment")


def operations_long(view: pd.DataFrame, definitions: pd.DataFrame, field_ids: list[str], granularity: str) -> pd.DataFrame:
    fields = [field for field in field_ids if field in view.columns]
    if not fields:
        return pd.DataFrame()
    rule = {"Daily": "D", "Weekly": "W", "Monthly": "ME", "Yearly": "YE"}[granularity]
    trend = view[["Timestamp"] + fields].copy().set_index("Timestamp").apply(pd.to_numeric, errors="coerce")
    trend = trend.resample(rule).mean().reset_index().melt("Timestamp", var_name="field_id", value_name="value")
    metadata = definitions.set_index("field_id")
    trend["field_name"] = trend["field_id"].map(metadata["field_name"])
    trend["uom"] = trend["field_id"].map(metadata["uom"])
    return trend.dropna(subset=["value"])


def page_operations(bu: str, user: auth.User) -> None:
    hero("Operations Dashboard", "Aligned KPI cards · Configurable data fields · Grid charts · Period reports")
    frame, definitions, errors = calculated_data(bu)
    if errors:
        st.warning("Formula warnings: " + " | ".join(errors))
    if frame.empty:
        st.info("No DCS data is available.")
        return
    template = template_selector(bu, "Operations Dashboard", "operations")
    view = period_filter(frame, "operations")
    mode = template.get("period_mode", template.get("name", "Selected Period"))
    if mode == "Month-to-Date" and not view.empty:
        last = view["Timestamp"].max()
        view = view[(view["Timestamp"].dt.year == last.year) & (view["Timestamp"].dt.month == last.month)]
    elif mode == "Year-to-Date" and not view.empty:
        last = view["Timestamp"].max()
        view = view[view["Timestamp"].dt.year == last.year]
    period = mode in {"Period Total", "Month-to-Date", "Year-to-Date"}
    st.markdown("### Key Performance Indicators")
    kpi_cards(view, definitions, period)
    granularity = st.selectbox("Trend Granularity", ["Daily", "Weekly", "Monthly", "Yearly"])
    chart_type, axis_mode = chart_controls(template.get("chart_type", "Line"), "operations")
    chart_fields = [field for field in template.get("chart_fields", []) if field in view.columns]
    trend = operations_long(view, definitions, chart_fields, granularity)
    st.markdown("### Charts")
    dashboard.render_chart_grid(trend, chart_fields, chart_type, axis_mode, "operations")
    table_fields = [field for field in template.get("table_fields", []) if field in view.columns]
    if not table_fields:
        table_fields = [field for field in definitions["field_id"] if field in view.columns][:8]
    records = []
    for field_id in table_fields:
        row = definitions[definitions["field_id"] == field_id].iloc[0]
        method = row.get("mtd_aggregation", row["aggregation"]) if mode == "Month-to-Date" else row.get("ytd_aggregation", row["aggregation"]) if mode == "Year-to-Date" else row["aggregation"]
        records.append({"KPI": row["field_name"], "Value": formula.aggregate(view[field_id], method), "Target": row["period_target"], "UOM": row["uom"], "Status": row["status"]})
    report = pd.DataFrame(records)
    st.markdown("### Data Table")
    st.dataframe(report, width="stretch", hide_index=True)
    st.markdown("#### Report Sign-Off")
    first, second, third = st.columns(3)
    prepared = first.text_input("Prepared By", user.display_name)
    reviewed = second.text_input("Reviewed By")
    remarks = third.text_input("Remarks")
    report["Prepared By"], report["Reviewed By"], report["Remarks"] = prepared, reviewed, remarks
    export_panel(report, f"{template['name']} Operations Report", bu, user, "operations")
    with st.expander("Save Dashboard Preset"):
        name = st.text_input("Preset Name", key="ops_preset_name")
        if st.button("Save Preset", key="ops_save_preset") and name:
            config.save_preset(bu, name, {"module": "Operations Dashboard", "template": template["id"], "granularity": granularity, "axis_mode": axis_mode}, user.username)
            st.success("Preset saved.")


def page_input(bu: str, user: auth.User) -> None:
    hero("Data Input", "Manual Lab and Field input · Validated bulk upload · DCS pipeline connector")
    if not auth.allowed(user, "input"):
        st.warning("Your role is view-only.")
        return
    manual, bulk, pipeline = st.tabs(["Manual Entry", "Bulk Upload", "DCS Pipeline"])
    with manual:
        source = st.selectbox("Source", list(storage.SOURCES), index=2)
        registry = active_registry(bu, source)
        if registry.empty:
            st.info("No active fields are configured for this source. A BU Admin can activate fields in Admin.")
        else:
            equipment = storage.equipment(bu)
            equipment = equipment[equipment["active"].str.lower() == "true"]
            field_options = {f"{row.field_id} — {row.field_name} ({row.uom})": row.field_id for row in registry.itertuples()}
            selected = st.multiselect("Data Fields", list(field_options), default=list(field_options)[:3])
            equipment_label = st.selectbox("Equipment", equipment.apply(lambda row: f"{row['equipment_id']} — {row['equipment_name']}", axis=1))
            equipment_id = equipment_label.split(" — ", 1)[0]
            equipment_row = equipment[equipment["equipment_id"] == equipment_id].iloc[0]
            with st.form("manual_input"):
                first, second = st.columns(2)
                day = first.date_input("Date", date.today())
                time_value = second.time_input("Time", datetime.now().replace(minute=0, second=0, microsecond=0).time())
                values = {field_options[label]: st.number_input(label, value=None, placeholder="Enter value") for label in selected}
                save = st.form_submit_button("Validate and Save", type="primary")
            if save:
                row = {"Date": day.isoformat(), "Time": time_value.strftime("%H:%M"), "Business unit": bu, "Plant": equipment_row["plant"], "Unit/Section": equipment_row["unit_section"], "Equipment": equipment_id, **values}
                clean, issues, flags = storage.validate_rows(bu, source, pd.DataFrame([row]))
                if not issues.empty:
                    st.error("Validation failed.")
                    st.dataframe(issues, hide_index=True)
                else:
                    count, flag_count = storage.save_validated_input(bu, source, clean, user.username)
                    storage.notify(bu, f"{count} {source} row saved ({flag_count} flags).", "error" if flag_count else "success", created_by=user.username)
                    st.success(f"Saved {count} row; {flag_count} validation flag(s).")
    with bulk:
        source = st.selectbox("Source", list(storage.SOURCES), key="bulk_source")
        st.download_button("Download CSV Template", storage.template_bytes(bu, source), f"{bu}_{source}_template.csv", "text/csv")
        upload = st.file_uploader("Upload Completed CSV or Excel", type=["csv", "xlsx"], key="bulk_file")
        if upload:
            try:
                frame = pd.read_csv(upload, dtype=str, keep_default_na=False) if upload.name.lower().endswith(".csv") else pd.read_excel(upload, dtype=str).fillna("")
                clean, issues, flags = storage.validate_rows(bu, source, frame)
                st.markdown("#### Validation Report")
                if issues.empty:
                    st.success(f"{len(clean)} rows passed structural validation.")
                else:
                    st.dataframe(issues, width="stretch", hide_index=True)
                if not flags.empty:
                    st.warning(f"{len(flags)} value(s) will be flagged but may still be saved.")
                    st.dataframe(flags, hide_index=True)
                if st.button("Save Validated Rows", disabled=not issues.empty, type="primary"):
                    count, flag_count = storage.save_validated_input(bu, source, clean, user.username)
                    storage.audit(bu, user.username, "bulk_upload", {"source": source, "rows": count, "flags": flag_count})
                    st.success(f"Saved {count} rows.")
            except Exception as exc:
                st.error(f"Upload could not be read: {exc}")
    with pipeline:
        settings = storage.json_setting(storage.bu_dir(bu) / "pipeline.json", {})
        st.code(settings.get("url") or "DCS endpoint not configured")
        if st.button("Pull DCS Data Now", disabled=not bool(settings.get("url"))):
            try:
                token = ""
                if settings.get("token_secret_name"):
                    token = str(st.secrets.get("dcs", {}).get(settings["token_secret_name"], ""))
                count, flag_count = dcs_connector.ingest(bu, settings["url"], token, user.username)
                st.success(f"Ingested {count} rows; {flag_count} flags.")
            except Exception as exc:
                st.error(f"DCS pull failed: {exc}")


def page_events(bu: str, user: auth.User) -> None:
    hero("Event Log", "Filter, print and export events · Optional Field Data update · Pictures · Notifications")
    events = storage.read_csv(storage.bu_dir(bu) / "events.csv")
    view_tab, input_tab = st.tabs(["View Event Log", "Input Event"])
    with view_tab:
        if events.empty:
            st.info("No events have been logged.")
        else:
            types = sorted(set(";".join(events["event_types"]).split(";")))
            selected = st.multiselect("Event Type", [item for item in types if item])
            view = events if not selected else events[events["event_types"].apply(lambda value: any(item in value.split(";") for item in selected))]
            first, second = st.columns(2)
            start = first.date_input("From", pd.to_datetime(view["event_date"]).min().date(), key="event_from")
            end = second.date_input("To", pd.to_datetime(view["event_date"]).max().date(), key="event_to")
            dates = pd.to_datetime(view["event_date"], errors="coerce").dt.date
            view = view[(dates >= start) & (dates <= end)]
            st.dataframe(view, width="stretch", hide_index=True)
            export_panel(view, "Event Log", bu, user, "events")
    with input_tab:
        if not auth.allowed(user, "events"):
            st.warning("Your role cannot create events.")
        else:
            event_types = ["Safety", "Process Deviation", "Equipment Failure", "Quality", "Environmental", "Shutdown", "Other"]
            selected_types = st.multiselect("Event Type(s)", event_types)
            event_format = st.radio("Event Format", ["Report", "Data Table", "Picture"], horizontal=True)
            equipment = storage.equipment(bu)
            equipment = equipment[equipment["active"].str.lower() == "true"]
            equipment_label = st.selectbox("Equipment", equipment.apply(lambda row: f"{row['equipment_id']} — {row['equipment_name']}", axis=1), key="event_eq")
            equipment_id = equipment_label.split(" — ", 1)[0]
            equipment_row = equipment[equipment["equipment_id"] == equipment_id].iloc[0]
            picture = st.file_uploader("Picture Attachment", type=["png", "jpg", "jpeg", "webp"], disabled=event_format != "Picture")
            send_field_update = st.checkbox("Send a Field Data Update With This Event", value=False)
            field_registry = active_registry(bu, "Field")
            field_options = {f"{row.field_id} — {row.field_name} ({row.uom})": row.field_id for row in field_registry.itertuples()}
            selected_fields = st.multiselect("Field Data Fields", list(field_options), disabled=not send_field_update, help="Choose any active F field to store with the event for later comparison with DCS data.")
            with st.form("event_input"):
                first, second = st.columns(2)
                day = first.date_input("Event Date", date.today())
                time_value = second.time_input("Event Time", datetime.now().replace(second=0, microsecond=0).time())
                title = st.text_input("Title")
                details = st.text_area("Report / Table Data / Observations")
                field_values = {field_options[label]: st.number_input(label, value=None, placeholder="Enter Field reading") for label in selected_fields}
                send_notification = st.checkbox("Send Notification", value=True)
                submit = st.form_submit_button("Save Event", type="primary")
            if submit:
                if not selected_types or not title.strip():
                    st.error("Select an event type and enter a title.")
                elif send_field_update and (not selected_fields or not any(value is not None for value in field_values.values())):
                    st.error("Select at least one Field Data field and enter a value.")
                else:
                    update_frame = pd.DataFrame()
                    if send_field_update:
                        update_frame = pd.DataFrame([{"Date": day.isoformat(), "Time": time_value.strftime("%H:%M"), "Business unit": bu, "Plant": equipment_row["plant"], "Unit/Section": equipment_row["unit_section"], "Equipment": equipment_id, **field_values}])
                        clean, issues, _ = storage.validate_rows(bu, "Field", update_frame)
                        if not issues.empty:
                            st.error("The Field Data update was not saved because validation failed.")
                            st.dataframe(issues, hide_index=True)
                            return
                        storage.save_validated_input(bu, "Field", clean, user.username)
                    picture_path = storage.save_attachment(bu, picture.name, picture.getvalue()) if picture else ""
                    event_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"
                    row = {"event_id": event_id, "timestamp": storage.utcnow(), "event_date": day.isoformat(), "event_time": time_value.strftime("%H:%M"), "event_types": ";".join(selected_types), "format": event_format, "plant": equipment_row["plant"], "unit_section": equipment_row["unit_section"], "equipment": equipment_id, "title": title, "details": details, "picture_path": picture_path, "reported_by": user.display_name, "notification_sent": str(send_notification).lower(), "field_update_sent": str(send_field_update).lower(), "field_update_ids": ";".join(field_values)}
                    storage.append_rows(storage.bu_dir(bu) / "events.csv", [row])
                    storage.audit(bu, user.username, "event_created", {"event_id": event_id, "types": selected_types, "field_update": list(field_values)})
                    if send_notification:
                        critical = any(item in selected_types for item in ["Safety", "Equipment Failure", "Shutdown"])
                        storage.notify(bu, f"New event {event_id}: {title}", "error" if critical else "success", created_by=user.username)
                    st.success(f"Event {event_id} saved" + (" with a Field Data update." if send_field_update else "."))


def page_analysis(bu: str, user: auth.User) -> None:
    hero("Data Analysis", "Compare fields on one axis or in an individual-axis chart grid · Field vs DCS")
    data = long_data(bu)
    compare, dcs_tab = st.tabs(["Field Comparison", "Field vs DCS"])
    with compare:
        if data.empty:
            st.info("No data is available.")
        else:
            registry = active_registry(bu)
            label_map = dashboard.field_label_map(registry)
            available_ids = list(dict.fromkeys(data["field_id"].astype(str).tolist()))
            labels = [label_map[field] for field in available_ids if field in label_map]
            selected_labels = st.multiselect("Select at Least Two Data Fields", labels, default=labels[:2])
            selected_ids = [label.split(" — ", 1)[0] for label in selected_labels]
            analysis = st.selectbox("Analysis Type", ["Trend", "Prediction", "Mean", "Average", "Standard Deviation", "Minimum / Maximum"])
            chart_type, axis_mode = chart_controls("Line", "analysis")
            view = period_filter(data[data["field_id"].isin(selected_ids)], "analysis") if selected_ids else pd.DataFrame()
            if len(selected_ids) < 2:
                st.info("Select two or more fields.")
            elif not view.empty:
                dashboard.render_chart_grid(view, selected_ids, chart_type, axis_mode, "analysis")
                summary = view.groupby(["field_id", "field_name", "uom"])["value"].agg(["count", "mean", "std", "min", "max"]).reset_index()
                if analysis == "Prediction":
                    horizon = st.slider("Forecast Horizon (Periods)", 1, 30, 7)
                    forecasts = []
                    for (field_id, name), group in view.groupby(["field_id", "field_name"]):
                        values = group.sort_values("Timestamp")["value"].dropna().to_numpy()
                        x = np.arange(len(values))
                        if len(values) >= 2:
                            slope, intercept = np.polyfit(x, values, 1)
                            forecasts.append({"Field ID": field_id, "Data Field": name, "Trend Slope": slope, "Forecast End": intercept + slope * (len(values) + horizon - 1)})
                    st.dataframe(pd.DataFrame(forecasts), hide_index=True)
                st.dataframe(summary, width="stretch", hide_index=True)
                export_panel(summary, f"{analysis} Analysis", bu, user, "analysis")
    with dcs_tab:
        field_registry = active_registry(bu, "Field")
        dcs_registry = active_registry(bu, "DCS")
        field_label = st.selectbox("Field Reading", field_registry.apply(lambda row: f"{row['field_id']} — {row['field_name']}", axis=1))
        dcs_label = st.selectbox("DCS Reading", dcs_registry.apply(lambda row: f"{row['field_id']} — {row['field_name']}", axis=1))
        monitor = st.number_input("Monitor Difference", min_value=0.0, value=5.0)
        critical = st.number_input("Critical Difference", min_value=monitor, value=max(10.0, monitor))
        exclude_shutdown = st.checkbox("Exclude Shutdown Days", value=True)
        field_id, dcs_id = field_label.split(" — ", 1)[0], dcs_label.split(" — ", 1)[0]
        field_frame, dcs_frame = source_frame(bu, "Field"), source_frame(bu, "DCS")
        keys = ["Date", "Time", "Equipment"]
        comparison = field_frame[keys + [field_id]].merge(dcs_frame[keys + [dcs_id]], on=keys, how="inner") if field_id in field_frame and dcs_id in dcs_frame else pd.DataFrame()
        if exclude_shutdown and not comparison.empty:
            events = storage.read_csv(storage.bu_dir(bu) / "events.csv")
            shutdown = set(events[events["event_types"].str.contains("Shutdown", case=False, na=False)]["event_date"]) if not events.empty else set()
            comparison = comparison[~comparison["Date"].isin(shutdown)]
        if not comparison.empty:
            comparison["Difference"] = (pd.to_numeric(comparison[field_id], errors="coerce") - pd.to_numeric(comparison[dcs_id], errors="coerce")).abs()
            comparison["Status"] = np.select([comparison["Difference"] >= critical, comparison["Difference"] >= monitor], ["Critical", "Monitor"], default="Normal")
            comparison["Timestamp"] = pd.to_datetime(comparison["Date"] + " " + comparison["Time"], errors="coerce")
            chart = comparison.melt(id_vars=["Timestamp"], value_vars=[field_id, dcs_id], var_name="field_id", value_name="value")
            names = {field_id: field_label.split(" — ", 1)[1], dcs_id: dcs_label.split(" — ", 1)[1]}
            units = pd.concat([field_registry, dcs_registry]).set_index("field_id")["uom"].to_dict()
            chart["field_name"] = chart["field_id"].map(names)
            chart["uom"] = chart["field_id"].map(units)
            chart_type, axis_mode = chart_controls("Line", "field_dcs")
            dashboard.render_chart_grid(chart, [field_id, dcs_id], chart_type, axis_mode, "field_dcs")
            st.dataframe(comparison, width="stretch", hide_index=True)
            export_panel(comparison, "Field vs DCS", bu, user, "field_dcs")
        else:
            st.info("No paired readings are available for this selection.")


def page_output(bu: str, user: auth.User) -> None:
    hero("Data Output", "Calculated fields · Selected-duration results · Input, calculated and merged Excel downloads")
    frame, definitions, errors = calculated_data(bu)
    if errors:
        st.warning(" | ".join(errors))
    if frame.empty:
        st.info("No data is available.")
        return
    view = period_filter(frame, "output")
    choices = definitions.apply(lambda row: f"{row['field_id']} — {row['field_name']}", axis=1).tolist()
    selected = st.multiselect("Calculated Fields", choices, default=choices[:4])
    method = st.selectbox("Calculate", ["Average", "Maximum", "Minimum"])
    rows = []
    for label in selected:
        field_id = label.split(" — ", 1)[0]
        metadata = definitions[definitions["field_id"] == field_id].iloc[0]
        value = formula.aggregate(view[field_id], method) if field_id in view else None
        target = float(metadata["period_target"]) if metadata["period_target"] else None
        status, variance = formula.target_status(value, target, metadata["target_direction"])
        rows.append({"Business Unit": bu, "Calculated Field": field_id, "Name": metadata["field_name"], method: value, "UOM": metadata["uom"], "Target": metadata["period_target"], "Variance": variance, "Status": status})
    result = pd.DataFrame(rows)
    st.dataframe(result, width="stretch", hide_index=True)
    export_panel(result, "Calculated Data Output", bu, user, "output")
    st.markdown("#### Complete Excel Workbooks")
    if st.button("Prepare Input, Calculated and Merged Excel"):
        inputs = storage.input_data(bu, list(storage.SOURCES))
        calculated_columns = [column for column in definitions["field_id"] if column in frame.columns]
        payload = exports.excel_bytes({"Input": inputs, "Calculated": frame[[column for column in storage.BASE_COLUMNS if column in frame] + calculated_columns], "Merged": frame})
        storage.audit(bu, user.username, "export_prepared", {"title": "Input Calculated Merged", "format": "Excel"})
        st.session_state.full_excel = payload
    if "full_excel" in st.session_state:
        st.download_button("Download Complete Excel", st.session_state.full_excel, f"{bu}_input_calculated_merged.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def page_parameters(bu: str, user: auth.User) -> None:
    hero("Operating Parameters", "Process and quality trends, tables, summaries and exports")
    process, quality = st.tabs(["Process", "Quality"])
    with process:
        data = long_data(bu, ["DCS", "Field"])
        if data.empty:
            st.info("No process data is available.")
        else:
            equipment = st.selectbox("Equipment", sorted(data["Equipment"].unique()), key="proc_eq")
            base = data[data["Equipment"] == equipment]
            fields = list(base.groupby("field_id")["value"].count().sort_values(ascending=False).head(8).index)
            registry = active_registry(bu)
            labels = dashboard.field_label_map(registry)
            selected_labels = st.multiselect("Data Fields", [labels[field] for field in fields if field in labels], default=[labels[field] for field in fields[:4] if field in labels], key="proc_fields")
            selected_ids = [label.split(" — ", 1)[0] for label in selected_labels]
            view = period_filter(base[base["field_id"].isin(selected_ids)], "process_params")
            view_format = st.selectbox("View Format", ["Trend", "Table", "Summary"], key="proc_view")
            if view_format == "Trend":
                chart_type, axis_mode = chart_controls("Line", "process_params")
                dashboard.render_chart_grid(view, selected_ids, chart_type, axis_mode, "process_params")
            elif view_format == "Table":
                st.dataframe(view, width="stretch", hide_index=True)
            else:
                st.dataframe(view.groupby(["field_id", "field_name", "uom"])["value"].agg(["mean", "min", "max"]).reset_index(), hide_index=True)
            export_panel(view, "Process Operating Parameters", bu, user, "proc_params")
    with quality:
        data = long_data(bu, ["Lab"])
        if data.empty:
            st.info("No quality data is available.")
        else:
            fields = sorted(data["field_name"].unique())
            selected_fields = st.multiselect("Data Fields", fields, default=fields[:2], key="quality_fields")
            view = period_filter(data[data["field_name"].isin(selected_fields)], "quality_params")
            view_format = st.selectbox("View Format", ["Trend", "Table", "Distribution"], key="qual_view")
            if view_format in {"Trend", "Distribution"}:
                chart_type, axis_mode = chart_controls("Line" if view_format == "Trend" else "Box Plot", "quality_params")
                dashboard.render_chart_grid(view, list(view["field_id"].unique()), chart_type, axis_mode, "quality_params")
            else:
                st.dataframe(view, width="stretch", hide_index=True)
            export_panel(view, "Quality Operating Parameters", bu, user, "qual_params")


def page_risk(bu: str, user: auth.User) -> None:
    hero("Risk Assessment", "Select a preset and job type, review identified risks, then print or export")
    register, source, problem = risk_store.resolve(bu)
    if not register:
        st.warning(problem or "Risk register update required.")
        return
    st.caption(f"{source} · {register.hazard_count} hazards · Fingerprint {register.fingerprint}")
    preset_names = {f"{preset['id']} — {preset['n']}": preset for preset in register.presets}
    preset_label = st.selectbox("Preset", list(preset_names) or ["Custom"])
    preset = preset_names.get(preset_label, {"tags": [], "et": "", "mo": "Running", "st": "Operational", "loc": "", "ref": "", "n": "Custom"})
    description = st.text_area("Job Description", value=preset.get("d", ""))
    suggested = suggest_from_text(register, description) if description else {"tags": []}
    tags = st.multiselect("Job Type / Activities", register.tag_names, default=[tag for tag in (preset.get("tags") or suggested.get("tags", [])) if tag in register.tag_names])
    locations = [item["n"] for item in register.locations]
    location_index = locations.index(preset["loc"]) if preset.get("loc") in locations else 0
    location = st.selectbox("Location", locations, index=location_index)
    available = [equipment for equipment in register.equipment if register.available(equipment, location)]
    equipment_names = [equipment["n"] for equipment in available]
    equipment_index = equipment_names.index(preset["ref"]) if preset.get("ref") in equipment_names else 0
    equipment = st.selectbox("Equipment", equipment_names, index=equipment_index)
    equipment_record = register.equip(equipment)
    motion = st.selectbox("Equipment Motion", register.motions, index=register.motions.index(preset["mo"]) if preset.get("mo") in register.motions else 0)
    status = st.selectbox("Equipment Status", register.statuses, index=register.statuses.index(preset["st"]) if preset.get("st") in register.statuses else 0)
    if st.button("Generate Risk Assessment", type="primary"):
        hazards = collect_hazards(register, tags, equipment_record["t"] if equipment_record else None, motion, status)
        st.session_state.risk_hazards = hazards
        st.session_state.risk_context = {"preset": preset["n"], "description": description, "location": location, "equipment": equipment, "motion": motion, "status": status, "tags": tags}
        storage.audit(bu, user.username, "risk_assessment_generated", {"preset": preset["n"], "hazards": len(hazards)})
    hazards = st.session_state.get("risk_hazards", [])
    context = st.session_state.get("risk_context", {})
    if hazards:
        table = pd.DataFrame([{"ID": hazard["uid"], "Category": hazard["cat"], "Hazard": hazard["hz"], "Initial": hazard["lv"], "Controls": hazard["ct"], "Residual": hazard["rd"], "Responsible": hazard["rp"]} for hazard in hazards])
        st.dataframe(table, width="stretch", hide_index=True)
        excluded = st.multiselect("Review: Exclude Risks That Are Not Applicable", [hazard["uid"] for hazard in hazards])
        if st.button("Prepare Printable PDF"):
            now = datetime.now(timezone.utc)
            serial = make_serial(now, context.get("equipment", ""), "")
            payload = {"serial": serial, "bu": bu.title(), "company": "OPERA — DANGOTE INDUSTRIES", "form_title": "RISK ASSESSMENT FORM", "register_status": "Approved", "register_source": source, "fingerprint": register.fingerprint, "header": [("Assessment No.", serial), ("Preset / Job", context.get("preset")), ("Description", context.get("description")), ("Location", context.get("location")), ("Equipment", context.get("equipment")), ("Motion / Status", f"{context.get('motion')} / {context.get('status')}")], "hazards": hazards, "excluded": set(excluded), "categories": register.categories, "erp": ["Raise alarm and stop work.", "Make the area safe without personal exposure.", "Notify the control room and emergency response team.", "Provide first aid only when trained and safe."], "assessed_by": user.display_name, "reviewed_by": "", "generated": now.isoformat(timespec="seconds")}
            st.session_state.risk_pdf = build_pdf(payload)
            st.session_state.risk_serial = serial
            storage.append_rows(storage.bu_dir(bu) / "risk_assessments.csv", [{"serial": serial, "timestamp": storage.utcnow(), "preset": context.get("preset"), "job_type": ";".join(context.get("tags", [])), "location": context.get("location"), "equipment": context.get("equipment"), "hazard_count": len(hazards) - len(excluded), "assessed_by": user.username}])
            storage.audit(bu, user.username, "risk_assessment_exported", {"serial": serial, "format": "PDF"})
        if "risk_pdf" in st.session_state:
            st.download_button("Print / Download PDF", st.session_state.risk_pdf, f"{st.session_state.risk_serial}.pdf", "application/pdf")
        export_panel(table, "Risk Assessment Hazards", bu, user, "risk_table")


def page_lessons(bu: str, user: auth.User) -> None:
    hero("Lesson Bank", "Capture independent lessons and optionally reference an Event Log entry")
    lessons = storage.read_csv(storage.bu_dir(bu) / "lessons.csv")
    events = storage.read_csv(storage.bu_dir(bu) / "events.csv")
    review, entry = st.tabs(["Review Lessons", "Input Lesson"])
    with review:
        if lessons.empty:
            st.info("No lessons have been recorded.")
        else:
            units = sorted([item for item in lessons["unit_section"].unique() if item])
            unit = st.selectbox("Unit / Section", ["All"] + units)
            view = lessons if unit == "All" else lessons[lessons["unit_section"] == unit]
            links = ["All", "Unlinked"] + sorted([item for item in view["event_id"].unique() if item])
            event_filter = st.selectbox("Event Reference", links)
            if event_filter == "Unlinked":
                view = view[view["event_id"] == ""]
            elif event_filter != "All":
                view = view[view["event_id"] == event_filter]
            st.dataframe(view, width="stretch", hide_index=True)
    with entry:
        if not auth.allowed(user, "lessons"):
            st.warning("Your role cannot add lessons.")
        else:
            link_event = st.checkbox("Link This Lesson to an Event", value=False, disabled=events.empty)
            event_row = None
            if link_event and not events.empty:
                event_labels = {f"{row.event_id} — {row.title}": row for row in events.itertuples()}
                label = st.selectbox("Event", list(event_labels))
                event_row = event_labels[label]
                unit_section = event_row.unit_section
                st.caption(f"Unit / Section: {unit_section}")
            else:
                equipment = storage.equipment(bu)
                unit_options = sorted([item for item in equipment["unit_section"].unique() if item and item != "Unassigned"])
                unit_section = st.selectbox("Unit / Section", unit_options)
            lesson = st.text_area("Lesson Learned")
            if st.button("Save Lesson", type="primary") and lesson.strip():
                lesson_id = f"LES-{uuid.uuid4().hex[:8].upper()}"
                event_id = event_row.event_id if event_row else ""
                storage.append_rows(storage.bu_dir(bu) / "lessons.csv", [{"lesson_id": lesson_id, "timestamp": storage.utcnow(), "event_id": event_id, "unit_section": unit_section, "lesson": lesson, "entered_by": user.username}])
                storage.audit(bu, user.username, "lesson_created", {"lesson_id": lesson_id, "event_id": event_id or None})
                st.success(f"Lesson {lesson_id} saved" + (f" and linked to {event_id}." if event_id else " without an event link."))


def add_user_form(current: auth.User) -> None:
    with st.form("add_user"):
        username = st.text_input("Username").strip().lower()
        name = st.text_input("Display Name")
        role = st.selectbox("Role", ["BU Admin", "Operator", "Viewer", "Super Admin"])
        business_units = st.multiselect("Business Units", config.business_units()["id"].tolist())
        password = st.text_input("Temporary Password", type="password")
        submit = st.form_submit_button("Create User")
    if submit:
        if not username or len(password) < 12:
            st.error("Username and a 12-character temporary password are required.")
        else:
            path = storage.DATA_ROOT / "shared" / "users.csv"
            users = storage.read_csv(path)
            if username in set(users["username"]):
                st.error("Username already exists.")
            else:
                row = {"username": username, "display_name": name or username, "password_hash": auth.hash_password(password), "role": role, "business_units": "*" if role == "Super Admin" else ";".join(business_units), "active": "true", "must_change_password": "true", "failed_attempts": "0", "lock_until": ""}
                storage.atomic_write_csv(path, pd.concat([users, pd.DataFrame([row])], ignore_index=True))
                storage.audit("shared", current.username, "user_created", {"username": username, "role": role})
                st.success("User created.")


def template_admin(bu: str, user: auth.User) -> None:
    templates = dashboard.load_templates(bu)
    module = st.selectbox("Dashboard", list(templates))
    module_templates = templates[module]
    labels = [template["name"] for template in module_templates]
    selected_name = st.selectbox("Template", labels)
    index = labels.index(selected_name)
    selected = module_templates[index]
    if module == "Operations Dashboard":
        registry = storage.read_csv(storage.bu_dir(bu) / "calculated_fields.csv")[["field_id", "field_name", "uom"]]
    else:
        registry = active_registry(bu)[["field_id", "field_name", "uom"]]
    label_map = dashboard.field_label_map(registry)
    reverse = {label: field_id for field_id, label in label_map.items()}
    name = st.text_input("Template Name", selected["name"])
    chart_labels = st.multiselect("Data Fields Shown on Charts", list(reverse), default=[label_map[field] for field in selected.get("chart_fields", []) if field in label_map])
    table_labels = st.multiselect("Data Fields Shown in the Table", list(reverse), default=[label_map[field] for field in selected.get("table_fields", []) if field in label_map])
    chart_type = st.selectbox("Chart Type", dashboard.CHART_TYPES, index=dashboard.CHART_TYPES.index(selected.get("chart_type", "Line")) if selected.get("chart_type", "Line") in dashboard.CHART_TYPES else 0, key="admin_template_chart")
    if st.button("Save Dashboard Template", type="primary"):
        if not name.strip():
            st.error("Enter a template name.")
        else:
            selected["name"] = name.strip()
            selected["chart_fields"] = [reverse[label] for label in chart_labels]
            selected["table_fields"] = [reverse[label] for label in table_labels]
            selected["chart_type"] = chart_type
            module_templates[index] = selected
            templates[module] = module_templates
            dashboard.save_templates(bu, templates)
            storage.audit(bu, user.username, "dashboard_template_changed", {"module": module, "template": selected["id"]})
            st.success("Dashboard template saved.")


def equipment_admin(bu: str, user: auth.User) -> None:
    records_tab, lists_tab = st.tabs(["Equipment Records", "Validation Lists"])
    with lists_tab:
        options = dashboard.hierarchy_options(bu)
        plants_text = st.text_area("Plants (One per Line)", "\n".join(options["plants"]), height=140)
        units_text = st.text_area("Units / Sections (One per Line)", "\n".join(options["units"]), height=180)
        types_text = st.text_area("Equipment Types (One per Line)", "\n".join(options["equipment_types"]), height=180)
        if st.button("Save Validation Lists", type="primary"):
            dashboard.save_hierarchy_options(bu, {"plants": plants_text.splitlines(), "units": units_text.splitlines(), "equipment_types": types_text.splitlines()})
            storage.audit(bu, user.username, "equipment_validation_lists_changed")
            st.success("Validation lists saved. The equipment dropdowns now use these values.")
    with records_tab:
        equipment = storage.equipment(bu)
        mode = st.radio("Record Set", ["Spare Placeholders", "All Equipment"], horizontal=True)
        candidates = equipment[equipment["placeholder"].str.lower() == "true"] if mode == "Spare Placeholders" else equipment
        if candidates.empty:
            st.info("No equipment records are available for this selection.")
            return
        labels = candidates.apply(lambda row: f"{row['equipment_id']} — {row['equipment_name']}", axis=1).tolist()
        selected_label = st.selectbox("Equipment Record", labels)
        selected_id = selected_label.split(" — ", 1)[0]
        index = equipment[equipment["equipment_id"] == selected_id].index[0]
        row = equipment.loc[index]
        options = dashboard.hierarchy_options(bu)
        plants = sorted(set(options["plants"] + [row["plant"]]))
        units = sorted(set(options["units"] + [row["unit_section"]]))
        types = sorted(set(options["equipment_types"] + [row["equipment_type"]]))
        name = st.text_input("Equipment Name", row["equipment_name"])
        first, second, third = st.columns(3)
        plant = first.selectbox("Plant", plants, index=plants.index(row["plant"]))
        unit = second.selectbox("Unit / Section", units, index=units.index(row["unit_section"]))
        equipment_type = third.selectbox("Equipment Type", types, index=types.index(row["equipment_type"]))
        active = st.checkbox("Active", value=row["active"].lower() == "true")
        keep_placeholder = st.checkbox("Keep as Spare Placeholder", value=row["placeholder"].lower() == "true" and mode != "Spare Placeholders", help="Clear this when converting a spare into normal equipment.")
        if st.button("Save Equipment Record", type="primary") and name.strip():
            equipment.loc[index, ["equipment_name", "plant", "unit_section", "equipment_type", "active", "placeholder"]] = [name.strip(), plant, unit, equipment_type, str(active).lower(), str(keep_placeholder).lower()]
            storage.atomic_write_csv(storage.bu_dir(bu) / "equipment.csv", equipment)
            storage.audit(bu, user.username, "equipment_configuration_changed", selected_id)
            st.success("Equipment record saved with validated hierarchy values.")
        st.dataframe(equipment.head(100), width="stretch", hide_index=True)


def page_admin(bu: str, user: auth.User) -> None:
    hero("Admin / Super Admin", "Business units · Users · Fields · Dashboard templates · Equipment · Storage · Audit")
    if not auth.allowed(user, "configure"):
        st.warning("Administrator role required.")
        return
    tabs = st.tabs(["Business Units", "Users & Roles", "Fields & Formulas", "Dashboard Templates", "Equipment", "Risk Registers", "DCS Connector", "Presets", "Audit & Backup"])
    with tabs[0]:
        st.dataframe(config.business_units(), width="stretch", hide_index=True)
        if user.role == "Super Admin":
            st.markdown("#### Clone a Business Unit")
            source = st.selectbox("Template Business Unit", config.business_units()["id"].tolist())
            name = st.text_input("New Business Unit Name")
            active = st.checkbox("Activate Immediately")
            if st.button("Clone Business Unit") and name:
                try:
                    new = config.clone_business_unit(source, name, active, user.username)
                    st.success(f"Created {new}.")
                except Exception as exc:
                    st.error(str(exc))
            st.markdown("#### Name or Activate a Placeholder")
            target = st.selectbox("Business Unit", config.business_units()["id"].tolist(), key="edit_bu")
            new_name = st.text_input("Display Name", key="edit_bu_name")
            enabled = st.checkbox("Active", key="edit_bu_active")
            if st.button("Save Business Unit Configuration") and new_name:
                config.set_business_unit(target, new_name, enabled, user.username)
                st.success("Business unit updated.")
    with tabs[1]:
        users = storage.read_csv(storage.DATA_ROOT / "shared" / "users.csv")
        st.dataframe(users.drop(columns=["password_hash"]), width="stretch", hide_index=True)
        if user.role == "Super Admin":
            add_user_form(user)
    with tabs[2]:
        registry = storage.registry(bu)
        source_filter = st.selectbox("Source Registry", list(storage.SOURCES), key="admin_field_source")
        candidates = registry[registry["source"] == source_filter]
        field_label = st.selectbox("Input Field", candidates.apply(lambda row: f"{row['field_id']} — {row['field_name']}", axis=1))
        field_id = field_label.split(" — ", 1)[0]
        metadata = candidates[candidates["field_id"] == field_id].iloc[0]
        field_name = st.text_input("Data Field Name", metadata["field_name"])
        first, second, third, fourth = st.columns(4)
        uom = first.text_input("UOM", metadata["uom"])
        low = second.text_input("Minimum", metadata["min_value"])
        high = third.text_input("Maximum", metadata["max_value"])
        target = fourth.text_input("Target", metadata["target"])
        direction = st.selectbox("Target Interpretation", ["High", "Low"], index=0 if metadata["target_direction"] == "High" else 1)
        is_active = st.checkbox("Active Field", value=metadata["active"].lower() == "true", help="Activate TA–TG fields here before manual entry, calculation or export.")
        if st.button("Save Input Field"):
            index = registry[registry["field_id"] == field_id].index[0]
            registry.loc[index, ["field_name", "uom", "min_value", "max_value", "target", "target_direction", "active"]] = [field_name, uom, low, high, target, direction, str(is_active).lower()]
            storage.atomic_write_csv(storage.bu_dir(bu) / "fields.csv", registry)
            storage.audit(bu, user.username, "field_configuration_changed", field_id)
            st.success("Input field updated.")
        st.markdown("#### Calculated Fields")
        definitions = storage.read_csv(storage.bu_dir(bu) / "calculated_fields.csv")
        st.dataframe(definitions, width="stretch", hide_index=True)
        if not definitions.empty:
            calculated_field = st.selectbox("Calculated Field", definitions["field_id"])
            row = definitions[definitions["field_id"] == calculated_field].iloc[0]
            calculated_name = st.text_input("Calculated Field Name", row["field_name"])
            expression = st.text_input("Formula", row["formula"])
            status = st.selectbox("Status", ["active", "on hold", "disabled"], index=["active", "on hold", "disabled"].index(row["status"]) if row["status"] in ["active", "on hold", "disabled"] else 0)
            if st.button("Save Calculated Field"):
                index = definitions[definitions["field_id"] == calculated_field].index[0]
                definitions.loc[index, ["field_name", "formula", "status"]] = [calculated_name, expression, status]
                storage.atomic_write_csv(storage.bu_dir(bu) / "calculated_fields.csv", definitions)
                storage.audit(bu, user.username, "formula_configuration_changed", calculated_field)
                st.success("Calculated field updated.")
        st.markdown("#### Baseline Constants")
        constants = storage.json_setting(storage.bu_dir(bu) / "constants.json", {})
        constant_text = st.text_area("JSON Constants", json.dumps(constants, indent=2), height=140, help="Reference a constant by key in a formula, for example B_capacity.")
        if st.button("Save Baseline Constants"):
            try:
                parsed = json.loads(constant_text)
                if not isinstance(parsed, dict) or not all(isinstance(value, (int, float)) for value in parsed.values()):
                    raise ValueError("Use a JSON object with numeric values.")
                storage.save_json(storage.bu_dir(bu) / "constants.json", parsed)
                storage.audit(bu, user.username, "baseline_constants_changed", {"keys": list(parsed)})
                st.success("Baseline constants saved.")
            except Exception as exc:
                st.error(str(exc))
    with tabs[3]:
        template_admin(bu, user)
    with tabs[4]:
        equipment_admin(bu, user)
    with tabs[5]:
        register, source, problem = risk_store.resolve(bu)
        st.write(f"Current: {source or problem}")
        st.write(f"Fingerprint: {register.fingerprint if register else '—'}")
        upload = st.file_uploader("Upload Approved Excel Risk Register", type=["xlsx"], key="risk_upload")
        note = st.text_input("Change Note")
        if upload and st.button("Validate and Activate Register"):
            try:
                risk_store.activate(bu, upload.getvalue(), user.username, note)
                st.success("Register validated and activated.")
            except Exception as exc:
                st.error(f"Register was not changed: {exc}")
        try:
            github = dict(st.secrets.get("github", {}))
        except Exception:
            github = {}
        if upload and github and st.button("Commit Uploaded Register to GitHub"):
            try:
                url = risk_store.github_commit(bu, upload.getvalue(), user.username, github)
                st.success(f"Committed: {url}")
            except Exception as exc:
                st.error(str(exc))
    with tabs[6]:
        settings = storage.json_setting(storage.bu_dir(bu) / "pipeline.json", {})
        url = st.text_input("DCS JSON Endpoint", settings.get("url", ""))
        token_name = st.text_input("Secret Key Under [dcs]", settings.get("token_secret_name", ""))
        if st.button("Save Connector Settings"):
            storage.save_json(storage.bu_dir(bu) / "pipeline.json", {"url": url, "token_secret_name": token_name})
            storage.audit(bu, user.username, "dcs_connector_configured", {"url": url})
            st.success("Connector settings saved; token value remains in Secrets.")
    with tabs[7]:
        presets = config.load_presets(bu)
        st.json(presets)
        st.download_button("Download Presets JSON", config.export_presets(bu), f"{bu}_presets.json", "application/json")
        upload = st.file_uploader("Upload Presets JSON", type=["json"], key="preset_upload")
        if upload and st.button("Import Presets"):
            try:
                count = config.import_presets(bu, upload.getvalue(), user.username)
                st.success(f"Imported {count} preset(s).")
            except Exception as exc:
                st.error(str(exc))
    with tabs[8]:
        audit = storage.read_csv(storage.bu_dir(bu) / "audit_log.csv")
        st.dataframe(audit.sort_values("timestamp", ascending=False) if not audit.empty else audit, width="stretch", hide_index=True)
        if st.button("Prepare Business Unit Backup ZIP"):
            output = io.BytesIO()
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
                for path in storage.bu_dir(bu).rglob("*"):
                    if path.is_file() and not path.name.endswith(".lock"):
                        archive.write(path, path.relative_to(storage.bu_dir(bu)))
            storage.audit(bu, user.username, "backup_prepared")
            st.session_state.backup_zip = output.getvalue()
        if "backup_zip" in st.session_state:
            st.download_button("Download Backup", st.session_state.backup_zip, f"{bu}_backup.zip", "application/zip")


def main() -> None:
    styles()
    if "user" not in st.session_state:
        do_login()
    user: auth.User = st.session_state.user
    password_change_gate(user)
    if "bu" not in st.session_state:
        choose_bu(user)
    bu = st.session_state.bu
    if not auth.can_access_bu(user, bu):
        st.session_state.pop("bu", None)
        st.rerun()
    page = sidebar(user, bu)
    routes = {
        "OPERA Home": page_home, "Plant Overview": page_plant, "Equipment Overview": page_equipment,
        "Operations Dashboard": page_operations, "Data Input": page_input, "Event Log": page_events,
        "Data Analysis": page_analysis, "Data Output": page_output, "Operating Parameters": page_parameters,
        "Risk Assessment": page_risk, "Lesson Bank": page_lessons, "Admin / Super Admin": page_admin,
    }
    routes[page](bu, user)


if __name__ == "__main__":
    main()
