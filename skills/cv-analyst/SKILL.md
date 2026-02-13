---
name: cv-analyst
description: >
  EXCLUSIVE handler for ALL requests about Francisco Perez-Sorrosal's CV,
  resume, or professional background. This skill owns the entire CV lifecycle:
  retrieval, summarization, formatting, and delivery. Supported output formats
  are markdown (default), plain text, PDF, and HTML — no other formats exist.
  Do NOT delegate CV output to any other skill or document-generation tool
  (no docx, no slides). HTML output uses built-in templates bundled with this
  skill — do NOT read or invoke any frontend, design, or HTML skill.
  Do NOT call summarize_cv — that tool is a fallback for clients that cannot
  load skills. Once you invoke this skill, follow its instructions to
  completion without reading or invoking other skills.
---

# CV Analyst

Analyze and summarize Francisco Perez-Sorrosal's CV, tailoring output to specific audiences, contexts, and formats.

## Data Sources

Fetch CV data using these MCP tools before generating any summary:

1. **`get_cv`** -- Full CV content. Accepts a `format` parameter: `"markdown"` (default, for analysis) or `"pdf"` (returns the original PDF binary). This is the tool for getting the CV in any format.
2. **`get_cv_pdf_link`** -- Returns a shareable PDF URL (not the PDF itself). Primary use: when the user explicitly asks for a link to share. Secondary use: failover for PDF delivery when `get_cv(format="pdf")` fails (e.g., `application/pdf` not supported) — download from this URL, save locally, and present as artifact.
3. **`get_google_scholar_link`** -- Google Scholar profile URL. Use when citation analysis is requested.

## Output Exclusivity

This skill is self-contained. Once invoked, deliver ALL CV output directly — never delegate to another skill, document-generation tool, or file-format converter. Do not read or invoke any other skill (including frontend, design, or HTML skills) — all templates, CSS, and JS are bundled in this skill's `references/` directory. The only supported output formats are `markdown`, `plain text`, `pdf`, and `html`. If the user asks for a format not in this list (e.g., docx, slides), tell them it is not supported and offer the four available options. Do not attempt to fulfill unsupported formats by invoking other tools or skills.

## Summarization Process

