# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Francisco Perez-Sorrosal's CV repository. Two branches serve different purposes:

- **`main`**: LaTeX source CV (`2025_FranciscoPerezSorrosal_CV_English.tex`) and generated PDF
- **`mcp`**: Python MCP server (v0.0.5) with structured YAML data layer, semantic overlay, and 16 query/rendering tools for AI systems

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
pixi run generate-tex              # generate LaTeX CV from YAML data
```

### Release
```bash
./scripts/release.sh               # release process (see RELEASE_PROCESS.md)
```

## Architecture and Structure

### Main Branch
- `2025_FranciscoPerezSorrosal_CV_English.tex` - LaTeX source (moderncv, classic green theme)
- `2025_FranciscoPerezSorrosal_CV_English.pdf` - Generated PDF

### MCP Branch (Python Project, v0.0.5)
```
src/cv_mcp_server/
  __init__.py
  main.py                 # MCP server: 16 tools, 15 resources, 1 prompt
  store.py                # ResumeStore: load, validate, query, write
  renderers.py            # Markdown and LaTeX renderers (full CV and per-section, 13 sections)
  utils.py                # Utility functions (YAML prompt loading)
  models/
    __init__.py            # Re-exports Resume, SemanticOverlay, TailoringSpec
    resume.py              # Pydantic models: Resume, WorkEntry, Project (with cross-refs), etc.
    semantics.py           # Pydantic models: SemanticOverlay, Topic, Relationship, etc.
    tailoring.py           # Pydantic models: TailoringSpec, SectionDirective, EntryEmphasis, KeywordHighlight
  data/
    resume.yaml            # Structured CV data (source of truth)
    resume-semantics.yaml  # Semantic overlay (topics, annotations, relationships)
  templates/
    cv.md.j2               # Jinja2 template for markdown output
    cv.tex.j2              # Jinja2 template for LaTeX output (moderncv)
    cv_tailored.tex.j2     # Jinja2 template for tailored LaTeX output
    _preamble.tex.j2       # Shared LaTeX preamble partial
    _work_entry.md.j2      # Markdown work entry partial
    _work_entry.tex.j2     # LaTeX work entry partial
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
  cv-tailoring/
    SKILL.md              # Agent Skill: Job-targeted CV tailoring with LaTeX/PDF output
    references/
      methodology.md      # Tailoring methodology (analysis, optimization, rendering)
config/
  cv_mcp.json             # Remote MCP server config (render.com, used for desktop remote injection)
scripts/
  release.sh              # Release automation
  generate_tex.py         # Standalone LaTeX generation from YAML data
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
- `get_cv` - Full CV in markdown, PDF binary, or LaTeX source
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

Rendering tools:
- `get_tailored_cv(tailoring_config)` - Render a tailored LaTeX CV from a TailoringSpec JSON (section reordering, entry filtering, profile override)

Prompt-wrapping tool (fallback for non-skill clients):
- `summarize_cv` - Configurable CV summary (depth, context, emphasis, audience, tone, format, length)

### MCP Resources (`fps-cv://` URI scheme)

Markdown:
- `fps-cv://pdf` - CV as PDF binary
- `fps-cv://md` - CV as full markdown
- `fps-cv://md/sections` - Section index (names + line counts)
- `fps-cv://md/sections/{name}` - Individual section by name

LaTeX:
- `fps-cv://latex` - Full CV as LaTeX source (moderncv package)

JSON:
- `fps-cv://resume` - Full resume as JSON
- `fps-cv://resume/entry/{id}` - Single entry as JSON
- `fps-cv://semantics` - Full semantic overlay as JSON
- `fps-cv://semantics/{entry_id}` - Annotations for an entry
- `fps-cv://taxonomy` - Topic taxonomy as JSON

Schema:
- `fps-cv://schema/resume` - JSON Schema for the Resume data model
- `fps-cv://schema/semantics` - JSON Schema for the SemanticOverlay data model

Templates:
- `fps-cv://templates` - Lightweight catalog of formats and capabilities
- `fps-cv://templates/{format_id}` - Per-format detail with template source code

