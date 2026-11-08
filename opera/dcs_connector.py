from __future__ import annotations

from typing import Any

import pandas as pd
import requests

from . import storage


def pull_json(url: str, token: str = "", timeout: int = 30) -> pd.DataFrame:
    headers: dict[str, Any] = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("data", payload) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("DCS endpoint must return a JSON array or {'data': [...]}.")
    return pd.DataFrame(rows)


def ingest(bu: str, url: str, token: str, user: str) -> tuple[int, int]:
    frame = pull_json(url, token)
    clean, issues, flags = storage.validate_rows(bu, "DCS", frame)
    if not issues.empty:
        raise ValueError("DCS payload failed validation: " + "; ".join(issues["message"].head(5)))
    return storage.save_validated_input(bu, "DCS", clean, user)
