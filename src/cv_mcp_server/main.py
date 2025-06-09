"""Main module for the CV MCP server with Anthropic integration."""

import os

from pathlib import Path
# from argparse import ArgumentParser, Namespace

import pymupdf4llm
from mcp.server.fastmcp import FastMCP


# Configure transport and statelessness
trspt = "stdio"
stateless_http = False
match os.environ.get("TRANSPORT", "stdio"):
    case "stdio":
        trspt = "stdio"
        stateless_http = False
    case "sse":
        trspt = "sse"
        stateless_http = False
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

@mcp.tool()
def get_cv() -> str:
    return cv()

@mcp.tool()
def summarize_cv(
    depth_level: str = "comprehensive",
    context: str = "industry R&D role",
    emphasis_distribution: str = "technical-first",
    output_format: str = "structured paragraphs",
    target_audience: str = "technical hiring manager",
    length_constraint: str = "half-page summary",
    tone: str = "professional and objective",
    additional_instructions: str = "",
    include_citations: bool = False
) -> str:
    """Generate a summary of Francisco Perez-Sorrosal's CV based on the specified parameters.
    
    This is a convenience wrapper around the summary() tool function that exposes the same parameters.
    See the summary() function returning the prompt, for detailed parameter documentation.
    
    Returns:
        str: The generated CV summary
    """
    return summary(
        depth_level=depth_level,
        context=context,
        emphasis_distribution=emphasis_distribution,
        output_format=output_format,
        target_audience=target_audience,
        length_constraint=length_constraint,
        tone=tone,
        additional_instructions=additional_instructions,
        include_citations=False
    )
    
@mcp.tool()
def summarize_cv_for_quick_hiring_screen() -> str:
    """Generate a brief summary of Francisco Perez-Sorrosal's CV for a quick hiring screen."""
    return summary(
        depth_level="brief",
        context="industry R&D role",
        emphasis_distribution="technical-first",
        output_format="structured paragraphs",
        target_audience="technical hiring manager",
        length_constraint="half-page summary",
        tone="professional and objective",
        additional_instructions="",
        include_citations=False
    )
    
@mcp.tool()
def summarize_cv_for_executive_briefing_for_startup() -> str:
    """Generate a summary of Francisco Perez-Sorrosal's CV for an executive briefing for a startup."""
    return summary(
        depth_level="moderate",
        context="startup technical leadership",
        emphasis_distribution="leadership-oriented",
        output_format="executive summary",
        target_audience="executive leadership",
        length_constraint="1-2 paragraphs",
        tone="enthusiastic and promotional",
        additional_instructions="",
        include_citations= False
    )

@mcp.tool()
def summarize_cv_for_executive_briefing_for_big_company() -> str:
    """Generate a summary of Francisco Perez-Sorrosal's CV for an executive briefing for a big company."""
    return summary(
        depth_level="moderate",
        context="big company technical leadership",
        emphasis_distribution="leadership-oriented",
        output_format="executive summary",
        target_audience="executive leadership",
        length_constraint="full-page overview",
        tone="professional and objective",
        additional_instructions="",
        include_citations=False
    )

@mcp.resource("cvfps://full")
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
    output_format: str = "structured paragraphs",
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
                          
        output_format: Format of the output.
                     Examples:
                     - "structured paragraphs": Narrative format with clear sections
                     - "bullet points": Concise, scannable format
                     - "executive summary": Business-oriented overview
                     - "technical brief": Engineering-focused summary
                     - "comparison table": Strengths/areas matrix
                     
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
    return f"""Please provide a {depth_level} summary of the CV of Francisco Perez-Sorrosal for a candidate with AI/ML expertise in {context}.

Focus on the following aspects with {emphasis_distribution} emphasis:
- Technical skills and expertise areas
- Research contributions and publications
- Industry experience and impact
- Academic background and achievements
- Leadership and collaboration experience

Format: {output_format}
Target audience: {target_audience}
Length: {length_constraint}
Tone: {tone}

{additional_instructions}

{'Please include a table of publications with citations and impacts from Google Scholar, and include a link to the Google Scholar profile.' if include_citations else ''}
"""


# TODO CLI Args not supported by MCP yet
# def parse_cli_arguments() -> Namespace:
#     """Parse command line arguments."""
#     parser: ArgumentParser = ArgumentParser(description='CV MCP Server')
#     parser.add_argument('--transport', 
#                       type=str, 
#                       default='stdio',
#                       choices=['stdio', 'sse', "streamable-http"],
#                       help='Transport type for the MCP server (default: stdio)')
#     return parser.parse_args()


if __name__ == "__main__":
    # args: Namespace = parse_cli_arguments()
    
    # Initialize and run the server with the specified transport
    print(f"Starting CV MCP server with {trspt} transport ({host}:{port}) and stateless_http={stateless_http}...")
    mcp.run(transport=trspt) #, mount_path="/cv")
