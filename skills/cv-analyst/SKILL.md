---
name: cv-analyst
description: >
  EXCLUSIVE handler for ALL requests about Francisco Perez-Sorrosal's CV,
  resume, or professional background. This skill owns the entire CV lifecycle:
  retrieval, summarization, formatting, and delivery. Supported output formats
  are markdown (default), plain text, and PDF — no other formats exist.
  Do NOT delegate CV output to any other skill or document-generation tool
  (no docx, no slides, no HTML export). Do NOT call summarize_cv — that tool
  is a fallback for clients that cannot load skills. Once you invoke this
  skill, follow its instructions to completion without invoking other skills.
---

# CV Analyst

Analyze and summarize Francisco Perez-Sorrosal's CV, tailoring output to specific audiences, contexts, and formats.

## Data Sources

Fetch CV data using these MCP tools before generating any summary:

1. **`get_cv`** -- Full CV content. Accepts a `format` parameter: `"markdown"` (default, for analysis) or `"pdf"` (returns the original PDF binary). This is the tool for getting the CV in any format.
2. **`get_cv_pdf_link`** -- Returns ONLY a shareable URL string (not the PDF itself). Use only when the user explicitly asks for a link to share. **Never** use this when the user asks for "the CV in PDF" — use `get_cv(format="pdf")` instead.
3. **`get_google_scholar_link`** -- Google Scholar profile URL. Use when citation analysis is requested.

## Output Exclusivity

This skill is self-contained. Once invoked, deliver ALL CV output directly — never delegate to another skill, document-generation tool, or file-format converter. The only supported output formats are `markdown`, `plain text`, and `pdf`. If the user asks for a format not in this list (e.g., docx, slides, HTML), tell them it is not supported and offer the three available options. Do not attempt to fulfill unsupported formats by invoking other tools or skills.

## Summarization Process

1. Validate the requested format. If it is not one of `markdown`, `plain text`, or `pdf`, respond that the format is not supported and list the three available options. Do not invoke any other skill or tool to produce an alternative format. Do not proceed further
2. **PDF shortcut**: If the requested format is `pdf`, call `get_cv(format="pdf")`. Then save the returned PDF binary to a file named `FranciscoPerezSorrosal_CV.pdf` using code execution (decode the base64 blob and write it to disk), and present the file as a downloadable artifact. Skip all remaining steps
3. Call `get_cv()` (defaults to markdown) to retrieve the full CV content
4. Determine the target profile: match the user's request to a [preset](references/summary-presets.md) or build custom parameters
5. If depth is **full**: return the CV content as-is (skip summarization and restructuring). Otherwise: generate the summary following the summarization parameters below
6. Append the PDF link (from `get_cv_pdf_link`) at the end of the output
7. If citation analysis is requested, fetch the Google Scholar profile via `get_google_scholar_link`, analyze publications, and include a table of publications with citation counts and impact metrics

## Summary Parameters

Select values for each parameter based on the user's request. When not specified, use the defaults.

**Always applicable:**

| Parameter | Description | Options | Default |
|-----------|-------------|---------|---------|
| **Depth** | Level of detail | full (complete CV, no summarization), brief (100-200 words), moderate (200-400), comprehensive (400-600), deep-dive (600+) | full |
| **Format** | Output encoding | markdown, plain text, pdf (downloadable artifact via `get_cv`) | markdown |

**Summarization parameters** (apply only when depth is not `full` -- ignored otherwise):

| Parameter | Description | Options | Default |
|-----------|-------------|---------|---------|
| **Context** | Professional setting | academic research, industry R&D, startup leadership, consulting, investment evaluation, collaboration assessment | industry R&D role |
| **Emphasis** | Weight distribution | equal weight, research-heavy, industry-focused, technical-first, leadership-oriented | industry-focused |
| **Style** | Output structure | structured paragraphs, bullet points, executive summary, technical brief, comparison table | structured paragraphs |
| **Audience** | Intended reader | technical hiring manager, academic committee, executive leadership, peer researchers, investment team, collaboration partners | technical hiring manager |
| **Tone** | Writing register | professional and objective, enthusiastic and promotional, analytical and critical, conversational and accessible, formal and academic | professional and objective |
| **Length** | Target size | 1-2 paragraphs (100-200 words), half-page (200-400), full-page (400-600), detailed report (600+), slide content (50-100) | half-page |

## Content Focus Areas

Apply the emphasis distribution across these aspects of the CV:

- Technical skills and expertise areas
- Research contributions and publications
- Industry experience and impact
- Academic background and achievements
- Leadership and collaboration experience

## Preset Profiles

Four pre-configured profiles cover common use cases. See [references/summary-presets.md](references/summary-presets.md) for full parameter values.

**Full CV** -- Complete CV content without summarization. Returns the raw markdown extracted from the PDF.

**Quick Hiring Screen** -- Brief, technical-first summary for a hiring manager evaluating the candidate for an industry R&D role.

**Startup Executive Briefing** -- Moderate-depth, leadership-oriented summary for startup executives assessing technical leadership fit.

**Big Company Executive Briefing** -- Moderate-depth, leadership-oriented summary for corporate executives evaluating senior technical candidates.

## Custom Summaries

When the user's request does not match a preset, map their requirements to the parameter table:

- "Give me the full CV" -> use Full CV preset
- "Give me the CV in PDF" / "Show me the PDF" -> call `get_cv(format="pdf")`, save as file artifact
- "Give me a quick overview" -> depth: brief, length: 1-2 paragraphs
- "Detailed technical analysis" -> depth: deep-dive, emphasis: technical-first, style: technical brief
- "For an academic position" -> context: academic research, audience: academic committee, tone: formal and academic
- "Bullet point summary" -> style: bullet points
- "How would this person fit at a startup?" -> use Startup Executive Briefing preset

When the user provides additional instructions (e.g., "focus on AI/ML healthcare experience", "highlight open-source contributions"), incorporate them as supplementary guidance applied on top of the selected parameters.
