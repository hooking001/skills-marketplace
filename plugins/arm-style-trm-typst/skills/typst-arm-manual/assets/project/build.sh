#!/usr/bin/env bash
# Run this script from any working directory. Optional argument: project-relative entrypoint.
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENTRY="${1:-main.typ}"
OUTPUT="${2:-build/manual.pdf}"
cd "${PROJECT_DIR}"
mkdir -p "$(dirname "${OUTPUT}")"
typst compile --root "${PROJECT_DIR}" --font-path "${PROJECT_DIR}/fonts/Pretendard" "${ENTRY}" "${OUTPUT}"
