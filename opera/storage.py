from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
from filelock import FileLock

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(os.getenv("OPERA_DATA_DIR", ROOT / "data"))
BASE_COLUMNS = ["Date", "Time", "Business unit", "Plant", "Unit/Section", "Equipment", "Recorded by", "Recorded at"]
SOURCES = {"DCS": "DP", "Lab": "L", "Field": "F", "TA": "TA", "TB": "TB", "TC": "TC", "TD": "TD", "TE": "TE", "TF": "TF", "TG": "TG"}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _path(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else DATA_ROOT / p


def read_csv(path: str | Path, columns: Iterable[str] | None = None) -> pd.DataFrame:
    p = _path(path)
    if not p.exists() or p.stat().st_size == 0:
        return pd.DataFrame(columns=list(columns or []))
    try:
        return pd.read_csv(p, dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=list(columns or []))


def _safe_cell(value: Any) -> Any:
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def atomic_write_csv(path: str | Path, frame: pd.DataFrame) -> Path:
    p = _path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    clean = frame.map(_safe_cell) if hasattr(frame, "map") else frame.applymap(_safe_cell)
    lock = FileLock(str(p) + ".lock", timeout=20)
    with lock:
        tmp = p.with_name(p.name + f".{uuid.uuid4().hex}.tmp")
        clean.to_csv(tmp, index=False, encoding="utf-8", lineterminator="\n")
        os.replace(tmp, p)
    return p


def atomic_write_bytes(path: str | Path, data: bytes) -> Path:
    p = _path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(str(p) + ".lock", timeout=20)
    with lock:
        tmp = p.with_name(p.name + f".{uuid.uuid4().hex}.tmp")
        tmp.write_bytes(data)
        os.replace(tmp, p)
    return p


def append_rows(path: str | Path, rows: list[dict[str, Any]] | pd.DataFrame, columns: Iterable[str] | None = None) -> Path:
    p = _path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    incoming = rows.copy() if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    lock = FileLock(str(p) + ".lock", timeout=20)
    with lock:
        current = read_csv(p, columns)
        all_columns = list(dict.fromkeys(list(current.columns) + list(incoming.columns) + list(columns or [])))
        merged = pd.concat([current.reindex(columns=all_columns), incoming.reindex(columns=all_columns)], ignore_index=True)
        tmp = p.with_name(p.name + f".{uuid.uuid4().hex}.tmp")
        clean = merged.map(_safe_cell) if hasattr(merged, "map") else merged.applymap(_safe_cell)
        clean.to_csv(tmp, index=False, encoding="utf-8", lineterminator="\n")
        os.replace(tmp, p)
    return p


def bu_dir(bu: str) -> Path:
    return DATA_ROOT / "business_units" / bu


def source_path(bu: str, source: str) -> Path:
    return bu_dir(bu) / "inputs" / f"{source.lower()}.csv"


def registry(bu: str) -> pd.DataFrame:
    return read_csv(bu_dir(bu) / "fields.csv")


def equipment(bu: str) -> pd.DataFrame:
    return read_csv(bu_dir(bu) / "equipment.csv")


def input_data(bu: str, sources: Iterable[str] | None = None) -> pd.DataFrame:
    frames = []
    for source in sources or SOURCES:
        frame = read_csv(source_path(bu, source))
        if not frame.empty:
            frame["Source"] = source
            frames.append(frame)
    return pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame(columns=BASE_COLUMNS + ["Source"])


def audit(bu: str, user: str, action: str, details: Any = "") -> None:
    payload = details if isinstance(details, str) else json.dumps(details, ensure_ascii=False, default=str)
    append_rows(bu_dir(bu) / "audit_log.csv", [{"timestamp": utcnow(), "business_unit": bu, "user": user, "action": action, "details": payload}],
                ["timestamp", "business_unit", "user", "action", "details"])


def notify(bu: str, message: str, level: str = "success", recipient: str = "all", created_by: str = "system") -> str:
    nid = uuid.uuid4().hex
    append_rows(bu_dir(bu) / "notifications.csv", [{"id": nid, "timestamp": utcnow(), "recipient": recipient, "level": level,
                                                        "message": message, "created_by": created_by, "read_by": ""}],
                ["id", "timestamp", "recipient", "level", "message", "created_by", "read_by"])
    return nid


def unread_notifications(bu: str, username: str) -> pd.DataFrame:
    frame = read_csv(bu_dir(bu) / "notifications.csv")
    if frame.empty:
        return frame
    allowed = frame["recipient"].isin(["all", username])
    unread = ~frame["read_by"].str.split(";").apply(lambda xs: username in xs)
    return frame[allowed & unread].sort_values("timestamp", ascending=False)


def mark_notifications_read(bu: str, username: str) -> None:
    p = bu_dir(bu) / "notifications.csv"
    frame = read_csv(p)
    if frame.empty:
        return
    def add(value: str) -> str:
        users = [x for x in value.split(";") if x]
        if username not in users:
            users.append(username)
        return ";".join(users)
    frame["read_by"] = frame["read_by"].map(add)
    atomic_write_csv(p, frame)


def save_attachment(bu: str, name: str, data: bytes) -> str:
    suffix = Path(name).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError("Only PNG, JPG, JPEG and WEBP pictures are supported.")
    folder = bu_dir(bu) / "attachments"
    folder.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).name)
    target = folder / f"{uuid.uuid4().hex}_{safe}"
    atomic_write_bytes(target, data)
    return target.relative_to(DATA_ROOT).as_posix()


