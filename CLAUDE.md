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
pixi run mcps --transport streamable-http   # run locally (streamable HTTP)

./install.sh                     # remote install from bit-agora marketplace (curl-friendly)
./install.sh desktop             # local: build MCPB + skill, show install instructions
./install.sh desktop remote      # remote: build skill + inject MCP config into Claude Desktop
./install.sh code                # local: local plugin + local MCP (dev mode)
./install.sh code remote         # remote: marketplace plugin (remote MCP built-in)
```

### Claude Code Plugin
```bash
make install-claude-code                       # local (default): local plugin + local MCP override
make install-claude-code MCP_TARGET=remote     # marketplace plugin (remote MCP built-in)
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

### MCP Branch (Python Project, v0.0.5)
```
src/cv_mcp_server/
  __init__.py
  main.py                 # MCP server: 15 tools, 10 resources, 1 prompt
  store.py                # ResumeStore: load, validate, query, write
  renderers.py            # Markdown renderer (full CV and per-section, 15 sections)
  utils.py                # Utility functions (YAML prompt loading)
  models/
    __init__.py            # Re-exports Resume, SemanticOverlay
    resume.py              # Pydantic models: Resume, WorkEntry, Project (with cross-refs), etc.
    semantics.py           # Pydantic models: SemanticOverlay, Topic, Relationship, etc.
  data/
    resume.yaml            # Structured CV data (source of truth)
    resume-semantics.yaml  # Semantic overlay (topics, annotations, relationships)
  prompts/
    summary.yaml           # Configurable CV summary prompt
.claude-plugin/
  plugin.json             # Claude Code plugin manifest (skills, remote MCP config)
  mcp-local.json          # MCP override: stdio via pixi (dev mode)
skills/
  cv-analyst/
    SKILL.md              # Agent Skill: CV summarization for different audiences
    references/
      summary-presets.md  # Pre-configured profiles (hiring screen, exec briefings)
config/
  cv_mcp.json             # Remote MCP server config (render.com, used for desktop remote injection)
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
- `get_cv` - Full CV in markdown or PDF binary
- `get_cv_sections(section_names, enrich)` - One or more sections by name (case-insensitive)
- `list_cv_sections` - Available section names with line counts
- `get_link(name)` - Profile/document link by network name
- `list_links` - All available links with URLs
- `get_cv_pdf_link` - Direct PDF link
- `get_google_scholar_link` - Google Scholar profile

Structured query tools:
- `query_work(company?, start_year?, end_year?, topic?)` - Filter work entries
- `get_entry(entry_id)` - Retrieve any entry by stable ID as JSON
- `list_entry_ids(section?)` - List all entry IDs with labels

Semantic query tools:
- `query_by_topic(topic)` - Find entries annotated with a topic
- `get_relationships(entry_id)` - Cross-references for an entry
- `get_skill_profile(topic?)` - Skill proficiency levels
- `get_entry_context(entry_id)` - Full semantic context (topics, relationships, impact)

Prompt-wrapping tool (fallback for non-skill clients):
- `summarize_cv` - Configurable CV summary (depth, context, emphasis, audience, tone, format, length)

### MCP Resources (`fps-cv://` URI scheme)

Markdown:
- `fps-cv://pdf` - CV as PDF binary
- `fps-cv://md` - CV as full markdown
- `fps-cv://md/sections` - Section index (names + line counts)
- `fps-cv://md/sections/{name}` - Individual section by name

JSON:
- `fps-cv://resume` - Full resume as JSON
- `fps-cv://resume/entry/{id}` - Single entry as JSON
- `fps-cv://semantics` - Full semantic overlay as JSON
- `fps-cv://semantics/{entry_id}` - Annotations for an entry
- `fps-cv://taxonomy` - Topic taxonomy as JSON

Links:
- `fps-cv://links/{name}` - Profile/document link by network name

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
- **Data layer**: `resume.yaml` (structured CV, source of truth) + `resume-semantics.yaml` (semantic overlay with topic taxonomy)
- **Pydantic models**: `models/resume.py` (Resume hierarchy) and `models/semantics.py` (SemanticOverlay hierarchy)
- **ResumeStore** (`store.py`): loads both YAML files, validates cross-references, provides query and write methods
- **Renderer** (`renderers.py`): generates markdown from Resume model (full doc + per-section)
- Entry IDs follow `<type>-<slug>` convention (e.g., `work-yahoo-kgs-2023`, `pub-htl-acl-2019`)
- MCP resources use hierarchical `fps-cv://` URI scheme
- Server supports stdio and streamable-http transports (SSE is deprecated)
- Run tests: `pixi run test`, `pixi run test-unit`, `pixi run test-integration`
- MCPB bundles vendor dependencies in `lib/` directory
- `manifest.json` defines the MCPB package metadata and tool declarations
- The `cv-analyst` skill in `skills/` handles CV summarization for skill-compatible clients; `summarize_cv` tool serves as fallback for other clients

## Plugins

When the `i-am` plugin is installed, use its agents, skills, rules, and hooks for all applicable work (planning, research, implementation, verification, code review, memory, etc.).

Prefer delegating to specialized agents (researcher, context-engineer, implementer, etc.) over doing multi-step work directly.

## Important Notes

- The CV contains real professional information - handle appropriately
- GitHub display README is `README_USER.md` (symlinked from `.github/README.md`)
- CI/CD workflows handle auto-rebasing, MCPB creation checks, releases, and Claude-powered code review
