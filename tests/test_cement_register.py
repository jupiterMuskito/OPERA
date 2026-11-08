from pathlib import Path

from openpyxl import load_workbook

from opera.risk_engine import REQUIRED_SHEETS, collect_hazards, load_register
from opera.risk_pdf import build_pdf

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "registers" / "OKPELLA_Master_Workbook_v8.xlsx"


def test_cement_register_schema_and_engine_load():
    wb = load_workbook(REGISTER, read_only=True, data_only=True)
    assert wb.sheetnames == ["ReadMe","Lists","Locations","JobTags","EquipmentTypes","Equipment","ActivityHazards","EquipmentHazards","TaskPresets","ToolRecognition","InferenceRules","ReportTemplate","AgentText"]
    assert all(name in wb.sheetnames for name in REQUIRED_SHEETS)
    wb.close()
    register = load_register(REGISTER)
    assert len(register.locations) == 46
    assert len(register.equipment) == 67
    assert len(register.activity_hazards) == 259
    assert len(register.equipment_hazards) == 101
    assert not register.warnings


def test_p23_generates_risk_assessment_pdf():
    register = load_register(REGISTER)
    preset = next(p for p in register.presets if p["id"] == "P23")
    hazards = collect_hazards(register, preset["tags"], preset["et"], preset["mo"], preset["st"])
    assert len(hazards) >= 1
    payload = {"serial":"TEST-P23","bu":"Cement","company":"OPERA","form_title":"RISK ASSESSMENT FORM","register_status":"Approved","register_source":"Bundled approved register","fingerprint":register.fingerprint,
               "header":[("Preset",preset["n"]),("Equipment",preset["ref"])],"hazards":hazards,"excluded":set(),"categories":register.categories,
               "erp":["Raise alarm and stop work."],"assessed_by":"Test User","reviewed_by":"","generated":"2026-11-08T12:00:00+00:00"}
    pdf = build_pdf(payload)
    assert pdf.startswith(b"%PDF") and len(pdf) > 5000
