#!/usr/bin/env bash
set -euo pipefail
PID_FILE="${HOME}/opera_logs/pipeline_scheduler.pid"
if [[ ! -f "${PID_FILE}" ]]; then
  echo "No OPERA-X pipeline scheduler PID file was found."
  exit 0
fi
PID="$(cat "${PID_FILE}")"
if kill -0 "${PID}" 2>/dev/null; then
  kill "${PID}"
  for _ in {1..20}; do
    kill -0 "${PID}" 2>/dev/null || break
    sleep 0.25
  done
fi
rm -f "${PID_FILE}"
echo "Stopped OPERA-X pipeline scheduler."
