# CV MCP Server with Anthropic Integration

A Python-based MCP (Model Context Protocol) server that serves a CV PDF as a resource and integrates with the Anthropic API for potential CV analysis tasks. This project follows the `src` layout for Python packaging.

## Features

- Serves your CV PDF (`2025_FranciscoPerezSorrosal_CV_English.pdf`) from the project root
- Endpoints for downloading and viewing the CV PDF directly in the browser
- Basic integration with the Anthropic API (requires `ANTHROPIC_API_KEY`)
- Placeholder endpoint (`/cv/analyze`) to demonstrate interaction with Anthropic API using CV content
- Built with FastAPI for high performance
- Uses Pixi for dependency management and task running
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
- Your CV PDF named `2025_FranciscoPerezSorrosal_CV_English.pdf` in the project root directory (`/Users/fperez/dev/cv/`)
- An Anthropic API Key (set as the `ANTHROPIC_API_KEY` environment variable) for using Anthropic-related features

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
```

The server will start at `http://localhost:8000`. It will automatically reload if you make changes to files in the `src/` directory.

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

To run with your Anthropic API key and local CV PDF:

```bash
docker run -d -p 8000:8000 \
  -e ANTHROPIC_API_KEY="your_anthropic_api_key_here" \
  -v "$(pwd)/2025_FranciscoPerezSorrosal_CV_English.pdf:/app/2025_FranciscoPerezSorrosal_CV_English.pdf:ro" \
  cv-mcp-server
```

The server will be available at `http://localhost:8000`.

## PDF Text Extraction (Future Enhancement)

The `/cv/analyze` endpoint currently uses simulated CV content. To make it fully functional, you would need to:

1. Add a PDF parsing library (e.g., `PyPDF2`, `pdfplumber`, or `pymupdf`) to `pyproject.toml` and `pixi.toml`
2. Implement the text extraction logic in `src/cv_mcp_server/main.py` within the `/cv/analyze` endpoint

## License

This project is licensed under the MIT License. See `pyproject.toml` (or create a `LICENSE` file) for details.

## MCP Server Configuration

### Local Configuration

Save this as `mcp.config.json` in your project root:

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

### Remote Configuration

For connecting to a remote MCP server:

```json
{
  "cv_francisco_perez_sorrosal": {
    "command": "npx",
    "args": ["mcp-remote", "http://localhost:8000/mcp"]
  }
}
```

> **Note**: Update the host and port as needed for your deployment.
