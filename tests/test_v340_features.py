from __future__ import annotations

from pathlib import Path

from opera import dashboard, storage


ROOT = Path(__file__).resolve().parents[1]


def test_opera_x_branding_and_flat_navigation_structure():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert 'page_title="OPERA-X"' in source
    assert '"OPERA-X Home"' in source
    assert "context-ribbon" not in source
    assert 'st.tabs(["Manual Entry", "Bulk Upload", "Derived Data", "Analyze Data"])' in source
    assert "DCS Pipeline" not in source
    assert 'with st.container(key="brand_ribbon")' in source
    assert 'with st.container(key="primary_navigation")' in source


def test_every_packaged_placeholder_has_equipment_and_template_mapping():
    for bu in ("cement", "refinery", "fertilizer", "nascon"):
        registry = storage.registry(bu)
        placeholders = registry[registry["active"].str.lower() != "true"]
        assert len(placeholders) == 9_940
        assert placeholders["field_id"].notna().all()
        assert set(placeholders["source"]) == {"DCS", "Lab", "Field", "TA", "TB", "TC", "TD", "TE", "TF", "TG"}
        mappings = dashboard.field_mapping_table(bu).set_index("Field ID")
        samples = placeholders.loc[
            placeholders.groupby("source", sort=False).head(1).index.union(
                placeholders.groupby("source", sort=False).tail(1).index
            )
        ]
        for row in samples.itertuples():
            mapping = mappings.loc[row.field_id]
            assert mapping["_equipment_ids"], f"{bu}/{row.field_id} has no equipment mapping"
            assert all("SPARE" in equipment_id for equipment_id in mapping["_equipment_ids"])
            assert mapping["_template_ids"], f"{bu}/{row.field_id} has no template mapping"
            assert set(mapping["_template_ids"]).issubset(dashboard.MAPPING_TEMPLATES)
            assert mapping["Confidence"] == "Review"


def test_mapping_filter_uses_equipment_and_template_context(monkeypatch):
    registry = storage.registry("refinery").head(3)
    equipment = storage.equipment("refinery")
    first_equipment = str(equipment[equipment["placeholder"].str.lower() != "true"].iloc[0]["equipment_id"])
    field_id = str(registry.iloc[0]["field_id"])
    monkeypatch.setattr(dashboard.storage, "equipment", lambda _bu: equipment)
    monkeypatch.setattr(
        dashboard,
        "load_field_mapping_overrides",
        lambda _bu: {field_id: {"equipment_ids": [first_equipment], "template_ids": ["plant-performance"]}},
    )
    selected = dashboard.mapped_field_ids(
        "refinery",
        registry,
        equipment_id=first_equipment,
        template_id="plant-performance",
    )
    assert field_id in selected


def test_excel_exports_carry_opera_x_metadata():
    from io import BytesIO

    import pandas as pd
    from openpyxl import load_workbook

    from opera.exports import excel_bytes

    workbook = load_workbook(BytesIO(excel_bytes(pd.DataFrame({"Value": [1]}))))
    assert workbook.properties.creator == "OPERA-X"
    assert workbook.properties.lastModifiedBy == "OPERA-X"