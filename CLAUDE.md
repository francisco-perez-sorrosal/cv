# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains Francisco Perez-Sorrosal's CV in multiple formats and implementations:

- **Main branch (`main`)**: Contains the LaTeX source CV (`2025_FranciscoPerezSorrosal_CV_English.tex`) and generated PDF
- **MCP branch (`mcp`)**: Contains a Python-based MCP (Model Context Protocol) server that serves the CV as a resource for AI systems

The repository serves as both a personal CV management system and a reference implementation of an MCP server for document serving.

## Common Commands

### LaTeX CV Management (main branch)
```bash
# Compile the CV to PDF using pdflatex
pdflatex 2025_FranciscoPerezSorrosal_CV_English.tex

# Or using latexmk (recommended for handling dependencies)
latexmk -pdf 2025_FranciscoPerezSorrosal_CV_English.tex

# Clean auxiliary files
latexmk -c 2025_FranciscoPerezSorrosal_CV_English.tex
```

### MCP Server Development (mcp branch)
```bash
# Switch to mcp branch
git checkout mcp

# Install dependencies using pixi (recommended)
pixi install

# Run MCP server locally
pixi run mcps --transport stdio

# Run with different transport types
pixi run mcps --transport sse
pixi run mcps --transport streamable-http

# Install MCP server for Claude Desktop
./install_claude_desktop_mcp.sh

# Development tasks
pixi run test      # Run tests
pixi run lint      # Check code quality
pixi run format    # Format code
pixi run build     # Build package
```

### Git Workflow
```bash
# List all branches
git branch -a

# Check current status
git status

# View recent commits
git log --oneline -10
```

## Architecture and Structure

### Main Branch Structure
- `2025_FranciscoPerezSorrosal_CV_English.tex` - LaTeX source file containing the complete CV
- `2025_FranciscoPerezSorrosal_CV_English.pdf` - Generated PDF output
- `.gitignore` - Ignores LaTeX auxiliary files and common editor artifacts

### MCP Branch Structure (Python Project)
```
src/cv_mcp_server/
├── __init__.py
└── main.py              # FastAPI-based MCP server implementation
config/
└── claude.json          # Claude Desktop MCP configuration
pyproject.toml           # Python project configuration with pixi tasks
requirements.txt         # Python dependencies for deployment
runtime.txt             # Python version specification
Dockerfile              # Container configuration
README.md               # Detailed MCP server documentation
```

### Key Components

#### LaTeX CV (`2025_FranciscoPerezSorrosal_CV_English.tex`)
- Uses `moderncv` document class with classic green theme
- Structured sections: Profile, Experience, Patents, Education, Skills, Languages
- Extensive professional experience spanning academic research and industry R&D
- Focus on AI/ML, distributed systems, and scalable architectures

#### MCP Server (`src/cv_mcp_server/main.py`)
- FastAPI-based server using the `mcp` library
- Serves CV as markdown via `pymupdf4llm` for AI consumption
- Provides tools for CV analysis and summarization
- Supports multiple transport protocols (stdio, sse, streamable-http)
- Includes comprehensive prompts for different use cases (hiring screens, executive briefings)

## Development Guidelines

### When Working with LaTeX (main branch)
- You are an expert editor in latex format, with a background of computer science, research, and software engineering.
- The CV is comprehensive and serves as the authoritative source
- Auxiliary files (.aux, .log, .out, etc.) are gitignored
- The instructions to use the `moderncv` package can be found in the document @.claude/docs/moderncv_userguide.txt
- Extract and Read the content of the `moderncv` pdf
- After you read the `moderncv` instructions, you are an expert, so use the package conventions for formatting
- Maintain chronological order in experience sections, with recent years first

### When Working with MCP Server (mcp branch)
- Follow Python packaging best practices with src/ layout
- Use pixi for dependency management and task execution
- The server stateless_http mode is configurable via environment variables
- MCP resources use custom URI scheme `cvfps://`
- Tool functions provide different levels of CV analysis

### Deployment Considerations
- MCP server configured for render.com deployment
- Environment variables: `TRANSPORT`, `PORT`, `HOST`
- Remote MCP configuration uses `npx mcp-remote`
- Local development supports multiple transport protocols

## Important Notes

- The CV contains real professional information and should be handled appropriately
- MCP server includes usage tracking via mcpcat
- Both branches serve different purposes but reference the same CV content
- The repository demonstrates both traditional document management and modern AI integration patterns
- The main README.md file in the mcp branch is README_USER.md. To make this possible in github, a symlink in the @.github/ directory named README.md points to the file README_USER.md in the project root