1. Validate the requested format. If it is not one of `markdown`, `plain text`, `pdf`, or `html`, respond that the format is not supported and list the four available options. Do not invoke any other skill or tool to produce an alternative format. Do not proceed further
2. **PDF shortcut**: If the requested format is `pdf`, call `get_cv(format="pdf")`. Then save the returned PDF binary to a file named `FranciscoPerezSorrosal_CV.pdf` using code execution (decode the base64 blob and write it to disk), and present the file as a downloadable artifact. Skip all remaining steps. **Failover**: If `get_cv(format="pdf")` returns an error or the response indicates that `application/pdf` objects are not supported, fall back to: (a) call `get_cv_pdf_link` to obtain the PDF URL, (b) download the PDF from that URL, (c) save it as `FranciscoPerezSorrosal_CV.pdf`, and (d) present the file as a downloadable artifact. Skip all remaining steps
3. **HTML generation**: If the requested format is `html` (everything needed is in this skill's `references/` — do NOT read or invoke any other skill):
   a. Call `get_cv()` to retrieve the full CV markdown
   b. If the user also requested summarization (any depth other than `full`), apply steps 5-6 to the markdown first to produce a summary. Otherwise use the full markdown
   c. Read the [HTML template](references/cv-template.html), the [CSS](references/cv-template.css), and the [JS](references/cv-template.js)
   d. Inline the assets to produce a self-contained HTML file (required for artifact sandboxes that cannot resolve sibling files):
      - Replace `<link rel="stylesheet" href="cv-template.css">` with `<style>` + CSS file contents + `</style>`
      - Replace `<script src="cv-template.js"></script>` with `<script>` + JS file contents + `</script>`
   e. Set the `.hero-label` text to match the output type: "Full CV" for depth full, "Candidate Summary" for general summaries, or the preset name (e.g., "Hiring Screen", "Executive Briefing")
   f. Convert the CV/summary content into rich HTML using the template's component classes. Map CV sections to visual components:
      - Profile/summary paragraph → `.profile-text`, key facts → `.tags > .tag`
      - Quantitative highlights (years, papers, citations, patents) → `.stats-row > .stat > .stat-number + .stat-label`
      - Skill categories → `.skills-grid > .skill-card > h3 + p`
      - Experience/achievements → `.achievements-list > .achievement > .achievement-meta + .achievement-title + p`
      - Education entries → `.edu-grid > .edu-card > .degree + .school + .year`
      - Wrap each group in `<section data-label="Name"><div class="container"><div class="section-label">NN — Label</div><h2 class="section-title">Title</h2>...</div></section>`
      - Make cards interactive: add class `expandable` to any stat, skill-card, achievement, or edu-card that has additional detail. Put the detail inside `<div class="expand-content">` and add `<span class="expand-indicator"></span>`. The component shows a + icon and expands on click to reveal the full content. Use rich formatting inside: `<strong>` for titles and names (papers, patents, projects), `<em>` for venues and the CV owner's name in author lists, `<small>` for metadata lines (authors, dates, citation counts)
      - **Data sourcing for expandable lists**: call `get_google_scholar_link()` and visit the profile page to obtain real publication data. Use this data to populate the expandable bullet-point lists in the generated HTML:
        - **Publications stat**: one `<li>` per paper — wrap title in `<a>` linking to its Google Scholar citation page, show venue, year, and citation count in `<small>`. Omit author lists for cleanliness
        - **Citations stat**: top-cited papers as bullet points — `<strong>` citation count + `<a>` linked short title in `<em>` + venue in `<small>`. Include h-index and a link to the full Google Scholar profile at the bottom
        - **Patents stat**: one `<li>` per patent — wrap title in `<a>` linking to its Google Scholar page, show patent app number and year in `<small>`
        - The template shows the HTML pattern for each list item type; populate with real data from the profile
   g. Replace everything inside `<main>` (`<!-- BODY_CONTENT -->`) with the generated section HTML
   h. Call `get_cv_pdf_link()` and replace `<!-- PDF_LINK -->` with the URL (all occurrences)
   i. Write the completed HTML to `tmp/FranciscoPerezSorrosal_CV.html` (full CV) or `tmp/FranciscoPerezSorrosal_CV_Summary.html` (summary)
   j. Open the file in the default browser: `open tmp/<filename>.html`
   k. Skip all remaining steps
4. Call `get_cv()` (defaults to markdown) to retrieve the full CV content
5. Determine the target profile: match the user's request to a [preset](references/summary-presets.md) or build custom parameters
6. If depth is **full**: return the CV content as-is (skip summarization and restructuring). Otherwise: generate the summary following the summarization parameters below
7. Append the PDF link (from `get_cv_pdf_link`) at the end of the output
8. If citation analysis is requested, fetch the Google Scholar profile via `get_google_scholar_link`, analyze publications, and include a table of publications with citation counts and impact metrics

## Summary Parameters

Select values for each parameter based on the user's request. When not specified, use the defaults.

**Always applicable:**

| Parameter | Description | Options | Default |
|-----------|-------------|---------|---------|
| **Depth** | Level of detail | full (complete CV, no summarization), brief (100-200 words), moderate (200-400), comprehensive (400-600), deep-dive (600+) | full |
| **Format** | Output encoding | markdown, plain text, pdf, html | markdown |

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
- "Give me the CV as HTML" / "HTML version" -> format: html, depth: full
- "Quick Hiring Screen in HTML" -> apply Quick Hiring Screen preset, format: html
- "Summarize for hiring managers as an HTML page" -> depth: brief, audience: technical hiring manager, format: html

When the user provides additional instructions (e.g., "focus on AI/ML healthcare experience", "highlight open-source contributions"), incorporate them as supplementary guidance applied on top of the selected parameters.
