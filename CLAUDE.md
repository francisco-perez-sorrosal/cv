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
pixi run render-cv                 # full pipeline: render tex → compile PDF → latest.pdf symlink
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
  main.py                 # Entry point: imports trigger registration, main()
  server.py               # Shared state: transport config, store, mcp instance
  resources.py            # 16 MCP resources (fps-cv:// endpoints) + _FORMAT_REGISTRY
  store.py                # ResumeStore: load, validate, query, write
  renderers.py            # Markdown, LaTeX, HTML, and Typst renderers (full CV, per-section, tailored)
  utils.py                # Utility functions (YAML prompt loading)
  tools/
    __init__.py            # Package marker
    data.py                # 8 data tools (get_cv, get_tailored_cv, links, sections)
    query.py               # 3 query tools (query_work, get_entry, list_entry_ids)
    semantic.py            # 4 semantic tools (topics, relationships, skills, context)
    summarize.py           # summarize_cv tool + summary prompt
  models/
    __init__.py            # Re-exports Resume, SemanticOverlay, TailoringSpec
    resume.py              # Pydantic models: Resume, WorkEntry, Project (with cross-refs), etc.
    semantics.py           # Pydantic models: SemanticOverlay, Topic, Relationship, etc.
    tailoring.py           # Pydantic models: TailoringSpec, SectionDirective, EntryEmphasis, KeywordHighlight
  templates/
    cv.md.j2               # Jinja2 template for markdown output
    cv.tex.j2              # Jinja2 template for LaTeX output (moderncv)
    cv_tailored.tex.j2     # Jinja2 template for tailored LaTeX output
    cv.html.j2             # Jinja2 template for HTML output (self-contained interactive)
    _cv_styles.css.j2      # HTML CSS partial (themes, responsive, print)
    _cv_scripts.js.j2      # HTML JS partial (theme switching, expandable cards)
    cv.typ.j2              # Jinja2 template for Typst output (moderner-cv)
    cv_tailored.typ.j2     # Jinja2 template for tailored Typst output
    _preamble.tex.j2       # Shared LaTeX preamble partial
    _preamble.typ.j2       # Shared Typst preamble partial (moderner-cv import, page setup)
    _work_entry.md.j2      # Markdown work entry partial
    _work_entry.tex.j2     # LaTeX work entry partial
    _work_entry.typ.j2     # Typst work entry partial
  prompts/
    summary.yaml           # Configurable CV summary prompt
cv-data/
  resume.yaml            # Structured CV data (source of truth)
  resume-semantics.yaml  # Semantic overlay (topics, annotations, relationships)
rendered-cv/             # Quick render workspace (gitignored); python scripts/render_cv.py -f <fmt>
  tex/ md/ html/ typst/  # One subdir per format
latest-cv/               # Snapshot renders (gitignored); pixi run render-cv
  tex/                   # <YYYY-MM-DD>_FranciscoPerezSorrosal_CV_English.{tex,pdf}
latest.pdf               # Symlink → latest-cv/tex/<date>_*.pdf (gitignored)
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
  render_cv.py            # Render CV to any format; --snapshot --compile --symlink for full pipeline
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
- `get_cv` - Full CV in markdown, PDF binary, LaTeX source, interactive HTML, or Typst source
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
- `get_tailored_cv(tailoring_config, format?)` - Render a tailored CV from a TailoringSpec JSON (section reordering, entry filtering, profile override). Supports `format="latex"` (default) and `format="typst"`

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

HTML:
- `fps-cv://html` - Full CV as self-contained interactive HTML

