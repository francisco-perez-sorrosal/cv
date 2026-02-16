#!/bin/bash

# Install CV plugin for Claude Desktop or Claude Code.
#
# Usage:
#   ./install.sh                       # remote install (default, curl-friendly)
#   ./install.sh desktop               # local: build MCPB + skills, show manual install steps
#   ./install.sh desktop remote        # remote: build skills + inject MCP config into Claude Desktop
#   ./install.sh code                  # local: local plugin + local MCP (dev mode)
#   ./install.sh code remote           # remote: marketplace plugin (remote MCP built-in)
#
# Remote usage (curl):
#   curl -sSL https://raw.githubusercontent.com/francisco-perez-sorrosal/cv/mcp/install.sh | bash

set -euo pipefail

show_usage() {
    echo "Usage: $0 [desktop|code] [local|remote]"
    echo ""
    echo "  (no args)          Install Claude Code plugin from bit-agora marketplace"
    echo "  desktop             Build MCPB + skills, show Claude Desktop install instructions"
    echo "  desktop remote      Build skills + inject remote MCP config into Claude Desktop"
    echo "  code                Install Claude Code plugin with local MCP (dev mode)"
    echo "  code remote         Install Claude Code plugin from bit-agora marketplace"
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
MCP_TARGET="${2:-local}"

case "$MODE" in
    desktop)
        if [ "$MCP_TARGET" != "local" ] && [ "$MCP_TARGET" != "remote" ]; then
            echo "Error: second argument must be 'local' or 'remote'"
            show_usage
        fi
        make install-claude-desktop MCP_TARGET="$MCP_TARGET"
        ;;
    code)
        if [ "$MCP_TARGET" != "local" ] && [ "$MCP_TARGET" != "remote" ]; then
            echo "Error: second argument must be 'local' or 'remote'"
            show_usage
        fi
        make install-claude-code MCP_TARGET="$MCP_TARGET"
        ;;
    *)
        echo "Error: first argument must be 'desktop' or 'code'"
        show_usage
        ;;
esac
