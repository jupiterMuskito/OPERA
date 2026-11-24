from io import BytesIO
from pathlib import Path

from openpyxl import load_workbook

from opera import __version__, dashboard, operational, storage
from test_v380_features import _configure_demo


ROOT = Path(__file__).resolve().parents[1]


def test_display_names_change_without_changing_persisted_source_ids():
    assert __version__ == "3.11.1"
    assert storage.SOURCES["DCS"] == "DP"
    assert storage.SOURCES["Field"] == "F"
    assert storage.source_label("DCS") == "Digital Data"
    assert storage.source_label("Field") == "Raw Field Data"
    assert operational.SOURCE_GROUPS["Digital Data"] == ("DCS",)
    assert operational.SOURCE_GROUPS["Raw Field Data"] == ("Field",)


def test_field_catalogue_maps_equipment_and_template_together(monkeypatch, tmp_path):
    _configure_demo(monkeypatch, tmp_path)
    workbook = load_workbook(BytesIO(dashboard.mapping_update_template_bytes("demo")))
    catalogue = workbook["Field Catalogue"]
    headers = [cell.value for cell in catalogue[1]]
    assert headers[5:10] == [
        "Equipment ID", "Equipment", "Dashboard Template ID", "Dashboard Template", "Include"
    ]
    formulas = {validation.formula1 for validation in catalogue.data_validations.dataValidation}
    assert {"=MappingEquipmentIDs", "=MappingTemplateIDs", "=MappingIncludeOptions"}.issubset(formulas)

    for row in range(2, catalogue.max_row + 1):
        if catalogue.cell(row, 1).value == "DP1":
            catalogue.cell(row, 6).value = "EQ2"
            catalogue.cell(row, 8).value = "reliability"
    review = workbook["Field Review"]
    for row in range(2, review.max_row + 1):
        if review.cell(row, 1).value == "DP1":
            review.cell(row, 2).value = "Yes"
            review.cell(row, 3).value = "Verified equipment and dashboard template in the combined Field Catalogue."
            review.cell(row, 4).value = "High"
    out = BytesIO()
    workbook.save(out)
    workbook.close()

    summary = dashboard.bulk_update_field_mappings("demo", out.getvalue())
    mapping = dashboard.load_effective_field_mappings("demo")["DP1"]
    assert summary == {"fields_updated": 1, "equipment_relationships": 1, "template_relationships": 1}
    assert mapping["equipment_ids"] == ["EQ2"]
    assert mapping["template_ids"] == ["reliability"]

    database = load_workbook(BytesIO(dashboard.mapping_database_bytes("demo")), read_only=True)
    database_sheet = database["Field Mappings"]
    exported_sources = {database_sheet.cell(row, 3).value for row in range(2, database_sheet.max_row + 1)}
    assert {"Digital Data", "Raw Field Data", "QAQC"}.issubset(exported_sources)
    database.close()


def test_branding_and_optimization_are_packaged():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert (ROOT / "assets" / "dangote_group_logo.webp").stat().st_size > 0
    assert (ROOT / "assets" / "dangote_vision_2030.png").stat().st_size > 0
    assert '"Operational Data Pipeline", "Process Optimization"' in source
    assert '"Operational Knowledge": ["Event Log", "Lesson Bank", "Job Risk Assessment"]' in source
    analysis = source[source.index("def page_analysis"):source.index("def page_process_optimization")]
    assert '"Optimization"' not in analysis
    assert "def page_process_optimization" in source
    assert "login-title" in source and "login-heading-row" in source and "opera-vision-block" in source


def test_job_risk_assessment_is_the_user_facing_name():
    app_source = (ROOT / "app.py").read_text(encoding="utf-8")
    pdf_source = (ROOT / "opera" / "risk_pdf.py").read_text(encoding="utf-8")
    assert '"Job Risk Assessment"' in app_source
    assert "Generate Job Risk Assessment" in app_source
    assert "Job Risk Assessment Hazards" in app_source
    assert "job_risk_assessment_generated" in app_source
    assert "job_risk_assessment_exported" in app_source
    assert "Job Risk Assessment" in pdf_source
    assert "risk_assessments.csv" in app_source  # existing live-data filename is intentionally stable