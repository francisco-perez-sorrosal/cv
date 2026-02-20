"""MCP resources: 16 fps-cv:// endpoints + format registry."""

import json

from pydantic import BaseModel

from cv_mcp_server.server import mcp, store, CV_PATH
from cv_mcp_server.renderers import (
    render_markdown,
    render_latex,
    render_html,
    render_typst,
    render_sections,
    get_section,
    section_names as list_section_names,
    TEMPLATES_DIR,
)
from cv_mcp_server.models import Resume, SemanticOverlay


# --- Rendered output (PDF, Markdown, LaTeX) ---

@mcp.resource("fps-cv://pdf")
def cv_pdf() -> bytes:
    """Return the full CV as the original PDF binary."""
    if not CV_PATH.exists():
        return b""
    return CV_PATH.read_bytes()


@mcp.resource("fps-cv://md")
def cv_md() -> str:
    """Return the full CV as markdown."""
    return render_markdown(store)


@mcp.resource("fps-cv://md/sections")
def cv_sections_index() -> str:
    """Return available CV section names with approximate line counts."""
    lines = []
    for name, content in render_sections(store).items():
        line_count = content.count("\n") + 1
        lines.append(f"- {name} (~{line_count} lines)")
    return "\n".join(lines)


@mcp.resource("fps-cv://md/sections/{name}")
def cv_section(name: str) -> str:
    """Return a single CV section by name."""
    content = get_section(store, name)
    if content is not None:
        return content
    available = ", ".join(list_section_names(store))
    return f"Section '{name}' not found. Available sections: {available}"


@mcp.resource("fps-cv://latex")
def cv_latex() -> str:
    """Return the full CV as LaTeX source (moderncv package)."""
    return render_latex(store)


@mcp.resource("fps-cv://html")
def cv_html() -> str:
    """Return the full CV as self-contained interactive HTML."""
    return render_html(store)


@mcp.resource("fps-cv://typst")
def cv_typst() -> str:
    """Return the full CV as Typst source (moderner-cv package)."""
    return render_typst(store)


# --- Structured data (JSON) ---

@mcp.resource("fps-cv://resume")
def resume_json() -> str:
    """Return the full resume data as JSON."""
    return json.dumps(store.resume.model_dump(by_alias=True), indent=2, default=str)


@mcp.resource("fps-cv://resume/entry/{entry_id}")
def entry_json(entry_id: str) -> str:
    """Return a specific resume entry as JSON."""
    entry = store.entry_by_id(entry_id)
    if entry is None:
        return json.dumps({"error": f"Entry '{entry_id}' not found"})
    if isinstance(entry, BaseModel):
        return json.dumps(entry.model_dump(by_alias=True), indent=2, default=str)
    return str(entry)


@mcp.resource("fps-cv://semantics")
def semantics_json() -> str:
    """Return the full semantic overlay data as JSON."""
    return json.dumps(store.semantics.model_dump(by_alias=True), indent=2, default=str)


@mcp.resource("fps-cv://semantics/{entry_id}")
def entry_semantics_json(entry_id: str) -> str:
    """Return semantic annotations for a specific entry as JSON."""
    ann = store.semantics.annotations_for(entry_id)
    if ann is None:
        return json.dumps({"error": f"No annotations for '{entry_id}'"})
    return json.dumps(ann.model_dump(by_alias=True), indent=2, default=str)


@mcp.resource("fps-cv://taxonomy")
def taxonomy_json() -> str:
    """Return the topic taxonomy as JSON."""
    return json.dumps(store.semantics.taxonomy.model_dump(by_alias=True), indent=2, default=str)


# --- Links ---

@mcp.resource("fps-cv://links/{name}")
def cv_link(name: str) -> str:
    """Return a profile or document link by network name."""
    name_lower = name.lower()
    for profile in store.resume.personal_info.profiles:
        if profile.network.lower() == name_lower:
            return profile.url
    available = ", ".join(p.network for p in store.resume.personal_info.profiles)
    return f"Link '{name}' not found. Available: {available}"


# --- Introspection (schemas, template catalog) ---

