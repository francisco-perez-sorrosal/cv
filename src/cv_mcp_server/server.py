"""Shared MCP server instance and data store — imported by tool modules."""

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from cv_mcp_server.store import ResumeStore


# Configure transport and statelessness
trspt = "stdio"
stateless_http = False
match os.environ.get("TRANSPORT", trspt):
    case "stdio":
        trspt = "stdio"
        stateless_http = False
    case "sse":
        raise ValueError("SSE transport is deprecated! Use streamable-http instead.")
    case "streamable-http":
        trspt = "streamable-http"
        stateless_http = True
    case _:
        trspt = "stdio"
        stateless_http = False


def find_project_root():
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / 'pyproject.toml').exists():
            return current
        current = current.parent
    return current


PROJECT_ROOT = find_project_root()
DATA_DIR = Path(__file__).parent / "data"
CV_PATH = PROJECT_ROOT / "2025_FranciscoPerezSorrosal_CV_English.pdf"

# Eager initialization: load structured data at import time
store = ResumeStore.load(DATA_DIR)

# Initialize FastMCP server
host = os.environ.get("HOST", "0.0.0.0")
port = int(os.environ.get("PORT", 10000))
mcp = FastMCP("cv_francisco_perez_sorrosal", stateless_http=stateless_http, host=host, port=port)
