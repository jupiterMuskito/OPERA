from __future__ import annotations

from pathlib import Path

import pandas as pd

from opera import dashboard, storage

ROOT = Path(__file__).resolve().parents[1]


def test_instrument_check_replaces_field_vs_dcs_in_user_interface():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "Instrument Check" in source
    assert "Field vs DCS" not in source
    assert 'active_registry(bu, "Field")' in source
    assert 'active_registry(bu, "DCS")' in source


def test_hourly_trend_granularities_are_available():
    assert dashboard.TREND_RULES["1 Hour"] == "1h"
    assert dashboard.TREND_RULES["6 Hours"] == "6h"
    assert dashboard.TREND_RULES["12 Hours"] == "12h"
    assert {"Daily", "Weekly", "Monthly", "Yearly"}.issubset(dashboard.TREND_RULES)


def test_intelligent_equipment_mapping_and_admin_override():
    registry = pd.DataFrame(
        [
            {"field_id": "DP1", "source": "DCS", "field_name": "Discharge Pressure", "uom": "bar", "active": "true"},
            {"field_id": "F1", "source": "Field", "field_name": "Pump Vibration", "uom": "mm/s", "active": "true"},
            {"field_id": "L1", "source": "Lab", "field_name": "Product Purity", "uom": "%", "active": "true"},
        ]
    )
    equipment = {"equipment_id": "P-01", "equipment_name": "Charge Pump", "equipment_type": "Pump"}
    mapped = dashboard.intelligent_equipment_fields(equipment, registry, {"DP1", "F1", "L1"})
    assert mapped[:2] == ["DP1", "F1"]

    template = {
        "chart_fields": ["DP1"],
        "table_fields": ["DP1"],
        "equipment_fields": {"P-01": {"chart_fields": ["F1"], "table_fields": ["L1"]}},
    }
    assert dashboard.equipment_overview_fields(template, equipment, registry, {"DP1", "F1", "L1"}) == (["F1"], ["L1"])


def test_operations_templates_keep_admin_configurable_kpi_fields():
    for template in dashboard.default_templates()["Operations Dashboard"]:
        assert template["kpi_fields"]
        assert isinstance(template["chart_fields"], list)
        assert isinstance(template["table_fields"], list)


def test_one_year_samples_cover_every_active_bu_field_and_all_cement_plants():
    expected_plants = {
        "Okpella Cement Plant",
        "Obajana Cement Plant",
        "Ibese Cement Plant",
    }
    for bu in ("cement", "refinery", "fertilizer", "nascon"):
        registry = storage.registry(bu)
        for source in ("DCS", "Field", "Lab"):
            active_ids = registry.loc[
                (registry["source"] == source) & (registry["active"].str.lower() == "true"), "field_id"
            ].tolist()
            path = storage.source_path(bu, source)
            frame = pd.read_csv(path, usecols=["Date", "Plant", "Equipment", *active_ids])
            dates = pd.to_datetime(frame["Date"])
            assert (dates.max() - dates.min()).days == 364
            assert len(dates.dt.date.unique()) == 365
            assert frame[active_ids].notna().all().all()
            if bu == "cement":
                assert set(frame["Plant"].unique()) == expected_plants
                assert frame["Equipment"].nunique() == 201
