"""Summarize tool and summary prompt — coupled because the tool delegates to the prompt."""

from pydantic import Field

from cv_mcp_server.server import mcp
from cv_mcp_server.utils import load_prompt


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
