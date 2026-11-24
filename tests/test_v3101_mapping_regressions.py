from io import BytesIO

import pytest
from openpyxl import load_workbook

from opera import dashboard, storage
from opera.version import version_badge_html
from test_v380_features import _configure_demo


def _make_pre_v39_mapping_database(monkeypatch, tmp_path):
    """Create live data whose mapping workbook predates template columns."""
    _configure_demo(monkeypatch, tmp_path)
    path = dashboard.ensure_mapping_database("demo")
    workbook = load_workbook(path)
    for sheet_name in ("Field Mappings", "Default Mappings"):
        sheet = workbook[sheet_name]
        headers = {cell.value: cell.column for cell in sheet[1]}
        for header in ("Dashboard Templates", "Template IDs"):
            column = headers.get(header)
            if column:
                sheet.delete_cols(column)
                headers = {cell.value: cell.column for cell in sheet[1]}
        note_column = sheet.max_column + 1
        sheet.cell(1, note_column).value = "Legacy Admin Note"
        sheet.cell(2, note_column).value = "preserve this live value"
    notes = workbook.create_sheet("Legacy Custom Sheet")
    notes.append(["Setting", "Value"])
    notes.append(["Owner", "Operations"])
    workbook.save(path)
    workbook.close()

    runtime_path = storage.bu_dir("demo") / "field_mappings.runtime.json.gz"
    runtime_path.unlink(missing_ok=True)
    dashboard._ensure_mapping_database_cached.cache_clear()
    dashboard._read_mapping_database_cached.cache_clear()
    dashboard._field_mapping_table_cached.cache_clear()
    return path


def _mark_dp1_for_update(workbook, basis="v3.10.1 regression update"):
    review = workbook["Field Review"]
    for row in range(2, review.max_row + 1):
        if review.cell(row, 1).value == "DP1":
            review.cell(row, 2).value = "Yes"
            review.cell(row, 3).value = basis
            review.cell(row, 4).value = "High"
            return
    raise AssertionError("DP1 was not present in Field Review")


def test_pre_v39_live_data_is_upgraded_before_in_app_template_download(monkeypatch, tmp_path):
    path = _make_pre_v39_mapping_database(monkeypatch, tmp_path)

    # Reproduces the live-server combination: current app/version code plus an
    # old persistent OPERA_DATA_DIR mapping workbook.
    assert version_badge_html() == '<div class="version">v3.11.1</div>'
    payload = dashboard.mapping_update_template_bytes("demo")

    template = load_workbook(BytesIO(payload))
    catalogue = template["Field Catalogue"]
    headers = [cell.value for cell in catalogue[1]]
    assert headers[5:10] == [
        "Equipment ID",
        "Equipment",
        "Dashboard Template ID",
        "Dashboard Template",
        "Include",
    ]
    validations = {item.formula1: str(item.sqref) for item in catalogue.data_validations.dataValidation}
    assert "=MappingEquipmentIDs" in validations
    assert "=MappingTemplateIDs" in validations
    assert "H2:H50000" in validations["=MappingTemplateIDs"]
    template_names = {
        template["Template Catalogue"].cell(row, 2).value
        for row in range(2, template["Template Catalogue"].max_row + 1)
    }
    assert template_names == {
        "Plant Performance",
        "Condition Monitoring",
        "Process Performance",
        "Quality and Compliance",
        "Reliability",
    }
    template.close()

    # The actual live workbook is upgraded in place and unrelated content is
    # retained rather than being replaced with a freshly seeded workbook.
    upgraded = load_workbook(path)
    for sheet_name in ("Field Mappings", "Default Mappings"):
        sheet = upgraded[sheet_name]
        upgraded_headers = [cell.value for cell in sheet[1]]
        assert "Template IDs" in upgraded_headers
        assert "Dashboard Templates" in upgraded_headers
        assert "Legacy Admin Note" in upgraded_headers
        assert sheet.cell(2, upgraded_headers.index("Legacy Admin Note") + 1).value == "preserve this live value"
        assert sheet.cell(2, upgraded_headers.index("Template IDs") + 1).value
        assert sheet.cell(2, upgraded_headers.index("Dashboard Templates") + 1).value
    assert upgraded["Legacy Custom Sheet"]["B2"].value == "Operations"
    upgraded.close()


def test_field_catalogue_bulk_upload_updates_multiple_templates_and_backend_database(monkeypatch, tmp_path):
    _make_pre_v39_mapping_database(monkeypatch, tmp_path)
    workbook = load_workbook(BytesIO(dashboard.mapping_update_template_bytes("demo")))
    catalogue = workbook["Field Catalogue"]

    for row in range(catalogue.max_row, 1, -1):
        if catalogue.cell(row, 1).value == "DP1":
            catalogue.delete_rows(row)
    catalogue.append(["DP1", "Pump discharge pressure", "Digital Data", "Active", "Input", "EQ2", "Pump Two", "plant-performance", "Plant Performance", "Yes"])
    catalogue.append(["DP1", "Pump discharge pressure", "Digital Data", "Active", "Input", "EQ2", "Pump Two", "reliability", "Reliability", "Yes"])
    _mark_dp1_for_update(workbook)
    output = BytesIO()
    workbook.save(output)
    workbook.close()

    summary = dashboard.bulk_update_field_mappings("demo", output.getvalue())
    mapping = dashboard.load_effective_field_mappings("demo")["DP1"]
    assert summary == {"fields_updated": 1, "equipment_relationships": 1, "template_relationships": 2}
    assert mapping["equipment_ids"] == ["EQ2"]
    assert mapping["template_ids"] == ["plant-performance", "reliability"]

    backend = load_workbook(BytesIO(dashboard.mapping_database_bytes("demo")), read_only=True)
    sheet = backend["Field Mappings"]
    headers = [cell.value for cell in sheet[1]]
    assert headers[headers.index("Equipment IDs") + 1:headers.index("Equipment IDs") + 3] == ["Template IDs", "Dashboard Templates"]
    dp1_row = next(row for row in range(2, sheet.max_row + 1) if sheet.cell(row, headers.index("Field ID") + 1).value == "DP1")
    assert sheet.cell(dp1_row, headers.index("Template IDs") + 1).value == "plant-performance; reliability"
    assert sheet.cell(dp1_row, headers.index("Dashboard Templates") + 1).value == "Plant Performance; Reliability"
    backend.close()


def test_field_catalogue_bulk_upload_reports_invalid_template_value(monkeypatch, tmp_path):
    _make_pre_v39_mapping_database(monkeypatch, tmp_path)
    workbook = load_workbook(BytesIO(dashboard.mapping_update_template_bytes("demo")))
    catalogue = workbook["Field Catalogue"]
    dp1_row = next(row for row in range(2, catalogue.max_row + 1) if catalogue.cell(row, 1).value == "DP1")
    catalogue.cell(dp1_row, 8).value = "not-a-dashboard-template"
    _mark_dp1_for_update(workbook, "invalid-template validation regression")
    output = BytesIO()
    workbook.save(output)
    workbook.close()

    with pytest.raises(ValueError, match="unknown Dashboard Template ID 'not-a-dashboard-template'"):
        dashboard.bulk_update_field_mappings("demo", output.getvalue())
