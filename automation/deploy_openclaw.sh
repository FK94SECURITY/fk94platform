#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
AUTOMATION_DIR="${PROJECT_DIR}/automation"

echo "[1/4] Running preflight checks..."
cd "${AUTOMATION_DIR}"
python3 preflight.py

echo "[2/4] Installing automation dependencies..."
python3 -m pip install -r requirements.txt

echo "[3/4] Running one-shot OpenClaw runner..."
python3 openclaw_runner.py --once

echo "[4/4] Done. If output was OK, enable cron:"
echo "crontab ${AUTOMATION_DIR}/crontab.txt"
