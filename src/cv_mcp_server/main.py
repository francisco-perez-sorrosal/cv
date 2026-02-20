"""Entry point for the CV MCP server — autodiscovery wires tools and resources."""

import sys
from typing import Literal, cast

from loguru import logger
from cv_mcp_server.server import mcp, trspt, host, port, stateless_http


def _register_modules():
    """Import tool/resource modules to activate @mcp.tool and @mcp.resource decorators.

    Tools are discovered automatically from the tools/ subpackage.
    New tool modules are picked up without editing this file.
    """
    import importlib
    import pkgutil
    import cv_mcp_server.tools

    for _, name, _ in pkgutil.iter_modules(cv_mcp_server.tools.__path__):
        importlib.import_module(f"cv_mcp_server.tools.{name}")
    importlib.import_module("cv_mcp_server.resources")


_register_modules()


def main():
    """Initialize and run the server with the specified transport."""
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Starting CV MCP server with {trspt} transport ({host}:{port}) and stateless_http={stateless_http}...")
    transport_as_literal = cast(Literal['stdio', 'streamable-http'], trspt)
    mcp.run(transport=transport_as_literal)


if __name__ == "__main__":
    main()
