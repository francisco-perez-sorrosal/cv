"""Main module for the CV MCP server with structured data layer."""

import base64
import json
import os
import sys

from pathlib import Path
from typing import Literal, cast

from pydantic import AnyUrl, BaseModel, Field

from mcp.server.fastmcp import FastMCP
from mcp.types import BlobResourceContents, EmbeddedResource

from loguru import logger
from cv_mcp_server.store import ResumeStore
from cv_mcp_server.renderers import (
    render_markdown,
    render_latex,
    render_tailored_latex,
    render_sections,
    render_work_entry,
    get_section,
    section_names as list_section_names,
    TEMPLATES_DIR,
)
from cv_mcp_server.models import Resume, SemanticOverlay, TailoringSpec
from cv_mcp_server.utils import load_prompt


# Configure transport and statelessness
trspt = "stdio"
stateless_http = False
match os.environ.get("TRANSPORT", trspt):
    case "stdio":
        trspt = "stdio"
        stateless_http = False
    case "sse":
        raise ValueError("SSE transport is deprecated! Use streamable-http instead.")
    case "streamable-http":
        trspt = "streamable-http"
        stateless_http = True
    case _:
        trspt = "stdio"
        stateless_http = False


def find_project_root():
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / 'pyproject.toml').exists():
            return current
        current = current.parent
    return current


PROJECT_ROOT = find_project_root()
DATA_DIR = Path(__file__).parent / "data"
CV_PATH = PROJECT_ROOT / "2025_FranciscoPerezSorrosal_CV_English.pdf"

# Eager initialization: load structured data at import time
store = ResumeStore.load(DATA_DIR)

# Initialize FastMCP server
host = os.environ.get("HOST", "0.0.0.0")
port = int(os.environ.get("PORT", 10000))
mcp = FastMCP("cv_francisco_perez_sorrosal", stateless_http=stateless_http, host=host, port=port)


# --- Data tools ---

@mcp.tool()
def get_cv(
    format: Literal["markdown", "pdf", "latex"] = Field(
        default="markdown",
        description="'markdown' returns LLM-readable text (default). 'pdf' returns the original binary PDF document for inline rendering. 'latex' returns the full CV as LaTeX source (moderncv package)."
    ),
    enrich: bool = Field(
        default=True,
        description="Include semantic enrichments (cross-references, skill levels)"
    ),
) -> str | list[EmbeddedResource]:
    """Data-layer tool: retrieves raw CV content in markdown, PDF binary, or LaTeX source.

    When the cv-analyst skill is available, prefer invoking that skill instead
    of calling this tool directly — the skill orchestrates retrieval with proper
    formatting, artifact delivery, and summarization.

    format='markdown' (default): LLM-readable text for analysis.
    format='pdf': original PDF binary for inline rendering.
    format='latex': full CV as LaTeX source (moderncv package) for typeset PDF generation.
    """
    if format == "pdf":
        logger.debug("Returning the CV as PDF binary...")
        pdf_data = cv_pdf()
        return [EmbeddedResource(
            type="resource",
            resource=BlobResourceContents(
                uri=AnyUrl("fps-cv://pdf"),
                blob=base64.b64encode(pdf_data).decode("ascii"),
                mimeType="application/pdf",
            ),
        )]
    if format == "latex":
        logger.debug("Returning the CV as LaTeX source...")
        return render_latex(store)
    logger.debug("Returning the CV in markdown format...")
    return render_markdown(store, enrich=enrich)


@mcp.tool()
def get_tailored_cv(
    tailoring_config: str = Field(
        description=(
            "JSON string of TailoringSpec. Controls section ordering, "
            "entry emphasis (weight 0-2, 0=omit), profile override, "
            "and page budget. See TailoringSpec schema for full field definitions."
        )
    ),
) -> str:
    """Render a tailored LaTeX CV from a TailoringSpec.

    The tailoring config controls section ordering, entry emphasis,
    and profile override. Returns compilable LaTeX source.
    Use this tool after analyzing a job description to produce a targeted CV.
    """
    try:
        spec = TailoringSpec.model_validate_json(tailoring_config)
    except Exception as exc:
        schema = json.dumps(TailoringSpec.model_json_schema(), indent=2)
        return (
            f"Invalid TailoringSpec: {exc}\n\n"
            f"Expected JSON schema:\n{schema}"
        )
    logger.debug(f"Rendering tailored CV for '{spec.job_title}' at '{spec.company}'...")
    return render_tailored_latex(store, spec)


