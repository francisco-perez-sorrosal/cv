#!/bin/bash
# Startup script for the CV MCP Server bundle.
#
# Why this script exists:
#   Claude Desktop is a macOS GUI app launched by launchd, which gives it a
#   sanitized PATH (typically "/usr/bin:/bin:/usr/sbin:/sbin"). Homebrew lives
#   in /opt/homebrew/bin (Apple Silicon) or /usr/local/bin (Intel) — NEITHER
#   is visible to Claude Desktop. So a bare `python3` in manifest.json
#   resolves to /usr/bin/python3 = Apple's Python 3.9.6, which is too old
#   (this project requires >=3.13).
#
# What this script does:
#   1. Augments PATH with common Python install locations.
#   2. Reads the Python (major.minor) version that lib/ was built against
#      from `lib/.python-version`. The native .so files (pydantic_core,
#      pyyaml, …) are ABI-locked to that exact minor version.
#   3. Locates the matching `python3.X` interpreter on the host machine.
#   4. Execs it on src/cv_mcp_server/main.py with the right PYTHONPATH.
#
# This keeps the bundle portable across machines (no hardcoded path) while
# guaranteeing ABI compatibility between the bundled binaries and the
# interpreter that loads them.

set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BUNDLE_DIR"

# 1. Augment PATH with the usual suspects (deduped via realpath when present)
export PATH="/opt/homebrew/bin:/usr/local/bin:/opt/local/bin:$HOME/.local/bin:$HOME/.pyenv/shims:${PATH:-/usr/bin:/bin}"

# 2. Read the Python (major.minor) version recorded at build time
PYVER_FILE="${BUNDLE_DIR}/lib/.python-version"
if [[ ! -f "$PYVER_FILE" ]]; then
    echo "[ERROR] Missing ${PYVER_FILE}; the bundle is malformed." >&2
    exit 1
fi
PYVER="$(tr -d '[:space:]' < "$PYVER_FILE")"

# 3. Locate a matching python3.X interpreter
PYTHON_BIN=""
for candidate in \
    "python${PYVER}" \
    "/opt/homebrew/bin/python${PYVER}" \
    "/usr/local/bin/python${PYVER}" \
    "/opt/local/bin/python${PYVER}"; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON_BIN="$(command -v "$candidate")"
        break
    fi
done

if [[ -z "$PYTHON_BIN" ]]; then
    echo "[ERROR] python${PYVER} not found on this machine." >&2
    echo "        Install with: brew install python@${PYVER}" >&2
    echo "        Searched PATH and /opt/homebrew, /usr/local, /opt/local." >&2
    exit 1
fi

echo "[INFO] CV MCP Server: using ${PYTHON_BIN}" >&2

# 4. Launch the server
export PYTHONPATH="${BUNDLE_DIR}/lib:${BUNDLE_DIR}/src:${BUNDLE_DIR}"
exec "$PYTHON_BIN" src/cv_mcp_server/main.py
