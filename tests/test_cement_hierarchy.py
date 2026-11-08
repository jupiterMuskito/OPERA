from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]


def test_cement_equipment_is_sourced_from_register_and_keeps_spares():
    workbook = load_workbook(ROOT / "registers" / "OKPELLA_Master_Workbook_v8.xlsx", read_only=True, data_only=True)
    sheet = workbook["Equipment"]
    register_ids = {str(row[0]) for row in sheet.iter_rows(min_row=2, values_only=True) if row[0]}
    workbook.close()
    equipment = pd.read_csv(ROOT / "data" / "business_units" / "cement" / "equipment.csv", dtype=str)
    named = equipment[equipment["placeholder"] == "false"]
    spares = equipment[equipment["placeholder"] == "true"]
    assert set(named["equipment_id"]) == register_ids
    assert len(named) == 67 and len(spares) == 500
    assert named["unit_section"].str.len().gt(0).all()
