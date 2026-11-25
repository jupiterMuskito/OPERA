from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from openpyxl import Workbook

from opera import auth, pipelines, storage

ROOT = Path(__file__).resolve().parents[1]


def _data_root(monkeypatch, tmp_path: Path) -> Path:
    root = tmp_path / "data"
    bu = root / "business_units" / "refinery"
    (bu / "inputs").mkdir(parents=True)
    pd.DataFrame([
        {"field_id": "DP1", "field_name": "Flow", "source": "DCS", "active": "true", "min_value": "0", "max_value": "1000", "jump_limit": ""},
        {"field_id": "DP2", "field_name": "Temperature", "source": "DCS", "active": "true", "min_value": "0", "max_value": "1000", "jump_limit": ""},
    ]).to_csv(bu / "fields.csv", index=False)
    pd.DataFrame([{"equipment_id": "REF-1", "plant": "Refinery", "unit_section": "CDU"}]).to_csv(bu / "equipment.csv", index=False)
    pd.DataFrame(columns=storage.BASE_COLUMNS + ["DP1", "DP2"]).to_csv(bu / "inputs" / "dcs.csv", index=False)
    monkeypatch.setattr(storage, "DATA_ROOT", root)
    storage.clear_data_caches()
    return root


def _workbook(path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Live Data"
    ws.append(["Date", "Time", "Business unit", "Plant", "Unit/Section", "Equipment", "DP1", "DP2"])
    ws.append(["2026-11-25", "05:00", "refinery", "Refinery", "CDU", "REF-1", 400, 180])
    wb.save(path)


def test_default_catalog_has_all_requested_pipelines_and_realistic_intervals():
    configs = pipelines.default_configurations()
    assert len(configs) == 11
    assert configs[0]["name"] == "SAP"
    assert configs[-1]["name"] == "Live Excel files 3"
    assert min(row["interval_seconds"] for row in configs) >= 1
    assert {row["kind"] for row in configs} >= {"api", "script", "live_excel"}
    assert all(str(row["source"]).startswith("~/opera_inbox/live_excel") for row in configs if row["kind"] == "live_excel")


def test_authenticated_pages_have_no_duplicate_page_heading_below_breadcrumb():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    forbidden = [
        "### OPERA-X Home", "### Modules", "### Plant Overview", "### Equipment Overview",
        "### Operations Dashboard", "### Operational Data Pipeline", "### Operating Parameters",
        "### Process Optimization", "### Event Log", "### Lesson Bank", "### Job Risk Assessment",
        "### Admin / Super Admin",
    ]
    assert all(heading not in source for heading in forbidden)


def test_unconfigured_connectors_never_claim_healthy():
    config = pipelines.default_configurations()[0]
    health, _ = pipelines.pipeline_health(config, {}, datetime(2026, 11, 25, tzinfo=timezone.utc))
    assert health == "Not connected"
    config.update({"enabled": True, "source": "https://example.invalid"})
    health, _ = pipelines.pipeline_health(config, {}, datetime(2026, 11, 25, tzinfo=timezone.utc))
    assert health == "Simulated / connector pending"


def test_live_excel_sync_is_validated_and_idempotent(monkeypatch, tmp_path):
    root = _data_root(monkeypatch, tmp_path)
    source = root / "pipeline_sources" / "live_excel_1.xlsx"
    source.parent.mkdir(parents=True)
    _workbook(source)
    configs = pipelines.default_configurations()
    target = next(row for row in configs if row["id"] == "live_excel_1")
    target["enabled"] = True
    target["source"] = "pipeline_sources/live_excel_1.xlsx"
    pipelines.save_configurations("refinery", configs)

    # First sighting is deliberately deferred so a half-copied workbook is
    # never parsed.  The unchanged next cycle imports it.
    assert pipelines.sync_live_excel("refinery") == (0, 0)
    assert pipelines.sync_live_excel("refinery") == (1, 0)
    assert pipelines.sync_live_excel("refinery") == (0, 0)
    saved = pd.read_csv(root / "business_units" / "refinery" / "inputs" / "dcs.csv")
    assert len(saved) == 1 and saved.loc[0, "DP1"] == 400
    assert pipelines.status_frame("refinery").set_index("Pipeline").loc["Live Excel files 1", "Health"] == "Healthy"
    runs = pd.read_csv(root / "business_units" / "refinery" / "pipeline_runs.csv")
    assert set(runs["status"]) == {"waiting", "success"}

    # Editing the same date/time/equipment key updates rather than duplicates.
    wb = pd.read_excel(source, sheet_name="Live Data")
    wb.loc[0, "DP1"] = 410
    with pd.ExcelWriter(source, engine="openpyxl") as writer:
        wb.to_excel(writer, sheet_name="Live Data", index=False)
    assert pipelines.sync_live_excel("refinery") == (0, 0)
    assert pipelines.sync_live_excel("refinery") == (1, 0)
    saved = pd.read_csv(root / "business_units" / "refinery" / "inputs" / "dcs.csv")
    assert len(saved) == 1 and saved.loc[0, "DP1"] == 410


def test_manager_operator_and_patroller_bu_scoping_and_permissions():
    manager = auth.User("m", "Manager", "Manager", ("cement",))
    operator = auth.User("o", "Operator", "Operator", ("refinery",))
    patroller = auth.User("p", "Patroller", "Patroller", ("cement",))
    assert auth.allowed(manager, "configure") and not auth.can_access_bu(manager, "refinery")
    assert auth.allowed(operator, "bulk_input") and not auth.allowed(operator, "configure")
    assert auth.allowed(patroller, "manual_input") and not auth.allowed(patroller, "bulk_input")
    assert auth.allowed(patroller, "view")
