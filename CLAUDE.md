# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Francisco Perez-Sorrosal's CV repository. Two branches serve different purposes:

- **Main branch (`main`)**: Contains the LaTeX source CV (`FranciscoPerezSorrosal_CV_English.tex`) and generated PDF
- **MCP branch (`mcp`)**: Contains a Python-based MCP (Model Context Protocol) server that serves the CV as a resource for AI systems

The repository serves as both a personal CV management system and a reference implementation of an MCP server for document serving.

## Common Commands

### LaTeX CV Management (main branch)
```bash
# Compile the CV to PDF using pdflatex
pdflatex FranciscoPerezSorrosal_CV_English.tex

# Or using latexmk (recommended for handling dependencies)
latexmk -pdf FranciscoPerezSorrosal_CV_English.tex

# Clean auxiliary files
latexmk -c FranciscoPerezSorrosal_CV_English.tex
```

### MCP Server Development (mcp branch)
```bash
pixi install                                # install dependencies
pixi run mcps --transport stdio             # run locally (stdio)
pixi run mcps --transport sse               # run locally (SSE)
pixi run mcps --transport streamable-http   # run locally (streamable HTTP)

./install_claude_mcp.sh desktop             # install for Claude Desktop
./install_claude_mcp.sh code [project_path] # install for Claude Code
```

### MCPB Bundle Build
```bash
make build-mcpb    # full bundle: deps -> lib/ -> .mcpb package
make build-wheel   # Python wheel only
make clean         # remove python-dist/, mcpb-package/, lib/
```

Individual pixi tasks:
```bash
pixi run -e dev update-mcpb-deps   # sync and export requirements.txt
pixi run -e dev mcp-bundle         # install deps to lib/
pixi run pack                      # create .mcpb bundle in mcpb-package/
```

### Release
```bash
./scripts/release.sh               # release process (see RELEASE_PROCESS.md)
```

## Architecture and Structure

### Main Branch Structure
- `FranciscoPerezSorrosal_CV_English.tex` - LaTeX source file containing the complete CV
- `FranciscoPerezSorrosal_CV_English.pdf` - Generated PDF output
- `.gitignore` - Ignores LaTeX auxiliary files and common editor artifacts

### MCP Branch (Python Project, v0.0.3)
```
src/cv_mcp_server/
  __init__.py
  main.py                 # MCP server implementation (mcp library + pymupdf4llm)
  utils.py                # Utility functions
  prompts/
    summary.yaml          # Configurable CV summary prompt
skills/
  cv-analyst/
    SKILL.md              # Agent Skill: CV summarization for different audiences
    references/
      summary-presets.md  # Pre-configured profiles (hiring screen, exec briefings)
config/
  claude.json             # Claude Desktop/Code MCP configuration
scripts/
  release.sh              # Release automation
mcpb-package/             # Built .mcpb bundles (fps-cv-mcp-*.mcpb)
python-dist/              # Built Python wheels
lib/                      # Vendored dependencies for MCPB bundles
.github/
  README.md -> ../README_USER.md   # Symlink for GitHub display
  workflows/              # CI/CD (rebase, auth check, mcpb creation, release, code review, CV improver)
manifest.json             # MCPB manifest (name: fps-cv-mcp)
server.json               # MCP server registry entry
pyproject.toml            # Project config (pixi + hatch build system)
Makefile                  # Build orchestration for MCPB bundles
Dockerfile                # Container deployment (render.com)
start_mcpb.sh             # MCPB startup script
install_claude_mcp.sh     # Installer for Claude Desktop/Code
README_USER.md            # Main README (displayed on GitHub via symlink)
README_DEV.md             # Developer documentation
README_CICD.md            # CI/CD documentation
RELEASE_PROCESS.md        # Release workflow documentation
```

### MCP Server Tools

Data tools (fetch CV content):
- `get_cv` - Full CV in markdown format (via pymupdf4llm)
- `get_cv_pdf_link` - Direct PDF link
- `get_google_scholar_link` - Google Scholar profile

Prompt-wrapping tools (legacy, kept for non-skill clients):
- `summarize_cv` - Configurable CV summary (depth, context, audience, tone, format)
- `summarize_cv_for_quick_hiring_screen` - Brief hiring screen summary
- `summarize_cv_for_executive_briefing_for_startup` - Startup executive briefing
- `summarize_cv_for_executive_briefing_for_big_company` - Big company executive briefing

#### LaTeX CV (`FranciscoPerezSorrosal_CV_English.tex`)
- Uses `moderncv` document class with classic green theme
- Structured sections: Profile, Experience, Patents, Education, Skills, Languages
- Extensive professional experience spanning academic research and industry R&D
- Focus on AI/ML, distributed systems, and scalable architectures

#### MCP Server (`src/cv_mcp_server/main.py`)
- FastAPI-based server using the `mcp` library
- Serves CV as markdown via `pymupdf4llm` for AI consumption
- Provides tools for CV analysis and summarization
- Supports multiple transport protocols (stdio, sse, streamable-http)
- Includes comprehensive prompts for different use cases (hiring screens, executive briefings)

## Development Guidelines

### When Working with LaTeX (main branch)
- You are an expert editor in LaTeX format, with a background of computer science, research, and software engineering
- The CV is the authoritative source of professional information
- Auxiliary files (.aux, .log, .out, etc.) are gitignored
- `moderncv` package docs: `.claude/docs/moderncv_userguide.txt` - read before editing
- Maintain chronological order in experience sections, with recent years first

### When Working with MCP Server (mcp branch)
- Python >=3.13, `src/` layout, hatch build system
- pixi for dependency management and task execution
- MCP resources use custom URI scheme `fps-cv://`
- Server supports stdio, SSE, and streamable-http transports
- MCPB bundles vendor dependencies in `lib/` directory
- `manifest.json` defines the MCPB package metadata and tool declarations
- The `cv-analyst` skill in `skills/` handles CV summarization for skill-compatible clients; MCP prompt-wrapping tools serve as fallback for other clients

## Important Notes

- The CV contains real professional information - handle appropriately
- GitHub display README is `README_USER.md` (symlinked from `.github/README.md`)
- MCP server includes usage tracking via mcpcat
- CI/CD workflows handle auto-rebasing, MCPB creation checks, releases, and Claude-powered code review
