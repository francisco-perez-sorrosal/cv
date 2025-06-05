"""Main module for the CV MCP server with Anthropic integration."""

import os

from pathlib import Path
# from argparse import ArgumentParser, Namespace

import pymupdf4llm
from mcp.server.fastmcp import FastMCP


# Configure transport and statelessness
match os.environ.get("TRANSPORT", "stdio"):
    case "stdio":
        transport = "stdio"
        stateless_http = False
    case "sse":
        transport = "sse"
        stateless_http = False
    case "streamable-http":
        transport = "streamable-http"
        stateless_http = True
    case _:
        transport = "stdio"
        stateless_http = False


def find_project_root():
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / 'pyproject.toml').exists():
            return current
        current = current.parent
    return current

PROJECT_ROOT = find_project_root()

# Initialize FastMCP server
port = int(os.environ.get("PORT", 10000))
mcp = FastMCP("cv_francisco_perez_sorrosal", stateless_http=stateless_http, port=port)

@mcp.tool()
def get_cv() -> str:
    return cv()

@mcp.resource("cvfps://full")
def cv() -> str:
    """
    Return the full CV of Francisco Perez Sorrosal as a markdown file.
    """
    content = "There's no CV found!"
    if os.path.exists(PROJECT_ROOT):
        cv_path = os.path.join(PROJECT_ROOT, "2025_FranciscoPerezSorrosal_CV_English.pdf")
        content: str = pymupdf4llm.to_markdown(cv_path)
    return content


# TODO CLI Args not supported by MCP yet
# def parse_cli_arguments() -> Namespace:
#     """Parse command line arguments."""
#     parser: ArgumentParser = ArgumentParser(description='CV MCP Server')
#     parser.add_argument('--transport', 
#                       type=str, 
#                       default='stdio',
#                       choices=['stdio', 'sse', "streamable-http"],
#                       help='Transport type for the MCP server (default: stdio)')
#     return parser.parse_args()


if __name__ == "__main__":
    # args: Namespace = parse_cli_arguments()
    
    # Initialize and run the server with the specified transport
    print(f"Starting CV MCP server with {transport} transport (port={port}) and stateless_http={stateless_http}...")
    mcp.run(transport=transport) #, mount_path="/cv")
