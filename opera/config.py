from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

import pandas as pd

from . import storage


def business_units(active_only: bool = False) -> pd.DataFrame:
    frame = storage.read_csv(storage.DATA_ROOT / "shared" / "business_units.csv")
    if active_only and not frame.empty:
        frame = frame[frame["active"].str.lower() == "true"]
    return frame


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not slug:
        raise ValueError("Enter a valid business-unit name.")
    return slug


def clone_business_unit(source: str, name: str, activate: bool, user: str) -> str:
    slug = slugify(name)
    bus = business_units()
    if slug in set(bus["id"]):
        raise ValueError("That business-unit ID already exists.")
    src = storage.bu_dir(source)
    if not src.exists():
        raise ValueError("Template business unit does not exist.")
    dst = storage.bu_dir(slug)
    shutil.copytree(src, dst)
    for csv_path in dst.rglob("*.csv"):
        frame = storage.read_csv(csv_path)
        if "Business unit" in frame.columns:
            frame["Business unit"] = slug
        if "business_unit" in frame.columns:
            frame["business_unit"] = slug
        storage.atomic_write_csv(csv_path, frame)
    row = {"id": slug, "name": name.strip(), "active": str(bool(activate)).lower(), "placeholder": "false", "register_file": "", "notes": f"Cloned from {source}"}
    storage.atomic_write_csv(storage.DATA_ROOT / "shared" / "business_units.csv", pd.concat([bus, pd.DataFrame([row])], ignore_index=True))
    storage.audit(slug, user, "business_unit_cloned", {"source": source, "name": name})
    return slug


def set_business_unit(bu: str, name: str, active: bool, user: str) -> None:
    p = storage.DATA_ROOT / "shared" / "business_units.csv"
    frame = business_units()
    hit = frame["id"] == bu
    if not hit.any():
        raise ValueError("Unknown business unit.")
    frame.loc[hit, ["name", "active", "placeholder"]] = [name.strip(), str(bool(active)).lower(), "false"]
    storage.atomic_write_csv(p, frame)
    storage.audit(bu, user, "business_unit_configuration_changed", {"name": name, "active": active})


def preset_path(bu: str) -> Path:
    return storage.bu_dir(bu) / "presets.json"


def load_presets(bu: str) -> dict[str, Any]:
    return storage.json_setting(preset_path(bu), {})


def save_preset(bu: str, name: str, settings: dict[str, Any], user: str) -> None:
    presets = load_presets(bu)
    presets[name] = settings
    storage.save_json(preset_path(bu), presets)
    storage.audit(bu, user, "preset_saved", name)


def import_presets(bu: str, payload: bytes, user: str) -> int:
    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Preset JSON must contain an object.")
    storage.save_json(preset_path(bu), data)
    storage.audit(bu, user, "presets_imported", {"count": len(data)})
    return len(data)


def export_presets(bu: str) -> bytes:
    return json.dumps(load_presets(bu), indent=2).encode("utf-8")
