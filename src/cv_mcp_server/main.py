"""Main module for the CV MCP server with Anthropic integration."""

import base64
import os
import sys

from pathlib import Path
from typing import Literal, cast

from pydantic import AnyUrl, Field

import pymupdf4llm
from mcp.server.fastmcp import FastMCP
from mcp.types import BlobResourceContents, EmbeddedResource

from loguru import logger
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


# Initialize FastMCP server
host = os.environ.get("HOST", "0.0.0.0")  # render.com needs '0.0.0.0' specified as host when deploying the service
port = int(os.environ.get("PORT", 10000))  # render.com has '10000' as default port
mcp = FastMCP("cv_francisco_perez_sorrosal", stateless_http=stateless_http, host=host, port=port)

# Track usage to understand how users interact with the MCP server
# NOTE:
# import mcpcat
# mcpcat.track(server=mcp, project_id="proj_2yl2y3eRvzgT2fUTQAUok0J6i6T")

# NOTE: We have to wrap the resources to be accessible to the LLMs from the prompts

@mcp.tool()
def get_cv(
    format: Literal["markdown", "pdf"] = Field(
        default="markdown",
        description="'markdown' returns LLM-readable text (default). 'pdf' returns the original binary PDF document for inline rendering."
    )
) -> str | list[EmbeddedResource]:
    """Data-layer tool: retrieves raw CV content in markdown or PDF binary.

    When the cv-analyst skill is available, prefer invoking that skill instead
    of calling this tool directly — the skill orchestrates retrieval with proper
    formatting, artifact delivery, and summarization.

    format='markdown' (default): LLM-readable text for analysis.
    format='pdf': original PDF binary for inline rendering.
    """
    if format == "pdf":
        logger.debug("Returning the CV as PDF binary...")
        pdf_data = cv_pdf()
        return [EmbeddedResource(
            type="resource",
            resource=BlobResourceContents(
                uri=AnyUrl("fps-cv://cv_pdf"),
                blob=base64.b64encode(pdf_data).decode("ascii"),
                mimeType="application/pdf",
            ),
        )]
    logger.debug("Returning the CV in markdown format...")
    return cv_md()


@mcp.tool()
def get_cv_pdf_link() -> str:
    """Returns a shareable GitHub URL pointing to the CV PDF (not the PDF itself).

    When the cv-analyst skill is available, prefer invoking that skill — it
    appends this link automatically when appropriate.
    """
    return cv_pdf_link()


@mcp.tool()
def get_google_scholar_link() -> str:
    """Get the link to Francisco Perez-Sorrosal's Google Scholar profile for publications and citations."""
    return google_scholar_link()


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

@mcp.resource("fps-cv://google_scholar_link")
def google_scholar_link() -> str:
    """
    Return the link to the Google Scholar profile of Francisco Perez-Sorrosal.
    """
    return "https://scholar.google.com/citations?user=nemqgScAAAAJ&hl=en"

@mcp.resource("fps-cv://cv_pdf_link")
def cv_pdf_link() -> str:
    """
    Return the link to the CV in pdf format.
    """
    return "https://github.com/francisco-perez-sorrosal/cv/blob/main/2025_FranciscoPerezSorrosal_CV_English.pdf"

@mcp.resource("fps-cv://cv_md")
def cv_md() -> str:
    """Return the full CV of Francisco Perez-Sorrosal as markdown."""
    cv_path = PROJECT_ROOT / "2025_FranciscoPerezSorrosal_CV_English.pdf"
    if not cv_path.exists():
        return "There's no CV found!"
    return pymupdf4llm.to_markdown(str(cv_path))


@mcp.resource("fps-cv://cv_pdf")
def cv_pdf() -> bytes:
    """Return the full CV of Francisco Perez-Sorrosal as the original PDF binary."""
    cv_path = PROJECT_ROOT / "2025_FranciscoPerezSorrosal_CV_English.pdf"
    if not cv_path.exists():
        return b""
    return cv_path.read_bytes()

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
    """Configurable prompt for generating a summary of Francisco Perez-Sorrosal's CV.

    Args:
        depth_level: Detail level — "brief" (100-200w), "comprehensive" (400-600w), "deep-dive" (600+w).
        context: Evaluation context — e.g. "industry R&D role", "academic research position".
        emphasis_distribution: Weight distribution — e.g. "technical-first", "research-heavy", "equal weight".
        style: Output style — e.g. "structured paragraphs", "bullet points", "executive summary".
        output_format: "markdown" (default) or "raw_text".
        target_audience: Intended reader — e.g. "technical hiring manager", "executive leadership".
        length_constraint: Target length — e.g. "half-page summary", "1-2 paragraphs", "detailed report".
        tone: Writing tone — e.g. "professional and objective", "conversational and accessible".
        additional_instructions: Free-form guidance — e.g. "Focus on AI/ML experience in healthcare".
        include_citations: Whether to include Google Scholar publication analysis.
    """
    # Load the prompt data from YAML
    prompt_data = load_prompt("summary")

    # Get citations instructions if needed
    citations_text = prompt_data.get('citation_instructions', '') if include_citations else ''

    # Format the prompt with provided parameters
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
    mcp.run(transport=transport_as_literal) #, mount_path="/cv")


if __name__ == "__main__":
    main()