Links:
- `fps-cv://links/{name}` - Profile/document link by network name

### Agent Skill: `cv-analyst`

The `skills/cv-analyst/` skill ([Agent Skills open format](https://agentskills.io)) provides CV summarization for any skill-compatible client (Claude Code, Claude Desktop, Cursor, Gemini CLI, VS Code, and others). It composes with the MCP data tools to fetch CV content and applies structured summarization instructions.

The skill is the preferred mechanism for CV summarization. The `summarize_cv` tool remains as a fallback for clients that do not support skills.

### Agent Skill: `cv-tailoring`

The `skills/cv-tailoring/` skill provides job-targeted CV tailoring. It analyzes a job description, generates a `TailoringSpec`, renders a page-constrained (2-3 pages) LaTeX CV via the `get_tailored_cv` MCP tool, and compiles it to PDF. Works with the LinkedIn MCP server for job description retrieval.

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
- **Data layer**: `resume.yaml` (structured CV, source of truth) + `resume-semantics.yaml` (semantic overlay with topic taxonomy)
- **Pydantic models**: `models/resume.py` (Resume hierarchy), `models/semantics.py` (SemanticOverlay hierarchy), `models/tailoring.py` (TailoringSpec)
- **ResumeStore** (`store.py`): loads both YAML files, validates cross-references, provides query and write methods
- **Renderer** (`renderers.py`): generates markdown, LaTeX, and tailored LaTeX from Resume model using Jinja2 templates (full doc + per-section + tailored)
- Entry IDs follow `<type>-<slug>` convention (e.g., `work-yahoo-kgs-2023`, `pub-htl-acl-2019`)
- MCP resources use hierarchical `fps-cv://` URI scheme
- Server supports stdio and streamable-http transports (SSE is deprecated)
- Run tests: `pixi run -e dev python -m pytest` (the `-e dev` flag is required — `pixi run test` may fail if pyenv intercepts pytest)
- MCPB bundles vendor dependencies in `lib/` directory
- `manifest.json` defines the MCPB package metadata and tool declarations
- The `cv-analyst` skill in `skills/` handles CV summarization for skill-compatible clients; `summarize_cv` tool serves as fallback for other clients
- The `cv-tailoring` skill in `skills/` handles job-targeted CV tailoring with LaTeX/PDF output via the `get_tailored_cv` tool

### Jinja2/LaTeX Template Gotchas
- `{% raw %}...{% endraw %}` blocks in templates protect LaTeX special chars from Jinja2. These work correctly inside `{% include %}` — included files process raw/endraw independently
- `_preamble.tex.j2` contains personal data (name, title, profiles) between two raw blocks. Both `cv.tex.j2` and `cv_tailored.tex.j2` get personal data from this shared partial. The `profile_override` is handled separately in `cv_tailored.tex.j2` inside `\begin{document}`, not in the preamble
- `_template_context()` passes `enrich=False` for all LaTeX rendering — semantic enrichment (project links, skill levels) is for markdown only
- LaTeX commands containing `{#N}` (e.g., `\newcommand{\foo}[1]{#1}`) must be inside `{% raw %}` blocks because `{#` triggers Jinja2's comment parser. This is distinct from the `{{ "{" }}` brace-escaping used elsewhere
- New Pydantic models follow `ConfigDict(populate_by_name=True)` + `Field()` pattern — same as `resume.py` and `semantics.py`

### Technical Debt
- `main.py` is at 688 lines (hard ceiling: 800). Future tools should extract tool registrations into separate modules

## Plugins

When the `i-am` plugin is installed, use its agents, skills, rules, and hooks for all applicable work (planning, research, implementation, verification, code review, memory, etc.).

Prefer delegating to specialized agents (researcher, context-engineer, implementer, etc.) over doing multi-step work directly.

## Important Notes

- The CV contains real professional information - handle appropriately
- GitHub display README is `README_USER.md` (symlinked from `.github/README.md`)
- CI/CD workflows handle auto-rebasing, MCPB creation checks, releases, and Claude-powered code review
