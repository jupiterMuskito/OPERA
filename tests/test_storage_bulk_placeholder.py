from pathlib import Path

import pandas as pd

from opera import exports, formula, storage


def setup_demo(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_ROOT", tmp_path)
    bu = tmp_path / "business_units" / "demo"
    (bu / "inputs").mkdir(parents=True)
    storage.atomic_write_csv(bu / "equipment.csv", pd.DataFrame([{"equipment_id":"EQ1","equipment_name":"Test Equipment","plant":"Plant","unit_section":"Unit","equipment_type":"Test","active":"true","placeholder":"false"}]))
    storage.atomic_write_csv(bu / "fields.csv", pd.DataFrame([{"field_id":"TA1","source":"TA","field_name":"Future test field","uom":"bar","min_value":"0","max_value":"10","data_format":"0.00","target":"5","target_direction":"High","jump_limit":"4","active":"true"}]))
    return bu


def test_atomic_append_and_formula_injection(tmp_path, monkeypatch):
    setup_demo(tmp_path, monkeypatch)
    p = tmp_path / "business_units" / "demo" / "events.csv"
    storage.append_rows(p, [{"title":"=HYPERLINK('x')","value":1}], ["title","value"])
    frame = storage.read_csv(p)
    assert frame.iloc[0]["title"].startswith("'")
    assert frame.iloc[0]["value"] == "1"


def test_ta_to_tg_placeholder_entry_calculation_and_excel_roundtrip(tmp_path, monkeypatch):
    setup_demo(tmp_path, monkeypatch)
    row = pd.DataFrame([{"Date":"2026-11-08","Time":"06:00","Business unit":"demo","Plant":"Plant","Unit/Section":"Unit","Equipment":"EQ1","TA1":"6.5"}])
    clean, issues, flags = storage.validate_rows("demo", "TA", row)
    assert issues.empty and flags.empty
    count, flag_count = storage.save_validated_input("demo", "TA", clean, "tester")
    assert (count, flag_count) == (1, 0)
    stored = storage.read_csv(storage.source_path("demo", "TA"))
    stored["TA1"] = pd.to_numeric(stored["TA1"])
    result = formula.evaluate_formula(stored, "[TA1] * 2")
    assert result.iloc[0] == 13
    payload = exports.excel_bytes(pd.DataFrame({"TA1":stored["TA1"],"CF1":result}))
    out = tmp_path / "roundtrip.xlsx"; out.write_bytes(payload)
    loaded = pd.read_excel(out)
    assert loaded.iloc[0].to_dict() == {"TA1":6.5,"CF1":13.0}
