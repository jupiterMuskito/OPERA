from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

SOURCE_GROUPS: dict[str, tuple[str, ...]] = {
    "DCS": ("DCS",),
    "Field": ("Field",),
    "QAQC": ("Lab",),
    "Others": ("TA", "TB", "TC", "TD", "TE", "TF", "TG"),
}


def grouped_registry(registry: pd.DataFrame, available_ids: set[str] | None = None) -> dict[str, pd.DataFrame]:
    """Return active fields in the four user-facing selector groups."""
    if registry.empty:
        return {name: registry.copy() for name in SOURCE_GROUPS}
    active = registry[registry["active"].astype(str).str.lower() == "true"].copy()
    if available_ids is not None:
        active = active[active["field_id"].astype(str).isin(available_ids)]
    return {
        name: active[active["source"].isin(sources)].sort_values(["source", "field_id"])
        for name, sources in SOURCE_GROUPS.items()
    }


def prepare_optimization_frame(data: pd.DataFrame, decision_ids: list[str], outcome_id: str) -> pd.DataFrame:
    """Align selected long-form fields at matching timestamps for model fitting."""
    wanted = list(dict.fromkeys(decision_ids + [outcome_id]))
    if data.empty or not decision_ids or not outcome_id:
        return pd.DataFrame(columns=wanted)
    view = data[data["field_id"].astype(str).isin(wanted)].copy()
    if view.empty:
        return pd.DataFrame(columns=wanted)
    view["value"] = pd.to_numeric(view["value"], errors="coerce")
    aligned = view.pivot_table(index="Timestamp", columns="field_id", values="value", aggfunc="mean")
    return aligned.reindex(columns=wanted).dropna()


def optimize_linear_response(
    aligned: pd.DataFrame,
    decision_ids: list[str],
    outcome_id: str,
    objective: str,
    target: float | None = None,
    bounds: dict[str, tuple[float, float]] | None = None,
) -> dict[str, Any]:
    """Fit a linear response model and solve a bounded deterministic recommendation.

    Maximise/minimise objectives use the exact solution for a linear model over box
    constraints. Target matching uses projected gradient descent on squared error.
    """
    required = list(dict.fromkeys(decision_ids + [outcome_id]))
    frame = aligned.reindex(columns=required).apply(pd.to_numeric, errors="coerce").dropna()
    if len(frame) < max(5, len(decision_ids) + 2):
        raise ValueError(f"At least {max(5, len(decision_ids) + 2)} aligned readings are required.")
    x = frame[decision_ids].to_numpy(dtype=float)
    y = frame[outcome_id].to_numpy(dtype=float)
    design = np.column_stack([np.ones(len(x)), x])
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    intercept, slopes = float(coefficients[0]), coefficients[1:].astype(float)
    predicted = design @ coefficients
    residual = float(np.sum((y - predicted) ** 2))
    total = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1.0 - residual / total if total > 0 else 1.0

    chosen_bounds: dict[str, tuple[float, float]] = {}
    for field_id in decision_ids:
        observed = frame[field_id]
        low, high = (float(observed.min()), float(observed.max()))
        if bounds and field_id in bounds:
            low, high = map(float, bounds[field_id])
        if low > high:
            low, high = high, low
        chosen_bounds[field_id] = (low, high)

    lows = np.array([chosen_bounds[field][0] for field in decision_ids], dtype=float)
    highs = np.array([chosen_bounds[field][1] for field in decision_ids], dtype=float)
    objective_key = objective.strip().lower()
    if objective_key.startswith("max"):
        recommendation = np.where(slopes >= 0, highs, lows)
    elif objective_key.startswith("min"):
        recommendation = np.where(slopes >= 0, lows, highs)
    else:
        if target is None:
            raise ValueError("Enter the target outcome value.")
        recommendation = np.clip(frame[decision_ids].mean().to_numpy(dtype=float), lows, highs)
        denominator = float(np.dot(slopes, slopes))
        if denominator > 0:
            for _ in range(200):
                error = intercept + float(np.dot(slopes, recommendation)) - float(target)
                candidate = np.clip(recommendation - error * slopes / denominator, lows, highs)
                if np.allclose(candidate, recommendation, rtol=0, atol=1e-9):
                    break
                recommendation = candidate

    predicted_outcome = intercept + float(np.dot(slopes, recommendation))
    baseline = frame[decision_ids].mean().to_numpy(dtype=float)
    baseline_outcome = intercept + float(np.dot(slopes, baseline))
    return {
        "rows": len(frame),
        "intercept": intercept,
        "coefficients": {field: float(value) for field, value in zip(decision_ids, slopes)},
        "r_squared": r_squared,
        "bounds": chosen_bounds,
        "recommendation": {field: float(value) for field, value in zip(decision_ids, recommendation)},
        "predicted_outcome": predicted_outcome,
        "baseline_outcome": baseline_outcome,
    }


