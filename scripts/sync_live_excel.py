#!/usr/bin/env python3
"""Sync configured OPERA-X Live Excel sources into Digital Data CSV files.

Designed for cron/systemd execution.  The module-level configuration determines
whether a pipeline is enabled and which source path to read.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from opera import pipelines  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pipeline", default="live_excel_1", choices=["live_excel_1", "live_excel_2", "live_excel_3"])
    args = parser.parse_args()
    try:
        rows, flags = pipelines.sync_live_excel(args.pipeline)
        print(f"{args.pipeline}: synced {rows} new row(s); {flags} flag(s)")
        return 0
    except Exception as exc:
        print(f"{args.pipeline}: sync failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
