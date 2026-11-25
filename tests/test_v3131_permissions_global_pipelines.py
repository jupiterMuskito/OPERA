from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from openpyxl import Workbook

from opera import auth, pipelines, storage
from scripts import pipeline_scheduler

ROOT = Path(__file__).resolve().parents[1]
BUS = {
    "refinery": ("Dangote Refinery", "REF-1", "Refinery", "CDU"),
    "cement": ("Dangote Cement", "CEM-1", "Okpella", "Kiln"),
    "fertilizer": ("Dangote Fertilizer", "FER-1", "Fertilizer", "Urea"),
}


def _three_bu_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    root = tmp_path / "data"
    (root / "shared").mkdir(parents=True)
    pd.DataFrame([
        {"id": bu, "name": values[0], "active": "true"}
        for bu, values in BUS.items()
    ]).to_csv(root / "shared" / "business_units.csv", index=False)
    for bu, (_, equipment_id, plant, section) in BUS.items():
        folder = root / "business_units" / bu
        (folder / "inputs").mkdir(parents=True)
        pd.DataFrame([
            {
                "field_id": "DP1", "field_name": "Production value", "source": "DCS",
                "active": "true", "min_value": "0", "max_value": "1000", "jump_limit": "",
            }
        ]).to_csv(folder / "fields.csv", index=False)
        pd.DataFrame([
            {
                "equipment_id": equipment_id, "equipment_name": equipment_id,
                "plant": plant, "unit_section": section, "active": "true", "placeholder": "false",
            }
        ]).to_csv(folder / "equipment.csv", index=False)
        pd.DataFrame(columns=storage.BASE_COLUMNS + ["DP1"]).to_csv(folder / "inputs" / "dcs.csv", index=False)
    monkeypatch.setattr(storage, "DATA_ROOT", root)
    storage.clear_data_caches()
    return root