@mcp.tool()
def get_link(
    name: str = Field(
        description="Network name (e.g. 'LinkedIn', 'GitHub', 'Google Scholar', 'Twitter', 'CV PDF'). Use list_links() to see all available."
    )
) -> str:
    """Return a profile or document link by network name."""
    name_lower = name.lower()
    for profile in store.resume.personal_info.profiles:
        if profile.network.lower() == name_lower:
            return profile.url
    available = ", ".join(p.network for p in store.resume.personal_info.profiles)
    return f"Link '{name}' not found. Available: {available}"


@mcp.tool()
def list_links() -> str:
    """List all available profile and document links."""
    return "\n".join(
        f"- {p.network}: {p.url}" for p in store.resume.personal_info.profiles if p.url
    )


@mcp.tool()
def get_cv_sections(
    section_names: list[str] = Field(
        description="One or more section names to retrieve (case-insensitive, '&' ignored). "
        "Use list_cv_sections() to see available names."
    ),
    enrich: bool = Field(
        default=True,
        description="Include semantic enrichments (cross-references, skill levels)"
    ),
) -> str:
    """Retrieve one or more CV sections in a single call.

    Accepts a list of section names. Returns all matched sections separated by blank lines.
    Reports any unrecognized names with the list of available sections.
    """
    results = []
    missing = []
    for name in section_names:
        content = get_section(store, name, enrich=enrich)
        if content is not None:
            results.append(content)
        else:
            missing.append(name)
    output = "\n\n".join(results)
    if missing:
        available = ", ".join(list_section_names(store))
        output += f"\n\nSections not found: {', '.join(missing)}. Available: {available}"
    return output


@mcp.tool()
def list_cv_sections() -> str:
    """List available CV section names with approximate line counts.

    Helps AI assistants pick the right section for targeted queries.
    """
    lines = []
    for name, content in render_sections(store).items():
        line_count = content.count("\n") + 1
        lines.append(f"- {name} (~{line_count} lines)")
    return "\n".join(lines)


@mcp.tool()
def get_cv_pdf_link() -> str:
    """Return the direct link to the PDF version of the CV."""
    for p in store.resume.personal_info.profiles:
        if p.network.lower() == "cv pdf":
            return p.url
    return store.resume.meta.canonical or "PDF link not available."


@mcp.tool()
def get_google_scholar_link() -> str:
    """Return the Google Scholar profile link."""
    for p in store.resume.personal_info.profiles:
        if p.network.lower() == "google scholar":
            return p.url
    return "Google Scholar link not available."


@mcp.tool()
def summarize_cv(
    depth_level: str = Field(
        default="comprehensive",
        description="Level of detail for the summary. Examples: 'brief' (100-200 words), 'moderate' (200-400 words), 'comprehensive' (400-600 words), 'deep-dive' (600+ words)"
    ),
    context: str = Field(
        default="industry R&D role",
        description="The context for the summary. Examples: 'academic research position', 'industry R&D role', 'startup technical leadership', 'consulting engagement', 'investment evaluation', 'collaboration assessment'"
    ),
    emphasis_distribution: str = Field(
        default="technical-first",
        description="Where to place emphasis in the summary. Examples: 'equal weight', 'research-heavy', 'industry-focused', 'technical-first', 'leadership-oriented'"
    ),
    style: str = Field(
        default="structured paragraphs",
        description="Style of the output. Examples: 'structured paragraphs', 'bullet points', 'executive summary', 'technical brief', 'comparison table'"
    ),
    output_format: str = Field(
        default="markdown",
        description="Output format for the summary. Examples: 'markdown' (default), 'raw_text'"
    ),
    target_audience: str = Field(
        default="technical hiring manager",
        description="Intended audience for the summary. Examples: 'technical hiring manager', 'academic search committee', 'executive leadership', 'peer researchers', 'investment team', 'collaboration partners'"
    ),
    length_constraint: str = Field(
        default="half-page summary",
        description="Desired length of the summary. Examples: '1-2 paragraphs' (100-200 words), 'half-page summary' (200-400 words), 'full-page overview' (400-600 words), 'detailed report' (600+ words), 'presentation slide content' (50-100 words)"
    ),
    tone: str = Field(
        default="professional and objective",
        description="Tone of the summary. Examples: 'professional and objective', 'enthusiastic and promotional', 'analytical and critical', 'conversational and accessible', 'formal and academic'"
    ),
    additional_instructions: str = Field(
        default="",
        description="Any specific instructions for the summary. Examples: 'Focus on AI/ML experience in healthcare applications', 'Highlight open-source contributions and community engagement', 'Compare with industry benchmarks for similar roles'"
    ),
    include_citations: bool = Field(
        default=False,
        description="Whether to include citations and publication analysis from Google Scholar profile"
    )
) -> str:
    """Fallback CV summarization for clients without Agent Skills support.

    When the cv-analyst skill is available, prefer invoking that skill instead —
    it provides richer orchestration, preset profiles, and artifact delivery.
    This tool exists for MCP clients that cannot load skills.
    """
    return summary(
        depth_level=depth_level,
        context=context,
        emphasis_distribution=emphasis_distribution,
        style=style,
        output_format=output_format,
        target_audience=target_audience,
        length_constraint=length_constraint,
        tone=tone,
        additional_instructions=additional_instructions,
        include_citations=include_citations
    )


