#!/bin/bash

# Install CV plugin for Claude Desktop or Claude Code.
#
# Usage:
#   ./install.sh                       # remote install (default, curl-friendly)
#   ./install.sh desktop               # build MCPB + skill, show manual install steps
#   ./install.sh code                  # dev: local plugin + local MCP
#   ./install.sh code remote           # marketplace plugin (remote MCP built-in)
#
# Remote usage (curl):
#   curl -sSL https://raw.githubusercontent.com/francisco-perez-sorrosal/cv/mcp/install.sh | bash

set -euo pipefail

show_usage() {
    echo "Usage: $0 [desktop|code] [remote]"
    echo ""
    echo "  (no args)        Install Claude Code plugin from bit-agora marketplace"
    echo "  desktop          Build packages and show Claude Desktop install instructions"
    echo "  code             Install Claude Code plugin from local directory (dev mode)"
    echo "  code remote      Install Claude Code plugin from bit-agora marketplace"
    exit 1
}

# No arguments: remote install (curl-friendly)
if [ $# -eq 0 ]; then
    ADD_OUTPUT=$(claude plugin marketplace add francisco-perez-sorrosal/bit-agora 2>&1) || true
    if echo "$ADD_OUTPUT" | grep -q "already installed"; then
        echo "Marketplace already installed, updating..."
        claude plugin marketplace update bit-agora
    else
        echo "$ADD_OUTPUT"
    fi
    claude plugin install --scope user cv
    exit 0
fi

MODE="$1"

case "$MODE" in
    desktop)
        make install-claude-desktop
        ;;
    code)
        PLUGIN_SOURCE="${2:-dev}"
        if [ "$PLUGIN_SOURCE" != "dev" ] && [ "$PLUGIN_SOURCE" != "remote" ]; then
            echo "Error: second argument must be 'dev' or 'remote'"
            show_usage
        fi
        make install-claude-code PLUGIN_SOURCE="$PLUGIN_SOURCE"
        ;;
    *)
        echo "Error: first argument must be 'desktop' or 'code'"
        show_usage
        ;;
esac
