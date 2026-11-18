#!/usr/bin/env python3
"""Non-destructive OPERA-X v3.6.x -> v3.7.0 live-data upgrade.

The script never replaces an existing reading. It adds only missing calculated-field
definitions, fills missing dashboard panel defaults, and appends packaged Obajana/Ibese
sample rows whose (Date, Time, Equipment) key is absent from the live source file.
Every modified file is copied to a timestamped backup directory first.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from filelock import FileLock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from opera.dashboard import default_templates
from scripts.seed_data import CALC_DEFINITIONS, CALC_TARGETS

CLONE_PLANTS = {"Obajana Cement Plant", "Ibese Cement Plant"}
KEY_COLUMNS = ["Date", "Time", "Equipment"]
CALCULATED_COLUMNS = ["field_id", "field_name", "formula", "uom", "aggregation", "daily_target", "period_target", "target_direction", "status", "evaluation_order", "mtd_aggregation", "ytd_aggregation", "dashboard", "dashboard_group", "chart"]


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(os.getenv("OPERAX_DATA_DIR", os.getenv("OPERA_DATA_DIR", Path.home() / "opera_data"))))
    parser.add_argument("--package-data", type=Path, default=ROOT / "data")
    parser.add_argument("--backup-dir", type=Path)
    parser.add_argument("--apply", action="store_true", help="Apply changes. Without this flag the script is a dry run.")
    return parser.parse_args()


def backup(path: Path, data_root: Path, backup_root: Path) -> None:
    if not path.exists():
        return
    relative = path.relative_to(data_root)
    target = backup_root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)


def atomic_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(path) + ".lock", timeout=30):
        with tempfile.NamedTemporaryFile("w", suffix=".tmp", prefix=path.name, dir=path.parent, delete=False, encoding="utf-8", newline="") as handle:
            temporary = Path(handle.name)
            frame.to_csv(handle, index=False, lineterminator="\n")
        os.replace(temporary, path)


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(path) + ".lock", timeout=30):
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(temporary, path)


def expected_calculated_fields(bu: str) -> pd.DataFrame:
    rows = []
    for index, (name, expression) in enumerate(CALC_DEFINITIONS.get(bu, []), start=1):
        target = CALC_TARGETS[bu][index - 1]
        aggregation = ["Average", "Maximum", "Minimum"][index % 3]
        rows.append({"field_id": f"CF{index}", "field_name": name, "formula": expression, "uom": "Derived", "aggregation": aggregation, "daily_target": target, "period_target": target, "target_direction": "High", "status": "active", "evaluation_order": index, "mtd_aggregation": aggregation, "ytd_aggregation": aggregation, "dashboard": "true", "dashboard_group": "Operations", "chart": "line"})
    return pd.DataFrame(rows, columns=CALCULATED_COLUMNS).astype(str)


def merge_calculated_fields(live: Path, bu: str) -> tuple[pd.DataFrame, int]:
    source = expected_calculated_fields(bu)
    current = pd.read_csv(live, dtype=str, keep_default_na=False) if live.exists() and live.stat().st_size else pd.DataFrame(columns=source.columns)
    if source.empty:
        return current, 0
    existing = set(current.get("field_id", pd.Series(dtype=str)).astype(str))
    additions = source[~source["field_id"].astype(str).isin(existing)]
    columns = list(dict.fromkeys(list(current.columns) + list(source.columns)))
    return pd.concat([current.reindex(columns=columns), additions.reindex(columns=columns)], ignore_index=True), len(additions)


def merge_templates(live: Path, baseline: dict) -> tuple[dict, int]:
    current = json.loads(live.read_text(encoding="utf-8")) if live.exists() else baseline
    changed = 0
    for module, defaults in baseline.items():
        current.setdefault(module, [])
        defaults_by_id = {item["id"]: item for item in defaults}
        current_by_id = {item.get("id"): item for item in current[module]}
        for template_id, default in defaults_by_id.items():
            if template_id not in current_by_id:
                current[module].append(default)
                changed += 1
                continue
            item = current_by_id[template_id]
            for key, limit in (("chart_fields", 12), ("table_fields", 12), ("kpi_fields", 8)):
                if key not in default:
                    continue
                configured = list(dict.fromkeys(str(value) for value in item.get(key, []) if str(value)))
                merged = (configured + [value for value in default[key] if value not in configured])[:limit]
                if merged != item.get(key, []):
                    item[key] = merged
                    changed += 1
    return current, changed


def merge_clone_rows(live: Path, packaged: Path) -> tuple[pd.DataFrame, int]:
    source = pd.read_csv(packaged, dtype=str, keep_default_na=False)
    additions = source[source.get("Plant", "").isin(CLONE_PLANTS)].copy()
    current = pd.read_csv(live, dtype=str, keep_default_na=False) if live.exists() and live.stat().st_size else pd.DataFrame(columns=source.columns)
    if additions.empty:
        return current, 0
    existing_keys = set(map(tuple, current.reindex(columns=KEY_COLUMNS).astype(str).itertuples(index=False, name=None)))
    keep = [tuple(str(row[column]) for column in KEY_COLUMNS) not in existing_keys for _, row in additions.iterrows()]
    additions = additions.loc[keep]
    columns = list(dict.fromkeys(list(current.columns) + list(source.columns)))
    return pd.concat([current.reindex(columns=columns), additions.reindex(columns=columns)], ignore_index=True), len(additions)


def main() -> int:
    args = arguments()
    data_root = args.data_dir.expanduser().resolve()
    package_root = args.package_data.expanduser().resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = (args.backup_dir or data_root.parent / "opera_data_backups" / f"v3.7.0_{stamp}").expanduser().resolve()
    if not data_root.exists():
        raise SystemExit(f"Live data directory does not exist: {data_root}")
    if not package_root.exists():
        raise SystemExit(f"Packaged data directory does not exist: {package_root}")

    changes: list[tuple[Path, object, int, str]] = []
    for bu_dir in sorted((data_root / "business_units").iterdir()):
        if not bu_dir.is_dir():
            continue
        packaged_bu = package_root / "business_units" / bu_dir.name
        if not packaged_bu.exists():
            continue
        live_calc, count = merge_calculated_fields(bu_dir / "calculated_fields.csv", bu_dir.name)
        if count:
            changes.append((bu_dir / "calculated_fields.csv", live_calc, count, "calculated field definition(s) added"))
        live_templates, count = merge_templates(bu_dir / "dashboard_templates.json", default_templates())
        if count:
            changes.append((bu_dir / "dashboard_templates.json", live_templates, count, "template panel default(s) filled"))

    live_cement = data_root / "business_units" / "cement" / "inputs"
    packaged_cement = package_root / "business_units" / "cement" / "inputs"
    for name in ("dcs.csv", "lab.csv", "field.csv"):
        merged, count = merge_clone_rows(live_cement / name, packaged_cement / name)
        if count:
            changes.append((live_cement / name, merged, count, "missing Obajana/Ibese sample row(s) appended"))

    print(f"Mode: {'APPLY' if args.apply else 'DRY RUN'}")
    print(f"Live data: {data_root}")
    print(f"Backup: {backup_root}")
    if not changes:
        print("No live-data changes are required.")
        return 0
    for path, _, count, description in changes:
        print(f"- {path.relative_to(data_root)}: {count} {description}")
    if not args.apply:
        print("Re-run with --apply to make these non-destructive additions.")
        return 0

    backup_root.mkdir(parents=True, exist_ok=True)
    for path, payload, _, _ in changes:
        backup(path, data_root, backup_root)
        if isinstance(payload, pd.DataFrame):
            atomic_csv(path, payload)
        else:
            atomic_json(path, payload)
    print(f"Applied {len(changes)} file update(s). Existing readings were not replaced.")
    print("field_mappings.xlsx is reconciled automatically by OPERA-X on first access after restart.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
