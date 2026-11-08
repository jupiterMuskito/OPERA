from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import storage
from .risk_engine import Register, RegisterError, load_register

ROOT = Path(__file__).resolve().parents[1]
REGISTER_DIR = ROOT / "registers"
UPLOAD_DIR = storage.DATA_ROOT / "registers"


def register_path(bu: str) -> Path | None:
    bus = storage.read_csv(storage.DATA_ROOT / "shared" / "business_units.csv")
    hit = bus[bus["id"] == bu]
    if hit.empty:
        return None
    uploaded = UPLOAD_DIR / f"{bu}.xlsx"
    if uploaded.exists():
        return uploaded
    configured = str(hit.iloc[0].get("register_file", "")).strip()
    return ROOT / configured if configured else None


def resolve(bu: str) -> tuple[Register | None, str, str | None]:
    path = register_path(bu)
    if path is None or not path.exists():
        return None, "", "No approved risk register is linked to this business unit."
    try:
        source = "Uploaded" if path.parent == UPLOAD_DIR else "Bundled approved register"
        return load_register(path), source, None
    except RegisterError as exc:
        return None, "", str(exc)


def activate(bu: str, data: bytes, user: str, note: str = "") -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    temp = UPLOAD_DIR / f"{bu}.tmp"
    storage.atomic_write_bytes(temp, data)
    register = load_register(temp)
    target = UPLOAD_DIR / f"{bu}.xlsx"
    storage.atomic_write_bytes(target, data)
    temp.unlink(missing_ok=True)
    history = UPLOAD_DIR / "history" / bu
    history.mkdir(parents=True, exist_ok=True)
    storage.atomic_write_bytes(history / f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}_{register.fingerprint}.xlsx", data)
    storage.audit(bu, user, "risk_register_activated", {"fingerprint": register.fingerprint, "note": note})
    return target


def github_commit(bu: str, data: bytes, user: str, github: dict[str, Any]) -> str:
    token, repo = github.get("token"), github.get("repo")
    if not token or not repo:
        raise RuntimeError("GitHub token and repo are required in Streamlit secrets.")
    branch = github.get("branch", "main")
    path = github.get("path", f"registers/{bu}.xlsx")
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "User-Agent": "opera-streamlit"}
    sha = None
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{url}?ref={branch}", headers=headers), timeout=20) as response:
            sha = json.loads(response.read()).get("sha")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise RuntimeError(f"GitHub read failed ({exc.code}).") from exc
    body = {"message": f"OPERA risk register update for {bu} by {user}", "content": base64.b64encode(data).decode(), "branch": branch}
    if sha:
        body["sha"] = sha
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers={**headers, "Content-Type": "application/json"}, method="PUT")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read())["commit"]["html_url"]
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GitHub commit failed ({exc.code}).") from exc
