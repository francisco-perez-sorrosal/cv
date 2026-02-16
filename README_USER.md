# CV Agent Toolkit

A suite of agent utilities for working with Francisco Perez-Sorrosal's CV and professional information. Combines an MCP server, an analysis skill, and a Claude Code plugin into a single installable package.

## Components

- **MCP Server** — serves CV content in markdown, PDF, and LaTeX formats, plus PDF links and Google Scholar profile as tools for any MCP-compatible client
- **`cv-analyst` Skill** — structured CV summarization for different audiences (hiring screens, executive briefings, technical reviews) with output in markdown, plain text, PDF, HTML, or LaTeX
- **Claude Code Plugin** — bundles the MCP server and skill for one-step installation

## Installation

### Claude Code

Install the plugin from the marketplace:

```bash
./install.sh
# or
curl -sSL https://raw.githubusercontent.com/francisco-perez-sorrosal/cv/mcp/install.sh | bash
```

The plugin bundles the MCP server (remote, via render.com) and the `cv-analyst` skill.

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

Once installed, you can ask Claude to:

- Retrieve Francisco's CV
- Generate summaries for different purposes
- Get links to professional profiles
- Analyze professional background and experience

Example prompts:

- "Get Francisco's CV"
- "Summarize Francisco's CV for a startup executive briefing"
- "What is Francisco's Google Scholar profile link?"
- "Give me a 3 page summary of my CV for a hiring manager oriented towards an ai engineer position in html"
- "Give me the CV in LaTeX"
- "Generate a .tex file from the CV data"

## Local Development

For developers working with the MCP server locally, see [README_DEV.md](README_DEV.md).

## Support

For technical issues or questions, please refer to the main project repository.