@mcp.resource("fps-cv://schema/resume")
def resume_schema() -> str:
    """JSON Schema describing the Resume data model (field names, types, constraints)."""
    return json.dumps(Resume.model_json_schema(), indent=2)


@mcp.resource("fps-cv://schema/semantics")
def semantics_schema() -> str:
    """JSON Schema describing the SemanticOverlay data model (annotations, topics, relationships)."""
    return json.dumps(SemanticOverlay.model_json_schema(), indent=2)


_FORMAT_REGISTRY: dict[str, dict] = {
    "markdown": {
        "description": "LLM-readable markdown for analysis and summarization",
        "files": [
            {"name": "cv.md.j2", "role": "main"},
            {"name": "_work_entry.md.j2", "role": "partial"},
        ],
        "capabilities": {
            "sections": True,
            "enrichment": True,
            "summarization": True,
        },
    },
    "latex": {
        "description": "LaTeX document using moderncv package for typeset PDF generation",
        "files": [
            {"name": "cv.tex.j2", "role": "main"},
            {"name": "_preamble.tex.j2", "role": "partial"},
            {"name": "_work_entry.tex.j2", "role": "partial"},
        ],
        "capabilities": {
            "sections": False,
            "enrichment": False,
            "summarization": False,
        },
    },
    "tailored-latex": {
        "description": "Job-tailored LaTeX CV with section reordering, entry filtering, and profile override. Accessed via get_tailored_cv tool.",
        "files": [
            {"name": "cv_tailored.tex.j2", "role": "main"},
            {"name": "_preamble.tex.j2", "role": "partial"},
            {"name": "_work_entry.tex.j2", "role": "partial"},
        ],
        "capabilities": {
            "sections": True,
            "enrichment": False,
            "summarization": False,
        },
    },
    "html": {
        "description": "Self-contained interactive HTML with theme switching, expandable cards, and print CSS",
        "files": [
            {"name": "cv.html.j2", "role": "main"},
            {"name": "_cv_styles.css.j2", "role": "partial"},
            {"name": "_cv_scripts.js.j2", "role": "partial"},
        ],
        "capabilities": {
            "sections": False,
            "enrichment": True,
            "summarization": False,
        },
    },
    "typst": {
        "description": "Typst document using moderner-cv package for typeset PDF generation",
        "files": [
            {"name": "cv.typ.j2", "role": "main"},
            {"name": "_preamble.typ.j2", "role": "partial"},
            {"name": "_work_entry.typ.j2", "role": "partial"},
        ],
        "capabilities": {
            "sections": False,
            "enrichment": True,
            "summarization": False,
        },
    },
    "tailored-typst": {
        "description": "Job-tailored Typst CV with section reordering, entry filtering, and profile override. Accessed via get_tailored_cv tool with format='typst'.",
        "files": [
            {"name": "cv_tailored.typ.j2", "role": "main"},
            {"name": "_preamble.typ.j2", "role": "partial"},
            {"name": "_work_entry.typ.j2", "role": "partial"},
        ],
        "capabilities": {
            "sections": True,
            "enrichment": False,
            "summarization": False,
        },
    },
}


@mcp.resource("fps-cv://templates")
def template_catalog() -> str:
    """Lightweight catalog of available output formats and their capabilities."""
    catalog = [
        {"id": fmt_id, "description": meta["description"], **meta["capabilities"]}
        for fmt_id, meta in _FORMAT_REGISTRY.items()
    ]
    return json.dumps(catalog, indent=2)


@mcp.resource("fps-cv://templates/{format_id}")
def template_detail(format_id: str) -> str:
    """Per-format detail: metadata, file roles, and template source code."""
    meta = _FORMAT_REGISTRY.get(format_id)
    if not meta:
        available = ", ".join(_FORMAT_REGISTRY)
        return f"Format '{format_id}' not found. Available: {available}"
    files = []
    for f in meta["files"]:
        source = (TEMPLATES_DIR / f["name"]).read_text()
        files.append({"name": f["name"], "role": f["role"], "source": source})
    return json.dumps(
        {"id": format_id, "description": meta["description"],
         "capabilities": meta["capabilities"], "files": files},
        indent=2,
    )
