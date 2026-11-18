from __future__ import annotations

import io
import json
from pathlib import Path

import pandas as pd
import pytest
from openpyxl import load_workbook

from opera import auth, config, dashboard, dcs_connector, formula, storage


@pytest.fixture()
def configured_data_root(tmp_path, monkeypatch):
    root = tmp_path / "data"
    bu = root / "business_units" / "demo"
    (bu / "inputs").mkdir(parents=True)
    (root / "shared").mkdir(parents=True)
    monkeypatch.setattr(storage, "DATA_ROOT", root)
    storage.clear_data_caches()
    dashboard._read_mapping_database_cached.cache_clear()
    dashboard._ensure_mapping_database_cached.cache_clear()
    dashboard._field_mapping_table_cached.cache_clear()

    storage.atomic_write_csv(root / "shared" / "business_units.csv", pd.DataFrame([
        {"id": "demo", "name": "Demo", "active": "true", "placeholder": "false", "register_file": "", "notes": ""}
    ]))
    storage.atomic_write_csv(root / "shared" / "users.csv", pd.DataFrame(columns=[
        "username", "display_name", "password_hash", "role", "business_units", "active",
        "must_change_password", "failed_attempts", "lock_until",
    ]))
    storage.atomic_write_csv(bu / "equipment.csv", pd.DataFrame([
        {"equipment_id": "EQ1", "equipment_name": "Kiln One", "plant": "Plant A", "unit_section": "Kiln", "equipment_type": "Kiln", "active": "true", "placeholder": "false"},
        {"equipment_id": "DEMO-SPARE-001", "equipment_name": "Spare 1", "plant": "Plant A", "unit_section": "Unassigned", "equipment_type": "Placeholder", "active": "true", "placeholder": "true"},
    ]))
    storage.atomic_write_csv(bu / "fields.csv", pd.DataFrame([
        {"field_id": "DP1", "source": "DCS", "field_name": "Kiln Feed", "uom": "t/h", "min_value": "0", "max_value": "500", "data_format": "0.00", "target": "400", "target_direction": "High", "jump_limit": "100", "active": "true"},
        {"field_id": "DP2", "source": "DCS", "field_name": "DCS placeholder field 2", "uom": "UOM?", "min_value": "", "max_value": "", "data_format": "0.00", "target": "", "target_direction": "High", "jump_limit": "", "active": "false"},
        {"field_id": "F1", "source": "Field", "field_name": "Local Kiln Feed", "uom": "t/h", "min_value": "0", "max_value": "500", "data_format": "0.00", "target": "400", "target_direction": "High", "jump_limit": "100", "active": "true"},
    ]))
    definitions = []
    for index in range(1, 13):
        definitions.append({"field_id": f"CF{index}", "field_name": f"Calculated {index}", "formula": "[DP1]", "uom": "t/h", "aggregation": "Average", "daily_target": "400", "period_target": "400", "target_direction": "High", "status": "active", "evaluation_order": str(index), "mtd_aggregation": "Average", "ytd_aggregation": "Average", "dashboard": "true", "dashboard_group": "Operations", "chart": "line"})
    storage.atomic_write_csv(bu / "calculated_fields.csv", pd.DataFrame(definitions))
    for source in storage.SOURCES:
        storage.atomic_write_csv(bu / "inputs" / f"{source.lower()}.csv", pd.DataFrame(columns=storage.BASE_COLUMNS))
    storage.atomic_write_csv(bu / "events.csv", pd.DataFrame(columns=["event_id", "equipment", "event_types", "event_date"]))
    storage.atomic_write_csv(bu / "lessons.csv", pd.DataFrame(columns=["lesson_id", "equipment", "lesson_title"]))
    storage.atomic_write_csv(bu / "audit_log.csv", pd.DataFrame(columns=["timestamp", "business_unit", "user", "action", "details"]))
    storage.atomic_write_csv(bu / "notifications.csv", pd.DataFrame(columns=["id", "timestamp", "recipient", "level", "message", "created_by", "read_by"]))
    storage.atomic_write_csv(bu / "flags.csv", pd.DataFrame(columns=["timestamp", "date", "time", "field_id", "value", "flag_type", "message", "status"]))
    storage.save_json(bu / "dashboard_templates.json", dashboard.default_templates())
    storage.save_json(bu / "constants.json", {"B_capacity": 500})
    storage.save_json(bu / "pipeline.json", {"url": "", "token_secret_name": ""})
    storage.save_json(bu / "presets.json", {})
    storage.save_json(bu / "equipment_validation.json", {"plants": ["Plant A"], "units": ["Kiln"], "equipment_types": ["Kiln"]})
    return root


