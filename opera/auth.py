from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Mapping, Any

import pandas as pd

from . import storage

ITERS = 200_000
MAX_TRIES = 5
LOCK_MINUTES = 15


@dataclass(frozen=True)
class User:
    username: str
    display_name: str
    role: str
    business_units: tuple[str, ...]
    must_change_password: bool = False


def hash_password(password: str, salt: str | None = None, iterations: int = ITERS) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), iterations).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt, _ = stored.split("$")
        return algorithm == "pbkdf2_sha256" and hmac.compare_digest(hash_password(password, salt, int(iterations)), stored)
    except Exception:
        return False


def _secret_record(username: str, secret_users: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if not secret_users:
        return None
    raw = secret_users.get(username) or secret_users.get(username.lower())
    return dict(raw) if raw else None


def authenticate(username: str, password: str, secret_users: Mapping[str, Any] | None = None) -> tuple[User | None, str]:
    username = username.strip().lower()
    rec = _secret_record(username, secret_users)
    source = "secrets"
    users = storage.read_csv(storage.DATA_ROOT / "shared" / "users.csv")
    row_index = None
    if rec is None:
        source = "csv"
        hit = users[users["username"].str.lower() == username]
        if hit.empty:
            return None, "Incorrect username or password."
        row_index = hit.index[0]
        rec = hit.iloc[0].to_dict()
    if str(rec.get("active", "true")).lower() != "true":
        return None, "This account is inactive."
    lock_until = str(rec.get("lock_until", "")).strip()
    if lock_until:
        try:
            if datetime.fromisoformat(lock_until) > datetime.now(timezone.utc):
                return None, "This account is temporarily locked."
        except ValueError:
            pass
    if not verify_password(password, str(rec.get("password_hash", ""))):
        if source == "csv" and row_index is not None:
            failures = int(rec.get("failed_attempts") or 0) + 1
            users.loc[row_index, "failed_attempts"] = str(failures)
            if failures >= MAX_TRIES:
                users.loc[row_index, "lock_until"] = (datetime.now(timezone.utc) + timedelta(minutes=LOCK_MINUTES)).isoformat(timespec="seconds")
                users.loc[row_index, "failed_attempts"] = "0"
            storage.atomic_write_csv(storage.DATA_ROOT / "shared" / "users.csv", users)
        return None, "Incorrect username or password."
    if source == "csv" and row_index is not None:
        users.loc[row_index, ["failed_attempts", "lock_until"]] = ["0", ""]
        storage.atomic_write_csv(storage.DATA_ROOT / "shared" / "users.csv", users)
    bus = tuple(x.strip() for x in str(rec.get("business_units", "*")).split(";") if x.strip())
    return User(username, str(rec.get("display_name") or rec.get("name") or username), str(rec.get("role") or "Viewer"), bus,
                str(rec.get("must_change_password", "false")).lower() == "true"), ""


def allowed(user: User, capability: str) -> bool:
    grants = {
        "Super Admin": {"view", "input", "events", "risk", "lessons", "configure", "users", "all_bu"},
        "BU Admin": {"view", "input", "events", "risk", "lessons", "configure"},
        "Operator": {"view", "input", "events", "risk", "lessons"},
        "Viewer": {"view"},
    }
    return capability in grants.get(user.role, set())


def can_access_bu(user: User, bu: str) -> bool:
    return "*" in user.business_units or bu in user.business_units


def change_password(username: str, old_password: str, new_password: str) -> tuple[bool, str]:
    if len(new_password) < 12 or not any(c.isupper() for c in new_password) or not any(c.islower() for c in new_password) or not any(c.isdigit() for c in new_password):
        return False, "Use at least 12 characters with upper-case, lower-case and a number."
    p = storage.DATA_ROOT / "shared" / "users.csv"
    users = storage.read_csv(p)
    hit = users[users["username"].str.lower() == username.lower()]
    if hit.empty or not verify_password(old_password, hit.iloc[0]["password_hash"]):
        return False, "Current password is incorrect."
    idx = hit.index[0]
    users.loc[idx, "password_hash"] = hash_password(new_password)
    users.loc[idx, "must_change_password"] = "false"
    storage.atomic_write_csv(p, users)
    return True, "Password changed."
