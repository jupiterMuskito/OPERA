from __future__ import annotations

import io
import json
import uuid
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from opera import auth, config, dcs_connector, exports, formula, risk_store, storage
from opera.risk_engine import collect_hazards, compile_ppe, make_serial, suggest_from_text
from opera.risk_pdf import build_pdf

st.set_page_config(page_title="OPERA", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")
ROOT = Path(__file__).resolve().parent
BLUE, BLUE_DARK, RED, PALE = "#1857C9", "#123A73", "#C6303E", "#EEF3FA"
CHART_COLORS = [BLUE, RED, "#23A6A6", "#E0A33A", "#6A5ACD", "#4F9D63"]
PAGES = ["OPERA Home", "Plant Overview", "Equipment Overview", "Operations Dashboard", "Data Input", "Event Log", "Data Analysis",
         "Data Output", "Operating Parameters", "Risk Assessment", "Lesson Bank", "Admin / Super Admin"]


def styles() -> None:
    st.markdown("""
<style>
:root{--opera-blue:#1857C9;--opera-deep:#123A73;--opera-red:#C6303E;--opera-soft:#EEF3FA}
[data-testid="stAppViewContainer"]{background:linear-gradient(180deg,#f8fbff 0,#fff 38%)}
[data-testid="stSidebar"]{background:#102D54;color:white}
[data-testid="stSidebar"] *{color:#f7fbff}.opera-hero{padding:1.2rem 1.4rem;border-radius:14px;background:linear-gradient(125deg,#123A73,#1857C9);color:#fff;border-bottom:4px solid #C6303E;margin-bottom:1rem}.opera-hero h1{margin:0;font-size:2rem}.opera-hero p{margin:.3rem 0 0;color:#d9e8ff}.badge-good,.badge-bad,.badge-neutral{display:inline-block;padding:.15rem .5rem;border-radius:999px;font-weight:700;font-size:.78rem}.badge-good{background:#dff2e4;color:#18612c}.badge-bad{background:#f9dfdf;color:#9f1f2a}.badge-neutral{background:#e8edf3;color:#44576b}.flow{background:#fff;border:1px solid #d7e3ee;border-radius:10px;padding:.65rem 1rem;color:#334e68}.small-note{color:#60758a;font-size:.84rem}.stButton button{border-radius:8px}.stDownloadButton button{border-radius:8px;border-color:#1857C9}.metric-card{border:1px solid #d7e3ee;border-top:4px solid #1857C9;background:#fff;border-radius:10px;padding:.75rem;min-height:112px}.metric-card.bad{border-top-color:#C6303E}.metric-value{font-size:1.55rem;font-weight:750;color:#123A73}.metric-title{font-size:.83rem;color:#50677e;font-weight:650}
</style>""", unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="opera-hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def secret_users() -> dict[str, Any]:
    try:
        return dict(st.secrets.get("users", {}))
    except Exception:
        return {}


def do_login() -> None:
    hero("OPERA", "Operational Excellence and Reliability Assistant")
    st.markdown('<div class="flow"><b>Credentials</b> → Business Unit → OPERA Home → role-based modules</div>', unsafe_allow_html=True)
    left, middle, right = st.columns([1, 1.15, 1])
    with middle:
        with st.container(border=True):
            st.subheader("Sign in")
            with st.form("login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
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
    bus = bus[bus["id"].map(lambda x: auth.can_access_bu(user, x))]
    hero("Select Business Unit", f"Signed in as {user.display_name} · {user.role}")
    if bus.empty:
        st.error("No active business unit is assigned to this account.")
        st.stop()
    labels = {row["name"]: row["id"] for _, row in bus.iterrows()}
    selected = st.selectbox("Business unit", labels)
    if st.button("Open OPERA", type="primary"):
        st.session_state.bu = labels[selected]
        st.rerun()
    st.stop()


def password_change_gate(user: auth.User) -> None:
    if not user.must_change_password:
        return
    hero("Password change required", "The seeded Super Admin password must be replaced before OPERA opens.")
    with st.form("force_password"):
        old = st.text_input("Current password", type="password")
        new = st.text_input("New password", type="password")
        confirm = st.text_input("Confirm new password", type="password")
        go = st.form_submit_button("Change password", type="primary")
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
            if st.button("Mark all read"):
                storage.mark_notifications_read(bu, user.username)
                st.rerun()
    available = [p for p in PAGES if p != "Admin / Super Admin" or auth.allowed(user, "configure")]
    page = st.sidebar.radio("Navigate", available)
    if st.sidebar.button("Change business unit", use_container_width=True):
        st.session_state.pop("bu", None)
        st.rerun()
    if st.sidebar.button("Sign out", use_container_width=True):
        storage.audit(bu, user.username, "logout")
        st.session_state.clear()
        st.rerun()
    st.sidebar.markdown("---")
    st.sidebar.caption("Data Input → Event Log → Data Analysis → Data Output")
    return page


def source_frame(bu: str, source: str) -> pd.DataFrame:
    frame = storage.read_csv(storage.source_path(bu, source))
    if not frame.empty:
        frame["Timestamp"] = pd.to_datetime(frame["Date"] + " " + frame["Time"], errors="coerce")
    return frame


def active_registry(bu: str, source: str | None = None) -> pd.DataFrame:
    reg = storage.registry(bu)
    reg = reg[reg["active"].str.lower() == "true"]
    return reg if source is None else reg[reg["source"] == source]


def long_data(bu: str, sources: list[str] | None = None) -> pd.DataFrame:
    items = []
    reg = active_registry(bu).set_index("field_id")
    for source in sources or ["DCS", "Lab", "Field"]:
        frame = source_frame(bu, source)
        if frame.empty:
            continue
        fields = [c for c in frame.columns if c in reg.index]
        if not fields:
            continue
        view = frame.melt(id_vars=[c for c in storage.BASE_COLUMNS if c in frame.columns] + ["Timestamp"], value_vars=fields,
                          var_name="field_id", value_name="value")
        view["value"] = pd.to_numeric(view["value"], errors="coerce")
        view["source"] = source
        view["field_name"] = view["field_id"].map(reg["field_name"])
        view["uom"] = view["field_id"].map(reg["uom"])
        view["target"] = pd.to_numeric(view["field_id"].map(reg["target"]), errors="coerce")
        items.append(view.dropna(subset=["value"]))
    return pd.concat(items, ignore_index=True) if items else pd.DataFrame()


def calculated_data(bu: str) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    dcs, field, lab = source_frame(bu, "DCS"), source_frame(bu, "Field"), source_frame(bu, "Lab")
    if dcs.empty:
        return pd.DataFrame(), pd.DataFrame(), []
    keys = [c for c in ["Date", "Time", "Business unit", "Plant", "Unit/Section", "Equipment", "Timestamp"] if c in dcs.columns]
    base = dcs.drop(columns=[c for c in ["Recorded by", "Recorded at"] if c in dcs.columns])
    if not field.empty:
        base = base.merge(field.drop(columns=[c for c in ["Recorded by", "Recorded at"] if c in field.columns]), on=keys, how="left")
    if not lab.empty:
        lab_daily = lab.drop(columns=[c for c in ["Time", "Plant", "Unit/Section", "Equipment", "Recorded by", "Recorded at", "Timestamp"] if c in lab.columns])
        base = base.merge(lab_daily, on=["Date", "Business unit"], how="left")
    defs = storage.read_csv(storage.bu_dir(bu) / "calculated_fields.csv")
    constants = storage.json_setting(storage.bu_dir(bu) / "constants.json", {})
    out, errors = formula.apply_ordered(base, defs.to_dict("records"), constants)
    return out, defs, errors


def period_filter(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    if frame.empty or "Timestamp" not in frame.columns:
        return frame
    good = frame["Timestamp"].dropna()
    if good.empty:
        return frame
    lo, hi = good.min().date(), good.max().date()
    c1, c2 = st.columns(2)
    start = c1.date_input("Start", lo, min_value=lo, max_value=hi, key=f"{key}_start")
    end = c2.date_input("End", hi, min_value=lo, max_value=hi, key=f"{key}_end")
    return frame[(frame["Timestamp"].dt.date >= start) & (frame["Timestamp"].dt.date <= end)]


def export_panel(frame: pd.DataFrame, title: str, bu: str, user: auth.User, key: str) -> None:
    fmt = st.selectbox("Export format", ["Excel", "CSV", "PDF"], key=f"{key}_fmt")
    if st.button("Prepare export", key=f"{key}_prepare"):
        data, ext, mime = exports.build_export(fmt, title, frame, bu, user.username)
        st.session_state[f"{key}_export"] = (data, ext, mime)
        st.success("Export prepared and recorded in the audit log.")
    if f"{key}_export" in st.session_state:
        data, ext, mime = st.session_state[f"{key}_export"]
        st.download_button(f"Download {fmt}", data, f"{title.lower().replace(' ','_')}.{ext}", mime, key=f"{key}_download")


def kpi_cards(frame: pd.DataFrame, defs: pd.DataFrame, period: bool = False) -> None:
    if frame.empty or defs.empty:
        st.info("No calculated KPI data is available.")
        return
    active = defs[(defs["status"].str.lower() != "disabled") & (defs["dashboard"].str.lower() == "true")].head(8)
    columns = st.columns(min(4, max(1, len(active))))
    for idx, (_, item) in enumerate(active.iterrows()):
        method = item["aggregation"] if period else "Latest"
        value = formula.aggregate(frame[item["field_id"]], method) if item["field_id"] in frame else None
        target_key = "period_target" if period else "daily_target"
        target = pd.to_numeric(item[target_key], errors="coerce")
        status, variance = formula.target_status(value, None if pd.isna(target) else float(target), item["target_direction"])
        bad = status == "Off Target"
        with columns[idx % len(columns)]:
            st.markdown(f'<div class="metric-card {"bad" if bad else ""}"><div class="metric-title">{item["field_name"]}</div><div class="metric-value">{"—" if value is None else f"{value:,.2f}"}</div><div>{item["uom"]} · target {"—" if pd.isna(target) else f"{target:,.2f}"}</div><span class="badge-{"bad" if bad else "good" if status=="On Target" else "neutral"}">{status}</span><div class="small-note">Variance {"—" if variance is None else f"{variance:+,.2f}"}</div></div>', unsafe_allow_html=True)


def page_home(bu: str, user: auth.User) -> None:
    hero("OPERA Home", "Operational intelligence · reliability · continuous improvement")
    data = long_data(bu)
    events = storage.read_csv(storage.bu_dir(bu) / "events.csv")
    flags = storage.read_csv(storage.bu_dir(bu) / "flags.csv")
    lessons = storage.read_csv(storage.bu_dir(bu) / "lessons.csv")
    cols = st.columns(5)
    for col, label, value in zip(cols, ["Readings", "Open flags", "Events", "Lessons", "Unread notifications"],
                                 [len(data), len(flags[flags.get("status", "") == "Open"]) if not flags.empty else 0, len(events), len(lessons), len(storage.unread_notifications(bu, user.username))]):
        col.metric(label, f"{value:,}")
    st.markdown("### Operating flow")
    st.markdown('<div class="flow"><b>Data Input</b> → validation & flags → <b>Event Log</b> → <b>Data Analysis</b> → <b>Data Output</b> → audited export</div>', unsafe_allow_html=True)
    st.markdown("### Modules")
    cards = [("Plant Overview","Plant-level conditions and period reports"),("Equipment Overview","Equipment trends with selectable templates"),("Operations Dashboard","CPP-style KPIs, targets and period views"),("Risk Assessment","Register-backed deterministic hazard assessment"),("Lesson Bank","Lessons linked to logged events"),("Admin","No-code business-unit, field and equipment configuration")]
    for row in [cards[:3], cards[3:]]:
        cols = st.columns(3)
        for col,(title,text) in zip(cols,row):
            col.markdown(f"**{title}**  \n{text}")


def page_plant(bu: str, user: auth.User) -> None:
    hero("Plant Overview", "Select plant → select period → operating conditions → export → audit log")
    data = long_data(bu)
    if data.empty:
        st.info("No operational data is available.")
        return
    plant = st.selectbox("Plant", sorted(data["Plant"].dropna().unique()))
    view = period_filter(data[data["Plant"] == plant], "plant")
    summary = view.groupby(["field_id", "field_name", "uom"], as_index=False).agg(Average=("value","mean"), Minimum=("value","min"), Maximum=("value","max"), Readings=("value","count"))
    summary["Target"] = summary["field_id"].map(active_registry(bu).set_index("field_id")["target"])
    st.dataframe(summary, use_container_width=True, hide_index=True)
    choices = summary["field_name"].head(6).tolist()
    trend = view[view["field_name"].isin(choices)]
    fig = px.line(trend, x="Timestamp", y="value", color="field_name", facet_row="uom", markers=False, color_discrete_sequence=CHART_COLORS)
    fig.update_layout(template="plotly_white", height=520, legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)
    export_panel(summary, f"{plant} Plant Overview", bu, user, "plant")


def page_equipment(bu: str, user: auth.User) -> None:
    hero("Equipment Overview", "Select equipment → period → dashboard template → export")
    data = long_data(bu)
    eq = storage.equipment(bu)
    eq = eq[(eq["active"].str.lower() == "true") & (eq["placeholder"].str.lower() != "true")]
    if eq.empty or data.empty:
        st.info("Equipment or operational data is not available.")
        return
    plant = st.selectbox("Plant", sorted(eq["plant"].unique()))
    section = st.selectbox("Unit / Section", sorted(eq[eq["plant"] == plant]["unit_section"].unique()))
    options = eq[(eq["plant"] == plant) & (eq["unit_section"] == section)]
    label = st.selectbox("Equipment", options.apply(lambda r: f"{r['equipment_id']} — {r['equipment_name']}", axis=1))
    equipment_id = label.split(" — ",1)[0]
    template = st.selectbox("Dashboard template", ["Condition Monitoring", "Process Performance", "Quality & Compliance", "Reliability"])
    view = period_filter(data[data["Equipment"] == equipment_id], "equipment")
    if view.empty:
        st.warning("No readings are assigned to this equipment in the selected period.")
        return
    names = view.groupby("field_name")["value"].count().sort_values(ascending=False).head(8).index.tolist()
    show = view[view["field_name"].isin(names)]
    if template in {"Condition Monitoring", "Reliability"}:
        fig = px.line(show, x="Timestamp", y="value", color="field_name", markers=True, color_discrete_sequence=CHART_COLORS)
    elif template == "Quality & Compliance":
        fig = px.box(show, x="field_name", y="value", color="field_name", color_discrete_sequence=CHART_COLORS)
    else:
        fig = px.area(show, x="Timestamp", y="value", color="field_name", color_discrete_sequence=CHART_COLORS)
    fig.update_layout(template="plotly_white", height=520, legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)
    summary = show.groupby(["field_id","field_name","uom"],as_index=False)["value"].agg(["mean","min","max","std"]).reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)
    export_panel(summary, f"{equipment_id} {template}", bu, user, "equipment")


def page_operations(bu: str, user: auth.User) -> None:
    hero("Operations Dashboard", "CPP-style KPI cards · targets · period reports · trend granularity · regression and forecast")
    frame, defs, errors = calculated_data(bu)
    if errors:
        st.warning("Formula warnings: " + " | ".join(errors))
    if frame.empty:
        st.info("No DCS data is available.")
        return
    template = st.selectbox("Dashboard template", ["Current", "Period Total", "Month-to-Date", "Year-to-Date", "Quality", "Reliability"])
    view = period_filter(frame, "operations")
    if template == "Month-to-Date" and not view.empty:
        last = view["Timestamp"].max()
        view = view[(view["Timestamp"].dt.year == last.year) & (view["Timestamp"].dt.month == last.month)]
    elif template == "Year-to-Date" and not view.empty:
        last = view["Timestamp"].max()
        view = view[view["Timestamp"].dt.year == last.year]
    kpi_cards(view, defs, template in {"Period Total", "Month-to-Date", "Year-to-Date"})
    granularity = st.selectbox("Trend granularity", ["Daily", "Weekly", "Monthly", "Yearly"])
    fields = [x for x in defs["field_id"] if x in view.columns][:6]
    names = defs.set_index("field_id")["field_name"].to_dict()
    trend = view[["Timestamp"] + fields].copy().set_index("Timestamp")
    rule = {"Daily":"D","Weekly":"W","Monthly":"ME","Yearly":"YE"}[granularity]
    trend = trend.resample(rule).mean().reset_index().melt("Timestamp", var_name="field_id", value_name="value")
    trend["KPI"] = trend["field_id"].map(names)
    fig = px.line(trend, x="Timestamp", y="value", color="KPI", markers=True, color_discrete_sequence=CHART_COLORS)
    fig.update_layout(template="plotly_white", height=480)
    st.plotly_chart(fig, use_container_width=True)
    report = pd.DataFrame([{"KPI":r["field_name"],"Value":formula.aggregate(view[r["field_id"]],r.get("mtd_aggregation",r["aggregation"]) if template=="Month-to-Date" else r.get("ytd_aggregation",r["aggregation"]) if template=="Year-to-Date" else r["aggregation"]),"Target":r["period_target"],"UOM":r["uom"],"Status":r["status"]} for _,r in defs.iterrows() if r["field_id"] in view])
    st.markdown("#### Report sign-off")
    c1,c2,c3=st.columns(3); prepared=c1.text_input("Prepared by",user.display_name); reviewed=c2.text_input("Reviewed by"); remarks=c3.text_input("Remarks")
    report["Prepared by"], report["Reviewed by"], report["Remarks"] = prepared, reviewed, remarks
    export_panel(report, f"{template} Operations Report", bu, user, "operations")
    with st.expander("Save this dashboard as a preset"):
        name = st.text_input("Preset name", key="ops_preset_name")
        if st.button("Save preset", key="ops_save_preset") and name:
            config.save_preset(bu, name, {"module":"Operations Dashboard","template":template,"granularity":granularity}, user.username)
            st.success("Preset saved.")


def page_input(bu: str, user: auth.User) -> None:
    hero("Data Input", "Manual Lab / Field input · validated bulk upload · DCS pipeline connector")
    if not auth.allowed(user, "input"):
        st.warning("Your role is view-only.")
        return
    manual, bulk, pipeline = st.tabs(["Manual entry", "Bulk upload", "DCS pipeline"])
    with manual:
        source = st.selectbox("Source", list(storage.SOURCES), index=2)
        reg = active_registry(bu, source)
        if reg.empty:
            st.info("No active fields are configured for this placeholder source. A BU Admin can activate fields in Admin.")
        else:
            eq = storage.equipment(bu); eq=eq[eq["active"].str.lower()=="true"]
            field_options = {f"{r.field_id} — {r.field_name} ({r.uom})":r.field_id for r in reg.itertuples()}
            selected = st.multiselect("Data fields", list(field_options), default=list(field_options)[:3])
            e_label = st.selectbox("Equipment", eq.apply(lambda r:f"{r['equipment_id']} — {r['equipment_name']}",axis=1))
            e_id=e_label.split(" — ",1)[0]; e=eq[eq["equipment_id"]==e_id].iloc[0]
            with st.form("manual_input"):
                c1,c2=st.columns(2); day=c1.date_input("Date",date.today()); tm=c2.time_input("Time",datetime.now().replace(minute=0,second=0,microsecond=0).time())
                values={field_options[label]:st.number_input(label,value=None,placeholder="Enter value") for label in selected}
                save=st.form_submit_button("Validate and save",type="primary")
            if save:
                row={"Date":day.isoformat(),"Time":tm.strftime("%H:%M"),"Business unit":bu,"Plant":e["plant"],"Unit/Section":e["unit_section"],"Equipment":e_id,**values}
                frame=pd.DataFrame([row]); clean,issues,flags=storage.validate_rows(bu,source,frame)
                if not issues.empty: st.error("Validation failed."); st.dataframe(issues,hide_index=True)
                else:
                    n,f=storage.save_validated_input(bu,source,clean,user.username); storage.notify(bu,f"{n} {source} row saved ({f} flags).","error" if f else "success",created_by=user.username)
                    st.success(f"Saved {n} row; {f} validation flag(s).")
    with bulk:
        source = st.selectbox("Source", list(storage.SOURCES), key="bulk_source")
        st.download_button("Download CSV template", storage.template_bytes(bu,source), f"{bu}_{source}_template.csv", "text/csv")
        upload=st.file_uploader("Upload completed CSV or Excel",type=["csv","xlsx"],key="bulk_file")
        if upload:
            try:
                frame=pd.read_csv(upload,dtype=str,keep_default_na=False) if upload.name.lower().endswith(".csv") else pd.read_excel(upload,dtype=str).fillna("")
                clean,issues,flags=storage.validate_rows(bu,source,frame)
                st.markdown("#### Validation report")
                if issues.empty: st.success(f"{len(clean)} rows passed structural validation.")
                else: st.dataframe(issues,use_container_width=True,hide_index=True)
                if not flags.empty: st.warning(f"{len(flags)} value(s) will be flagged but may still be saved."); st.dataframe(flags,hide_index=True)
                if st.button("Save validated rows",disabled=not issues.empty,type="primary"):
                    n,f=storage.save_validated_input(bu,source,clean,user.username); storage.audit(bu,user.username,"bulk_upload",{"source":source,"rows":n,"flags":f}); st.success(f"Saved {n} rows.")
            except Exception as exc: st.error(f"Upload could not be read: {exc}")
    with pipeline:
        cfg=storage.json_setting(storage.bu_dir(bu)/"pipeline.json",{})
        st.code(cfg.get("url") or "DCS endpoint not configured")
        if st.button("Pull DCS data now",disabled=not bool(cfg.get("url"))):
            try:
                token=""
                if cfg.get("token_secret_name"):
                    token=str(st.secrets.get("dcs",{}).get(cfg["token_secret_name"],""))
                n,f=dcs_connector.ingest(bu,cfg["url"],token,user.username); st.success(f"Ingested {n} rows; {f} flags.")
            except Exception as exc: st.error(f"DCS pull failed: {exc}")


def page_events(bu: str, user: auth.User) -> None:
    hero("Event Log", "Filter / print / export events · structured event input · pictures · notifications")
    events=storage.read_csv(storage.bu_dir(bu)/"events.csv")
    view_tab,input_tab=st.tabs(["View event log","Input event"])
    with view_tab:
        if events.empty: st.info("No events have been logged.")
        else:
            types=sorted(set(";".join(events["event_types"]).split(";")))
            selected=st.multiselect("Event type",[x for x in types if x])
            view=events if not selected else events[events["event_types"].apply(lambda x:any(t in x.split(";") for t in selected))]
            c1,c2=st.columns(2); start=c1.date_input("From",pd.to_datetime(view["event_date"]).min().date(),key="event_from"); end=c2.date_input("To",pd.to_datetime(view["event_date"]).max().date(),key="event_to")
            dates=pd.to_datetime(view["event_date"],errors="coerce").dt.date; view=view[(dates>=start)&(dates<=end)]
            st.dataframe(view,use_container_width=True,hide_index=True)
            export_panel(view,"Event Log",bu,user,"events")
    with input_tab:
        if not auth.allowed(user,"events"): st.warning("Your role cannot create events.")
        else:
            types=["Safety","Process deviation","Equipment failure","Quality","Environmental","Shutdown","Other"]
            selected=st.multiselect("Tick event type(s)",types)
            fmt=st.radio("Event format",["Report","Data table","Picture"],horizontal=True)
            eq=storage.equipment(bu); eq=eq[eq["active"].str.lower()=="true"]
            label=st.selectbox("Equipment",eq.apply(lambda r:f"{r['equipment_id']} — {r['equipment_name']}",axis=1),key="event_eq")
            eid=label.split(" — ",1)[0]; erow=eq[eq["equipment_id"]==eid].iloc[0]
            picture=st.file_uploader("Picture attachment",type=["png","jpg","jpeg","webp"],disabled=fmt!="Picture")
            with st.form("event_input"):
                c1,c2=st.columns(2); day=c1.date_input("Event date",date.today()); tm=c2.time_input("Event time",datetime.now().time())
                title=st.text_input("Title"); details=st.text_area("Report / table data / observations"); send=st.checkbox("Send notification",value=True)
                submit=st.form_submit_button("Save event",type="primary")
            if submit:
                if not selected or not title.strip(): st.error("Select an event type and enter a title.")
                else:
                    pic=storage.save_attachment(bu,picture.name,picture.getvalue()) if picture else ""
                    event_id=f"EVT-{uuid.uuid4().hex[:8].upper()}"
                    row={"event_id":event_id,"timestamp":storage.utcnow(),"event_date":day.isoformat(),"event_time":tm.strftime("%H:%M"),"event_types":";".join(selected),"format":fmt,"plant":erow["plant"],"unit_section":erow["unit_section"],"equipment":eid,"title":title,"details":details,"picture_path":pic,"reported_by":user.display_name,"notification_sent":str(send).lower()}
                    storage.append_rows(storage.bu_dir(bu)/"events.csv",[row]); storage.audit(bu,user.username,"event_created",{"event_id":event_id,"types":selected})
                    if send: storage.notify(bu,f"New event {event_id}: {title}","error" if any(x in selected for x in ["Safety","Equipment failure","Shutdown"]) else "success",created_by=user.username)
                    st.success(f"Event {event_id} saved; name and time were recorded automatically.")


def page_analysis(bu: str, user: auth.User) -> None:
    hero("Data Analysis", "Compare two or more fields · statistics · chart selection · prediction · Field vs DCS")
    data=long_data(bu)
    compare,dcs_tab=st.tabs(["Field comparison","Field vs DCS"])
    with compare:
        if data.empty: st.info("No data is available.")
        else:
            options=sorted(data["field_name"].unique()); selected=st.multiselect("Select at least two data fields",options,default=options[:2])
            analysis=st.selectbox("Analysis type",["Trend","Prediction","Mean","Average","Standard deviation","Minimum / Maximum"])
            chart=st.selectbox("Comparison / chart type",["Line graph","Bar chart","Scatter","Box plot"])
            view=period_filter(data[data["field_name"].isin(selected)],"analysis") if selected else pd.DataFrame()
            if len(selected)<2: st.info("Select two or more fields.")
            elif not view.empty:
                if chart=="Line graph": fig=px.line(view,x="Timestamp",y="value",color="field_name",markers=True,color_discrete_sequence=CHART_COLORS)
                elif chart=="Bar chart": fig=px.bar(view.groupby("field_name",as_index=False)["value"].mean(),x="field_name",y="value",color="field_name",color_discrete_sequence=CHART_COLORS)
                elif chart=="Scatter": fig=px.scatter(view,x="Timestamp",y="value",color="field_name",trendline="ols",color_discrete_sequence=CHART_COLORS)
                else: fig=px.box(view,x="field_name",y="value",color="field_name",color_discrete_sequence=CHART_COLORS)
                fig.update_layout(template="plotly_white",height=500); st.plotly_chart(fig,use_container_width=True)
                summary=view.groupby("field_name")["value"].agg(["count","mean","std","min","max"]).reset_index()
                if analysis=="Prediction":
                    horizon=st.slider("Forecast horizon (periods)",1,30,7)
                    forecasts=[]
                    for name,group in view.groupby("field_name"):
                        vals=group.sort_values("Timestamp")["value"].dropna().to_numpy(); x=np.arange(len(vals))
                        if len(vals)>=2:
                            slope,intercept=np.polyfit(x,vals,1); forecasts.append({"field_name":name,"trend_slope":slope,"forecast_end":intercept+slope*(len(vals)+horizon-1)})
                    st.dataframe(pd.DataFrame(forecasts),hide_index=True)
                st.dataframe(summary,use_container_width=True,hide_index=True)
                export_panel(summary,f"{analysis} Analysis",bu,user,"analysis")
    with dcs_tab:
        field_reg=active_registry(bu,"Field"); dcs_reg=active_registry(bu,"DCS")
        f_label=st.selectbox("Field reading",field_reg.apply(lambda r:f"{r['field_id']} — {r['field_name']}",axis=1)); d_label=st.selectbox("DCS reading",dcs_reg.apply(lambda r:f"{r['field_id']} — {r['field_name']}",axis=1))
        monitor=st.number_input("Monitor difference",min_value=0.0,value=5.0); critical=st.number_input("Critical difference",min_value=monitor,value=max(10.0,monitor))
        exclude_shutdown=st.checkbox("Exclude shutdown days",value=True)
        fid,did=f_label.split(" — ",1)[0],d_label.split(" — ",1)[0]
        ff,dd=source_frame(bu,"Field"),source_frame(bu,"DCS")
        keys=["Date","Time","Equipment"]; cmp=ff[keys+[fid]].merge(dd[keys+[did]],on=keys,how="inner") if fid in ff and did in dd else pd.DataFrame()
        if exclude_shutdown and not cmp.empty:
            events=storage.read_csv(storage.bu_dir(bu)/"events.csv"); shutdown=set(events[events["event_types"].str.contains("Shutdown",case=False,na=False)]["event_date"]) if not events.empty else set(); cmp=cmp[~cmp["Date"].isin(shutdown)]
        if not cmp.empty:
            cmp["Difference"]=(pd.to_numeric(cmp[fid],errors="coerce")-pd.to_numeric(cmp[did],errors="coerce")).abs(); cmp["Status"]=np.select([cmp["Difference"]>=critical,cmp["Difference"]>=monitor],["Critical","Monitor"],default="Normal")
            st.dataframe(cmp,use_container_width=True,hide_index=True); export_panel(cmp,"Field vs DCS",bu,user,"field_dcs")
        else: st.info("No paired readings are available for this selection.")


def page_output(bu: str, user: auth.User) -> None:
    hero("Data Output", "Calculated fields · selected-duration results · input / calculated / merged Excel downloads")
    frame,defs,errors=calculated_data(bu)
    if errors: st.warning(" | ".join(errors))
    if frame.empty: st.info("No data is available."); return
    view=period_filter(frame,"output")
    choices=defs.apply(lambda r:f"{r['field_id']} — {r['field_name']}",axis=1).tolist(); selected=st.multiselect("Calculated fields",choices,default=choices[:4]); method=st.selectbox("Calculate",["Average","Maximum","Minimum"])
    rows=[]
    for label in selected:
        field=label.split(" — ",1)[0]; meta=defs[defs["field_id"]==field].iloc[0]; value=formula.aggregate(view[field],method) if field in view else None
        status,var=formula.target_status(value,float(meta["period_target"]) if meta["period_target"] else None,meta["target_direction"]); rows.append({"Business unit":bu,"Calculated field":field,"Name":meta["field_name"],method:value,"UOM":meta["uom"],"Target":meta["period_target"],"Variance":var,"Status":status})
    result=pd.DataFrame(rows); st.dataframe(result,use_container_width=True,hide_index=True)
    export_panel(result,"Calculated Data Output",bu,user,"output")
    st.markdown("#### Complete Excel workbooks")
    if st.button("Prepare input, calculated and merged Excel"):
        inputs=storage.input_data(bu,list(storage.SOURCES)); calculated_cols=[c for c in defs["field_id"] if c in frame.columns]
        payload=exports.excel_bytes({"Input":inputs,"Calculated":frame[[c for c in storage.BASE_COLUMNS if c in frame]+calculated_cols],"Merged":frame})
        storage.audit(bu,user.username,"export_prepared",{"title":"Input Calculated Merged","format":"Excel"}); st.session_state.full_excel=payload
    if "full_excel" in st.session_state: st.download_button("Download complete Excel",st.session_state.full_excel,f"{bu}_input_calculated_merged.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def page_parameters(bu: str, user: auth.User) -> None:
    hero("Operating Parameters", "Process → equipment → duration → view → export · Quality → field → duration → view → export")
    process,quality=st.tabs(["Process","Quality"])
    with process:
        data=long_data(bu,["DCS","Field"])
        if not data.empty:
            eq=st.selectbox("Equipment",sorted(data["Equipment"].unique()),key="proc_eq"); view=period_filter(data[data["Equipment"]==eq],"process_params"); fmt=st.selectbox("View format",["Trend","Table","Summary"],key="proc_view")
            if fmt=="Trend": st.plotly_chart(px.line(view,x="Timestamp",y="value",color="field_name",color_discrete_sequence=CHART_COLORS),use_container_width=True)
            elif fmt=="Table": st.dataframe(view,use_container_width=True,hide_index=True)
            else: st.dataframe(view.groupby(["field_name","uom"])["value"].agg(["mean","min","max"]).reset_index(),hide_index=True)
            export_panel(view,"Process Operating Parameters",bu,user,"proc_params")
    with quality:
        data=long_data(bu,["Lab"])
        if not data.empty:
            field=st.selectbox("Data field",sorted(data["field_name"].unique()),key="qual_field"); view=period_filter(data[data["field_name"]==field],"quality_params"); fmt=st.selectbox("View format",["Trend","Table","Distribution"],key="qual_view")
            if fmt=="Trend": st.plotly_chart(px.line(view,x="Timestamp",y="value",markers=True,color_discrete_sequence=CHART_COLORS),use_container_width=True)
            elif fmt=="Distribution": st.plotly_chart(px.histogram(view,x="value",marginal="box",color_discrete_sequence=CHART_COLORS),use_container_width=True)
            else: st.dataframe(view,use_container_width=True,hide_index=True)
            export_panel(view,"Quality Operating Parameters",bu,user,"qual_params")


def page_risk(bu: str, user: auth.User) -> None:
    hero("Risk Assessment", "Select preset → job type → generate → review identified risks → print / export → audit log")
    register,source,problem=risk_store.resolve(bu)
    if not register:
        st.warning(problem or "Risk register update required.")
        return
    st.caption(f"{source} · {register.hazard_count} hazards · fingerprint {register.fingerprint}")
    preset_names={f"{p['id']} — {p['n']}":p for p in register.presets}
    preset_label=st.selectbox("Preset",list(preset_names) or ["Custom"]); preset=preset_names.get(preset_label,{"tags":[],"et":"","mo":"Running","st":"Operational","loc":"","ref":"","n":"Custom"})
    description=st.text_area("Job description",value=preset.get("d", "")); suggested=suggest_from_text(register,description) if description else {"tags":[]}
    tags=st.multiselect("Job type / activities",register.tag_names,default=[t for t in (preset.get("tags") or suggested.get("tags",[])) if t in register.tag_names])
    locations=[x["n"] for x in register.locations]; loc_default=locations.index(preset["loc"]) if preset.get("loc") in locations else 0; location=st.selectbox("Location",locations,index=loc_default)
    available=[e for e in register.equipment if register.available(e,location)]; eq_names=[e["n"] for e in available]; eq_default=eq_names.index(preset["ref"]) if preset.get("ref") in eq_names else 0; equipment=st.selectbox("Equipment",eq_names,index=eq_default)
    equip=register.equip(equipment); motion=st.selectbox("Equipment motion",register.motions,index=register.motions.index(preset["mo"]) if preset.get("mo") in register.motions else 0); status=st.selectbox("Equipment status",register.statuses,index=register.statuses.index(preset["st"]) if preset.get("st") in register.statuses else 0)
    if st.button("Generate risk assessment",type="primary"):
        hazards=collect_hazards(register,tags,equip["t"] if equip else None,motion,status); st.session_state.risk_hazards=hazards; st.session_state.risk_context={"preset":preset["n"],"description":description,"location":location,"equipment":equipment,"motion":motion,"status":status,"tags":tags}
        storage.audit(bu,user.username,"risk_assessment_generated",{"preset":preset["n"],"hazards":len(hazards)})
    hazards=st.session_state.get("risk_hazards",[]); ctx=st.session_state.get("risk_context",{})
    if hazards:
        table=pd.DataFrame([{"ID":h["uid"],"Category":h["cat"],"Hazard":h["hz"],"Initial":h["lv"],"Controls":h["ct"],"Residual":h["rd"],"Responsible":h["rp"]} for h in hazards])
        st.dataframe(table,use_container_width=True,hide_index=True)
        excluded=st.multiselect("Review: exclude risks that are not applicable",[h["uid"] for h in hazards])
        if st.button("Prepare printable PDF"):
            now=datetime.now(timezone.utc); serial=make_serial(now,ctx.get("equipment",""),"")
            payload={"serial":serial,"bu":bu.title(),"company":"OPERA — DANGOTE INDUSTRIES","form_title":"RISK ASSESSMENT FORM","register_status":"Approved","register_source":source,"fingerprint":register.fingerprint,
                     "header":[("Assessment No.",serial),("Preset / job",ctx.get("preset")),("Description",ctx.get("description")),("Location",ctx.get("location")),("Equipment",ctx.get("equipment")),("Motion / status",f"{ctx.get('motion')} / {ctx.get('status')}")],
                     "hazards":hazards,"excluded":set(excluded),"categories":register.categories,"erp":["Raise alarm and stop work.","Make the area safe without personal exposure.","Notify the control room and emergency response team.","Provide first aid only when trained and safe."],
                     "assessed_by":user.display_name,"reviewed_by":"","generated":now.isoformat(timespec="seconds")}
            st.session_state.risk_pdf=build_pdf(payload); st.session_state.risk_serial=serial
            storage.append_rows(storage.bu_dir(bu)/"risk_assessments.csv",[{"serial":serial,"timestamp":storage.utcnow(),"preset":ctx.get("preset"),"job_type":";".join(ctx.get("tags",[])),"location":ctx.get("location"),"equipment":ctx.get("equipment"),"hazard_count":len(hazards)-len(excluded),"assessed_by":user.username}]); storage.audit(bu,user.username,"risk_assessment_exported",{"serial":serial,"format":"PDF"})
        if "risk_pdf" in st.session_state: st.download_button("Print / download PDF",st.session_state.risk_pdf,f"{st.session_state.risk_serial}.pdf","application/pdf")
        export_panel(table,"Risk Assessment Hazards",bu,user,"risk_table")


def page_lessons(bu: str, user: auth.User) -> None:
    hero("Lesson Bank", "Review lesson: unit → event → lesson · Input lesson linked to an Event Log event")
    lessons=storage.read_csv(storage.bu_dir(bu)/"lessons.csv"); events=storage.read_csv(storage.bu_dir(bu)/"events.csv")
    review,entry=st.tabs(["Review lessons","Input lesson"])
    with review:
        if lessons.empty: st.info("No lessons have been recorded.")
        else:
            unit=st.selectbox("Unit",sorted(lessons["unit_section"].unique())); event=st.selectbox("Event",sorted(lessons[lessons["unit_section"]==unit]["event_id"].unique())); st.dataframe(lessons[(lessons["unit_section"]==unit)&(lessons["event_id"]==event)],use_container_width=True,hide_index=True)
    with entry:
        if not auth.allowed(user,"lessons"): st.warning("Your role cannot add lessons.")
        elif events.empty: st.info("Create an Event Log event before adding a linked lesson.")
        else:
            event_labels={f"{r.event_id} — {r.title}":r for r in events.itertuples()}; label=st.selectbox("Event",list(event_labels)); lesson=st.text_area("Lesson learned")
            if st.button("Save lesson",type="primary") and lesson.strip():
                ev=event_labels[label]; lid=f"LES-{uuid.uuid4().hex[:8].upper()}"; storage.append_rows(storage.bu_dir(bu)/"lessons.csv",[{"lesson_id":lid,"timestamp":storage.utcnow(),"event_id":ev.event_id,"unit_section":ev.unit_section,"lesson":lesson,"entered_by":user.username}]); storage.audit(bu,user.username,"lesson_created",{"lesson_id":lid,"event_id":ev.event_id}); st.success(f"Lesson {lid} saved and linked to {ev.event_id}.")


def add_user_form(current: auth.User) -> None:
    with st.form("add_user"):
        username=st.text_input("Username").strip().lower(); name=st.text_input("Display name"); role=st.selectbox("Role",["BU Admin","Operator","Viewer","Super Admin"]); bus=st.multiselect("Business units",config.business_units()["id"].tolist()); password=st.text_input("Temporary password",type="password"); submit=st.form_submit_button("Create user")
    if submit:
        if not username or len(password)<12: st.error("Username and a 12-character temporary password are required.")
        else:
            p=storage.DATA_ROOT/"shared"/"users.csv"; users=storage.read_csv(p)
            if username in set(users["username"]): st.error("Username already exists.")
            else:
                row={"username":username,"display_name":name or username,"password_hash":auth.hash_password(password),"role":role,"business_units":"*" if role=="Super Admin" else ";".join(bus),"active":"true","must_change_password":"true","failed_attempts":"0","lock_until":""}; storage.atomic_write_csv(p,pd.concat([users,pd.DataFrame([row])],ignore_index=True)); storage.audit("shared",current.username,"user_created",{"username":username,"role":role}); st.success("User created.")


def page_admin(bu: str, user: auth.User) -> None:
    hero("Admin / Super Admin", "Business units · users · UOM / targets / formulas · equipment · storage · audit")
    if not auth.allowed(user,"configure"): st.warning("Administrator role required."); return
    tabs=st.tabs(["Business units","Users & roles","Fields & formulas","Equipment","Risk registers","DCS connector","Presets","Audit & backup"])
    with tabs[0]:
        st.dataframe(config.business_units(),use_container_width=True,hide_index=True)
        if user.role=="Super Admin":
            st.markdown("#### Clone a business unit — no code required")
            source=st.selectbox("Template BU",config.business_units()["id"].tolist()); name=st.text_input("New business-unit name"); active=st.checkbox("Activate immediately")
            if st.button("Clone BU") and name:
                try: new=config.clone_business_unit(source,name,active,user.username); st.success(f"Created {new}.")
                except Exception as exc: st.error(str(exc))
            st.markdown("#### Name / activate a placeholder")
            target=st.selectbox("Business unit",config.business_units()["id"].tolist(),key="edit_bu"); new_name=st.text_input("Display name",key="edit_bu_name"); enabled=st.checkbox("Active",key="edit_bu_active")
            if st.button("Save BU configuration") and new_name:
                config.set_business_unit(target,new_name,enabled,user.username); st.success("Business unit updated.")
    with tabs[1]:
        users=storage.read_csv(storage.DATA_ROOT/"shared"/"users.csv"); st.dataframe(users.drop(columns=["password_hash"]),use_container_width=True,hide_index=True)
        if user.role=="Super Admin": add_user_form(user)
    with tabs[2]:
        reg=storage.registry(bu)
        source_filter=st.selectbox("Source registry",list(storage.SOURCES),key="admin_field_source")
        candidates=reg[reg["source"]==source_filter]
        field=st.selectbox("Input field",candidates.apply(lambda r:f"{r['field_id']} — {r['field_name']}",axis=1)); fid=field.split(" — ",1)[0]; meta=candidates[candidates["field_id"]==fid].iloc[0]
        c1,c2,c3,c4=st.columns(4); uom=c1.text_input("UOM",meta["uom"]); low=c2.text_input("Minimum",meta["min_value"]); high=c3.text_input("Maximum",meta["max_value"]); target=c4.text_input("Target",meta["target"]); direction=st.selectbox("Target interpretation",["High","Low"],index=0 if meta["target_direction"]=="High" else 1)
        is_active=st.checkbox("Active field",value=meta["active"].lower()=="true",help="Activate TA–TG fields here before manual entry, calculation or export.")
        if st.button("Save input field"):
            idx=reg[reg["field_id"]==fid].index[0]; reg.loc[idx,["uom","min_value","max_value","target","target_direction","active"]]=[uom,low,high,target,direction,str(is_active).lower()]; storage.atomic_write_csv(storage.bu_dir(bu)/"fields.csv",reg); storage.audit(bu,user.username,"field_configuration_changed",fid); st.success("Field updated.")
        st.markdown("#### Calculated fields (ordered CPP-style engine)")
        defs=storage.read_csv(storage.bu_dir(bu)/"calculated_fields.csv"); st.dataframe(defs,use_container_width=True,hide_index=True)
        if not defs.empty:
            cf=st.selectbox("Calculated field",defs["field_id"]); row=defs[defs["field_id"]==cf].iloc[0]; expression=st.text_input("Formula",row["formula"]); status=st.selectbox("Status",["active","on hold","disabled"],index=["active","on hold","disabled"].index(row["status"]) if row["status"] in ["active","on hold","disabled"] else 0)
            if st.button("Save calculated field"):
                idx=defs[defs["field_id"]==cf].index[0]; defs.loc[idx,["formula","status"]]=[expression,status]; storage.atomic_write_csv(storage.bu_dir(bu)/"calculated_fields.csv",defs); storage.audit(bu,user.username,"formula_configuration_changed",cf); st.success("Calculated field updated.")
        st.markdown("#### Baseline constants")
        constants=storage.json_setting(storage.bu_dir(bu)/"constants.json",{})
        constant_text=st.text_area("JSON constants (reference by key in formulas, e.g. B_capacity)",json.dumps(constants,indent=2),height=140)
        if st.button("Save baseline constants"):
            try:
                parsed=json.loads(constant_text)
                if not isinstance(parsed,dict) or not all(isinstance(v,(int,float)) for v in parsed.values()): raise ValueError("Use a JSON object with numeric values.")
                storage.save_json(storage.bu_dir(bu)/"constants.json",parsed); storage.audit(bu,user.username,"baseline_constants_changed",{"keys":list(parsed)}); st.success("Baseline constants saved.")
            except Exception as exc: st.error(str(exc))
    with tabs[3]:
        eq=storage.equipment(bu); st.dataframe(eq.head(100),use_container_width=True,hide_index=True); spare=eq[eq["placeholder"].str.lower()=="true"]["equipment_id"].tolist(); selected=st.selectbox("Convert spare placeholder",spare); name=st.text_input("Equipment name"); plant=st.text_input("Plant"); section=st.text_input("Unit / Section"); etype=st.text_input("Equipment type")
        if st.button("Add / activate equipment") and name:
            idx=eq[eq["equipment_id"]==selected].index[0]; eq.loc[idx,["equipment_name","plant","unit_section","equipment_type","active","placeholder"]]=[name,plant,section,etype,"true","false"]; storage.atomic_write_csv(storage.bu_dir(bu)/"equipment.csv",eq); storage.audit(bu,user.username,"equipment_configuration_changed",selected); st.success("Equipment activated.")
    with tabs[4]:
        register,source,problem=risk_store.resolve(bu); st.write(f"Current: {source or problem}"); st.write(f"Fingerprint: {register.fingerprint if register else '—'}")
        upload=st.file_uploader("Upload approved Excel risk register",type=["xlsx"],key="risk_upload"); note=st.text_input("Change note")
        if upload and st.button("Validate and activate register"):
            try:
                risk_store.activate(bu,upload.getvalue(),user.username,note); st.success("Register validated and activated.")
            except Exception as exc: st.error(f"Register was not changed: {exc}")
        try: github=dict(st.secrets.get("github",{}))
        except Exception: github={}
        if upload and github and st.button("Commit uploaded register to GitHub"):
            try: url=risk_store.github_commit(bu,upload.getvalue(),user.username,github); st.success(f"Committed: {url}")
            except Exception as exc: st.error(str(exc))
    with tabs[5]:
        cfg=storage.json_setting(storage.bu_dir(bu)/"pipeline.json",{}); url=st.text_input("DCS JSON endpoint",cfg.get("url","")); token_name=st.text_input("Secret key under [dcs]",cfg.get("token_secret_name",""))
        if st.button("Save connector settings"):
            storage.save_json(storage.bu_dir(bu)/"pipeline.json",{"url":url,"token_secret_name":token_name}); storage.audit(bu,user.username,"dcs_connector_configured",{"url":url}); st.success("Connector settings saved; token value remains in Secrets.")
    with tabs[6]:
        presets=config.load_presets(bu); st.json(presets); st.download_button("Download presets JSON",config.export_presets(bu),f"{bu}_presets.json","application/json"); upload=st.file_uploader("Upload presets JSON",type=["json"],key="preset_upload")
        if upload and st.button("Import presets"):
            try: count=config.import_presets(bu,upload.getvalue(),user.username); st.success(f"Imported {count} preset(s).")
            except Exception as exc: st.error(str(exc))
    with tabs[7]:
        audit=storage.read_csv(storage.bu_dir(bu)/"audit_log.csv"); st.dataframe(audit.sort_values("timestamp",ascending=False) if not audit.empty else audit,use_container_width=True,hide_index=True)
        if st.button("Prepare BU backup ZIP"):
            out=io.BytesIO()
            with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
                for p in storage.bu_dir(bu).rglob("*"):
                    if p.is_file() and not p.name.endswith(".lock"): z.write(p,p.relative_to(storage.bu_dir(bu)))
            storage.audit(bu,user.username,"backup_prepared"); st.session_state.backup_zip=out.getvalue()
        if "backup_zip" in st.session_state: st.download_button("Download backup",st.session_state.backup_zip,f"{bu}_backup.zip","application/zip")


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
        st.session_state.pop("bu", None); st.rerun()
    page = sidebar(user, bu)
    routes = {"OPERA Home":page_home,"Plant Overview":page_plant,"Equipment Overview":page_equipment,"Operations Dashboard":page_operations,"Data Input":page_input,
              "Event Log":page_events,"Data Analysis":page_analysis,"Data Output":page_output,"Operating Parameters":page_parameters,"Risk Assessment":page_risk,"Lesson Bank":page_lessons,"Admin / Super Admin":page_admin}
    routes[page](bu,user)


if __name__ == "__main__":
    main()
