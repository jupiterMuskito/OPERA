from io import BytesIO
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

from opera import __version__, dashboard, exports, storage


ROOT = Path(__file__).resolve().parents[1]


def _configure_demo(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "DATA_ROOT", tmp_path)
    storage.clear_data_caches()
    dashboard._ensure_mapping_database_cached.cache_clear()
    dashboard._read_mapping_database_cached.cache_clear()
    dashboard._field_mapping_table_cached.cache_clear()
    bu = tmp_path / "business_units" / "demo"
    bu.mkdir(parents=True)
    storage.atomic_write_csv(
        bu / "equipment.csv",
        pd.DataFrame(
            [
                {"equipment_id": "EQ1", "equipment_name": "Pump One", "plant": "Plant", "unit_section": "Unit", "equipment_type": "Pump", "active": "true", "placeholder": "false"},
                {"equipment_id": "EQ2", "equipment_name": "Pump Two", "plant": "Plant", "unit_section": "Unit", "equipment_type": "Pump", "active": "true", "placeholder": "false"},
            ]
        ),
    )
    storage.atomic_write_csv(
        bu / "fields.csv",
        pd.DataFrame(
            [
                {"field_id": "DP1", "field_name": "Pump discharge pressure", "source": "DCS", "uom": "bar", "target": "10", "target_direction": "High", "active": "true"},
                {"field_id": "F1", "field_name": "Local discharge pressure", "source": "Field", "uom": "bar", "target": "10", "target_direction": "High", "active": "true"},
                {"field_id": "L1", "field_name": "Product quality", "source": "Lab", "uom": "%", "target": "95", "target_direction": "High", "active": "true"},
            ]
        ),
    )
    storage.atomic_write_csv(
        bu / "calculated_fields.csv",
        pd.DataFrame(
            [
                {"field_id": "CF1", "field_name": "Calculated output", "formula": "[DP1]", "uom": "bar", "aggregation": "Average", "daily_target": "10", "period_target": "10", "target_direction": "High", "status": "active", "dashboard": "true"}
            ]
        ),
    )


def test_v380_version_banner_home_permissions_and_sign_out_text_are_present():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert __version__ == "3.8.0"
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "3.8.0"
    assert 'f\'<div class="version">v{APP_VERSION}</div>' in source
    assert "Super Admin access is required to open and export this operational register" in source
    assert 'signout.button("↪ Sign Out"' in source
    assert ".st-key-top_sign_out button{white-space:nowrap" in source


def test_home_readings_export_is_grouped_into_excel_sheets(monkeypatch, tmp_path):
    from app import home_detail_sheets

    _configure_demo(monkeypatch, tmp_path)
    input_dir = tmp_path / "business_units" / "demo" / "inputs"
    input_dir.mkdir()
    storage.atomic_write_csv(input_dir / "dcs.csv", pd.DataFrame([{"Date": "2026-11-18", "DP1": "10"}]))
    storage.atomic_write_csv(input_dir / "field.csv", pd.DataFrame([{"Date": "2026-11-18", "F1": "9"}]))
    storage.atomic_write_csv(input_dir / "lab.csv", pd.DataFrame([{"Date": "2026-11-18", "L1": "96"}]))
    sheets = home_detail_sheets("demo", "viewer", "Readings")
    assert list(sheets) == ["DCS", "Field", "QAQC", "Other TA", "Other TB", "Other TC", "Other TD", "Other TE", "Other TF", "Other TG"]
    assert all(frame.empty or "Source" in frame.columns for frame in sheets.values())
    workbook = load_workbook(BytesIO(exports.excel_bytes(sheets)), read_only=True)
    assert workbook.sheetnames == list(sheets)
    workbook.close()


def test_operations_dashboard_accepts_dcs_field_qaqc_and_calculated_fields(monkeypatch, tmp_path):
    _configure_demo(monkeypatch, tmp_path)
    catalog = dashboard.operations_field_catalog("demo")
    assert set(catalog["source"]) == {"DCS", "Field", "Lab", "Calculated"}
    assert set(catalog["field_id"]) == {"DP1", "F1", "L1", "CF1"}
    defaults = dashboard.default_templates()["Operations Dashboard"]
    assert all({"DP1", "F1", "L1", "CF1"}.issubset(template["chart_fields"]) for template in defaults)


def test_chart_height_is_reduced_by_thirty_percent():
    frame = pd.DataFrame(
        {
            "Timestamp": pd.to_datetime(["2026-11-18 00:00", "2026-11-18 01:00"]),
            "value": [1.0, 2.0],
            "field_name": ["Pressure", "Pressure"],
            "uom": ["bar", "bar"],
        }
    )
    figure = dashboard._figure(frame, "Line", False, "Pressure")
    assert dashboard.CHART_HEIGHT == 231
    assert figure.layout.height == 231


def test_field_catalogue_shows_equipment_and_uses_dropdown_for_bulk_update(monkeypatch, tmp_path):
    _configure_demo(monkeypatch, tmp_path)
    payload = dashboard.mapping_update_template_bytes("demo")
    workbook = load_workbook(BytesIO(payload))
    sheet = workbook["Field Catalogue"]
    assert [cell.value for cell in sheet[1]] == [
        "Field ID", "Data Field", "Source", "Status", "Field Type", "Equipment ID", "Equipment", "Include"
    ]
    formulas = {validation.formula1 for validation in sheet.data_validations.dataValidation}
    assert formulas == {"=MappingFieldIDs", "=MappingEquipmentIDs", "=MappingIncludeOptions"}
    assert any(sheet.cell(row, 7).value for row in range(2, sheet.max_row + 1))

    for row in range(2, sheet.max_row + 1):
        if sheet.cell(row, 1).value == "DP1":
            sheet.cell(row, 6).value = "EQ2"
    review = workbook["Field Review"]
    for row in range(2, review.max_row + 1):
        if review.cell(row, 1).value == "DP1":
            review.cell(row, 2).value = "Yes"
            review.cell(row, 3).value = "Verified equipment selection from the Field Catalogue dropdown."
            review.cell(row, 4).value = "High"
    out = BytesIO()
    workbook.save(out)
    workbook.close()

    result = dashboard.bulk_update_field_mappings("demo", out.getvalue())
    assert result["fields_updated"] == 1
    assert dashboard.load_effective_field_mappings("demo")["DP1"]["equipment_ids"] == ["EQ2"]