Typst:
- `fps-cv://typst` - Full CV as Typst source (moderner-cv package)

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
- **Data layer**: `cv-data/resume.yaml` (structured CV, source of truth) + `cv-data/resume-semantics.yaml` (semantic overlay with topic taxonomy); located at the project root, outside the Python package. Override via `CV_DATA_DIR` env var
- **Pydantic models**: `models/resume.py` (Resume hierarchy), `models/semantics.py` (SemanticOverlay hierarchy), `models/tailoring.py` (TailoringSpec)
- **ResumeStore** (`store.py`): loads both YAML files, validates cross-references, provides query and write methods
- **Renderer** (`renderers.py`): generates markdown, LaTeX, HTML, Typst, and tailored LaTeX/Typst from Resume model using Jinja2 templates (full doc + per-section + tailored)
- Entry IDs follow `<type>-<slug>` convention (e.g., `work-yahoo-kgs-2023`, `pub-htl-acl-2019`)
- MCP resources use hierarchical `fps-cv://` URI scheme
- Server supports stdio and streamable-http transports (SSE is deprecated)
- Run tests: `pixi run -e dev python -m pytest` (the `-e dev` flag is required — `pixi run test` may fail if pyenv intercepts pytest)
- MCPB bundles vendor dependencies in `lib/` directory
- `manifest.json` defines the MCPB package metadata and tool declarations
- The `cv-analyst` skill in `skills/` handles CV summarization for skill-compatible clients; `summarize_cv` tool serves as fallback for other clients
- The `cv-tailoring` skill in `skills/` handles job-targeted CV tailoring with LaTeX/PDF or Typst/PDF output via the `get_tailored_cv` tool

### Jinja2/LaTeX Template Gotchas
- `{% raw %}...{% endraw %}` blocks in templates protect LaTeX special chars from Jinja2. These work correctly inside `{% include %}` — included files process raw/endraw independently
- `_preamble.tex.j2` contains personal data (name, title, profiles) between two raw blocks. Both `cv.tex.j2` and `cv_tailored.tex.j2` get personal data from this shared partial. The `profile_override` is handled separately in `cv_tailored.tex.j2` inside `\begin{document}`, not in the preamble
- `_template_context()` passes `enrich=False` for all LaTeX rendering — semantic enrichment (project links, skill levels) is for markdown, HTML, and Typst
- LaTeX commands containing `{#N}` (e.g., `\newcommand{\foo}[1]{#1}`) must be inside `{% raw %}` blocks because `{#` triggers Jinja2's comment parser. This is distinct from the `{{ "{" }}` brace-escaping used elsewhere
- New Pydantic models follow `ConfigDict(populate_by_name=True)` + `Field()` pattern — same as `resume.py` and `semantics.py`

### Jinja2/Typst Template Gotchas
- Typst templates (`.typ.j2`) use the same `{% raw %}` block pattern as LaTeX for native Typst code (e.g., `#import`, `#cv-entry(`, `= Section Heading`)
- `_preamble.typ.j2` imports `moderner-cv` 0.2.1 and sets up `#show: moderner-cv.with(...)` with personal data injection between raw blocks
- Typst special characters (`#`, `$`, `@`, `<`, `>`) are escaped via `_typst_escape_filter` — lighter than LaTeX (fewer specials in content mode)
- `render_typst()` defaults to `enrich=True` (like markdown), unlike LaTeX which always uses `enrich=False`. This means the Typst work entry partial renders project links when enriched
- `render_tailored_typst()` uses `enrich=False` (like tailored LaTeX) — tailored output stays focused on job relevance
- The `moderner-cv` package is resolved client-side by Typst's package manager on first compile. No server-side dependency
- Both `cv.typ.j2` and `cv_tailored.typ.j2` share `_preamble.typ.j2` and `_work_entry.typ.j2` partials

### Technical Debt
- No current items — tool extraction complete (`main.py` ~216 lines, tools in `tools/` subpackage)

## Plugins

When the `i-am` plugin is installed, use its agents, skills, rules, and hooks for all applicable work (planning, research, implementation, verification, code review, memory, etc.).

Prefer delegating to specialized agents (researcher, context-engineer, implementer, etc.) over doing multi-step work directly.

## Important Notes

- The CV contains real professional information - handle appropriately
- GitHub display README is `README_USER.md` (symlinked from `.github/README.md`)
- CI/CD workflows handle auto-rebasing, MCPB creation checks, releases, and Claude-powered code review
