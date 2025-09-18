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

# MCPB (MCP Bundle) tasks
pixi run python-bundle   # Build Python wheel package to python-dist/
pixi run update-mcpb-deps # Update dependencies and export requirements.txt
pixi run mcp-bundle      # Install dependencies to lib/ directory
pixi run pack            # Package bundle into .mcpb file
pixi run clean-bundles   # Remove temporary files and bundles

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

#### Create MCPB package

The project supports creating MCP Bundle (MCPB) packages for easy distribution and installation. MCPB is the standard format for distributing MCP servers as portable, installable bundles.

##### Prerequisites

Ensure you have all required files in the project root:
- `manifest.json` - MCPB manifest (already created)
- `requirements.txt` - Python dependencies (generate if missing)
- `runtime.txt` - Python version specification (generate if missing)
- `2025_FranciscoPerezSorrosal_CV_English.pdf` - CV PDF (optional, will use remote if missing)

```bash
# Generate requirements.txt if missing
uv pip compile pyproject.toml > requirements.txt

# Create runtime.txt if missing
echo "python-3.11.11" > runtime.txt
```

##### Build MCPB Bundle

Install the CLI:

```sh
npm install -g @anthropic-ai/mcpb
```

**Important**: The MCPB bundle dependencies are built using the system Python to ensure compatibility with Claude Desktop. The build process automatically uses the appropriate Python version to match the target deployment environment.

Use the pixi tasks to create the MCPB bundle:

```bash
# Update dependencies and export requirements.txt
pixi run update-mcpb-deps

# Install dependencies to lib/ directory (uses Python 3.13)
pixi run mcp-bundle

# Package into .mcpb file
pixi run pack

# Clean up temporary files (optional)
pixi run clean-bundles
```

Or use the Makefile for convenience:
```bash
make build-wheel     # Build Python wheel package
make build-mcpb      # Runs: pixi install && pixi run update-mcpb-deps && pixi run mcp-bundle && pixi run pack
make clean           # Removes generated .mcpb files, python-dist/, and lib/ directories
```

This creates `fps-cv-mcp-0.0.1.mcpb` ready for distribution.

##### Bundle Contents

The MCPB bundle includes:
- `src/` - Python source code
- `lib/` - Bundled Python dependencies (built for target Python version)
- `start_mcpb.sh` - Startup script with proper PYTHONPATH configuration
- `manifest.json` - Bundle metadata and configuration
- `requirements.txt` - Python dependencies list
- `2025_FranciscoPerezSorrosal_CV_English.pdf` - CV PDF (if available)

##### Installation and Usage

Users can install the bundle using MCPB tooling (no additional prerequisites required - all dependencies are bundled):

```bash
# Install MCPB CLI tool
npm install -g @anthropic-ai/mcpb

# Install the bundle
mcpb install fps-cv-mcp-0.0.1.mcpb

# Or for development/testing
mcpb install --dev fps-cv-mcp-0.0.1.mcpb
```

##### Testing the Bundle

Before distribution, test the bundle locally:

```bash
# Extract and test bundle
unzip fps-cv-mcp-0.0.1.mcpb -d test-bundle/
cd test-bundle/

# Test server startup using the startup script
./start_mcpb.sh

# Test with MCP inspector
DANGEROUSLY_OMIT_AUTH=true npx @modelcontextprotocol/inspector
```

##### Available MCPB Tasks

```bash
pixi run python-bundle    # Build Python wheel package to python-dist/
pixi run update-mcpb-deps # Update dependencies and export requirements.txt
pixi run mcp-bundle       # Install dependencies to lib/ directory (uses Python 3.13)
pixi run pack             # Package bundle into .mcpb file
pixi run clean-bundles    # Remove temporary files and bundles
```

#### Automated Releases

The project includes GitHub Actions workflows for automated MCPB bundle releases.

##### Creating a Release

Use the release script for easy version management:

```bash
# Create a new release (updates versions and creates git tag)
./scripts/release.sh 0.0.1

# This will:
# 1. Update manifest.json and pyproject.toml versions
# 2. Commit the changes
# 3. Create and push a git tag (v0.0.1)
# 4. Trigger GitHub Actions to build and release the MCPB bundle
```

##### Manual Release Process

If you prefer manual control:

```bash
# 1. Update versions in manifest.json and pyproject.toml
# 2. Commit changes
git add manifest.json pyproject.toml
git commit -m "chore: bump version to 0.0.1"

# 3. Create and push tag
git tag -a v0.0.1 -m "Release version 0.0.1"
git push origin mcp
git push origin v0.0.1
```

##### GitHub Workflows

- **`release-mcpb.yml`**: Builds and releases MCPB bundle when tags are pushed
- **`check-mcpb-creation.yml`**: Tests MCPB bundle build on pull requests and pushes

The release workflow automatically:
- Builds dependencies with Python 3.13 for Claude Desktop compatibility
- Creates versioned MCPB bundle (`fps-cv-mcp-{version}.mcpb`)
- Publishes GitHub release with bundle attached
- Provides detailed release notes and installation instructions

#### Publish to Github's MCP Server Registry

Install tool
```sh
brew install mcp-publisher


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