# --- Structured query tools ---

@mcp.tool(
    description="Filter work entries by company, date range, or topic. Returns matching entries as markdown."
)
def query_work(
    company: str = "",
    start_year: str = "",
    end_year: str = "",
    topic: str = "",
    enrich: bool = Field(
        default=True,
        description="Include semantic enrichments (cross-references to publications/patents)"
    ),
) -> str:
    """Filter work entries by company, date range, or topic. Returns matching entries as markdown."""
    results = list(store.resume.work)

    if company:
        company_lower = company.lower()
        filtered = []
        for w in results:
            inst = store.institution_by_id(w.institution_id)
            if inst is None:
                continue
            names = [inst.name.lower()] + [a.lower() for a in inst.aliases]
            if any(company_lower in n for n in names):
                filtered.append(w)
        results = filtered

    if start_year and end_year:
        results = [
            w for w in results
            if w.start_date <= end_year and (w.end_date >= start_year or w.end_date == "")
        ]

    if topic:
        topic_entry_ids = {e["id"] for e in store.entries_by_topic(topic)}
        results = [
            w for w in results
            if w.id in topic_entry_ids or any(p.id in topic_entry_ids for p in w.projects)
        ]

    if not results:
        return "No matching work entries found."

    return "\n\n".join(render_work_entry(w, store, enrich=enrich) for w in results)


@mcp.tool(description="Retrieve a specific resume entry by its stable ID. Returns JSON representation.")
def get_entry(entry_id: str) -> str:
    entry = store.entry_by_id(entry_id)
    if entry is None:
        return f"Entry '{entry_id}' not found."
    if isinstance(entry, BaseModel):
        return json.dumps(entry.model_dump(by_alias=True), indent=2, default=str)
    return str(entry)


@mcp.tool(
    description="List all entry IDs with labels, optionally filtered by section type (work, patents, publications, education, certificates, conferences, memberships, skills)."
)
def list_entry_ids(section: str = "") -> str:
    lines = []
    r = store.resume

    section_map = {
        "work": [(w.id, f"{w.position} at {store.institution_name(w.institution_id)}") for w in r.work]
                + [(p.id, f"  Project: {p.name}") for w in r.work for p in w.projects],
        "institutions": [(i.id, f"{i.name} ({i.type.value})") for i in r.institutions],
        "patents": [(p.id, p.title) for p in r.patents],
        "publications": [(p.id, p.name) for p in r.publications],
        "education": [(e.id, f"{e.study_type} at {store.institution_name(e.institution_id)}") for e in r.education],
        "certificates": [(c.id, c.name) for c in r.certificates],
        "conferences": [(c.id, c.name) for c in r.conferences],
        "memberships": [(m.id, m.organization) for m in r.memberships],
        "skills": [(s.id, s.name) for s in r.skills],
    }

    if section:
        section_lower = section.lower()
        if section_lower not in section_map:
            return f"Unknown section '{section}'. Available: {', '.join(section_map.keys())}"
        entries = section_map[section_lower]
        for eid, label in entries:
            lines.append(f"- {eid}: {label}")
    else:
        for sec_name, entries in section_map.items():
            if entries:
                lines.append(f"\n## {sec_name}")
                for eid, label in entries:
                    lines.append(f"- {eid}: {label}")

    return "\n".join(lines) if lines else "No entries found."


# --- Semantic query tools ---

@mcp.tool(description="Find resume entries annotated with a topic. Returns entry IDs with labels.")
def query_by_topic(topic: str, include_subtopics: bool = True) -> str:
    results = store.entries_by_topic(topic) if include_subtopics else [
        {"id": eid, "entry": store.entry_by_id(eid)}
        for eid in store.semantics.entries_by_topic(topic, include_descendants=False)
    ]
    if not results:
        return f"No entries annotated with topic '{topic}'."
    lines = []
    for r in results:
        entry = r.get("entry") or r.get("entry")
        label = getattr(entry, "name", None) or getattr(entry, "title", None) or getattr(entry, "position", None) or str(r["id"])
        lines.append(f"- {r['id']}: {label}")
    return "\n".join(lines)


