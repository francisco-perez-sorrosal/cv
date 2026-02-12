---
name: cv-analyst
description: >
  Analyzes and summarizes Francisco Perez-Sorrosal's CV for different audiences,
  contexts, and formats. Fetches CV data via MCP tools and applies structured
  summarization with configurable depth, emphasis, audience, tone, and style.
  Includes preset profiles for common scenarios: quick hiring screen, startup
  executive briefing, big company executive briefing. Supports citation analysis
  via Google Scholar when requested. Trigger terms: summarize CV, CV summary,
  hiring screen, executive briefing, CV analysis, professional background,
  candidate overview, career summary, qualifications review.
---

# CV Analyst

Analyze and summarize Francisco Perez-Sorrosal's CV, tailoring output to specific audiences, contexts, and formats.

## Data Sources

Fetch CV data using these MCP tools before generating any summary:

1. **`get_cv`** -- Full CV in markdown format (extracted from PDF). Always call this first.
2. **`get_cv_pdf_link`** -- Direct URL to the CV PDF on GitHub. Append to every summary.
3. **`get_google_scholar_link`** -- Google Scholar profile URL. Use when citation analysis is requested.

## Summarization Process

1. Call `get_cv` to retrieve the full CV content
2. Determine the target profile: match the user's request to a [preset](references/summary-presets.md) or build custom parameters
3. Generate the summary following the parameter values below
4. Append the PDF link (from `get_cv_pdf_link`) at the end of the output
5. If citation analysis is requested, fetch the Google Scholar profile via `get_google_scholar_link`, analyze publications, and include a table of publications with citation counts and impact metrics

## Summary Parameters

Select values for each parameter based on the user's request. When not specified, use the defaults.

| Parameter | Description | Options | Default |
|-----------|-------------|---------|---------|
| **Depth** | Level of detail | brief (100-200 words), moderate (200-400), comprehensive (400-600), deep-dive (600+) | comprehensive |
| **Context** | Professional setting | academic research, industry R&D, startup leadership, consulting, investment evaluation, collaboration assessment | industry R&D role |
| **Emphasis** | Weight distribution | equal weight, research-heavy, industry-focused, technical-first, leadership-oriented | technical-first |
| **Style** | Output structure | structured paragraphs, bullet points, executive summary, technical brief, comparison table | structured paragraphs |
| **Audience** | Intended reader | technical hiring manager, academic committee, executive leadership, peer researchers, investment team, collaboration partners | technical hiring manager |
| **Tone** | Writing register | professional and objective, enthusiastic and promotional, analytical and critical, conversational and accessible, formal and academic | professional and objective |
| **Format** | Output encoding | markdown, plain text | markdown |
| **Length** | Target size | 1-2 paragraphs (100-200 words), half-page (200-400), full-page (400-600), detailed report (600+), slide content (50-100) | half-page |

## Content Focus Areas

Apply the emphasis distribution across these aspects of the CV:

- Technical skills and expertise areas
- Research contributions and publications
- Industry experience and impact
- Academic background and achievements
- Leadership and collaboration experience

## Preset Profiles

Three pre-configured profiles cover common use cases. See [references/summary-presets.md](references/summary-presets.md) for full parameter values.

**Quick Hiring Screen** -- Brief, technical-first summary for a hiring manager evaluating the candidate for an industry R&D role.

**Startup Executive Briefing** -- Moderate-depth, leadership-oriented summary for startup executives assessing technical leadership fit.

**Big Company Executive Briefing** -- Moderate-depth, leadership-oriented summary for corporate executives evaluating senior technical candidates.

## Custom Summaries

When the user's request does not match a preset, map their requirements to the parameter table:

- "Give me a quick overview" -> depth: brief, length: 1-2 paragraphs
- "Detailed technical analysis" -> depth: deep-dive, emphasis: technical-first, style: technical brief
- "For an academic position" -> context: academic research, audience: academic committee, tone: formal and academic
- "Bullet point summary" -> style: bullet points
- "How would this person fit at a startup?" -> use Startup Executive Briefing preset

When the user provides additional instructions (e.g., "focus on AI/ML healthcare experience", "highlight open-source contributions"), incorporate them as supplementary guidance applied on top of the selected parameters.
