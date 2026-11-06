#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/../../../scripts/rtl_flow.py" --project "${SCRIPT_DIR}/.." tb "$@"
