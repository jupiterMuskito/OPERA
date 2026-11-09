from pathlib import Path

import pandas as pd

from opera import dashboard

ROOT = Path(__file__).resolve().parents[1]


def test_nascon_name_and_storage_are_global():
    business_units = pd.read_csv(ROOT / "data" / "shared" / "business_units.csv", dtype=str)
    assert "nascon" in set(business_units["id"])
    assert "NASCON" in set(business_units["name"])
    assert "nasco" not in set(business_units["id"])
    assert (ROOT / "data" / "business_units" / "nascon").is_dir()
    assert not (ROOT / "data" / "business_units" / "nasco").exists()


def test_every_dashboard_template_controls_chart_and_table_fields():
    templates = dashboard.default_templates()
    assert set(templates) == {"Plant Overview", "Equipment Overview", "Operations Dashboard"}
    for module_templates in templates.values():
        assert module_templates
        for template in module_templates:
            assert template["name"]
            assert template["chart_type"] in dashboard.CHART_TYPES
            assert isinstance(template["chart_fields"], list)
            assert isinstance(template["table_fields"], list)


def test_equipment_validation_lists_cover_all_three_cement_plants():
    options = dashboard.hierarchy_options("cement")
    assert {"Okpella Cement Plant", "Obajana Cement Plant", "Ibese Cement Plant"}.issubset(options["plants"])
    assert options["units"]
    assert options["equipment_types"]


def test_event_and_lesson_schemas_support_optional_link_and_field_update():
    events = pd.read_csv(ROOT / "data" / "business_units" / "cement" / "events.csv", dtype=str)
    lessons = pd.read_csv(ROOT / "data" / "business_units" / "cement" / "lessons.csv", dtype=str)
    assert {"field_update_sent", "field_update_ids"}.issubset(events.columns)
    assert "event_id" in lessons.columns
