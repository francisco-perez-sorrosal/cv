# Skills

[Agent Skills](https://agentskills.io) for skill-compatible AI clients (Claude Code, Claude Desktop, Cursor, Gemini CLI, VS Code, and others). Each skill composes with the CV MCP server tools to provide structured workflows.

## Skills Catalog

| Skill | Purpose | Trigger Examples |
|-------|---------|-----------------|
| [cv-analyst](cv-analyst/SKILL.md) | CV retrieval, summarization, and rendering | "summarize CV", "HTML version", "LaTeX", "quick overview" |
| [cv-tailoring](cv-tailoring/SKILL.md) | Job-targeted CV tailoring with compiled PDF output | "tailor CV for this job", "adapt resume", "CV for job" |

## cv-analyst

General-purpose CV retrieval and summarization. Outputs: markdown, plain text, PDF, HTML, LaTeX.

- HTML and LaTeX are server-rendered via `get_cv(format=...)` — no client-side template assembly
- Summarization (depth, audience, tone, emphasis) applies to markdown/plain text only
- Delegates to cv-tailoring when a job description is introduced

Reference files: [summary-presets.md](cv-analyst/references/summary-presets.md)

## cv-tailoring

Job-targeted CV tailoring. Analyzes a job description, generates a `TailoringSpec`, renders a page-constrained LaTeX CV via `get_tailored_cv`, and compiles to PDF.

- Integrates with LinkedIn MCP server for job description retrieval
- 7-step workflow: obtain job context, retrieve CV, analyze, generate spec, render, integrity check, deliver
- Produces 6 deliverables: intelligence brief, repositioned CV, spec, compiled PDF, alignment assessment, positioning summary

Reference files: [methodology.md](cv-tailoring/references/methodology.md)
