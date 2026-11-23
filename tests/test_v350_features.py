from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from streamlit.testing.v1 import AppTest

from opera import dashboard, exports, storage


ROOT = Path(__file__).resolve().parents[1]


def test_blue_page_hero_was_deleted_and_only_brand_navigation_structure_remains():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "def hero(" not in source
    assert "hero(" not in source
    assert "opera-hero" not in source
    assert 'with st.container(key="brand_ribbon")' in source
    assert 'with st.container(key="primary_navigation")' in source
    assert source.count("background:linear-gradient") == 2  # fixed brand ribbon and sign-in panel only


def test_complete_mapping_includes_all_sources_placeholders_and_calculated_fields():
    mappings = dashboard.field_mapping_table("cement")
    assert len(mappings) == 10_012
    assert set(mappings["Source"]) == {"Digital Data", "Raw Field Data", "QAQC", "Others", "Calculated"}
    assert set(mappings["Field Type"]) == {"Input", "Placeholder", "Calculated"}
    assert (mappings["Field Type"] == "Placeholder").sum() == 9_940
    assert (mappings["Field Type"] == "Calculated").sum() == 12
    assert mappings["_equipment_ids"].map(bool).all()
    assert mappings["_template_ids"].map(bool).all()

    by_equipment, by_template = dashboard.mapping_reverse_views("cement", mappings)
    active_equipment = storage.equipment("cement")
    active_equipment = active_equipment[active_equipment["active"].str.lower() == "true"]
    assert set(by_equipment["Equipment ID"]).issubset(set(active_equipment["equipment_id"]))
    assert set(mappings[mappings["Field Type"] == "Placeholder"]["Equipment IDs"].str.split("; ").explode()).issubset(
        set(active_equipment[active_equipment["placeholder"].str.lower() == "true"]["equipment_id"])
    )
    assert set(by_template["Template ID"]) == set(dashboard.MAPPING_TEMPLATES)


def test_mapping_override_reset_and_excel_review_workbook(tmp_path, monkeypatch):
    data_root = tmp_path / "data"
    bu = data_root / "business_units" / "demo"
    bu.mkdir(parents=True)
    monkeypatch.setattr(storage, "DATA_ROOT", data_root)
    storage.atomic_write_csv(
        bu / "equipment.csv",
        pd.DataFrame(
            [
                {"equipment_id": "EQ1", "equipment_name": "Pump One", "plant": "Plant A", "unit_section": "Unit A", "equipment_type": "Pump", "active": "true", "placeholder": "false"},
                {"equipment_id": "EQ2", "equipment_name": "Pump Two", "plant": "Plant A", "unit_section": "Unit B", "equipment_type": "Pump", "active": "true", "placeholder": "false"},
            ]
        ),
    )
    storage.atomic_write_csv(
        bu / "fields.csv",
        pd.DataFrame(
            [
                {"field_id": "DP1", "field_name": "Pump discharge pressure", "source": "DCS", "active": "true"},
                {"field_id": "TA1", "field_name": "TA Placeholder 1", "source": "TA", "active": "false"},
            ]
        ),
    )
    storage.atomic_write_csv(
        bu / "calculated_fields.csv",
        pd.DataFrame([{"field_id": "CF1", "field_name": "Calculated efficiency", "status": "active"}]),
    )

    dashboard.save_field_mapping("demo", "DP1", ["EQ2"], ["reliability"])
    table = dashboard.field_mapping_table("demo")
    row = table[table["Field ID"] == "DP1"].iloc[0]
    assert row["Mapping Type"] == "Admin Override"
    assert row["_equipment_ids"] == ("EQ2",)
    assert row["_template_ids"] == ("reliability",)

    workbook = load_workbook(BytesIO(exports.excel_bytes(dashboard.mapping_export_sheets("demo", table))), read_only=True)
    assert workbook.sheetnames == ["Field Mappings", "By Equipment", "By Template", "Guide"]
    workbook.close()

    assert dashboard.reset_field_mapping("demo", "DP1")
    reset = dashboard.field_mapping_table("demo")
    assert reset.loc[reset["Field ID"] == "DP1", "Mapping Type"].iloc[0] == "Computed Default"


def test_every_authenticated_page_renders_without_exception():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    at.text_input[0].set_value("buadmin")
    at.text_input[1].set_value("ChangeMe!2026")
    at.button[0].click().run(timeout=60)
    at.selectbox[0].set_value("Cement")
    at.button[0].click().run(timeout=60)

    pages = [
        "OPERA-X Home",
        "Plant Overview",
        "Equipment Overview",
        "Operations Dashboard",
        "Operational Data",
        "Event Log",
        "Operating Parameters",
        "Process Optimization",
        "Job Risk Assessment",
        "Lesson Bank",
        "Admin / Super Admin",
    ]
    for page in pages:
        at.radio[0].set_value(page).run(timeout=120)
        assert not at.exception, f"{page} raised: {at.exception}"
