"""Configuration, health reporting and safe ingestion for automatic data pipelines."""

from __future__ import annotations

import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from . import storage

# Intervals are intentionally batch-oriented.  A 100 ms loop would contend on the
# CSV/file locks, repeatedly rerun Streamlit and overload API/file sources without
# making operator decisions meaningfully fresher.
DEFAULT_PIPELINES: tuple[dict[str, Any], ...] = (
    {"id": "sap_api", "name": "SAP", "method": "API End Point", "kind": "api", "interval_seconds": 300, "implemented": False},
    {"id": "refinery_server_1", "name": "Refinery Production Server 1", "method": "Python scripts", "kind": "script", "interval_seconds": 60, "implemented": False},
    {"id": "refinery_dcs", "name": "Refinery DCS", "method": "Python scripts", "kind": "script", "interval_seconds": 5, "implemented": False},
    {"id": "okpella_server_1", "name": "Okpella Cement Production Server 1", "method": "Python scripts", "kind": "script", "interval_seconds": 60, "implemented": False},
    {"id": "ibese_server_1", "name": "Ibese Production Server 1", "method": "Python scripts", "kind": "script", "interval_seconds": 60, "implemented": False},
    {"id": "obajana_server_1", "name": "Obajana Production Server 1", "method": "Python scripts", "kind": "script", "interval_seconds": 60, "implemented": False},
    {"id": "nascon_server_1", "name": "NASCON Production Server 1", "method": "Python scripts", "kind": "script", "interval_seconds": 60, "implemented": False},
    {"id": "fertilizer_server_1", "name": "Fertilizer Production Server 1", "method": "Python script", "kind": "script", "interval_seconds": 60, "implemented": False},
    {"id": "live_excel_1", "name": "Live Excel files 1", "method": "Python scripts", "kind": "live_excel", "interval_seconds": 60, "implemented": True, "source": "~/opera_inbox/live_excel/"},
    {"id": "live_excel_2", "name": "Live Excel files 2", "method": "Python scripts", "kind": "live_excel", "interval_seconds": 60, "implemented": True, "source": "~/opera_inbox/live_excel/"},
    {"id": "live_excel_3", "name": "Live Excel files 3", "method": "Python scripts", "kind": "live_excel", "interval_seconds": 60, "implemented": True, "source": "~/opera_inbox/live_excel/"},
)


def _config_path(bu: str) -> Path:
    return storage.bu_dir(bu) / "pipeline_configurations.json"


def _state_path(bu: str) -> Path:
    return storage.bu_dir(bu) / "pipeline_state.json"


def default_configurations() -> list[dict[str, Any]]:
    rows = []
    for pipeline in DEFAULT_PIPELINES:
        rows.append({
            **pipeline,
            "enabled": False,
            "source": pipeline.get("source", ""),
            "secret_name": "",
            "notes": "",
        })
    return rows


def load_configurations(bu: str) -> list[dict[str, Any]]:
    saved = storage.json_setting(_config_path(bu), [])
    by_id = {str(row.get("id")): row for row in saved if isinstance(row, dict)}
    merged = []
    for default in default_configurations():
        current = {**default, **by_id.get(default["id"], {})}
        # Immutable catalogue values prevent a damaged settings file from
        # relabelling a connector or claiming an implementation exists.
        for key in ("id", "name", "method", "kind", "implemented"):
            current[key] = default[key]
        try:
            current["interval_seconds"] = int(current.get("interval_seconds", default["interval_seconds"]))
        except (TypeError, ValueError):
            current["interval_seconds"] = default["interval_seconds"]
        merged.append(current)
    return merged


