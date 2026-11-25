#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${HOME}/opera_logs"
PID_FILE="${LOG_DIR}/pipeline_scheduler.pid"
mkdir -p "${LOG_DIR}" "${HOME}/opera_inbox/live_excel"
if [[ -f "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
  echo "OPERA-X pipeline scheduler is already running (PID $(cat "${PID_FILE}"))."
  exit 0
fi
PYTHON="${ROOT}/.venv/bin/python"
[[ -x "${PYTHON}" ]] || PYTHON="$(command -v python3)"
export OPERA_DATA_DIR="${OPERA_DATA_DIR:-${HOME}/opera_data}"
nohup "${PYTHON}" -u "${ROOT}/scripts/pipeline_scheduler.py" >>"${LOG_DIR}/pipeline_scheduler.log" 2>&1 &
echo $! >"${PID_FILE}"
echo "Started OPERA-X pipeline scheduler (PID $(cat "${PID_FILE}"))."
echo "Log: ${LOG_DIR}/pipeline_scheduler.log"
