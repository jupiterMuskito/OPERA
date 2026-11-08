import numpy as np
import pandas as pd
import pytest

from opera.formula import FormulaError, apply_ordered, evaluate_formula, target_status


def test_cpp_functions_and_ordered_evaluation():
    frame = pd.DataFrame({"DP1": [2.0, 5.0], "DP2": [3.0, 1.0]})
    defs = [
        {"field_id": "CF1", "formula": "MAX([DP1],[DP2])", "evaluation_order": 1, "status": "active"},
        {"field_id": "CF2", "formula": "IF([CF1] > 3, ABS([DP1]-[DP2]), MOD([DP2],2))", "evaluation_order": 2, "status": "on hold"},
    ]
    out, errors = apply_ordered(frame, defs)
    assert not errors
    assert out["CF1"].tolist() == [3.0, 5.0]
    assert out["CF2"].tolist() == [1.0, 4.0]


def test_formula_blocks_unsafe_code():
    with pytest.raises(FormulaError):
        evaluate_formula(pd.DataFrame({"DP1": [1]}), "__import__('os').system('id') + [DP1]")


def test_target_direction():
    assert target_status(11, 10, "High")[0] == "On Target"
    assert target_status(11, 10, "Low")[0] == "Off Target"
