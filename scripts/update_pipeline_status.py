#!/usr/bin/env python3
"""Report an external OPERA-X connector run for the health dashboard."""

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
    parser.add_argument("--bu", required=True)
    parser.add_argument("--pipeline", required=True, choices=[row["id"] for row in pipelines.DEFAULT_PIPELINES])
    parser.add_argument("--status", required=True, choices=["success", "error"])
    parser.add_argument("--message", default="")
    args = parser.parse_args()
    pipelines.record_external_status(args.bu, args.pipeline, args.status == "success", args.message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
