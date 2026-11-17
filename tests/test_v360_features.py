from __future__ import annotations

from io import BytesIO
import re
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

from opera import dashboard, storage


ROOT = Path(__file__).resolve().parents[1]


def test_named_engineering_mappings_use_physical_equipment_and_meaningful_templates():
    cement = dashboard.field_mapping_table("cement").set_index("Field ID")
    assert set(cement.at["DP1", "_equipment_ids"]) == {"EQ04", "OBJ-EQ04", "IBE-EQ04"}
    assert set(cement.at["DP8", "_equipment_ids"]) == {"EQ05", "OBJ-EQ05", "IBE-EQ05"}
    assert set(cement.at["DP12", "_equipment_ids"]) == {"EQ07", "OBJ-EQ07", "IBE-EQ07"}
    assert set(cement.at["L12", "_equipment_ids"]) == {"EQ31", "OBJ-EQ31", "IBE-EQ31"}
    assert "quality-compliance" in cement.at["L12", "_template_ids"]
    assert cement.at["DP1", "Confidence"] == "High"
    assert "round-robin" not in cement.at["DP1", "Mapping Basis"].lower()

    refinery = dashboard.field_mapping_table("refinery").set_index("Field ID")
    assert set(refinery.at["DP2", "_equipment_ids"]) == {"REF-BUT-RX-01", "REF-BUT-RX-02"}
    assert refinery.at["DP11", "_equipment_ids"] == ("REF-BUT-DRY-01",)
    assert refinery.at["DP8", "_equipment_ids"] == ("REF-BUT-STAB-01",)

    fertilizer = dashboard.field_mapping_table("fertilizer").set_index("Field ID")
    assert fertilizer.at["DP9", "_equipment_ids"] == ("FER-UREA-RX-01",)
    assert fertilizer.at["DP14", "_equipment_ids"] == ("FER-GRAN-01",)

    nascon = dashboard.field_mapping_table("nascon").set_index("Field ID")
    assert nascon.at["DP1", "_equipment_ids"] == ("NAS-SALT-EVAP-01",)
    assert nascon.at["DP14", "_equipment_ids"] == ("NAS-SUGAR-CENT-01",)


def test_placeholder_mappings_use_spares_source_templates_and_review_basis():
    expected = {
        "DP21": {"process-performance"},
        "L21": {"quality-compliance"},
        "F21": {"process-performance", "condition-monitoring"},
        "TA1": {"process-performance"},
    }
    mappings = dashboard.field_mapping_table("cement").set_index("Field ID")
    for field_id, template_ids in expected.items():
        row = mappings.loc[field_id]
        assert all("SPARE" in equipment_id for equipment_id in row["_equipment_ids"])
        assert set(row["_template_ids"]) == template_ids
        assert row["Confidence"] == "Review"
        assert row["Mapping Basis"] == "Default placeholder mapping – review when field is named."


def test_instrument_check_pairs_are_recorded_for_same_point_measurements():
    refinery_pairs = dashboard.instrument_check_pairs("refinery")
    assert refinery_pairs["F17"] == ["DP1"]
    assert refinery_pairs["F18"] == ["DP2"]
    assert refinery_pairs["F3"] == ["DP4"]
    assert dashboard.instrument_check_pairs("fertilizer")["F7"] == ["DP9"]
    assert dashboard.instrument_check_pairs("nascon")["F1"] == ["DP2"]
    assert dashboard.instrument_check_pairs("nascon")["F11"] == ["DP12"]
    assert dashboard.instrument_check_pairs("cement") == {}


def test_calculated_fields_match_formulas_and_inherit_input_equipment():
    expected_names_and_formulas = {
        ("fertilizer", "CF5"): ("Field-DCS Urea Pressure Deviation", "ABS([F7]-[DP9])"),
        ("nascon", "CF5"): ("Salt Evaporator Temperature Deviation", "ABS([F1]-[DP2])"),
        ("refinery", "CF6"): ("Reactor Temperature Rise", "ABS([DP3]-[DP2])"),
        ("cement", "CF6"): ("Calciner-Preheater Temperature Difference", "ABS([DP5]-[DP4])"),
    }
    for bu in ("cement", "refinery", "fertilizer", "nascon"):
        calculated = storage.read_csv(storage.bu_dir(bu) / "calculated_fields.csv").set_index("field_id")
        records = dashboard.load_default_field_mappings(bu)
        for field_id, row in calculated.iterrows():
            inputs = list(dict.fromkeys(re.findall(r"\[([^\]]+)\]", row["formula"])))
            inherited = []
            for input_id in inputs:
                inherited.extend(records[input_id]["equipment_ids"])
            assert set(records[field_id]["equipment_ids"]) == set(inherited)
            assert all(input_id in records[field_id]["mapping_basis"] for input_id in inputs)
    for (bu, field_id), (name, formula) in expected_names_and_formulas.items():
        row = storage.read_csv(storage.bu_dir(bu) / "calculated_fields.csv").set_index("field_id").loc[field_id]
        assert row["field_name"] == name
        assert row["formula"] == formula


