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

./install.sh                     # remote install from bit-agora marketplace (curl-friendly)
./install.sh desktop             # build packages + Claude Desktop install instructions
./install.sh code                # dev: local plugin + local MCP
./install.sh code remote         # marketplace plugin (remote MCP built-in)
```

### Claude Code Plugin
```bash
make install-claude-code                        # dev (default): local plugin + local MCP override
make install-claude-code PLUGIN_SOURCE=remote   # marketplace plugin (remote MCP built-in)
```

### MCPB Bundle Build
```bash
make build-mcpb    # full bundle: deps -> lib/ -> .mcpb package
make build-wheel   # Python wheel only
make clean         # remove dist/, lib/
```

Individual pixi tasks:
```bash
pixi run -e dev update-mcpb-deps   # sync and export requirements.txt
pixi run -e dev mcp-bundle         # install deps to lib/
pixi run pack                      # create .mcpb bundle in dist/mcpb/
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
.claude-plugin/
  plugin.json             # Claude Code plugin manifest (skills, remote MCP config)
  mcp-local.json          # MCP override: stdio via pixi (dev mode)
commands/
  create-mcpb.md          # MCPB bundle build guidance
  get-job-desc.md         # LinkedIn job description fetcher
skills/
  cv-analyst/
    SKILL.md              # Agent Skill: CV summarization for different audiences
    references/
      summary-presets.md  # Pre-configured profiles (hiring screen, exec briefings)
config/
  claude.json             # Claude Desktop/Code MCP configuration
scripts/
  release.sh              # Release automation
dist/
  mcpb/                   # Built .mcpb bundles (fps-cv-mcp-*.mcpb)
  wheel/                  # Built Python wheels
  skill/                  # Packaged skills (cv-analyst.zip)
lib/                      # Vendored dependencies for MCPB bundles
.github/
  README.md -> ../README_USER.md   # Symlink for GitHub display
  workflows/              # CI/CD (rebase, auth check, mcpb creation, release, code review, CV improver)
manifest.json             # MCPB manifest (name: fps-cv-mcp)
server.json               # MCP server registry entry
pyproject.toml            # Project config (pixi + hatch build system)
Makefile                  # Build orchestration for MCPB bundles
start_mcpb.sh             # MCPB startup script
install.sh                # Marketplace plugin installer (curl-friendly)
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

Prompt-wrapping tool (fallback for non-skill clients):
- `summarize_cv` - Configurable CV summary (depth, context, emphasis, audience, tone, format, length). Preset scenarios (hiring screen, exec briefings) are handled by the `cv-analyst` skill.

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
- The `cv-analyst` skill in `skills/` handles CV summarization for skill-compatible clients; `summarize_cv` tool serves as fallback for other clients

## Plugins

When the `i-am` plugin is installed, use its agents, skills, rules, and hooks for all applicable work (planning, research, implementation, verification, code review, memory, etc.).

## Important Notes

- The CV contains real professional information - handle appropriately
- GitHub display README is `README_USER.md` (symlinked from `.github/README.md`)
- MCP server includes usage tracking via mcpcat
- CI/CD workflows handle auto-rebasing, MCPB creation checks, releases, and Claude-powered code review
