# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Francisco Perez-Sorrosal's CV repository. Two branches serve different purposes:

- **`main`**: LaTeX source CV (`2025_FranciscoPerezSorrosal_CV_English.tex`) and generated PDF
- **`mcp`**: Python MCP server (v0.0.3) that serves the CV as a resource for AI systems, packaged as an MCPB bundle

## Common Commands

### LaTeX CV Management (main branch)
```bash
pdflatex 2025_FranciscoPerezSorrosal_CV_English.tex
latexmk -pdf 2025_FranciscoPerezSorrosal_CV_English.tex   # recommended
latexmk -c 2025_FranciscoPerezSorrosal_CV_English.tex     # clean aux files
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

### Main Branch
- `2025_FranciscoPerezSorrosal_CV_English.tex` - LaTeX source (moderncv, classic green theme)
- `2025_FranciscoPerezSorrosal_CV_English.pdf` - Generated PDF

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

### Agent Skill: `cv-analyst`

The `skills/cv-analyst/` skill ([Agent Skills open format](https://agentskills.io)) provides CV summarization for any skill-compatible client (Claude Code, Claude Desktop, Cursor, Gemini CLI, VS Code, and others). It composes with the MCP data tools to fetch CV content and applies structured summarization instructions.

The skill is the preferred mechanism for CV summarization. The `summarize_cv` tool remains as a fallback for clients that do not support skills.

### Deployment
- **render.com**: env vars `TRANSPORT`, `PORT`, `HOST`
- **Wasmer**: MCPB bundle at `https://fps-cv.wasmer.app/mcp` (see `.mcp.json`)
- **MCPB Registry**: Published via `server.json` with SHA256 verification
- **Claude Code Plugin**: `.claude-plugin/` with local/remote MCP templates, skill auto-discovery via `plugin.json` (plugin name: `cv`)
- **Local**: stdio transport via `pixi run mcps` or `start_mcpb.sh`
- Remote access via `npx mcp-remote` (configured in `.mcp.json`)

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

Prefer delegating to specialized agents (researcher, context-engineer, implementer, etc.) over doing multi-step work directly.

## Important Notes

- The CV contains real professional information - handle appropriately
- GitHub display README is `README_USER.md` (symlinked from `.github/README.md`)
- MCP server includes usage tracking via mcpcat
- CI/CD workflows handle auto-rebasing, MCPB creation checks, releases, and Claude-powered code review
