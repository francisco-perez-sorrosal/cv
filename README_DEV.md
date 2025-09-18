# Francisco Perez-Sorrosal CV - Development Guide

This repository contains Francisco Perez-Sorrosal's CV in multiple formats and implementations.

## Repository Structure

### Main Branch - LaTeX CV

The main branch contains the authoritative LaTeX CV source.

#### Requirements (macOS)

- LaTeX distribution (MacTeX recommended)

MacTeX includes:

1. `pdflatex` a common compiler for converting LaTeX files into PDF
2. `latexmk` a Perl script that runs pdflatex plus other necessary tools like BibTeX or Biber

#### Installing MacTeX with Homebrew

```bash
brew install --cask mactex
```

Or download from https://tug.org/mactex/

#### CV Compilation

```bash
# Compile CV to PDF with latexmk (recommended) (-c cleans auxiliary files)
latexmk -pdf -c 2025_FranciscoPerezSorrosal_CV_English.tex

# or compile it with pdflatex
pdflatex 2025_FranciscoPerezSorrosal_CV_English.tex
```

### MCP Branch - Python MCP Server

The MCP branch contains a Python-based Model Context Protocol server implementation.

#### Development Setup

```bash
# Switch to MCP branch
git checkout mcp

# Install dependencies using pixi
pixi install

# Run the MCP server
pixi run cv-mcp-server
```

#### Available Pixi Commands

```bash
# Primary commands
pixi run cv-mcp-server    # Main MCP server command (project script)
pixi run mcps            # Direct Python module execution
pixi run start           # Alias for mcps

# Development tasks
pixi run test            # Run tests (if available)
pixi run lint            # Code linting (if available)
pixi run format          # Code formatting (if available)
pixi run build           # Build package (if available)
```

#### Transport Configuration

The server supports multiple transport protocols:

- **`stdio`** (default): Standard input/output for local development
- **`streamable-http`**: HTTP-based transport for web clients
- **`sse`**: ⚠️ **DEPRECATED** - No longer supported

Set transport via environment variable:
```bash
TRANSPORT=stdio pixi run cv-mcp-server              # Default
TRANSPORT=streamable-http pixi run cv-mcp-server    # Web/HTTP clients
```

#### Project Scripts

The `pyproject.toml` defines console script entry points:

```toml
[project.scripts]
cv-mcp-server = "cv_mcp_server.main:main"
```

This allows running the server via pixi after the package is installed in editable mode.

#### Dev Local Installation for Claude Desktop/Code (without DXT)

Add this to your Claude Desktop (`claude_desktop_config.json`) or Code MCP server configurations:

TODO: Check Locally with this config.

```json
{
  "fps_cv_mcp": {
    "command": "uv",
    "args": [
      "run",
      "--with", "mcp[cli]",
      "--with", "pymupdf4llm",
      "--with", "httpx",
      "--with", "mcpcat",
      "--with", "loguru",
      "mcp", "run",
      "src/cv_mcp_server/main.py",
      "--transport", "streamable-http"
    ]
  }
}
```

#### Remote Configuration for Claude Desktop/Code

For connecting to a remote MCP server:

```json
{
  "fps_cv_mcp": {
    "command": "npx",
    "args": ["mcp-remote", "http://localhost:10000/mcp"]
  }
}
```

Then check it exercising the MCP inspector with:

```sh
DANGEROUSLY_OMIT_AUTH=true  npx @modelcontextprotocol/inspector
```

And setting up the Transport Type to `Streamable HTTP` and the URL to `http://localhost:10000/mcp`. Then press the `Connect` button to connect the inspector to the server.

> **Note**: Update the host and port as needed for your deployment.

Currently I'm using `render.com` to host the MCP server. The configuration for Claude Desktop/Code is in the `config/claude.json` file. It will use `streamable-http` as transport protocol, deprecating finally `sse`.

There's a script to install the Claude Desktop or Code config files in the root directory:

```sh
install_claude_mcp.sh desktop
# or
install_claude_mcp.sh code
```

This will make the MCP server accessible at `https://fps-cv.onrender.com/mcp". You can check it also with the MCP inspector:

```sh
DANGEROUSLY_OMIT_AUTH=true  npx @modelcontextprotocol/inspector
```

And setting up the Transport Type to `Streamable HTTP` and the URL to `http://fps-cv.onrender.com/mcp"`. Then press the `Connect` button to connect the inspector to the server.

Render requires `requirements.txt` to be present in the root directory. You can generate it using:

```bash
uv pip compile pyproject.toml > requirements.txt
```

TODO: Develop an install process from a python package directly (a la DTX/MCP Bundles (MCPB))

Also requires `runtime.txt` to be present in the root directory with the Python version specified:

```txt
python-3.11.11
```

Remember also to set the environment variables in the render.com dashboard:

```bash
TRANSPORT=streamable-http
PORT=10000
```

#### Publish to Github's MCP Server Registry

**Install tool**

```sh
brew install mcp-publisher
```

**Create `server.json`**

```sh
# In the project dir
mcp-publisher init
```

The output is a json file `server.json` with content similar to this:

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-07-09/server.schema.json",
  "name": "io.github.francisco-perez-sorrosal/cv",
  "description": "An MCP server that provides Francisco Perez-Sorrosal's CV",
  "status": "active",
  "repository": {
    "url": "https://github.com/francisco-perez-sorrosal/cv",
    "source": "github"
  },
  "version": "0.0.1",
  "packages": [
    {
      "registry_type": "pypi",
      "registry_base_url": "https://pypi.org",
      "identifier": "cv-mcp-server",
      "version": "0.0.1",
      "transport": {
        "type": "stdio"
      },
      "environment_variables": [
        {
          "description": "Your API key for the service",
          "is_required": true,
          "format": "string",
          "is_secret": true,
          "name": "YOUR_API_KEY"
        }
      ]
    }
  ]
}
```

**Publish**

```sh
# Login to github
mcp-publisher login github  # for io.github.* or other method ([see doc](https://github.com/modelcontextprotocol/registry/blob/main/docs/guides/publishing/publish-server.md))
# Publish to github
mcp-publisher publish
```

## Development Workflow

### Working on LaTeX CV (Main Branch)

1. Make changes to `2025_FranciscoPerezSorrosal_CV_English.tex`
2. Test compilation: `latexmk -pdf -c 2025_FranciscoPerezSorrosal_CV_English.tex`
3. Commit changes to main branch

### Working on MCP Server (MCP Branch)

1. Switch to MCP branch: `git checkout mcp`
2. Make changes to Python code in `src/cv_mcp_server/`
3. Test locally: `pixi run cv-mcp-server`
4. Commit changes to MCP branch

### Branch Synchronization

The repository uses automated CI/CD workflows to keep branches synchronized. See [CI/CD Documentation](README_CICD.md) for details.

## Documentation
1. [User Guide](README_USER.md)
2. [CI/CD Documentation](README_CICD.md)
