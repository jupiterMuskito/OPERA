#!/usr/bin/env python3
"""Long-running OPERA-X pipeline scheduler for DDF server use."""

from __future__ import annotations

import argparse
import time
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from opera import pipelines  # noqa: E402


def due(last_attempt: object, interval: int) -> bool:
    try:
        parsed = datetime.fromisoformat(str(last_attempt))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).total_seconds() >= interval
    except (TypeError, ValueError):
        return True


def cycle() -> None:
    states = pipelines.load_state()
    for item in pipelines.load_configurations():
        if item.get("kind") != "live_excel" or not item.get("enabled"):
            continue
        pipelines.ensure_source_folder(item)
        if not due(states.get(item["id"], {}).get("last_attempt"), int(item["interval_seconds"])):
            continue
        targets = ",".join(pipelines.pipeline_targets(item)) or "row-routed"
        try:
            rows, flags = pipelines.sync_live_excel(item["id"])
            print(f"{datetime.now().isoformat(timespec='seconds')} {item['name']} -> {targets}: {rows} row(s), {flags} flag(s)", flush=True)
        except Exception as exc:
            # Continue so one bad source never stops the other pipelines.
            print(f"{datetime.now().isoformat(timespec='seconds')} {item['name']} -> {targets}: ERROR {exc}", file=sys.stderr, flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="Run one scheduler cycle and exit")
    args = parser.parse_args()
    while True:
        cycle()
        if args.once:
            return 0
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
