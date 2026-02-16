# CV Agent Toolkit

A suite of agent utilities for working with Francisco Perez-Sorrosal's CV and professional information. Combines an MCP server, two agent skills, and a Claude Code plugin into a single installable package.

## Components

- **MCP Server** — serves CV content in markdown, PDF, and LaTeX formats via 16 tools, plus semantic query capabilities and tailored CV rendering
- **`cv-analyst` Skill** — structured CV summarization for different audiences (hiring screens, executive briefings, technical reviews) with output in markdown, plain text, PDF, HTML, or LaTeX
- **`cv-tailoring` Skill** — job-targeted CV tailoring that analyzes a job description, selects relevant content, and produces a page-constrained (2-3 pages) compiled LaTeX/PDF CV
- **Claude Code Plugin** — bundles the MCP server and both skills for one-step installation

## Installation

### Claude Code

Install the plugin from the marketplace:

```bash
./install.sh
# or
curl -sSL https://raw.githubusercontent.com/francisco-perez-sorrosal/cv/mcp/install.sh | bash
```

The plugin bundles the MCP server (remote, via render.com) and both skills (`cv-analyst` and `cv-tailoring`).

To add complementary MCP servers (e.g. Playwright, LinkedIn), configure them in your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "linkedin_mcp_fps": {
      "command": "npx",
      "args": ["mcp-remote", "https://linkedin-mcp.wasmer.app/mcp"]
    }
  }
}
```

### Claude Desktop

Install the MCP server and skill as separate packages:

1. **MCP Server** — Open Settings > Extensions > Add, then choose one:
   - **Local**: Install the `.mcpb` package from `dist/mcpb/` (build with `make build-mcpb`)
   - **Remote**: Add manually to `claude_desktop_config.json`:

     ```json
     {
       "mcpServers": {
         "fps_cv_mcp": {
           "command": "npx",
           "args": ["mcp-remote", "https://fps-cv.onrender.com/mcp"]
         }
       }
     }
     ```

     Config file location:
     - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
     - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Skill** — Open Settings > Features > Add Skill, upload `dist/skill/cv-analyst.zip` (build with `make build-skill`)

Restart Claude Desktop after installation.

## Usage

### CV Retrieval and Analysis

Retrieve, summarize, and format Francisco's CV for different purposes:

- "Get Francisco's CV"
- "Summarize Francisco's CV for a startup executive briefing"
- "What is Francisco's Google Scholar profile link?"
- "Give me a 3 page summary of my CV for a hiring manager oriented towards an ai engineer position in html"
- "Give me the CV in LaTeX"

### CV Tailoring for Job Applications

Tailor the CV to a specific job description. The skill analyzes the job, selects the most relevant content, and produces a 2-3 page compiled PDF:

- "Tailor my CV for this job: [paste job description]"
- "Adapt my resume for a Senior ML Engineer position at Google"
- "Customize my CV for this LinkedIn job" (with LinkedIn MCP configured)

The tailoring pipeline:
1. Analyzes the job description against CV content and semantic data
2. Generates a fit assessment and gap analysis
3. Produces a `TailoringSpec` that controls section ordering, entry selection, and keyword emphasis
4. Renders a tailored LaTeX CV via the `get_tailored_cv` MCP tool
5. Compiles to PDF with automatic error correction

## Local Development

For developers working with the MCP server locally, see [README_DEV.md](README_DEV.md).

## Support

For technical issues or questions, please refer to the main project repository.
