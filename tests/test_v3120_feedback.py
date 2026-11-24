from io import BytesIO
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

import app
from opera import dashboard, exports, storage


ROOT = Path(__file__).resolve().parents[1]


def _set_data_root(monkeypatch, tmp_path):
    root = tmp_path / "data"
    (root / "business_units" / "demo").mkdir(parents=True)
    monkeypatch.setattr(storage, "DATA_ROOT", root)
    storage.clear_data_caches()
    return root / "business_units" / "demo"


def test_legacy_lessons_gain_categories_atomically_without_manual_edit(monkeypatch, tmp_path):
    bu = _set_data_root(monkeypatch, tmp_path)
    legacy = pd.DataFrame(
        [
            {"lesson_id": "L1", "equipment": "EQ-1", "lesson_title": "Bearing lesson"},
            {"lesson_id": "L2", "equipment": "", "lesson_title": "General lesson"},
        ]
    )
    legacy.to_csv(bu / "lessons.csv", index=False)

    migrated = storage.load_lessons("demo")

    assert list(migrated.columns) == storage.LESSON_COLUMNS
    assert migrated.set_index("lesson_id")["category"].to_dict() == {"L1": "Equipment", "L2": "General"}
    persisted = pd.read_csv(bu / "lessons.csv", dtype=str, keep_default_na=False)
    assert persisted.set_index("lesson_id")["category"].to_dict() == {"L1": "Equipment", "L2": "General"}


def test_lesson_category_validation_list_has_required_defaults_and_is_editable(monkeypatch, tmp_path):
    bu = _set_data_root(monkeypatch, tmp_path)
    pd.DataFrame(columns=["equipment_id", "plant", "unit_section", "equipment_type"]).to_csv(bu / "equipment.csv", index=False)

    assert dashboard.hierarchy_options("demo")["lesson_categories"] == [
        "Equipment", "Safety", "General", "Plant Operations"
    ]
    dashboard.save_hierarchy_options(
        "demo",
        {"plants": [], "units": [], "equipment_types": [], "lesson_categories": ["Equipment", "General", "Environment"]},
    )
    categories = dashboard.hierarchy_options("demo")["lesson_categories"]
    assert "Environment" in categories
    assert {"Equipment", "General"}.issubset(categories)


def test_lesson_excel_export_contains_category_column():
    frame = pd.DataFrame([{"lesson_id": "L1", "category": "Safety", "lesson": "Isolate first"}])
    workbook = load_workbook(BytesIO(exports.excel_bytes({"Lessons": frame})), read_only=True)
    assert [cell.value for cell in workbook["Lessons"][1]] == ["lesson_id", "category", "lesson"]
    assert workbook["Lessons"]["B2"].value == "Safety"
    workbook.close()


def test_header_assets_are_encoded_once_per_process():
    app.asset_data_uri.cache_clear()
    first = app.asset_data_uri(app.DANGOTE_LOGO)
    second = app.asset_data_uri(app.DANGOTE_LOGO)
    assert first == second and first.startswith("data:image/webp;base64,")
    assert app.asset_data_uri.cache_info().hits == 1


def test_feedback_contract_is_present_in_app_source():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert '"Operations Dashboard": "KPI\'s"' in source
    assert "@media(min-width:1100px) and (max-width:1365px)" in source
    assert "@media(max-width:1099px)" in source
    assert "font-size:14px" in source
    assert "Download Filtered Lessons Excel" in source
    assert '"Category": row["category"]' in source
    assert 'category_filter = first.selectbox("Category"' in source
    assert 'st.selectbox("Equipment (Optional)"' in source
    assert "Lesson Categories (One per Line)" in source
    assert "stMainBlockContainer" in source and "stFileUploaderDropzone" in source and "stExpander" in source


def test_authenticated_pages_no_longer_add_the_v3111_leftover_h1_titles():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    home = source[source.index("def page_home"):source.index("def page_plant")]
    equipment = source[source.index("def page_equipment"):source.index("def operations_long")]
    admin = source[source.index("def page_admin"):source.index("def main")]
    assert "st.title(" not in home
    assert "st.title(" not in equipment
    assert "st.title(" not in admin


def test_operations_snapshot_cache_reuses_data_and_invalidates_on_file_change(monkeypatch, tmp_path):
    _set_data_root(monkeypatch, tmp_path)
    calls = {"long": 0}

    def fake_long_data(_bu):
        calls["long"] += 1
        return pd.DataFrame()

    monkeypatch.setattr(app, "long_data", fake_long_data)
    monkeypatch.setattr(app, "calculated_data", lambda _bu: (pd.DataFrame(), pd.DataFrame(), []))
    monkeypatch.setattr(
        app.dashboard,
        "operations_field_catalog",
        lambda _bu: pd.DataFrame(columns=["source", "field_id"]),
    )
    app._operations_dashboard_data_cached.cache_clear()

    app.operations_dashboard_data("demo")
    app.operations_dashboard_data("demo")
    assert calls["long"] == 1

    storage.atomic_write_csv(storage.source_path("demo", "DCS"), pd.DataFrame(columns=storage.BASE_COLUMNS))
    app.operations_dashboard_data("demo")
    assert calls["long"] == 2


def test_repeated_header_assets_are_right_sized_webp_payloads():
    assert app.VISION_2030_LOGO.suffix == ".webp"
    assert app.VISION_2030_COMPACT.suffix == ".webp"
    assert app.VISION_2030_LOGO.stat().st_size < 30_000
    assert app.VISION_2030_COMPACT.stat().st_size < 30_000
