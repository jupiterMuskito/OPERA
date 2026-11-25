"""Global configuration, health reporting and safe ingestion for automatic pipelines."""

from __future__ import annotations

import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from . import storage

ROUTE_BY_COLUMN = "__business_unit_column__"

DEFAULT_PIPELINES: tuple[dict[str, Any], ...] = (
    {"id": "sap_api", "name": "SAP", "method": "System connection", "kind": "api", "interval_seconds": 300, "implemented": False, "target_mode": "row", "target_bu": ""},
    {"id": "refinery_server_1", "name": "Refinery Production Server 1", "method": "Automated data source", "kind": "script", "interval_seconds": 60, "implemented": False, "target_mode": "fixed", "target_bu": "refinery"},
    {"id": "refinery_dcs", "name": "Refinery DCS", "method": "Digital data source", "kind": "script", "interval_seconds": 5, "implemented": False, "target_mode": "fixed", "target_bu": "refinery"},
    {"id": "okpella_server_1", "name": "Okpella Cement Production Server 1", "method": "Automated data source", "kind": "script", "interval_seconds": 60, "implemented": False, "target_mode": "fixed", "target_bu": "cement"},
    {"id": "ibese_server_1", "name": "Ibese Production Server 1", "method": "Automated data source", "kind": "script", "interval_seconds": 60, "implemented": False, "target_mode": "fixed", "target_bu": "cement"},
    {"id": "obajana_server_1", "name": "Obajana Production Server 1", "method": "Automated data source", "kind": "script", "interval_seconds": 60, "implemented": False, "target_mode": "fixed", "target_bu": "cement"},
    {"id": "nascon_server_1", "name": "NASCON Production Server 1", "method": "Automated data source", "kind": "script", "interval_seconds": 60, "implemented": False, "target_mode": "fixed", "target_bu": "nascon"},
    {"id": "fertilizer_server_1", "name": "Fertilizer Production Server 1", "method": "Automated data source", "kind": "script", "interval_seconds": 60, "implemented": False, "target_mode": "fixed", "target_bu": "fertilizer"},
    {"id": "live_excel_1", "name": "Live Excel files 1", "method": "Excel import", "kind": "live_excel", "interval_seconds": 60, "implemented": True, "source": "~/opera_inbox/live_excel/", "target_mode": "fixed", "target_bu": "refinery"},
    {"id": "live_excel_2", "name": "Live Excel files 2", "method": "Excel import", "kind": "live_excel", "interval_seconds": 60, "implemented": True, "source": "~/opera_inbox/live_excel/", "target_mode": "fixed", "target_bu": "cement"},
    {"id": "live_excel_3", "name": "Live Excel files 3", "method": "Excel import", "kind": "live_excel", "interval_seconds": 60, "implemented": True, "source": "~/opera_inbox/live_excel/", "target_mode": "fixed", "target_bu": "fertilizer"},
)


def _config_path() -> Path:
    return storage.DATA_ROOT / "shared" / "pipeline_configurations.json"


def _state_path() -> Path:
    return storage.DATA_ROOT / "shared" / "pipeline_state.json"


def _legacy_config_path(bu: str) -> Path:
    return storage.bu_dir(bu) / "pipeline_configurations.json"


def _legacy_state_path(bu: str) -> Path:
    return storage.bu_dir(bu) / "pipeline_state.json"


def known_business_units() -> list[str]:
    values: list[str] = []
    frame = storage.read_csv(storage.DATA_ROOT / "shared" / "business_units.csv")
    if not frame.empty and "id" in frame:
        values.extend(str(value).strip() for value in frame["id"] if str(value).strip())
    folder = storage.DATA_ROOT / "business_units"
    if folder.exists():
        values.extend(path.name for path in folder.iterdir() if path.is_dir())
    return list(dict.fromkeys(values))


