# CV Data Repository

The single source of truth for Francisco Perez-Sorrosal's CV content. YAML data, validation schema, and publishing workflow. Rendered artifacts (PDF, HTML, LaTeX, Typst, Markdown) are generated and released via GitHub Releases, never committed here.

## What's here

- `cv-data/resume.yaml` — structured CV content (experience, education, skills, publications, patents, etc.)
- `cv-data/resume-semantics.yaml` — semantic overlay (topics, relationships, annotations)
- `schemas/` — JSON Schema for validation; mirrored from [`cv-forge`](https://github.com/francisco-perez-sorrosal/cv-forge)
- `.github/workflows/` — CI validation and tag-triggered publishing

## Making changes

To propose an edit to the CV data:

1. **Clone this repo** and create a branch: `git switch -c update/your-change`
2. **Edit** `cv-data/resume.yaml` or `cv-data/resume-semantics.yaml`
3. **Validate locally** (see below)
4. **Push and open a PR** against `main`

The CI workflow validates automatically; if checks pass, merge and proceed to Publishing.

### Validate before you PR

```bash
# Install check-jsonschema (standalone CLI)
pip install check-jsonschema

# Validate both files
check-jsonschema --schemafile schemas/resume.schema.json cv-data/resume.yaml
check-jsonschema --schemafile schemas/semantics.schema.json cv-data/resume-semantics.yaml
```

All green? Ready to PR.

## Publishing a release

A release is triggered by pushing a CalVer tag in the form `YYYY.MM.DD` (with optional `.N` for same-day re-releases, e.g. `2026.09.13.1`).

```bash
git tag 2026.09.13
git push origin 2026.09.13
```

The workflow automatically:
- Renders the CV in all formats (PDF, LaTeX, Typst, Markdown, HTML)
- Publishes eight assets to the GitHub Release
- Deploys the HTML to the live CV site at https://fps-cv.wasmer.app
- Creates a `release.json` manifest (consumed by the MCP server)

All assets are stable, version-free URLs under `releases/latest/download/<name>`.

## Consuming the CV

### As data

- **YAML sources**: `resume.yaml` and `resume-semantics.yaml` at `https://github.com/francisco-perez-sorrosal/cv/releases/latest/download/resume.yaml` (and `.semantics.yaml`)
- **JSON**: `resume` and `semantics` as structured JSON

### As documents

- **PDF**: `FranciscoPerezSorrosal_CV.pdf`
- **HTML** (interactive): `FranciscoPerezSorrosal_CV.html` or live at https://fps-cv.wasmer.app
- **LaTeX** (moderncv): `FranciscoPerezSorrosal_CV.tex`
- **Typst** (moderner-cv): `FranciscoPerezSorrosal_CV.typ`
- **Markdown**: `FranciscoPerezSorrosal_CV.md`

All at `https://github.com/francisco-perez-sorrosal/cv/releases/latest/download/<filename>`.

### Via MCP

The `cv` Claude Code plugin connects to an MCP server that serves the CV:

```
MCP Server: https://fps-cv-mcp.wasmer.app/mcp
```

The server fetches the latest release data automatically; no deploy required when you publish.

## Data conventions

See [`CLAUDE.md`](CLAUDE.md) for entry ID scheme, cross-reference rules, date format, and validation commands.

## Editing with the plugin

The `cv-forge` maintainer plugin provides an interactive edit flow:

1. **Launch** from Claude Code: "Update my CV" or "Add this job"
2. **Edit** the YAML directly in the conversation
3. **Validate** automatically against the schema
4. **Preview** the rendered output
5. **Diff** and confirm before opening a PR

No manual YAML editing or command-line work required. The plugin uses your `gh` auth for the PR.

## Related repositories

- **[`cv-forge`](https://github.com/francisco-perez-sorrosal/cv-forge)** — machinery that renders, serves, and publishes this data. Contains the CLI, MCP server, and the two Claude Code plugins (`cv` consumer, `cv-forge` maintainer).