@mcp.tool(description="Get cross-references and relationships for a resume entry.")
def get_relationships(entry_id: str) -> str:
    rels = store.relationships_for(entry_id)
    if not rels:
        return f"No relationships found for '{entry_id}'."
    lines = []
    for r in rels:
        direction = "→" if r.source_id == entry_id else "←"
        other = r.target_id if r.source_id == entry_id else r.source_id
        lines.append(f"- {direction} {r.type.value} {other}: {r.description}")
    return "\n".join(lines)


@mcp.tool(description="Get skill proficiency levels across the career, optionally filtered by topic.")
def get_skill_profile(topic: str = "") -> str:
    profs = store.semantics.skill_proficiency
    if topic:
        match_ids = set(store.semantics.taxonomy.descendants(topic))
        profs = [p for p in profs if p.topic_id in match_ids]
    if not profs:
        return f"No skill proficiency data{' for topic ' + topic if topic else ''}."
    lines = []
    for p in profs:
        t = store.semantics.taxonomy.topic_by_id(p.topic_id)
        label = t.label if t else p.topic_id
        lines.append(f"- **{label}**: {p.level.value} — {p.evidence}")
    return "\n".join(lines)


@mcp.tool(description="Get full semantic context for an entry: topics, relationships, summaries, impact.")
def get_entry_context(entry_id: str) -> str:
    entry = store.entry_by_id(entry_id)
    if entry is None:
        return f"Entry '{entry_id}' not found."

    parts = [f"## Context for {entry_id}"]

    ann = store.semantics.annotations_for(entry_id)
    if ann:
        if ann.topics:
            parts.append("\n### Topics")
            for t in ann.topics:
                topic = store.semantics.taxonomy.topic_by_id(t.topic_id)
                label = topic.label if topic else t.topic_id
                primary = " (primary)" if t.primary else ""
                parts.append(f"- {label}{primary} — confidence: {t.confidence}, {t.rationale}")
        if ann.impact:
            parts.append("\n### Impact")
            for i in ann.impact:
                parts.append(f"- {i.metric}: {i.value} ({i.scope})")
        if ann.summaries:
            parts.append("\n### Summaries")
            for s in ann.summaries:
                parts.append(f"- [{s.audience}] {s.summary}")

    rels = store.relationships_for(entry_id)
    if rels:
        parts.append("\n### Relationships")
        for r in rels:
            direction = "→" if r.source_id == entry_id else "←"
            other = r.target_id if r.source_id == entry_id else r.source_id
            parts.append(f"- {direction} {r.type.value} {other}: {r.description}")

    return "\n".join(parts)


# --- Resources: Rendered output (PDF, Markdown, LaTeX) ---

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


# --- Resources: Structured data (JSON) ---

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


# --- Resources: Links ---

@mcp.resource("fps-cv://links/{name}")
def cv_link(name: str) -> str:
    """Return a profile or document link by network name."""
    name_lower = name.lower()
    for profile in store.resume.personal_info.profiles:
        if profile.network.lower() == name_lower:
            return profile.url
    available = ", ".join(p.network for p in store.resume.personal_info.profiles)
    return f"Link '{name}' not found. Available: {available}"


# --- Resources: Introspection (schemas, template catalog) ---

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


# --- Prompt ---

@mcp.prompt()
def summary(
    depth_level: str = "comprehensive",
    context: str = "industry R&D role",
    emphasis_distribution: str = "technical-first",
    style: str = "structured paragraphs",
    output_format: str = "markdown",
    target_audience: str = "technical hiring manager",
    length_constraint: str = "half-page summary",
    tone: str = "professional and objective",
    additional_instructions: str = "",
    include_citations: bool = False
) -> str:
    """Configurable prompt for generating a summary of Francisco Perez-Sorrosal's CV."""
    prompt_data = load_prompt("summary")
    citations_text = prompt_data.get('citation_instructions', '') if include_citations else ''
    return prompt_data['prompt'].format(
        depth_level=depth_level,
        context=context,
        emphasis_distribution=emphasis_distribution,
        style=style,
        output_format=output_format,
        target_audience=target_audience,
        length_constraint=length_constraint,
        tone=tone,
        additional_instructions=additional_instructions,
        citation_instructions=citations_text
    )


def main():
    """Main entry point: initialize and run the server with the specified transport."""
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Starting CV MCP server with {trspt} transport ({host}:{port}) and stateless_http={stateless_http}...")
    transport_as_literal = cast(Literal['stdio', 'streamable-http'], trspt)
    mcp.run(transport=transport_as_literal)


if __name__ == "__main__":
    main()
