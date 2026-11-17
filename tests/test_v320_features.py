from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from opera import dashboard, exports, operational, storage

ROOT = Path(__file__).resolve().parents[1]


def test_four_field_groups_map_qaqc_to_lab_and_others_to_ta_tg():
    registry = storage.registry("cement")
    groups = operational.grouped_registry(registry)
    assert set(groups) == {"DCS", "Field", "QAQC", "Others"}
    assert set(groups["DCS"]["source"]) == {"DCS"}
    assert set(groups["Field"]["source"]) == {"Field"}
    assert set(groups["QAQC"]["source"]) == {"Lab"}
    assert set(groups["Others"]["source"]).issubset({"TA", "TB", "TC", "TD", "TE", "TF", "TG"})


def test_selective_bulk_template_contains_only_requested_fields():
    columns = pd.read_csv(__import__("io").BytesIO(storage.template_bytes("cement", "DCS", ["DP1", "DP3"]))).columns.tolist()
    assert columns == ["Date", "Time", "Business unit", "Plant", "Unit/Section", "Equipment", "DP1", "DP3"]


def test_equipment_template_override_falls_back_to_default():
    template = {"chart_fields": ["DP1"], "table_fields": ["DP2"], "equipment_fields": {"EQ04": {"chart_fields": ["F1"], "table_fields": ["F2"]}}}
    assert dashboard.fields_for_equipment(template, "EQ04") == (["F1"], ["F2"])
    assert dashboard.fields_for_equipment(template, "EQ05") == (["DP1"], ["DP2"])


def test_bounded_linear_optimization_maximizes_known_response():
    x1 = np.tile(np.arange(1.0, 6.0), 5)
    x2 = np.repeat(np.arange(1.0, 6.0), 5)
    aligned = pd.DataFrame({"DP1": x1, "DP2": x2, "L1": 10 + 2 * x1 - 3 * x2})
    result = operational.optimize_linear_response(aligned, ["DP1", "DP2"], "L1", "Maximize outcome", bounds={"DP1": (1, 5), "DP2": (1, 5)})
    assert result["recommendation"] == {"DP1": 5.0, "DP2": 1.0}
    assert result["r_squared"] > 0.999


def test_out_of_target_mask_marks_input_and_calculated_values():
    inputs = pd.DataFrame([{"field_id": "DP1", "min_value": "0", "max_value": "10"}])
    calculated = pd.DataFrame([{"field_id": "CF1", "field_name": "Output", "period_target": "5", "target_direction": "High"}])
    frame = pd.DataFrame([{"Field ID": "DP1", "Average": 12}, {"Field ID": "DP1", "Average": 8}])
    mask = operational.out_of_target_mask(frame, inputs, calculated)
    assert bool(mask.loc[0, "Average"])
    assert not bool(mask.loc[1, "Average"])
    report = pd.DataFrame([{"KPI": "Output", "Value": 4}, {"KPI": "Output", "Value": 6}])
    report_mask = operational.out_of_target_mask(report, inputs, calculated)
    assert bool(report_mask.loc[0, "Value"])
    assert not bool(report_mask.loc[1, "Value"])


def test_lesson_schema_and_corrected_cement_calculated_names():
    lessons = storage.read_csv(storage.bu_dir("cement") / "lessons.csv")
    assert {"lesson_title", "equipment", "attachment_path", "attachment_name", "attachment_type", "read_count"}.issubset(lessons.columns)
    definitions = storage.read_csv(storage.bu_dir("cement") / "calculated_fields.csv").set_index("field_id")
    assert definitions.at["CF2", "field_name"] == "Kiln Speed"
    assert definitions.at["CF3", "field_name"] == "Kiln Inlet Oxygen"


def test_pdf_export_wraps_long_text_and_returns_valid_pdf():
    frame = pd.DataFrame([{f"Column {i}": "A long value that must wrap instead of overlap " * 3 for i in range(10)}])
    payload = exports.pdf_bytes("Readable Export", frame)
    assert payload.startswith(b"%PDF")
    assert len(payload) > 1500