def test_mapping_template_has_controlled_lists_and_partial_bulk_update(tmp_path, monkeypatch):
    data_root = tmp_path / "data"
    bu_dir = data_root / "business_units" / "demo"
    bu_dir.mkdir(parents=True)
    monkeypatch.setattr(storage, "DATA_ROOT", data_root)
    storage.atomic_write_csv(
        bu_dir / "equipment.csv",
        pd.DataFrame(
            [
                {"equipment_id": "EQ1", "equipment_name": "Pump One", "plant": "Plant", "unit_section": "Unit", "equipment_type": "Pump", "active": "true", "placeholder": "false"},
                {"equipment_id": "EQ2", "equipment_name": "Pump Two", "plant": "Plant", "unit_section": "Unit", "equipment_type": "Pump", "active": "true", "placeholder": "false"},
                {"equipment_id": "DEMO-SPARE-001", "equipment_name": "Spare equipment 001", "plant": "Plant", "unit_section": "Unassigned", "equipment_type": "Placeholder", "active": "true", "placeholder": "true"},
            ]
        ),
    )
    storage.atomic_write_csv(
        bu_dir / "fields.csv",
        pd.DataFrame(
            [
                {"field_id": "DP1", "field_name": "Pump discharge pressure", "source": "DCS", "uom": "bar", "active": "true"},
                {"field_id": "F1", "field_name": "Local discharge pressure", "source": "Field", "uom": "bar", "active": "true"},
            ]
        ),
    )
    storage.atomic_write_csv(bu_dir / "calculated_fields.csv", pd.DataFrame(columns=["field_id", "field_name", "formula", "status"]))

    template = dashboard.mapping_update_template_bytes("demo")
    workbook = load_workbook(BytesIO(template))
    assert {"Instructions", "Equipment Mappings", "Template Mappings", "Field Review", "Lists"}.issubset(workbook.sheetnames)
    assert workbook["Lists"].sheet_state == "hidden"
    assert len(workbook["Equipment Mappings"].data_validations.dataValidation) == 3
    assert len(workbook["Template Mappings"].data_validations.dataValidation) == 3
    assert len(workbook["Field Review"].data_validations.dataValidation) == 3
    assert {"MappingFieldIDs", "MappingEquipmentIDs", "MappingTemplateIDs", "MappingIncludeOptions", "MappingConfidenceOptions"}.issubset(set(workbook.defined_names))

    equipment_sheet = workbook["Equipment Mappings"]
    for row in range(2, equipment_sheet.max_row + 1):
        if equipment_sheet.cell(row, 1).value == "DP1":
            equipment_sheet.cell(row, 2).value = "EQ2"
    review_sheet = workbook["Field Review"]
    for row in range(2, review_sheet.max_row + 1):
        if review_sheet.cell(row, 1).value == "DP1":
            review_sheet.cell(row, 2).value = "Yes"
            review_sheet.cell(row, 3).value = "Verified pump discharge mapping for the demo test."
            review_sheet.cell(row, 4).value = "High"
    out = BytesIO()
    workbook.save(out)
    workbook.close()

    summary = dashboard.bulk_update_field_mappings("demo", out.getvalue())
    assert summary["fields_updated"] == 1
    updated = dashboard.load_effective_field_mappings("demo")
    assert updated["DP1"]["equipment_ids"] == ["EQ2"]
    assert updated["DP1"]["mapping_type"] == "Admin Override"
    assert updated["DP1"]["confidence"] == "High"
    assert updated["F1"]["mapping_type"] == "Computed Default"


def test_mapping_quality_report_contains_counts_review_list_and_twenty_samples():
    report = (ROOT / "MAPPING_QUALITY_REPORT.md").read_text(encoding="utf-8")
    assert "Mapping counts by BU and dashboard template" in report
    assert "Named mappings marked Review" in report
    assert "Placeholder Review summary" in report
    assert "Twenty named mappings for spot-checking" in report
    sample_section = report.split("## Twenty named mappings for spot-checking", 1)[1].split("## Calculated-field check", 1)[0]
    assert sample_section.count("| cement |") == 5
    assert sample_section.count("| refinery |") == 5
    assert sample_section.count("| fertilizer |") == 5
    assert sample_section.count("| nascon |") == 5
