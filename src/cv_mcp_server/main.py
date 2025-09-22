"""Main module for the CV MCP server with Anthropic integration."""

import os
import sys

from pathlib import Path
from typing import Literal, cast
from pydantic import Field

import pymupdf4llm
from mcp.server.fastmcp import FastMCP

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
def get_cv() -> str:
    """Retrieve the full CV of Francisco Perez-Sorrosal in markdown format.
    
    Extracts and converts Francisco's CV from PDF format to markdown,
    making it easily readable and processable by AI systems.
    
    Includes, among other things:
    - Educational background and academic credentials
    - Research experience and publications
    - Industry experience and technical roles
    - Technical skills and expertise areas
    - Professional achievements and awards
    - Leadership and collaboration experience
    
    Returns:
        str: The CV content in markdown format
        
    Example:
        >>> get_cv()
        "# Francisco Perez-Sorrosal\n\n## Education\nPhD in Computer Science..."
    """
    logger.debug(f"Returning the CV in markdown format...")
    return cv()


@mcp.tool()
def get_cv_pdf_link() -> str:
    """Get the direct link to Francisco Perez-Sorrosal's CV in PDF format.
    
    Use cases:
    - Direct access to the original PDF for download or viewing
    - Sharing the CV link with others
    - Integration with systems that require PDF format
    - Professional document management and archiving
    
    Returns:
        str: Direct URL to the CV PDF file on GitHub
        
    Example:
        >>> get_cv_pdf_link()
        "https://github.com/francisco-perez-sorrosal/cv/blob/main/2025_FranciscoPerezSorrosal_CV_English.pdf"
        
    Note:
        The PDF is hosted on GitHub and is publicly accessible.
        This is the authoritative source for Francisco's CV in PDF format.
    """
    return cv_pdf_link()


@mcp.tool()
def get_google_scholar_link() -> str:
    """Get the link to Francisco Perez-Sorrosal's Google Scholar profile.
    
    Profile contents include:
    - Academic publications and research papers
    - Citation counts and h-index metrics
    - Research areas and expertise
    - Co-authors and collaboration network
    - Publication timeline and research evolution
    
    Use cases:
    - Academic evaluation and research assessment
    - Citation analysis and impact measurement
    - Research collaboration opportunities
    - Academic networking and discovery
    - Publication verification and reference
    
    Returns:
        str: Direct URL to Francisco's Google Scholar profile
        
    Example:
        >>> get_google_scholar_link()
        "https://scholar.google.com/citations?user=nemqgScAAAAJ&hl=en"
        
    Note:
        The Google Scholar profile provides real-time citation metrics and
        is regularly updated with new publications and citations.
    """
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
    """Generate a summary/overview of Francisco Perez-Sorrosal's CV based on the specified parameters.
    
    This is a convenience wrapper around the summary() tool function that exposes the same parameters.
    See the summary() function returning the prompt, for detailed parameter documentation.
    
    Returns:
        str: The generated CV summary
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
    
@mcp.tool()
def summarize_cv_for_quick_hiring_screen() -> str:
    """Generate a brief summary/overview of Francisco Perez-Sorrosal's CV for a quick hiring screen."""
    return summary(
        depth_level="brief",
        context="industry R&D role",
        emphasis_distribution="technical-first",
        style="structured paragraphs",
        output_format="markdown",
        target_audience="technical hiring manager",
        length_constraint="half-page summary",
        tone="professional and objective",
        additional_instructions="",
        include_citations=False
    )
    
@mcp.tool()
def summarize_cv_for_executive_briefing_for_startup() -> str:
    """Generate a summary/overview of Francisco Perez-Sorrosal's CV for an executive briefing for a startup."""
    return summary(
        depth_level="moderate",
        context="startup technical leadership",
        emphasis_distribution="leadership-oriented",
        style="executive summary",
        output_format="markdown",
        target_audience="executive leadership",
        length_constraint="1-2 paragraphs",
        tone="enthusiastic and promotional",
        additional_instructions="",
        include_citations=False
    )

@mcp.tool()
def summarize_cv_for_executive_briefing_for_big_company() -> str:
    """Generate a summary/overview of Francisco Perez-Sorrosal's CV for an executive briefing for a big company."""
    return summary(
        depth_level="moderate",
        context="big company technical leadership",
        emphasis_distribution="leadership-oriented",
        style="executive summary",
        output_format="markdown",
        target_audience="executive leadership",
        length_constraint="full-page overview",
        tone="professional and objective",
        additional_instructions="",
        include_citations=False
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

@mcp.resource("fps-cv://cv")
def cv() -> str:
    """
    Return the full CV of Francisco Perez Sorrosal as a markdown file.
    """
    content = "There's no CV found!"
    if os.path.exists(PROJECT_ROOT):
        cv_path = os.path.join(PROJECT_ROOT, "2025_FranciscoPerezSorrosal_CV_English.pdf")
        content: str = pymupdf4llm.to_markdown(cv_path)
    return content

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
    """Prompt for generating a summary of Francisco Perez-Sorrosal's CV based on the specified parameters.
    
    Args:
        depth_level: Level of detail for the summary. 
                   Examples: 
                   - "brief": High-level overview, key highlights only (100-200 words)
                   - "moderate": Balanced detail across all sections (200-400 words)
                   - "comprehensive": Detailed analysis with specific examples (400-600 words)
                   - "deep-dive": Thorough examination with context and implications (600+ words)
                   
        context: The context for the summary.
               Examples:
               - "academic research position"
               - "industry R&D role"
               - "startup technical leadership"
               - "consulting engagement"
               - "investment evaluation"
               - "collaboration assessment"
               
        emphasis_distribution: Where to place emphasis in the summary.
                          Examples:
                          - "equal weight": Balanced coverage of all sections
                          - "research-heavy": 60% research, 40% other content
                          - "industry-focused": 60% industry experience
                          - "technical-first": Prioritize technical skills
                          - "leadership-oriented": Emphasize management experience
                          
        style: Style of the output.
                     Examples:
                     - "structured paragraphs": Narrative format with clear sections
                     - "bullet points": Concise, scannable format
                     - "executive summary": Business-oriented overview
                     - "technical brief": Engineering-focused summary
                     - "comparison table": Strengths/areas matrix
                     
        output_format: Output format for the summary.
                      Examples:
                      - "markdown": Markdown formatted text (default)
                      - "raw_text": Plain text without formatting
                     
        target_audience: Intended audience for the summary.
                         Examples:
                         - "technical hiring manager"
                         - "academic search committee"
                         - "executive leadership"
                         - "peer researchers"
                         - "investment team"
                         - "collaboration partners"
                         
        length_constraint: Desired length of the summary.
                        Examples:
                        - "1-2 paragraphs" (100-200 words)
                        - "half-page summary" (200-400 words)
                        - "full-page overview" (400-600 words)
                        - "detailed report" (600+ words)
                        - "presentation slide content" (50-100 words)
                        
        tone: Tone of the summary.
             Examples:
             - "professional and objective"
             - "enthusiastic and promotional"
             - "analytical and critical"
             - "conversational and accessible"
             - "formal and academic"
             
        additional_instructions: Any specific instructions for the summary.
                            Example:
                            - "Focus on AI/ML experience in healthcare applications"
                            - "Highlight open-source contributions and community engagement"
                            - "Compare with industry benchmarks for similar roles"
    
    Returns:
        str: A prompt for generating the CV summary
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
