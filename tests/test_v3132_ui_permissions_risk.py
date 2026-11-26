from pathlib import Path

from app import MANUAL_RISK_MODE, _risk_form_signature, home_detail_sheets
from opera import auth, exports, storage


ROOT = Path(__file__).resolve().parents[1]
HOME_DETAILS = ("Readings", "Open Flags", "Events", "Lessons", "Notifications")


def test_secrets_and_csv_super_admin_can_open_and_export_every_home_register(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "DATA_ROOT", tmp_path)
    secret_admin = auth.get_secret_user(
        "root",
        {"root": {"name": "OPERA Super Admin", "role": "OPERA Super Admin", "business_units": "", "active": True}},
    )
    csv_admin = auth.user_from_record(
        {"username": "csvroot", "display_name": "CSV Super Admin", "role": "  SUPER_ADMIN  ", "business_units": "cement"}
    )
    assert secret_admin is not None
    for user in (secret_admin, csv_admin):
        assert user.role == "Super Admin"
        assert auth.allowed(user, "home_drilldown")
        assert auth.allowed(user, "export")
        assert auth.can_access_bu(user, "cement")
        for detail in HOME_DETAILS:
            sheets = home_detail_sheets("cement", user.username, detail)
            assert sheets
            assert exports.excel_bytes(sheets).startswith(b"PK")


def test_risk_page_restores_manual_editable_preset_and_direct_audited_pdf_contract():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    risk = source[source.index("def page_risk"):source.index("def page_lessons")]
    assert MANUAL_RISK_MODE == "Manual / no preset"
    assert "mode_options = [MANUAL_RISK_MODE] + list(preset_names)" in risk
    assert 'st.multiselect("Job Type / Activities"' in risk
    assert '"Equipment Type"' in risk
    assert '"Equipment Motion"' in risk and '"Equipment Status"' in risk
    assert "on_change=apply_risk_mode" in risk
    assert '"Print / Download Job Risk Assessment PDF"' in risk
    assert "Prepare Job Risk Assessment PDF" not in risk
    assert "on_click=lambda: _audit_risk_pdf_download" in risk
    assert "job_risk_assessment_exported" in source


def test_risk_signature_changes_when_any_editable_assessment_field_changes():
    values = {
        "mode": MANUAL_RISK_MODE,
        "description": "Inspect pump",
        "tags": ["Inspection"],
        "location": "Area A",
        "equipment_type": "Pump",
        "equipment": "P-101",
        "motion": "Static",
        "status": "Shutdown/Isolated",
    }
    baseline = _risk_form_signature(values)
    for field in values:
        changed = dict(values)
        changed[field] = ["Inspection", "Lifting"] if field == "tags" else f"{values[field]} changed"
        assert _risk_form_signature(changed) != baseline


def test_home_and_header_buttons_do_not_define_sticky_hover_help():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    home = source[source.index("def page_home"):source.index("def page_plant")]
    header = source[source.index("def top_navigation"):source.index("def source_frame")]
    assert "Open the {label.lower()} table" not in home
    assert 'help="Account menu"' not in header
    assert "unread notification(s)" not in header


def test_post_breadcrumb_page_level_headings_and_intro_captions_are_removed():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    risk = source[source.index("def page_risk"):source.index("def page_lessons")]
    optimization = source[source.index("def page_process_optimization"):source.index("def page_output")]
    analysis = source[source.index("def page_analysis"):source.index("def page_process_optimization")]
    automatic = source[source.index("def automatic_upload_panel"):source.index("def page_operational_data")]
    mapping = source[source.index("def field_mapping_admin"):source.index("def equipment_admin")]
    pipeline = source[source.index("def pipeline_admin"):source.index("def page_admin")]
    assert "## Job Risk Assessment" not in risk
    assert "approved hazards are available for assessment" not in risk
    assert 'class="risk-hazard-summary"' in risk
    assert "#### Bounded Response Optimization" not in optimization
    assert "#### Compare Any Data Field" not in analysis
    assert "#### Instrument Check" not in analysis
    assert "Review the latest status for each automatic data source below" not in automatic
    assert "#### Data Field Mapping" not in mapping
    assert "Configure every automatic data source you are permitted to manage" not in pipeline