def save_configurations(bu: str, rows: list[dict[str, Any]]) -> Path:
    allowed_ids = {row["id"] for row in DEFAULT_PIPELINES}
    normalized = []
    for row in rows:
        if row.get("id") not in allowed_ids:
            raise ValueError(f"Unknown pipeline: {row.get('id')}")
        interval = int(row.get("interval_seconds", 0))
        if interval < 1 or interval > 86_400:
            raise ValueError("Sync interval must be between 1 second and 24 hours.")
        normalized.append({
            "id": row["id"],
            "interval_seconds": interval,
            "enabled": bool(row.get("enabled", False)),
            "source": str(row.get("source", "")).strip(),
            "secret_name": str(row.get("secret_name", "")).strip(),
            "notes": str(row.get("notes", "")).strip(),
        })
    return storage.save_json(_config_path(bu), normalized)


def load_state(bu: str) -> dict[str, dict[str, Any]]:
    state = storage.json_setting(_state_path(bu), {})
    return state if isinstance(state, dict) else {}


def _save_state(bu: str, state: dict[str, dict[str, Any]]) -> Path:
    return storage.save_json(_state_path(bu), state)


def resolve_source_path(source: str) -> Path:
    expanded = Path(os.path.expandvars(os.path.expanduser(source)))
    return expanded if expanded.is_absolute() else storage.DATA_ROOT / expanded


def source_file(config: dict[str, Any]) -> Path:
    """Resolve a configured watched folder or explicit workbook path."""
    source = resolve_source_path(str(config.get("source", "")))
    if source.suffix.lower() in {".xlsx", ".xlsm"}:
        return source
    return source / f"{config['id']}.xlsx"


def ensure_source_folder(config: dict[str, Any]) -> Path:
    workbook = source_file(config)
    workbook.parent.mkdir(parents=True, exist_ok=True)
    return workbook


def _log_run(bu: str, pipeline_id: str, status: str, source: Path, rows: int = 0, flags: int = 0, message: str = "") -> None:
    storage.append_rows(
        storage.bu_dir(bu) / "pipeline_runs.csv",
        [{"timestamp": storage.utcnow(), "pipeline": pipeline_id, "status": status, "rows": rows, "flags": flags, "source": str(source), "message": message}],
        ["timestamp", "pipeline", "status", "rows", "flags", "source", "message"],
    )


