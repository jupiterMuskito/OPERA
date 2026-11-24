from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def test_home_grouping_and_pipeline_label_match_the_corrected_requirement():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert '"Operational Data": [' in source
    assert '"Operational Data Pipeline", "Process Optimization"' in source
    assert '"Operational Knowledge": ["Event Log", "Lesson Bank", "Job Risk Assessment"]' in source
    assert '"Operational Data Pipeline": page_operational_data' in source
    assert 'st.markdown("### Operational Data Pipeline")' in source
    rejected_name = "Operational Data Collection" + " and Retrieval"
    assert rejected_name not in source


def test_v38_style_navigation_has_no_category_labels_or_colour_formatting():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    navigation = source[source.index("def top_navigation"):source.index("def source_frame")]
    assert "format_func=navigation_label" not in navigation
    assert "nav-category-legend" not in source
    assert "CATEGORY_STYLE" not in source
    assert "category-chip" not in source
    assert "category-data" not in source


def test_admin_is_navigation_only_and_header_actions_are_in_the_user_menu():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    home = source[source.index("def page_home"):source.index("def page_plant")]
    navigation = source[source.index("def top_navigation"):source.index("def source_frame")]
    assert "Admin / Super Admin" not in home
    assert '"Admin / Super Admin": page_admin' in source
    assert 'st.button(_user_initials(user.display_name), key="user_menu"' in navigation
    assert 'with st.container(key="header_user_panel")' in navigation
    assert navigation.index('button("Change Business Unit"') < navigation.index('button("Help"')
    assert navigation.index('button("Help"') < navigation.index('button("Sign Out"')


def test_vision_2030_assets_have_real_transparency_and_old_jpegs_are_removed():
    for name in ["dangote_vision_2030.png", "dangote_vision_2030_compact.png"]:
        image = Image.open(ROOT / "assets" / name)
        assert image.mode == "RGBA"
        assert image.getextrema()[3][0] == 0
        assert image.getextrema()[3][1] == 255
    assert not (ROOT / "assets" / "dangote_vision_2030.jpg").exists()
    assert not (ROOT / "assets" / "dangote_vision_2030_compact.jpg").exists()


def test_pipeline_name_is_used_for_exports_and_displayed_audit_labels():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "Operational Data Pipeline Calculated Data Output" in source
    assert "Operational Data Pipeline Instrument Check" in source
    assert '"data_input_saved": "operational_data_pipeline_input_saved"' in source
    assert '"bulk_upload": "operational_data_pipeline_bulk_upload"' in source