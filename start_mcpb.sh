#!/bin/bash

# Startup script for CV MCP Server MCPB bundle
# This script runs the MCP server directly from the source

set -e

BUNDLE_DIR="$(dirname "$0")"
cd "$BUNDLE_DIR"

echo "[INFO] Starting CV MCP Server..." >&2

# Set PYTHONPATH to include lib directory for dependencies
export PYTHONPATH="${BUNDLE_DIR}/lib:${BUNDLE_DIR}/src:${BUNDLE_DIR}"

# Run the MCP server directly
exec python3 src/cv_mcp_server/main.py
