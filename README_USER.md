# CV MCP Server

A Model Context Protocol (MCP) server that provides access to Francisco Perez-Sorrosal's CV and professional information for AI systems like Claude Desktop/Code.

## What is this?

This MCP server allows AI assistants to access and analyze Francisco's CV data, including:

- Complete CV content in markdown format
- CV summarization tools for different contexts (hiring screens, executive briefings)
- Direct links to CV PDF and Google Scholar profile
- Professional background analysis

## Installation

### For Claude Users

You can use the script `install_claude_mcp.sh` to add it automatically to your Claude Desktop or Code configuration. This will add the configuration in the `config/claude.json` file to your Claude Desktop or Code instances.

**Installation script usage:**
```bash
# For Claude Desktop
./install_claude_mcp.sh desktop

# For Claude Code (current directory)
./install_claude_mcp.sh code

# For Claude Code (custom project directory)
./install_claude_mcp.sh code /path/to/your/project
```

#### Claude Desktop Details

The script above adds the following configuration to your Claude Desktop settings file:

**Location of MCP settings file:**

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Added configuration:**

```json
{
  "mcpServers": {
    ...
    # The entry below is added by the install script
    "fps_cv_mcp": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://fps-cv.onrender.com/mcp""
      ]
    }
  }
}
```

**Note:** SSE transport has been DEPRECATED. The server now uses `streamable-http` transport instead.

#### Claude Code

**Location of MCP settings file:**

- `${YOUR_PROJECT_DIR}/.mcp.json`

In the same way, the script adds the same mcp server configuration above to your Claude Code project's `.mcp.json` file. This will make the MCP's functionality accessible to your Claude Code project.

### Restart Claude Desktop/Code

After adding the configuration, restart Claude Desktop/Code instance for the changes to take effect.

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

## Local Development

For developers working with the MCP server locally:

### Available Commands

```bash
# Main command to run the MCP server
pixi run cv-mcp-server

# Alternative aliases
pixi run start           # Generic start alias
pixi run mcps            # Short alias

# Run with specific transport (SSE deprecated)
TRANSPORT=stdio pixi run cv-mcp-server              # Default: stdio
TRANSPORT=streamable-http pixi run cv-mcp-server    # For HTTP/web clients
```

### Transport Options

- **`stdio`** (default): Standard input/output transport for local development
- **`streamable-http`**: HTTP-based transport for web clients and remote access
- **`sse`**: ⚠️ **DEPRECATED** - No longer supported, use `streamable-http` instead

### Development Workflow

1. Clone the repository and switch to the `mcp` branch:
   ```bash
   git clone https://github.com/francisco-perez-sorrosal/cv.git
   cd cv
   git checkout mcp
   ```

2. Install dependencies:
   ```bash
   pixi install
   ```

3. Run the server:
   ```bash
   pixi run cv-mcp-server
   ```

## Support

This is a personal CV serving system. For technical issues or questions, please refer to the main project repository.
