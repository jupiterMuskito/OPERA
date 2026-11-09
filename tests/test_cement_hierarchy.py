from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]


def test_cement_equipment_is_sourced_from_register_cloned_to_three_plants_and_keeps_spares():
    workbook = load_workbook(ROOT / "registers" / "OKPELLA_Master_Workbook_v8.xlsx", read_only=True, data_only=True)
    sheet = workbook["Equipment"]
    register_ids = {str(row[0]) for row in sheet.iter_rows(min_row=2, values_only=True) if row[0]}
    workbook.close()
    equipment = pd.read_csv(ROOT / "data" / "business_units" / "cement" / "equipment.csv", dtype=str)
    named = equipment[equipment["placeholder"] == "false"]
    spares = equipment[equipment["placeholder"] == "true"]
    okpella = named[named["plant"] == "Okpella Cement Plant"]
    obajana = named[named["plant"] == "Obajana Cement Plant"]
    ibese = named[named["plant"] == "Ibese Cement Plant"]
    assert set(okpella["equipment_id"]) == register_ids
    assert set(obajana["equipment_id"]) == {f"OBJ-{item}" for item in register_ids}
    assert set(ibese["equipment_id"]) == {f"IBE-{item}" for item in register_ids}
    assert len(okpella) == len(obajana) == len(ibese) == 67
    assert len(named) == 201 and len(spares) == 500
    assert named["unit_section"].str.len().gt(0).all()
    assert not named["equipment_id"].str.contains("SPARE").any()
