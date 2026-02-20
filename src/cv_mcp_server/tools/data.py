"""Data tools: fetch CV content in various formats."""

import base64
import json
from typing import Literal

from pydantic import AnyUrl, Field

from mcp.types import BlobResourceContents, EmbeddedResource

from loguru import logger
from cv_mcp_server.server import mcp, store, CV_PATH
from cv_mcp_server.renderers import (
    render_markdown,
    render_latex,
    render_html,
    render_tailored_latex,
    render_sections,
    get_section,
    section_names as list_section_names,
)
from cv_mcp_server.models import TailoringSpec


@mcp.tool()
def get_cv(
    format: Literal["markdown", "pdf", "latex", "html"] = Field(
        default="markdown",
        description="'markdown' returns LLM-readable text (default). 'pdf' returns the original binary PDF document for inline rendering. 'latex' returns the full CV as LaTeX source (moderncv package). 'html' returns a self-contained interactive HTML document."
    ),
    enrich: bool = Field(
        default=True,
        description="Include semantic enrichments (cross-references, skill levels)"
    ),
) -> str | list[EmbeddedResource]:
    """Data-layer tool: retrieves raw CV content in markdown, PDF, LaTeX, or HTML.

    When the cv-analyst skill is available, prefer invoking that skill instead
    of calling this tool directly — the skill orchestrates retrieval with proper
    formatting, artifact delivery, and summarization.

    format='markdown' (default): LLM-readable text for analysis.
    format='pdf': original PDF binary for inline rendering.
    format='latex': full CV as LaTeX source (moderncv package) for typeset PDF generation.
    format='html': self-contained interactive HTML with theme switching and expandable cards.
    """
    if format == "pdf":
        logger.debug("Returning the CV as PDF binary...")
        pdf_data = CV_PATH.read_bytes() if CV_PATH.exists() else b""
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
    if format == "html":
        logger.debug("Returning the CV as interactive HTML...")
        return render_html(store, enrich=enrich)
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