def out_of_target_mask(
    frame: pd.DataFrame,
    input_registry: pd.DataFrame,
    calculated_registry: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Return a cell-level mask for values outside configured range/target."""
    mask = pd.DataFrame(False, index=frame.index, columns=frame.columns)
    if frame.empty:
        return mask
    input_specs: dict[str, tuple[float | None, float | None]] = {}
    if not input_registry.empty:
        for row in input_registry.itertuples():
            low = pd.to_numeric(getattr(row, "min_value", None), errors="coerce")
            high = pd.to_numeric(getattr(row, "max_value", None), errors="coerce")
            input_specs[str(row.field_id)] = (None if pd.isna(low) else float(low), None if pd.isna(high) else float(high))
    calculated_specs: dict[str, tuple[float | None, str]] = {}
    calculated_names: dict[str, str] = {}
    if calculated_registry is not None and not calculated_registry.empty:
        for _, row in calculated_registry.iterrows():
            target = pd.to_numeric(row.get("period_target", row.get("daily_target")), errors="coerce")
            calculated_specs[str(row.get("field_id", ""))] = (None if pd.isna(target) else float(target), str(row.get("target_direction", "High")))
            calculated_names[str(row.get("field_name", ""))] = str(row.get("field_id", ""))

    id_columns = [column for column in ("field_id", "Field ID", "Calculated Field") if column in frame.columns]
    numeric_value_columns = {
        "value", "Value", "Average", "mean", "Mean", "Minimum", "min", "Maximum", "max",
        "Standard Deviation", "Forecast End", "Average Value", "Minimum Value", "Maximum Value",
    }
    skip_columns = {"Target", "target", "Readings", "count", "Variance", "Trend Slope"}
    for idx, row in frame.iterrows():
        field_id = str(row[id_columns[0]]) if id_columns else calculated_names.get(str(row.get("KPI", "")), "")
        input_spec = input_specs.get(field_id)
        calc_spec = calculated_specs.get(field_id)
        for column in frame.columns:
            if column in skip_columns:
                continue
            candidate_field = str(column) if str(column) in input_specs or str(column) in calculated_specs else field_id
            value_column = column in numeric_value_columns or candidate_field == str(column)
            if not value_column:
                continue
            value = pd.to_numeric(row[column], errors="coerce")
            if pd.isna(value):
                continue
            spec = input_specs.get(candidate_field, input_spec)
            if spec:
                low, high = spec
                mask.at[idx, column] = (low is not None and value < low) or (high is not None and value > high)
                continue
            target_spec = calculated_specs.get(candidate_field, calc_spec)
            if target_spec and target_spec[0] is not None:
                target_value, direction = target_spec
                mask.at[idx, column] = value < target_value if direction.strip().lower() == "high" else value > target_value
        if str(row.get("Status", "")).lower() == "off target":
            for column in frame.columns:
                if column in numeric_value_columns:
                    mask.at[idx, column] = True
    return mask


def target_styler(
    frame: pd.DataFrame,
    input_registry: pd.DataFrame,
    calculated_registry: pd.DataFrame | None = None,
) -> pd.io.formats.style.Styler:
    mask = out_of_target_mask(frame, input_registry, calculated_registry)
    styles = mask.map(lambda flagged: "background-color: #FBE5E5; color: #9F1F2A; font-weight: 700" if flagged else "")
    return frame.style.apply(lambda _: styles, axis=None)
