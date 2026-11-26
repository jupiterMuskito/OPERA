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
SUPPORTED_ROLES = ("Super Admin", "BU Admin", "Manager", "Operator", "Patroller", "Viewer")
SINGLE_BU_ROLES = {"Manager", "Operator", "Patroller"}

ROLE_ALIASES = {
    "super admin": "Super Admin",
    "superadmin": "Super Admin",
    "super administrator": "Super Admin",
    "opera super admin": "Super Admin",
    "opera x super admin": "Super Admin",
    "bu admin": "BU Admin",
    "buadmin": "BU Admin",
    "business unit admin": "BU Admin",
    "business unit administrator": "BU Admin",
    "manager": "Manager",
    "operator": "Operator",
    "patroller": "Patroller",
    "viewer": "Viewer",
}

# Capabilities are inherited from left to right. Super Admin is built from the
# union of every lower-role grant, so adding a lower-role privilege cannot
# accidentally deny it to Super Admin.
_VIEWER_GRANTS = frozenset({"view"})
_PATROLLER_GRANTS = _VIEWER_GRANTS | {"input", "manual_input"}
_OPERATOR_GRANTS = _PATROLLER_GRANTS | {
    "bulk_input", "events", "risk", "lessons", "export", "home_drilldown",
}
_MANAGER_GRANTS = _OPERATOR_GRANTS | {"configure"}
_BU_ADMIN_GRANTS = _MANAGER_GRANTS
_SUPER_ADMIN_ONLY = frozenset({"users", "manage_business_units", "all_bu"})
ROLE_GRANTS = {
    "Viewer": _VIEWER_GRANTS,
    "Patroller": _PATROLLER_GRANTS,
    "Operator": _OPERATOR_GRANTS,
    "Manager": _MANAGER_GRANTS,
    "BU Admin": _BU_ADMIN_GRANTS,
}
ROLE_GRANTS["Super Admin"] = frozenset().union(*ROLE_GRANTS.values(), _SUPER_ADMIN_ONLY)

# User-facing and administrative actions that must always be covered by the
# role matrix. Tests iterate this list and fail if Super Admin lacks any item.
ACTION_CAPABILITIES = (
    "view", "manual_input", "bulk_input", "events", "lessons", "risk",
    "export", "home_drilldown", "configure", "users",
    "manage_business_units", "all_bu",
)


def canonical_role(value: Any) -> str:
    """Return the supported role name for legacy casing and separator variants."""
    key = " ".join(str(value or "Viewer").strip().replace("_", " ").replace("-", " ").split()).casefold()
    return ROLE_ALIASES.get(key, "Viewer")


@dataclass(frozen=True)
class User:
    username: str
    display_name: str
    role: str
    business_units: tuple[str, ...]
    must_change_password: bool = False

    def __post_init__(self) -> None:
        role = canonical_role(self.role)
        business_units = tuple(dict.fromkeys(str(item).strip() for item in self.business_units if str(item).strip()))
        if role in SINGLE_BU_ROLES:
            business_units = business_units[:1]
        object.__setattr__(self, "role", role)
        object.__setattr__(self, "business_units", business_units)


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
    display_name = str(rec.get("display_name") or rec.get("name") or username)
    if display_name == "OPERA Super Admin":
        display_name = "OPERA-X Super Admin"
    return User(username, display_name, canonical_role(rec.get("role")), bus,
                str(rec.get("must_change_password", "false")).lower() == "true"), ""


def allowed(user: User, capability: str) -> bool:
    role = canonical_role(user.role)
    # Fail closed for unknown roles, but never let a recognized Super Admin
    # principal lose an application action because one grant path was stale.
    if role == "Super Admin" and capability in ACTION_CAPABILITIES:
        return True
    return capability in ROLE_GRANTS[role]


def can_access_bu(user: User, bu: str) -> bool:
    return allowed(user, "all_bu") or "*" in user.business_units or bu in user.business_units


def user_from_record(record: Mapping[str, Any]) -> User:
    username = str(record.get("username", "")).strip().lower()
    business_units = tuple(item.strip() for item in str(record.get("business_units", "")).split(";") if item.strip())
    return User(
        username,
        str(record.get("display_name") or username),
        canonical_role(record.get("role")),
        business_units,
        str(record.get("must_change_password", "false")).lower() == "true",
    )


def get_secret_user(username: str, secret_users: Mapping[str, Any] | None) -> User | None:
    """Reload a Secrets account without falling back to a same-named CSV row."""
    record = _secret_record(username.strip().lower(), secret_users)
    if record is None or str(record.get("active", "true")).lower() != "true":
        return None
    record = {**record, "username": username.strip().lower()}
    return user_from_record(record)


def get_user(username: str) -> User | None:
    """Reload a CSV account so role/BU changes apply on the next rerun."""
    users = storage.read_csv(storage.DATA_ROOT / "shared" / "users.csv")
    if users.empty or "username" not in users:
        return None
    hit = users[users["username"].str.lower() == username.strip().lower()]
    if hit.empty or str(hit.iloc[0].get("active", "false")).lower() != "true":
        return None
    return user_from_record(hit.iloc[0].to_dict())


def create_user(username: str, display_name: str, role: str, business_units: list[str], password: str) -> User:
    username = username.strip().lower()
    if not username or len(password) < 12:
        raise ValueError("Username and a 12-character temporary password are required.")
    if role not in SUPPORTED_ROLES:
        raise ValueError("Choose a supported role.")
    business_units = list(dict.fromkeys(business_units))
    if role != "Super Admin" and not business_units:
        raise ValueError("Choose at least one business unit.")
    if role in SINGLE_BU_ROLES and len(business_units) != 1:
        raise ValueError(f"{role} accounts must be assigned to exactly one business unit.")
    path = storage.DATA_ROOT / "shared" / "users.csv"
    users = storage.read_csv(path)
    if not users.empty and username in set(users["username"].str.lower()):
        raise ValueError("Username already exists.")
    row = {
        "username": username,
        "display_name": display_name.strip() or username,
        "password_hash": hash_password(password),
        "role": role,
        "business_units": "*" if role == "Super Admin" else ";".join(business_units),
        "active": "true",
        "must_change_password": "true",
        "failed_attempts": "0",
        "lock_until": "",
    }
    storage.atomic_write_csv(path, pd.concat([users, pd.DataFrame([row])], ignore_index=True))
    return user_from_record(row)


def update_user_access(username: str, display_name: str, role: str, business_units: list[str], active: bool) -> User:
    path = storage.DATA_ROOT / "shared" / "users.csv"
    users = storage.read_csv(path)
    hit = users["username"].str.lower() == username.strip().lower()
    if not hit.any():
        raise ValueError("Unknown user.")
    if role not in SUPPORTED_ROLES:
        raise ValueError("Choose a supported role.")
    business_units = list(dict.fromkeys(business_units))
    if role != "Super Admin" and not business_units:
        raise ValueError("Choose at least one business unit.")
    if role in SINGLE_BU_ROLES and len(business_units) != 1:
        raise ValueError(f"{role} accounts must be assigned to exactly one business unit.")
    users.loc[hit, ["display_name", "role", "business_units", "active"]] = [
        display_name.strip() or username,
        role,
        "*" if role == "Super Admin" else ";".join(business_units),
        str(bool(active)).lower(),
    ]
    storage.atomic_write_csv(path, users)
    return user_from_record(users.loc[hit].iloc[0].to_dict())


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