def test_admin_field_mapping_to_chart_end_to_end_without_restart(configured_data_root):
    bu = "demo"
    dashboard.ensure_mapping_database(bu)

    # Simulate Admin renaming and activating a placeholder with real metadata.
    fields = storage.registry(bu)
    idx = fields[fields["field_id"] == "DP2"].index[0]
    fields.loc[idx, ["field_name", "uom", "min_value", "max_value", "target", "active"]] = [
        "Kiln Main Drive Current", "A", "100", "500", "320", "true"
    ]
    storage.atomic_write_csv(storage.bu_dir(bu) / "fields.csv", fields)
    dashboard.save_field_mapping(bu, "DP2", ["EQ1"], ["plant-performance", "process-performance"])

    templates = dashboard.load_templates(bu)
    plant_template = templates["Plant Overview"][0]
    plant_template["chart_fields"] = ["DP2"] + [field for field in plant_template["chart_fields"] if field != "DP2"][:11]
    dashboard.save_templates(bu, templates)

    row = {"Date": "2026-11-18", "Time": "12:00", "Business unit": bu, "Plant": "Plant A", "Unit/Section": "Kiln", "Equipment": "EQ1", "DP2": "325"}
    count, flags = storage.save_validated_input(bu, "DCS", pd.DataFrame([row]), "admin")
    assert (count, flags) == (1, 0)

    # Same runtime process: every downstream selector/data path sees the change.
    registry = storage.registry(bu)
    assert registry.set_index("field_id").at["DP2", "uom"] == "A"
    assert "DP2" in dashboard.mapped_field_ids(bu, registry[registry["active"] == "true"], equipment_id="EQ1", template_id="plant-performance")
    assert dashboard.load_templates(bu)["Plant Overview"][0]["chart_fields"][0] == "DP2"
    assert storage.source_data(bu, "DCS", ["DP2"])["DP2"].tolist() == ["325"]
    assert all(len(item["chart_fields"]) == 12 and len(item["table_fields"]) == 12 for templates in dashboard.load_templates(bu).values() for item in templates)


def test_excel_mapping_template_validation_and_bulk_upload_are_immediate(configured_data_root):
    dashboard.ensure_mapping_database("demo")
    payload = dashboard.mapping_update_template_bytes("demo")
    workbook = load_workbook(io.BytesIO(payload))
    assert workbook["Equipment Mappings"].data_validations.count >= 3
    assert workbook["Template Mappings"].data_validations.count >= 3
    review = workbook["Field Review"]
    row = next(index for index in range(2, review.max_row + 1) if review.cell(index, 1).value == "DP1")
    review.cell(row, 2).value = "Yes"
    review.cell(row, 3).value = "E2E Admin mapping update"
    review.cell(row, 4).value = "High"
    template_sheet = workbook["Template Mappings"]
    template_sheet.append(["DP1", "plant-performance", "Yes"])
    output = io.BytesIO()
    workbook.save(output)
    summary = dashboard.bulk_update_field_mappings("demo", output.getvalue())
    assert summary["fields_updated"] == 1
    assert dashboard.load_effective_field_mappings("demo")["DP1"]["mapping_type"] == "Admin Override"