def _write_workbook(path: Path, rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Live Data"
    sheet.append(["Date", "Time", "Business unit", "Plant", "Unit/Section", "Equipment", "DP1"])
    for row in rows:
        sheet.append(row)
    workbook.save(path)


def _row(bu: str, value: float) -> list[object]:
    _, equipment_id, plant, section = BUS[bu]
    return ["2026-11-25", "06:00", bu, plant, section, equipment_id, value]


def _enable_live_sources(root: Path) -> None:
    configs = pipelines.default_configurations()
    for number, bu in enumerate(("refinery", "cement", "fertilizer"), start=1):
        item = next(row for row in configs if row["id"] == f"live_excel_{number}")
        item.update({
            "enabled": True,
            "interval_seconds": 1,
            "source": "pipeline_sources",
            "target_mode": "fixed",
            "target_bu": bu,
        })
        _write_workbook(root / "pipeline_sources" / f"live_excel_{number}.xlsx", [_row(bu, number * 100)])
    pipelines.save_configurations(configs)


def test_permission_matrix_is_hierarchical_and_super_admin_cannot_miss_an_action():
    expected = {
        "Viewer": {"view"},
        "Patroller": {"view", "manual_input"},
        "Operator": {"view", "manual_input", "bulk_input", "events", "lessons", "risk", "export", "home_drilldown"},
        "Manager": {"view", "manual_input", "bulk_input", "events", "lessons", "risk", "export", "home_drilldown", "configure"},
        "BU Admin": {"view", "manual_input", "bulk_input", "events", "lessons", "risk", "export", "home_drilldown", "configure"},
        "Super Admin": set(auth.ACTION_CAPABILITIES),
    }
    for role, allowed_capabilities in expected.items():
        user = auth.User(role.lower(), role, role, ("cement",))
        for capability in auth.ACTION_CAPABILITIES:
            assert auth.allowed(user, capability) is (capability in allowed_capabilities), (role, capability)
    super_admin = auth.User("root", "Root", "super_admin", ())
    assert all(auth.allowed(super_admin, capability) for capability in auth.ACTION_CAPABILITIES)
    assert auth.can_access_bu(super_admin, "any-future-business-unit")
    operator = auth.User("legacy", "Legacy Operator", "Operator", ("cement", "refinery"))
    assert operator.business_units == ("cement",)
    assert auth.can_access_bu(operator, "cement") and not auth.can_access_bu(operator, "refinery")


def test_secret_role_is_canonical_and_is_not_replaced_by_a_csv_default():
    secret_user = auth.get_secret_user("root", {
        "root": {"name": "Root", "role": "Super-Administrator", "business_units": "", "active": True}
    })
    assert secret_user is not None
    assert secret_user.role == "Super Admin"
    assert auth.allowed(secret_user, "manual_input")
    assert auth.can_access_bu(secret_user, "fertilizer")


def test_legacy_per_bu_pipeline_settings_migrate_once_and_prefer_intended_target(monkeypatch, tmp_path):
    root = _three_bu_root(monkeypatch, tmp_path)
    wrong = [{"id": "live_excel_1", "enabled": True, "source": "wrong.xlsx", "interval_seconds": 9, "notes": "saved under cement"}]
    right = [{"id": "live_excel_1", "enabled": False, "source": "right.xlsx", "interval_seconds": 17, "notes": "saved under refinery"}]
    storage.save_json(root / "business_units" / "cement" / "pipeline_configurations.json", wrong)
    storage.save_json(root / "business_units" / "refinery" / "pipeline_configurations.json", right)

    migrated = {row["id"]: row for row in pipelines.load_configurations()}
    assert migrated["live_excel_1"]["source"] == "right.xlsx"
    assert migrated["live_excel_1"]["interval_seconds"] == 17
    assert migrated["live_excel_1"]["target_bu"] == "refinery"
    assert (root / "shared" / "pipeline_configurations.json").is_file()
    assert (root / "business_units" / "cement" / "pipeline_configurations.json").is_file()


def test_scheduler_without_a_user_session_imports_three_files_to_their_target_bus(monkeypatch, tmp_path):
    root = _three_bu_root(monkeypatch, tmp_path)
    _enable_live_sources(root)
    monkeypatch.setattr(pipeline_scheduler, "due", lambda *_: True)

    pipeline_scheduler.cycle()  # stability check
    pipeline_scheduler.cycle()  # import

    for number, bu in enumerate(("refinery", "cement", "fertilizer"), start=1):
        saved = pd.read_csv(root / "business_units" / bu / "inputs" / "dcs.csv")
        assert len(saved) == 1
        assert saved.loc[0, "Business unit"] == bu
        assert saved.loc[0, "DP1"] == number * 100
        runs = pd.read_csv(root / "business_units" / bu / "pipeline_runs.csv")
        success = runs[runs["status"] == "success"].iloc[-1]
        assert success["pipeline_name"] == f"Live Excel files {number}"
        assert success["target_bu"] == bu


def test_multi_bu_workbook_routes_each_row_and_fixed_pipeline_rejects_only_disallowed_rows(monkeypatch, tmp_path):
    root = _three_bu_root(monkeypatch, tmp_path)
    source = root / "pipeline_sources" / "multi.xlsx"
    _write_workbook(source, [_row("refinery", 101), _row("cement", 202), _row("fertilizer", 303)])
    configs = pipelines.default_configurations()
    live = next(row for row in configs if row["id"] == "live_excel_1")
    live.update({
        "enabled": True,
        "source": "pipeline_sources/multi.xlsx",
        "target_mode": "row",
        "target_bu": "",
        "allowed_business_units": list(BUS),
    })
    pipelines.save_configurations(configs)
    assert pipelines.sync_live_excel("live_excel_1") == (0, 0)
    assert pipelines.sync_live_excel("live_excel_1") == (3, 0)
    for bu, value in (("refinery", 101), ("cement", 202), ("fertilizer", 303)):
        saved = pd.read_csv(root / "business_units" / bu / "inputs" / "dcs.csv")
        assert saved.loc[0, "DP1"] == value

    # A fixed target imports its valid row and rejects the other BU row without
    # using any signed-in/active BU context.
    fixed_source = root / "pipeline_sources" / "fixed.xlsx"
    _write_workbook(fixed_source, [_row("refinery", 111), _row("fertilizer", 999)])
    configs = pipelines.load_configurations()
    live = next(row for row in configs if row["id"] == "live_excel_1")
    live.update({"source": "pipeline_sources/fixed.xlsx", "target_mode": "fixed", "target_bu": "refinery", "allowed_business_units": []})
    pipelines.save_configurations(configs)
    assert pipelines.sync_live_excel("live_excel_1") == (0, 0)
    assert pipelines.sync_live_excel("live_excel_1") == (1, 0)
    state = pipelines.load_state()["live_excel_1"]
    assert state["rejected"] == 1
    fertilizer = pd.read_csv(root / "business_units" / "fertilizer" / "inputs" / "dcs.csv")
    assert 999 not in set(fertilizer["DP1"])


def test_pipeline_visibility_filters_health_without_changing_global_behavior(monkeypatch, tmp_path):
    root = _three_bu_root(monkeypatch, tmp_path)
    _enable_live_sources(root)
    before = json.loads((root / "shared" / "pipeline_configurations.json").read_text(encoding="utf-8"))

    cement_view = pipelines.status_frame(["cement"])
    assert set(cement_view["Target BU"]) == {"cement"}
    assert "Live Excel files 2" in set(cement_view["Pipeline"])
    assert "Live Excel files 1" not in set(cement_view["Pipeline"])
    assert "Live Excel files 3" not in set(cement_view["Pipeline"])

    # Viewing another active BU changes only the filtered result; the global
    # scheduler configuration and targets remain byte-for-byte equivalent.
    refinery_view = pipelines.status_frame(["refinery"])
    assert set(refinery_view["Target BU"]) == {"refinery"}
    after = json.loads((root / "shared" / "pipeline_configurations.json").read_text(encoding="utf-8"))
    assert after == before


def test_user_interface_contains_no_developer_notes_or_bu_bound_pipeline_calls():
    app_source = (ROOT / "app.py").read_text(encoding="utf-8")
    scheduler_source = (ROOT / "scripts" / "pipeline_scheduler.py").read_text(encoding="utf-8")
    forbidden = [
        "A 100 ms sync interval is not recommended",
        "CSV lock contention",
        "without changing code",
        "OPERA_DATA_DIR",
        "Streamlit Secrets",
        "live backend database",
        "Fingerprint:",
    ]
    assert all(text not in app_source for text in forbidden)
    assert "pipelines.sync_live_excel(str(bu)" not in scheduler_source
    assert "for bu in" not in scheduler_source
    assert "pipelines.load_configurations()" in scheduler_source
