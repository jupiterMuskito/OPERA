from __future__ import annotations

import ast
import re
from typing import Any

import numpy as np
import pandas as pd


class FormulaError(ValueError):
    pass


_PLACEHOLDER = re.compile(r"\[([^\[\]]+)\]")
_BINARY = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b,
           ast.Div: lambda a, b: a / b, ast.FloorDiv: lambda a, b: a // b, ast.Mod: lambda a, b: a % b, ast.Pow: lambda a, b: a ** b}
_COMPARE = {ast.Gt: lambda a, b: a > b, ast.GtE: lambda a, b: a >= b, ast.Lt: lambda a, b: a < b,
            ast.LtE: lambda a, b: a <= b, ast.Eq: lambda a, b: a == b, ast.NotEq: lambda a, b: a != b}


def _min(*args):
    return np.minimum.reduce(args)


def _max(*args):
    return np.maximum.reduce(args)


_FUNCTIONS = {"ABS": np.abs, "MIN": _min, "MAX": _max, "MOD": np.mod, "IF": np.where, "ROUND": np.round}


def _eval(node: ast.AST, names: dict[str, Any]) -> Any:
    if isinstance(node, ast.Expression):
        return _eval(node.body, names)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float, bool)):
        return node.value
    if isinstance(node, ast.Name) and node.id in names:
        return names[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        return _BINARY[type(node.op)](_eval(node.left, names), _eval(node.right, names))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub, ast.Not)):
        value = _eval(node.operand, names)
        return -value if isinstance(node.op, ast.USub) else (~value if isinstance(node.op, ast.Not) and hasattr(value, "index") else (not value if isinstance(node.op, ast.Not) else value))
    if isinstance(node, ast.Compare) and len(node.ops) == len(node.comparators) == 1 and type(node.ops[0]) in _COMPARE:
        return _COMPARE[type(node.ops[0])](_eval(node.left, names), _eval(node.comparators[0], names))
    if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
        values = [_eval(v, names) for v in node.values]
        result = values[0]
        for value in values[1:]:
            result = result & value if isinstance(node.op, ast.And) else result | value
        return result
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
        fn = _FUNCTIONS.get(node.func.id.upper())
        if fn:
            return fn(*[_eval(arg, names) for arg in node.args])
    raise FormulaError("Expression contains an unsupported operation or function.")


def evaluate_formula(frame: pd.DataFrame, expression: str, constants: dict[str, float] | None = None) -> pd.Series:
    if not expression.strip():
        raise FormulaError("Enter a formula.")
    names: dict[str, Any] = {str(k): float(v) for k, v in (constants or {}).items()}
    safe = expression
    for i, column in enumerate(dict.fromkeys(_PLACEHOLDER.findall(expression))):
        if column not in frame.columns:
            raise FormulaError(f"Unknown field: {column}")
        token = f"field_{i}"
        names[token] = pd.to_numeric(frame[column], errors="coerce")
        safe = safe.replace(f"[{column}]", token)
    try:
        result = _eval(ast.parse(safe, mode="eval"), names)
    except FormulaError:
        raise
    except Exception as exc:
        raise FormulaError(f"Formula could not be evaluated: {exc}") from exc
    if np.isscalar(result):
        result = pd.Series([result] * len(frame), index=frame.index)
    return pd.Series(result, index=frame.index).replace([np.inf, -np.inf], np.nan)


def apply_ordered(frame: pd.DataFrame, definitions: list[dict[str, Any]], constants: dict[str, float] | None = None) -> tuple[pd.DataFrame, list[str]]:
    result, errors = frame.copy(), []
    ordered = sorted(definitions, key=lambda d: int(d.get("evaluation_order", 0)))
    for item in ordered:
        if str(item.get("status", "active")).lower() == "disabled":
            continue
        name, expression = str(item.get("field_id") or item.get("name") or "").strip(), str(item.get("formula") or item.get("expression") or "").strip()
        if not name or not expression:
            continue
        try:
            result[name] = evaluate_formula(result, expression, constants)
        except FormulaError as exc:
            errors.append(f"{name}: {exc}")
    return result, errors


def aggregate(series: pd.Series, method: str) -> float | None:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return None
    ops = {"Average": values.mean, "Maximum": values.max, "Minimum": values.min, "Sum": values.sum, "Latest": lambda: values.iloc[-1]}
    return float(ops.get(method, values.mean)())


def target_status(value: float | None, target: float | None, direction: str) -> tuple[str, float | None]:
    if value is None or target is None or pd.isna(value) or pd.isna(target):
        return "No target", None
    variance = value - target
    good = value >= target if str(direction).lower() in {"high", "above target is good", "normal"} else value <= target
    return ("On Target" if good else "Off Target"), variance