def _business_unit_aliases() -> dict[str, str]:
    aliases = {bu.casefold(): bu for bu in known_business_units()}
    frame = storage.read_csv(storage.DATA_ROOT / "shared" / "business_units.csv")
    if not frame.empty and {"id", "name"}.issubset(frame.columns):
        for row in frame.itertuples(index=False):
            bu = str(getattr(row, "id")).strip()
            name = str(getattr(row, "name")).strip()
            if bu:
                aliases[bu.casefold()] = bu
                if name:
                    aliases[name.casefold()] = bu
    return aliases


def canonical_business_unit(value: Any) -> str | None:
    return _business_unit_aliases().get(str(value).strip().casefold())


def default_configurations() -> list[dict[str, Any]]:
    return [
        {
            **pipeline,
            "enabled": False,
            "source": pipeline.get("source", ""),
            "secret_name": "",
            "notes": "",
            "allowed_business_units": [],
        }
        for pipeline in DEFAULT_PIPELINES
    ]


def _merge_configurations(saved: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {str(row.get("id")): row for row in saved if isinstance(row, dict)}
    merged: list[dict[str, Any]] = []
    for default in default_configurations():
        current = {**default, **by_id.get(default["id"], {})}
        for key in ("id", "name", "method", "kind", "implemented"):
            current[key] = default[key]
        try:
            current["interval_seconds"] = int(current.get("interval_seconds", default["interval_seconds"]))
        except (TypeError, ValueError):
            current["interval_seconds"] = default["interval_seconds"]
        mode = str(current.get("target_mode", default["target_mode"]))
        current["target_mode"] = mode if mode in {"fixed", "row"} else default["target_mode"]
        current["target_bu"] = str(current.get("target_bu", default.get("target_bu", ""))).strip()
        allowed = current.get("allowed_business_units", [])
        if isinstance(allowed, str):
            allowed = [item.strip() for item in allowed.split(";") if item.strip()]
        current["allowed_business_units"] = list(dict.fromkeys(str(item).strip() for item in allowed if str(item).strip()))
        merged.append(current)
    return merged


def _legacy_candidates() -> dict[str, list[tuple[str, dict[str, Any]]]]:
    candidates: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for bu in known_business_units():
        saved = storage.json_setting(_legacy_config_path(bu), [])
        for row in saved if isinstance(saved, list) else []:
            if isinstance(row, dict) and row.get("id"):
                candidates.setdefault(str(row["id"]), []).append((bu, row))
    return candidates


def _migrate_legacy_configurations() -> list[dict[str, Any]]:
    defaults = default_configurations()
    candidates = _legacy_candidates()
    migrated: list[dict[str, Any]] = []
    for default in defaults:
        options = candidates.get(default["id"], [])
        intended = str(default.get("target_bu", ""))
        matching = [item for item in options if item[0] == intended]
        pool = matching or options
        selected = next((item for item in pool if bool(item[1].get("enabled"))), pool[0] if pool else None)
        if selected:
            legacy_bu, legacy = selected
            current = {
                **default,
                **{key: legacy.get(key, default.get(key)) for key in ("enabled", "source", "secret_name", "notes", "interval_seconds")},
            }
            # The catalogue target is authoritative during migration. This
            # de-duplicates settings saved under the wrong signed-in BU.
            current["target_mode"] = default["target_mode"]
            current["target_bu"] = default.get("target_bu", legacy_bu)
            current["allowed_business_units"] = default.get("allowed_business_units", [])
            migrated.append(current)
        else:
            migrated.append(default)
    return _merge_configurations(migrated)


def load_configurations() -> list[dict[str, Any]]:
    path = _config_path()
    if not path.exists():
        migrated = _migrate_legacy_configurations()
        save_configurations(migrated)
        return migrated
    saved = storage.json_setting(path, [])
    return _merge_configurations(saved if isinstance(saved, list) else [])


def save_configurations(rows: list[dict[str, Any]]) -> Path:
    defaults = {row["id"]: row for row in default_configurations()}
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        pipeline_id = str(row.get("id", ""))
        if pipeline_id not in defaults:
            raise ValueError(f"Unknown pipeline: {pipeline_id}")
        if pipeline_id in seen:
            raise ValueError(f"Duplicate pipeline: {pipeline_id}")
        seen.add(pipeline_id)
        interval = int(row.get("interval_seconds", 0))
        if interval < 1 or interval > 86_400:
            raise ValueError("Sync interval must be between 1 second and 24 hours.")
        mode = str(row.get("target_mode", defaults[pipeline_id]["target_mode"]))
        if mode not in {"fixed", "row"}:
            raise ValueError("Choose a fixed target business unit or route by the Business unit column.")
        target_bu = str(row.get("target_bu", "")).strip()
        if mode == "fixed" and not target_bu:
            raise ValueError("A target business unit is required.")
        allowed = row.get("allowed_business_units", [])
        if isinstance(allowed, str):
            allowed = [item.strip() for item in allowed.split(";") if item.strip()]
        normalized.append({
            "id": pipeline_id,
            "interval_seconds": interval,
            "enabled": bool(row.get("enabled", False)),
            "source": str(row.get("source", "")).strip(),
            "secret_name": str(row.get("secret_name", "")).strip(),
            "notes": str(row.get("notes", "")).strip(),
            "target_mode": mode,
            "target_bu": target_bu if mode == "fixed" else "",
            "allowed_business_units": list(dict.fromkeys(str(item).strip() for item in allowed if str(item).strip())) if mode == "row" else [],
        })
    # Preserve catalogue completeness even if a caller submits a subset.
    for pipeline_id, default in defaults.items():
        if pipeline_id not in seen:
            normalized.append({key: default[key] for key in ("id", "interval_seconds", "enabled", "source", "secret_name", "notes", "target_mode", "target_bu", "allowed_business_units")})
    return storage.save_json(_config_path(), normalized)


def pipeline_targets(config: dict[str, Any]) -> tuple[str, ...]:
    if config.get("target_mode") == "fixed":
        target = str(config.get("target_bu", "")).strip()
        return (target,) if target else ()
    allowed = tuple(str(item).strip() for item in config.get("allowed_business_units", []) if str(item).strip())
    return allowed or tuple(known_business_units())


def configurations_for_business_units(business_units: Iterable[str] | None) -> list[dict[str, Any]]:
    configurations = load_configurations()
    if business_units is None:
        return configurations
    allowed = {str(item) for item in business_units}
    return [item for item in configurations if allowed.intersection(pipeline_targets(item))]


def _migrate_legacy_state() -> dict[str, dict[str, Any]]:
    all_states: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for bu in known_business_units():
        saved = storage.json_setting(_legacy_state_path(bu), {})
        if isinstance(saved, dict):
            for pipeline_id, state in saved.items():
                if isinstance(state, dict):
                    all_states.setdefault(str(pipeline_id), []).append((bu, state))
    configs = {row["id"]: row for row in load_configurations()}
    migrated: dict[str, dict[str, Any]] = {}
    for pipeline_id, options in all_states.items():
        config = configs.get(pipeline_id)
        intended = str(config.get("target_bu", "")) if config else ""
        selected = next((item for item in options if item[0] == intended), options[0])
        bu, state = selected
        migrated[pipeline_id] = {**state, "targets": {bu: dict(state)}}
    return migrated


def load_state() -> dict[str, dict[str, Any]]:
    path = _state_path()
    if not path.exists():
        migrated = _migrate_legacy_state()
        if migrated:
            _save_state(migrated)
        return migrated
    state = storage.json_setting(path, {})
    return state if isinstance(state, dict) else {}


def _save_state(state: dict[str, dict[str, Any]]) -> Path:
    return storage.save_json(_state_path(), state)


def resolve_source_path(source: str) -> Path:
    expanded = Path(os.path.expandvars(os.path.expanduser(source)))
    return expanded if expanded.is_absolute() else storage.DATA_ROOT / expanded


def source_file(config: dict[str, Any]) -> Path:
    source = resolve_source_path(str(config.get("source", "")))
    if source.suffix.lower() in {".xlsx", ".xlsm"}:
        return source
    return source / f"{config['id']}.xlsx"


def ensure_source_folder(config: dict[str, Any]) -> Path:
    workbook = source_file(config)
    workbook.parent.mkdir(parents=True, exist_ok=True)
    return workbook


def _log_run(bu: str, config: dict[str, Any], status: str, source: Path, rows: int = 0, flags: int = 0, rejected: int = 0, message: str = "") -> None:
    storage.append_rows(
        storage.bu_dir(bu) / "pipeline_runs.csv",
        [{"timestamp": storage.utcnow(), "pipeline": config["id"], "pipeline_name": config["name"], "target_bu": bu, "status": status, "rows": rows, "flags": flags, "rejected": rejected, "source": str(source), "message": message}],
        ["timestamp", "pipeline", "pipeline_name", "target_bu", "status", "rows", "flags", "rejected", "source", "message"],
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
        return "Not connected", "No source is configured."
    if not config.get("implemented") and not state.get("last_synced"):
        return "Not connected", "This source has not completed a successful run."
    if config.get("kind") == "live_excel" and not source_file(config).is_file():
        return "Not connected", "The configured Excel source is not available."
    if state.get("last_status") == "waiting" and not state.get("last_synced"):
        return "Waiting", str(state.get("message") or "The source will be checked again.")
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


def status_frame(business_units: Iterable[str] | None = None) -> pd.DataFrame:
    states = load_state()
    visible = None if business_units is None else {str(item) for item in business_units}
    records: list[dict[str, Any]] = []
    for config in configurations_for_business_units(visible):
        current = states.get(config["id"], {})
        targets = [target for target in pipeline_targets(config) if visible is None or target in visible]
        for target in targets:
            target_state = dict(current)
            target_state.update(current.get("targets", {}).get(target, {}))
            health, detail = pipeline_health(config, target_state)
            records.append({
                "Pipeline": config["name"],
                "Target BU": target,
                "Method": config["method"],
                "Health": health,
                "Last synced (UTC)": target_state.get("last_synced") or "Never",
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


def _upsert_rows(bu: str, rows: list[pd.Series], data_fields: list[str], operator: str) -> tuple[int, int]:
    existing = storage.read_csv(storage.source_path(bu, "DCS"))
    all_columns = list(dict.fromkeys(list(existing.columns) + list(storage.BASE_COLUMNS) + data_fields + ["Recorded by", "Recorded at"]))
    existing = existing.reindex(columns=all_columns)
    recorded_at = storage.utcnow()
    inserted = updated = 0
    required = ["Date", "Time", "Business unit", "Plant", "Unit/Section", "Equipment"]
    for row in rows:
        mask = pd.Series(True, index=existing.index)
        for column in required:
            mask &= existing[column].astype(str) == str(row.get(column, ""))
        if mask.any():
            index = existing.index[mask][0]
            for column in data_fields:
                existing.loc[index, column] = row.get(column, "")
            existing.loc[index, ["Recorded by", "Recorded at"]] = [operator, recorded_at]
            updated += 1
        else:
            record = {column: row.get(column, "") for column in all_columns}
            record.update({"Recorded by": operator, "Recorded at": recorded_at})
            existing = pd.concat([existing, pd.DataFrame([record], columns=all_columns)], ignore_index=True)
            inserted += 1
    if rows:
        storage.atomic_write_csv(storage.source_path(bu, "DCS"), existing)
    return inserted, updated


def sync_live_excel(pipeline_id: str = "live_excel_1", user: str | None = None) -> tuple[int, int]:
    configurations = {row["id"]: row for row in load_configurations()}
    config = configurations.get(pipeline_id)
    if not config or config.get("kind") != "live_excel":
        raise ValueError("Choose a configured Live Excel pipeline.")
    source = ensure_source_folder(config)
    now = storage.utcnow()
    states = load_state()
    current = dict(states.get(pipeline_id, {}))
    current["last_attempt"] = now
    targets = pipeline_targets(config)
    target_states = {key: dict(value) for key, value in current.get("targets", {}).items()}

    def save_waiting(message: str) -> tuple[int, int]:
        current.update({"last_status": "waiting", "message": message, "targets": target_states})
        for target in targets:
            target_states[target] = {**target_states.get(target, {}), "last_attempt": now, "last_status": "waiting", "message": message}
            _log_run(target, config, "waiting", source, message=message)
        states[pipeline_id] = current
        _save_state(states)
        return 0, 0

    try:
        if not config.get("enabled"):
            raise ValueError("Pipeline is disabled.")
        if not source.is_file():
            return save_waiting("Waiting for the configured workbook.")
        stat = source.stat()
        signature = f"{stat.st_size}:{stat.st_mtime_ns}"
        if current.get("stable_candidate") != signature:
            current["stable_candidate"] = signature
            return save_waiting("The workbook changed recently and will be checked again.")
        try:
            frame = _normalise_excel_rows(pd.read_excel(source, sheet_name="Live Data", dtype=object))
        except (PermissionError, OSError, ValueError, zipfile.BadZipFile) as exc:
            return save_waiting(f"The workbook is not ready and will be checked again: {exc}")
        if frame.empty:
            raise ValueError("The 'Live Data' sheet has no rows.")
        required = ["Date", "Time", "Business unit", "Plant", "Unit/Section", "Equipment"]
        missing = [column for column in required if column not in frame]
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(missing))

        allowed_targets = set(targets)
        aliases = _business_unit_aliases()
        frame["_target_bu"] = frame["Business unit"].map(lambda value: aliases.get(str(value).strip().casefold(), ""))
        unknown_mask = frame["_target_bu"].eq("")
        disallowed_mask = ~unknown_mask & ~frame["_target_bu"].isin(allowed_targets)
        rejected_unknown = int(unknown_mask.sum())
        rejected_disallowed = int(disallowed_mask.sum())
        valid = frame[~unknown_mask & ~disallowed_mask].copy()
        valid["Business unit"] = valid["_target_bu"]
        valid = valid.drop(columns="_target_bu")

        imported_fingerprints = {str(key): str(value) for key, value in dict(current.get("row_fingerprints", {})).items()}
        operator = user or f"pipeline:{pipeline_id}"
        total_count = 0
        total_flags = 0
        total_rejected = rejected_unknown + rejected_disallowed
        processed_any = False

        for target in targets:
            group = valid[valid["Business unit"] == target].copy()
            target_rejected = 0
            validated_rows = 0
            inserted = updated = flag_count = 0
            if not group.empty:
                processed_any = True
                registry = storage.registry(target)
                digital_ids = set(registry.loc[(registry["source"] == "DCS") & (registry["active"].astype(str).str.lower() == "true"), "field_id"].astype(str))
                populated = [column for column in group.columns if column not in required and group[column].map(lambda value: str(value).strip() not in {"", "nan", "None"}).any()]
                data_fields = [column for column in populated if str(column) in digital_ids]
                unknown_fields = [str(column) for column in populated if str(column) not in digital_ids]
                if unknown_fields or not data_fields:
                    target_rejected += len(group)
                    group = group.iloc[0:0]
                else:
                    selected = group[required + data_fields].drop_duplicates(subset=required, keep="last").reset_index(drop=True)
                    successful_rows: list[pd.Series] = []
                    successful_keys: list[tuple[str, str]] = []
                    all_flags: list[pd.DataFrame] = []
                    for _, row in selected.iterrows():
                        key = _fingerprint(row, required)
                        fingerprint = _fingerprint(row, required + data_fields)
                        if imported_fingerprints.get(key) == fingerprint:
                            validated_rows += 1
                            continue
                        clean, issues, flags = storage.validate_rows(target, "DCS", pd.DataFrame([row], columns=required + data_fields))
                        errors = issues[issues["severity"].eq("Error")] if not issues.empty and "severity" in issues else issues
                        if errors is not None and not errors.empty:
                            target_rejected += 1
                            continue
                        successful_rows.append(clean.iloc[0])
                        validated_rows += 1
                        successful_keys.append((key, fingerprint))
                        if not flags.empty:
                            all_flags.append(flags)
                    inserted, updated = _upsert_rows(target, successful_rows, data_fields, operator)
                    for key, fingerprint in successful_keys:
                        imported_fingerprints[key] = fingerprint
                    if all_flags:
                        combined_flags = pd.concat(all_flags, ignore_index=True)
                        storage.append_rows(storage.bu_dir(target) / "flags.csv", combined_flags)
                        flag_count = len(combined_flags)
                    if successful_rows:
                        storage.audit(target, operator, "live_excel_pipeline_upsert", {"pipeline": pipeline_id, "target_bu": target, "inserted": inserted, "updated": updated, "flags": flag_count, "rejected": target_rejected})
            count = inserted + updated
            total_count += count
            total_flags += flag_count
            total_rejected += target_rejected
            message = f"Sync completed for {target}: {inserted} appended, {updated} updated, {flag_count} flag(s), {target_rejected} rejected row(s)."
            target_status = "error" if target_rejected and validated_rows == 0 else "success"
            target_states[target] = {
                **target_states.get(target, {}),
                "last_attempt": now,
                "last_status": target_status,
                "last_synced": now if target_status == "success" else target_states.get(target, {}).get("last_synced", ""),
                "rows": count,
                "inserted": inserted,
                "updated": updated,
                "flags": flag_count,
                "rejected": target_rejected,
                "message": message,
            }
            _log_run(target, config, target_status, source, count, flag_count, target_rejected, message)

        if not processed_any and total_rejected:
            for target in targets:
                target_states[target] = {**target_states.get(target, {}), "last_attempt": now, "last_status": "error", "message": f"No rows were imported; {total_rejected} row(s) named an unknown or disallowed business unit."}
        overall_status = "error" if not processed_any and total_rejected else "success"
        current.update({
            "last_status": overall_status,
            "last_synced": now if overall_status == "success" else current.get("last_synced", ""),
            "rows": total_count,
            "flags": total_flags,
            "rejected": total_rejected,
            "message": f"Sync completed: {total_count} imported or updated, {total_flags} flag(s), {total_rejected} rejected row(s).",
            "row_fingerprints": imported_fingerprints,
            "targets": target_states,
        })
        states[pipeline_id] = current
        _save_state(states)
        return total_count, total_flags
    except Exception as exc:
        current.update({"last_status": "error", "message": str(exc), "targets": target_states})
        for target in targets:
            target_states[target] = {**target_states.get(target, {}), "last_attempt": now, "last_status": "error", "message": str(exc)}
            _log_run(target, config, "error", source, message=str(exc))
        states[pipeline_id] = current
        _save_state(states)
        raise


def record_external_status(pipeline_id: str, success: bool, message: str = "", target_bu: str | None = None) -> None:
    configs = {row["id"]: row for row in load_configurations()}
    config = configs.get(pipeline_id)
    if not config:
        raise ValueError("Unknown pipeline ID.")
    targets = pipeline_targets(config)
    if target_bu:
        if target_bu not in targets:
            raise ValueError("The selected business unit is not allowed for this pipeline.")
        targets = (target_bu,)
    states = load_state()
    now = storage.utcnow()
    current = dict(states.get(pipeline_id, {}))
    target_states = {key: dict(value) for key, value in current.get("targets", {}).items()}
    for target in targets:
        target_states[target] = {**target_states.get(target, {}), "last_attempt": now, "last_status": "success" if success else "error", "message": message}
        if success:
            target_states[target]["last_synced"] = now
    current.update({"last_attempt": now, "last_status": "success" if success else "error", "message": message, "targets": target_states})
    if success:
        current["last_synced"] = now
    states[pipeline_id] = current
    _save_state(states)