def test_business_unit_user_role_equipment_and_validation_changes_are_immediate(configured_data_root):
    new_bu = config.clone_business_unit("demo", "Second Plant", True, "superadmin")
    assert new_bu == "second-plant"
    assert new_bu in set(config.business_units(active_only=True)["id"])

    created = auth.create_user("operator2", "Operator Two", "Operator", ["demo"], "Temporary1234")
    assert auth.allowed(created, "input") and not auth.allowed(created, "configure")
    updated = auth.update_user_access("operator2", "Administrator Two", "BU Admin", ["demo", new_bu], True)
    assert auth.allowed(updated, "configure") and auth.can_access_bu(auth.get_user("operator2"), new_bu)

    equipment = storage.equipment("demo")
    equipment.loc[equipment["equipment_id"] == "EQ1", "equipment_name"] = "Kiln One Renamed"
    storage.atomic_write_csv(storage.bu_dir("demo") / "equipment.csv", equipment)
    dashboard.save_hierarchy_options("demo", {"plants": ["Plant A", "Plant B"], "units": ["Kiln", "Packing"], "equipment_types": ["Kiln", "Packer"]})
    assert storage.equipment("demo").set_index("equipment_id").at["EQ1", "equipment_name"] == "Kiln One Renamed"
    assert "Plant B" in dashboard.hierarchy_options("demo")["plants"]


def test_ranges_targets_formulas_constants_presets_events_and_lessons(configured_data_root):
    fields = storage.registry("demo")
    fields.loc[fields["field_id"] == "DP1", ["max_value", "target"]] = ["410", "405"]
    storage.atomic_write_csv(storage.bu_dir("demo") / "fields.csv", fields)
    invalid = pd.DataFrame([{"Date": "2026-11-18", "Time": "06:00", "Business unit": "demo", "Plant": "Plant A", "Unit/Section": "Kiln", "Equipment": "EQ1", "DP1": "450"}])
    _, issues, flags = storage.validate_rows("demo", "DCS", invalid)
    assert issues.empty and flags.iloc[0]["flag_type"] == "Out of range"

    storage.save_json(storage.bu_dir("demo") / "constants.json", {"B_capacity": 500, "loss": 25})
    output, errors = formula.apply_ordered(pd.DataFrame([{"DP1": 400}]), [{"field_id": "CFX", "formula": "[DP1] / B_capacity * 100", "status": "active", "evaluation_order": 1}], storage.json_setting(storage.bu_dir("demo") / "constants.json", {}))
    assert not errors and output.at[0, "CFX"] == 80

    config.save_preset("demo", "Shift View", {"module": "Plant Overview"}, "admin")
    assert config.load_presets("demo")["Shift View"]["module"] == "Plant Overview"
    storage.append_rows(storage.bu_dir("demo") / "events.csv", [{"event_id": "EV1", "equipment": "EQ1", "event_types": "Process Deviation", "event_date": "2026-11-18"}])
    storage.append_rows(storage.bu_dir("demo") / "lessons.csv", [{"lesson_id": "LE1", "equipment": "EQ1", "lesson_title": "Stable feed"}])
    assert storage.read_csv(storage.bu_dir("demo") / "events.csv").iloc[-1]["equipment"] == "EQ1"
    assert storage.read_csv(storage.bu_dir("demo") / "lessons.csv").iloc[-1]["equipment"] == "EQ1"


def test_dcs_connector_uses_latest_settings_and_validates_ingest(configured_data_root, monkeypatch):
    settings = {"url": "https://dcs.example/api", "token_secret_name": "plant_token"}
    storage.save_json(storage.bu_dir("demo") / "pipeline.json", settings)
    assert storage.json_setting(storage.bu_dir("demo") / "pipeline.json", {}) == settings
    payload = pd.DataFrame([{"Date": "2026-11-18", "Time": "18:00", "Business unit": "demo", "Plant": "Plant A", "Unit/Section": "Kiln", "Equipment": "EQ1", "DP1": "401"}])
    monkeypatch.setattr(dcs_connector, "pull_json", lambda url, token: payload)
    count, flags = dcs_connector.ingest("demo", settings["url"], "secret", "admin")
    assert (count, flags) == (1, 0)
    assert storage.source_data("demo", "DCS", ["DP1"])["DP1"].tolist() == ["401"]