def _parsed_utc(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def pipeline_health(config: dict[str, Any], state: dict[str, Any], now: datetime | None = None) -> tuple[str, str]:
    now = now or datetime.now(timezone.utc)
    if not config.get("enabled"):
        return "Not connected", "Enable and configure this pipeline before scheduling it."
    source = str(config.get("source", "")).strip()
    if not source:
        return "Not connected", "No endpoint, command or source path is configured."
    if not config.get("implemented") and not state.get("last_synced"):
        return "Simulated / connector pending", "Configuration is recorded, but a production connector has not reported a successful run."
    if config.get("kind") == "live_excel" and not source_file(config).is_file():
        return "Not connected", "The configured Excel source file is not available on this server."
    if state.get("last_status") == "waiting" and not state.get("last_synced"):
        return "Waiting for stable file", str(state.get("message") or "The workbook will be retried on the next cycle.")
    if state.get("last_status") == "error":
        return "Error", str(state.get("message") or "The latest run failed.")
    last = _parsed_utc(state.get("last_synced"))
    if last is None:
        return "Not connected", "No successful sync has been recorded."
    interval = max(1, int(config.get("interval_seconds", 60)))
    grace_seconds = max(60, interval * 3)
    age = (now - last).total_seconds()
    if age > grace_seconds:
        return "Stale", f"Last successful sync is {int(age)} seconds old; expected every {interval} seconds."
    return "Healthy", str(state.get("message") or "Latest sync completed successfully.")


def status_frame(bu: str) -> pd.DataFrame:
    states = load_state(bu)
    records = []
    for config in load_configurations(bu):
        state = states.get(config["id"], {})
        health, detail = pipeline_health(config, state)
        records.append({
            "Pipeline": config["name"],
            "Method": config["method"],
            "Health": health,
            "Last synced (UTC)": state.get("last_synced") or "Never",
            "Sync interval": f"{config['interval_seconds']} s",
            "Enabled": "Yes" if config.get("enabled") else "No",
            "Details": detail,
        })
    return pd.DataFrame(records)


def _normalise_excel_rows(frame: pd.DataFrame) -> pd.DataFrame:
    work = frame.dropna(how="all").copy()
    if work.empty:
        return work
    if "Date" in work:
        dates = pd.to_datetime(work["Date"], errors="coerce")
        work["Date"] = dates.dt.strftime("%Y-%m-%d").fillna(work["Date"].astype(str))
    if "Time" in work:
        def format_time(value: Any) -> str:
            if hasattr(value, "strftime"):
                return value.strftime("%H:%M")
            text = str(value).strip()
            return text[:5] if len(text) >= 5 else text
        work["Time"] = work["Time"].map(format_time)
    return work.astype(object).where(pd.notna(work), "")


def _fingerprint(row: pd.Series, columns: list[str]) -> str:
    payload = json.dumps([str(row.get(column, "")) for column in columns], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sync_live_excel(bu: str, pipeline_id: str = "live_excel_1", user: str | None = None) -> tuple[int, int]:
    configurations = {row["id"]: row for row in load_configurations(bu)}
    config = configurations.get(pipeline_id)
    if not config or config.get("kind") != "live_excel":
        raise ValueError("Choose a configured Live Excel pipeline.")
    source = ensure_source_folder(config)
    now = storage.utcnow()
    states = load_state(bu)
    current = dict(states.get(pipeline_id, {}))
    current["last_attempt"] = now
    try:
        if not config.get("enabled"):
            raise ValueError("Pipeline is disabled.")
        if not source.is_file():
            message = f"Waiting for workbook: {source}"
            current.update({"last_status": "waiting", "message": message})
            states[pipeline_id] = current
            _save_state(bu, states)
            _log_run(bu, pipeline_id, "waiting", source, message=message)
            return 0, 0

        # A workbook must have the same size and mtime for two scheduler cycles.
        # This avoids reading a locked/half-copied upload and naturally retries it.
        stat = source.stat()
        signature = f"{stat.st_size}:{stat.st_mtime_ns}"
        if current.get("stable_candidate") != signature:
            message = "Workbook changed or is still being copied; it will be retried next cycle."
            current.update({"last_status": "waiting", "message": message, "stable_candidate": signature})
            states[pipeline_id] = current
            _save_state(bu, states)
            _log_run(bu, pipeline_id, "waiting", source, message=message)
            return 0, 0
        try:
            frame = _normalise_excel_rows(pd.read_excel(source, sheet_name="Live Data", dtype=object))
        except (PermissionError, OSError, ValueError, zipfile.BadZipFile) as exc:
            message = f"Workbook is locked, incomplete or unreadable; retrying next cycle: {exc}"
            current.update({"last_status": "waiting", "message": message})
            states[pipeline_id] = current
            _save_state(bu, states)
            _log_run(bu, pipeline_id, "waiting", source, message=message)
            return 0, 0
        if frame.empty:
            raise ValueError("The 'Live Data' sheet has no rows.")
        allowed = storage.registry(bu)
        digital_ids = set(allowed.loc[(allowed["source"] == "DCS") & (allowed["active"].str.lower() == "true"), "field_id"].astype(str))
        required = ["Date", "Time", "Business unit", "Plant", "Unit/Section", "Equipment"]
        missing = [column for column in required if column not in frame]
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(missing))
        data_fields = [column for column in frame.columns if str(column) in digital_ids]
        if not data_fields:
            raise ValueError("No active DP1–DP1000 Digital Data columns were found.")
        selected = frame[required + data_fields].copy()
        selected = selected.drop_duplicates(subset=required, keep="last").reset_index(drop=True)
        fingerprint_columns = required + data_fields
        keys = selected.apply(lambda row: _fingerprint(row, required), axis=1)
        fingerprints = selected.apply(lambda row: _fingerprint(row, fingerprint_columns), axis=1)
        imported = {str(key): str(value) for key, value in dict(current.get("row_fingerprints", {})).items()}
        changed = pd.Series([imported.get(str(key)) != str(value) for key, value in zip(keys, fingerprints)])
        incoming = selected.loc[changed].reset_index(drop=True)
        incoming_keys = keys.loc[changed].reset_index(drop=True)
        incoming_fingerprints = fingerprints.loc[changed].reset_index(drop=True)
        count = inserted = updated = flag_count = 0
        if not incoming.empty:
            clean, issues, flags = storage.validate_rows(bu, "DCS", incoming)
            errors = issues[issues.get("severity", "").eq("Error")] if not issues.empty else issues
            if not errors.empty:
                sample = "; ".join(f"row {r.row} {r.field}: {r.message}" for r in errors.head(5).itertuples())
                raise ValueError(f"Excel validation failed: {sample}")
            operator = user or f"pipeline:{pipeline_id}"
            existing = storage.read_csv(storage.source_path(bu, "DCS"))
            all_columns = list(dict.fromkeys(list(existing.columns) + list(clean.columns) + ["Recorded by", "Recorded at"]))
            existing = existing.reindex(columns=all_columns)
            recorded_at = storage.utcnow()
            for _, row in clean.iterrows():
                if existing.empty:
                    mask = pd.Series(dtype=bool)
                else:
                    mask = pd.Series(True, index=existing.index)
                    for column in required:
                        mask &= existing[column].astype(str) == str(row[column])
                if mask.any():
                    index = existing.index[mask][0]
                    for column in data_fields:
                        existing.loc[index, column] = row[column]
                    existing.loc[index, ["Recorded by", "Recorded at"]] = [operator, recorded_at]
                    updated += 1
                else:
                    record = {column: row.get(column, "") for column in all_columns}
                    record.update({"Recorded by": operator, "Recorded at": recorded_at})
                    existing = pd.concat([existing, pd.DataFrame([record], columns=all_columns)], ignore_index=True)
                    inserted += 1
            storage.atomic_write_csv(storage.source_path(bu, "DCS"), existing)
            if not flags.empty:
                storage.append_rows(storage.bu_dir(bu) / "flags.csv", flags)
            flag_count = len(flags)
            count = inserted + updated
            storage.audit(bu, operator, "live_excel_pipeline_upsert", {"pipeline": pipeline_id, "inserted": inserted, "updated": updated, "flags": flag_count})
        for key, value in zip(incoming_keys, incoming_fingerprints):
            imported[str(key)] = str(value)
        current.update({
            "last_status": "success",
            "last_synced": now,
            "rows": count,
            "inserted": inserted,
            "updated": updated,
            "flags": flag_count,
            "message": f"Sync completed: {inserted} appended, {updated} updated, {flag_count} validation flag(s).",
            "row_fingerprints": imported,
        })
        states[pipeline_id] = current
        _save_state(bu, states)
        _log_run(bu, pipeline_id, "success", source, count, flag_count, current["message"])
        return count, flag_count
    except Exception as exc:
        current.update({"last_status": "error", "message": str(exc)})
        states[pipeline_id] = current
        _save_state(bu, states)
        _log_run(bu, pipeline_id, "error", source, message=str(exc))
        raise


def record_external_status(bu: str, pipeline_id: str, success: bool, message: str = "") -> None:
    """Allow a production connector to report health without pretending to ingest it."""
    if pipeline_id not in {row["id"] for row in DEFAULT_PIPELINES}:
        raise ValueError("Unknown pipeline ID.")
    states = load_state(bu)
    now = storage.utcnow()
    current = dict(states.get(pipeline_id, {}))
    current.update({"last_attempt": now, "last_status": "success" if success else "error", "message": message})
    if success:
        current["last_synced"] = now
    states[pipeline_id] = current
    _save_state(bu, states)
