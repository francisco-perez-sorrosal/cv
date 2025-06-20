# CV MCP Server with Anthropic Integration

A Python-based MCP (Model Context Protocol) server that serves a CV PDF as a resource and integrates with the Anthropic API for potential CV analysis tasks. This project follows the `src` layout for Python packaging.

# TL;DR Install for Claude Desktop Access to the CV

```bash
# 1.a) Install the mcp server access in Claude Desktop
./install_claude_desktop_mcp.sh

# 1.b) or manually integrate this JSON snippet to the `mcpServers` section of your `claude_desktop_config.json` (e.g. `~/Library/Application\ Support/Claude/claude_desktop_config.json`)

{
  "cv_francisco_perez_sorrosal": {
    "command": "npx",
    "args": ["mcp-remote", "http://localhost:10000/mcp"]
  }
}

# 2) Restart Claude and check that the 'Add from cv_francisco_perez_sorrosal` option is available in the mcp servers list

# 3) Query the CV served from the mcp server in Claude Desktop!

e.g. Give me a summary of Francisco Perez-Sorrosal's CV.
e.g. Give me a brief summary of Francisco Perez-Sorrosal's CV for a quick hiring screen.
e.g. Summarize Francisco Perez-Sorrosal's CV for an executive of a Google. Include citations.
e.g. Generate an exhaustive summary of Francisco's CV for a hiring manager highlighting his skills. Do not include citations.
```

## Features

- Serves your CV PDF (`2025_FranciscoPerezSorrosal_CV_English.pdf`) from the project root
- Endpoints for downloading and viewing the CV PDF directly in the browser
- Built with FastAPI for high performance and with Pixi for dependency management and task running
- Source code organized in the `src/` directory
- Includes configurations for:
  - Docker (optional, for containerization)
  - Linting (Ruff, Black, iSort)
  - Formatting
  - Type checking (MyPy)

## Prerequisites

- Python 3.11+
- [Pixi](https://pixi.sh/) (for dependency management and task execution)
- Docker (optional, for containerization)
- Your CV PDF named `2025_FranciscoPerezSorrosal_CV_English.pdf` in the project root directory

## Project Structure

```bash
.
├── .dockerignore
├── .gitignore
├── Dockerfile
├── pyproject.toml    # Python project metadata and dependencies (PEP 621)
├── README.md
├── src/
│   └── cv_mcp_server/
│       ├── __init__.py
│       └── main.py     # FastAPI application logic
├── tests/             # Test files (e.g., tests_main.py)
└── 2025_FranciscoPerezSorrosal_CV_English.pdf  # Your CV PDF
```

## Setup and Installation

1. **Clone the repository** (if applicable) or ensure you are in the project root directory.

2. **Place your CV**: Ensure your CV PDF is named `2025_FranciscoPerezSorrosal_CV_English.pdf` and is present in the project root directory.

3. **Install dependencies using Pixi**:

This command will create a virtual environment and install all necessary dependencies:

```bash
pixi install
```

This also runs the `install-editable` activation script, making your `src/cv_mcp_server` package importable in an editable way.

## Running the Server

Pixi tasks are defined in `pyproject.toml`:

### mcps (MCP Server)

```bash
pixi run mcps --transport stdio
```

### Development Mode (with auto-reload)

```bash
# Using pixi directly
pixi run mcps --transport stdio  # or sse, streamable-http

# Alternatively, using uv directly
uv run --with "mcp[cli]" mcp run src/cv_mcp_server/main.py --transport streamable-http

# Go to http://127.0.0.1:10000/mcp
```

The server will start at `http://localhost:10000`. It will automatically reload if you make changes to files in the `src/` directory.

### MCP Inspection Mode

```bash
# Using pixi
npx @modelcontextprotocol/inspector pixi run mcps --transport stdio

# Direct execution
npx @modelcontextprotocol/inspector pixi run python src/cv_mcp_server/main.py --transport streamable-http
```

This starts the inspector for the MCP Server.

## Development Tasks

### Run Tests

```bash
pixi run test
```

### Lint and Check Formatting

```bash
pixi run lint
```

### Apply Formatting and Fix Lint Issues

```bash
pixi run format
```

### Build the Package

Creates sdist and wheel in `dist/`:

```bash
pixi run build
```

## Docker Support (Optional)

### Build the Docker Image

```bash
docker build -t cv-mcp-server .
```

### Run the Docker Container

TODO: Rewrite this if necessary. Docker support not yet done.

To run with your Anthropic API key and local CV PDF:

```bash
docker run -d -p 8000:8000 \
  -e ANTHROPIC_API_KEY="your_anthropic_api_key_here" \
  -v "$(pwd)/2025_FranciscoPerezSorrosal_CV_English.pdf:/app/2025_FranciscoPerezSorrosal_CV_English.pdf:ro" \
  cv-mcp-server
```

The server will be available at `http://localhost:8000`.

## MCP Server Configuration

### Local Configuration for Claude Desktop

```json
{
  "cv_francisco_perez_sorrosal": {
    "command": "uv",
    "args": [
      "run",
      "--with", "mcp[cli]",
      "--with", "pymupdf4llm",
      "mcp", "run",
      "src/cv_mcp_server/main.py",
      "--transport", "streamable-http"
    ]
  }
}
```

### Remote Configuration for Claude Desktop

For connecting to a remote MCP server:

```json
{
  "cv_francisco_perez_sorrosal": {
    "command": "npx",
    "args": ["mcp-remote", "http://localhost:10000/mcp"]
  }
}
```

> **Note**: Update the host and port as needed for your deployment.

Currently I'm using `render.com` to host the MCP server. The configuration is in the `config/claude.json` file.

Render requires `requirements.txt` to be present in the root directory. You can generate it using:

```bash
uv pip compile pyproject.toml > requirements.txt
```

Also requires `runtime.txt` to be present in the root directory with the Python version specified:

```txt
python-3.11.11
```

Remember also to set the environment variables in the render.com dashboard:

```bash
TRANSPORT=sse
PORT=10000
```

Then you can query in Claude Desktop using the `cv_francisco_perez_sorrosal` MCP server to get info:

```text
Give me an overview of the cv of Francisco Perez-Sorrosal hightlighting the most relevant skills.
```

## License

This project is licensed under the MIT License. See `pyproject.toml` (See `LICENSE` file) for details.
