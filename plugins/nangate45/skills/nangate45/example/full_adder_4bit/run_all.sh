#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "${PROJECT_DIR}/script/run_tb.sh"
bash "${PROJECT_DIR}/script/run_synth.sh" "$@"