def field_record(bu: str, field_id: str) -> dict[str, str] | None:
    reg = registry(bu)
    hit = reg[reg["field_id"] == field_id]
    return None if hit.empty else hit.iloc[0].to_dict()


def validate_rows(bu: str, source: str, frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    required = ["Date", "Time", "Business unit", "Plant", "Unit/Section", "Equipment"]
    issues: list[dict[str, Any]] = []
    flags: list[dict[str, Any]] = []
    work = frame.copy()
    for col in required:
        if col not in work.columns:
            issues.append({"row": 0, "field": col, "severity": "Error", "message": "Required column is missing"})
    if issues:
        return work, pd.DataFrame(issues), pd.DataFrame(flags)
    reg = registry(bu)
    allowed = reg[(reg["source"] == source) & (reg["active"].str.lower() == "true")].set_index("field_id")
    source_fields = [c for c in work.columns if c in allowed.index]
    existing = read_csv(source_path(bu, source))
    previous: dict[str, float] = {}
    for field in source_fields:
        if field in existing.columns:
            prior = pd.to_numeric(existing[field], errors="coerce").dropna()
            if not prior.empty:
                previous[field] = float(prior.iloc[-1])
    unknown = [c for c in work.columns if c not in required + ["Recorded by", "Recorded at"] and c not in allowed.index]
    for col in unknown:
        issues.append({"row": 0, "field": col, "severity": "Error", "message": "Unknown or inactive field for this source"})
    eq = set(equipment(bu)["equipment_id"].tolist())
    for idx, row in work.iterrows():
        excel_row = idx + 2
        try:
            pd.to_datetime(str(row["Date"]), format="%Y-%m-%d", errors="raise")
        except Exception:
            issues.append({"row": excel_row, "field": "Date", "severity": "Error", "message": "Use ISO date YYYY-MM-DD"})
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", str(row["Time"])):
            issues.append({"row": excel_row, "field": "Time", "severity": "Error", "message": "Use 24-hour time HH:MM"})
        if str(row["Business unit"]).strip().lower() != bu.lower():
            issues.append({"row": excel_row, "field": "Business unit", "severity": "Error", "message": f"Must be {bu}"})
        if str(row["Equipment"]) not in eq:
            issues.append({"row": excel_row, "field": "Equipment", "severity": "Error", "message": "Equipment is not registered"})
        for field in source_fields:
            raw = row[field]
            if raw in ("", None) or pd.isna(raw):
                continue
            try:
                value = float(raw)
            except Exception:
                issues.append({"row": excel_row, "field": field, "severity": "Error", "message": "Value must be numeric"})
                continue
            meta = allowed.loc[field]
            low = pd.to_numeric(meta.get("min_value"), errors="coerce")
            high = pd.to_numeric(meta.get("max_value"), errors="coerce")
            if (pd.notna(low) and value < low) or (pd.notna(high) and value > high):
                flags.append({"timestamp": utcnow(), "date": row["Date"], "time": row["Time"], "field_id": field, "value": value,
                              "flag_type": "Out of range", "message": f"Expected {low} to {high}", "status": "Open"})
            jump = pd.to_numeric(meta.get("jump_limit"), errors="coerce")
            if field in previous and pd.notna(jump) and abs(value - previous[field]) > jump:
                flags.append({"timestamp": utcnow(), "date": row["Date"], "time": row["Time"], "field_id": field, "value": value,
                              "flag_type": "Abnormal jump", "message": f"Change {abs(value-previous[field]):.3f} exceeds jump limit {jump}", "status": "Open"})
            previous[field] = value
    return work, pd.DataFrame(issues), pd.DataFrame(flags)


def save_validated_input(bu: str, source: str, frame: pd.DataFrame, user: str) -> tuple[int, int]:
    clean, issues, flags = validate_rows(bu, source, frame)
    if not issues.empty and (issues["severity"] == "Error").any():
        raise ValueError("Validation errors must be corrected before saving.")
    clean["Recorded by"] = user
    clean["Recorded at"] = utcnow()
    append_rows(source_path(bu, source), clean)
    if not flags.empty:
        append_rows(bu_dir(bu) / "flags.csv", flags)
    audit(bu, user, "data_input_saved", {"source": source, "rows": len(clean), "flags": len(flags)})
    return len(clean), len(flags)


def template_bytes(bu: str, source: str, fields: list[str] | None = None) -> bytes:
    reg = registry(bu)
    active = reg[(reg["source"] == source) & (reg["active"].str.lower() == "true")]
    selected = fields or active["field_id"].head(20).tolist()
    eq = equipment(bu)
    first = eq[eq["placeholder"].str.lower() != "true"].iloc[0]
    row = {"Date": datetime.now().date().isoformat(), "Time": "06:00", "Business unit": bu, "Plant": first["plant"],
           "Unit/Section": first["unit_section"], "Equipment": first["equipment_id"]}
    row.update({field: "" for field in selected})
    return pd.DataFrame([row]).to_csv(index=False).encode("utf-8")


def json_setting(path: str | Path, default: Any = None) -> Any:
    p = _path(path)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: str | Path, value: Any) -> Path:
    p = _path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(str(p) + ".lock", timeout=20)
    with lock:
        tmp = p.with_name(p.name + f".{uuid.uuid4().hex}.tmp")
        tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        os.replace(tmp, p)
    return p
