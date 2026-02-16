---
name: cv-analyst
description: >
  Handler for general CV retrieval, summarization, rendering, and formatting
  requests about Francisco Perez-Sorrosal's professional background. Supported
  output formats are markdown (default), plain text, PDF, HTML, and LaTeX.
  Do NOT use for job-specific tailoring -- use the cv-tailoring skill instead
  when the user provides a job description or wants to adapt the CV for a
  specific role. Do NOT delegate CV output to document-generation tools
  (no docx, no slides). HTML output uses built-in templates bundled with this
  skill -- do NOT read or invoke any frontend, design, or HTML skill.
  Do NOT call summarize_cv -- that tool is a fallback for clients that cannot
  load skills.
  Trigger phrases: "LaTeX", "tex", "moderncv", "typeset CV", "generate .tex".
---

# CV Analyst

Analyze and summarize Francisco Perez-Sorrosal's CV, tailoring output to specific audiences, contexts, and formats.

## Data Sources

Fetch CV data using these MCP tools before generating any summary. The CV data comes from a structured YAML data layer with a semantic overlay, rendered to markdown via Jinja2 templates. For targeted questions, prefer section-specific or structured query tools over `get_cv` to save tokens.

### Full CV tools

1. **`get_cv(format, enrich)`** -- Full CV content. `format`: `"markdown"` (default, for analysis), `"pdf"` (returns the original PDF binary), or `"latex"` (returns LaTeX source using moderncv package). `enrich` (default `true`): when enabled, the markdown output includes semantic enrichments -- cross-references to related publications/patents and skill proficiency levels from the semantic overlay. Use when the full CV is needed or when the question spans multiple sections.
2. **`get_link(name)`** -- Returns a profile or document link by name. Available: `CV PDF` (shareable CV URL), `Google Scholar`, `LinkedIn`, `GitHub`, `Twitter`. Primary use for `CV PDF`: when the user explicitly asks for a link to share. Secondary use: failover for PDF delivery when `get_cv(format="pdf")` fails -- call `get_link("CV PDF")`, download from that URL, save locally, and present as artifact.

### Section tools (preferred for targeted queries)

1. **`list_cv_sections`** -- Lists available section names with line counts. Call first when unsure which section contains the answer. Current sections: header, quote, Profile and Goals, Professional Experience, Patents, Academic Research Experience, Skills, Courses and Certifications, Education, Leadership & Communication, Languages, Other Activities Related to CS, Hobbies and Interests.
2. **`get_cv_sections(section_names, enrich)`** -- Retrieve one or more sections in a single call. `section_names` is a list of strings (case-insensitive, `&` ignored). `enrich` (default `true`): include semantic enrichments. Reports unrecognized names with the list of available sections.

### Structured query tools (for precise, token-efficient answers)

Prefer these over `get_cv` when the user asks about a specific company, time period, topic, or entry. They return focused results without loading the entire CV.

1. **`query_work(company, start_year, end_year, topic, enrich)`** -- Filter work entries by company name, date range, or semantic topic. Returns matching entries as markdown. All parameters are optional.
2. **`get_entry(entry_id)`** -- Retrieve any resume entry by its stable ID as JSON. Entry IDs follow the `<type>-<slug>` convention (e.g., `work-yahoo-kgs-2023`, `pub-htl-acl-2019`).
3. **`list_entry_ids(section)`** -- List all entry IDs with labels, optionally filtered by section type (work, patents, publications, education, certificates, conferences, memberships, skills).

### Semantic query tools (for topic-based and cross-reference queries)

Use these when the user asks about themes, skill proficiency, or connections between CV entries.

1. **`query_by_topic(topic, include_subtopics)`** -- Find entries annotated with a topic from the semantic taxonomy. Returns entry IDs with labels.
2. **`get_relationships(entry_id)`** -- Get cross-references between entries (e.g., which publications came from which work experience).
3. **`get_skill_profile(topic)`** -- Get skill proficiency levels with evidence, optionally filtered by topic.
4. **`get_entry_context(entry_id)`** -- Full semantic context for an entry: topics, relationships, impact metrics, and audience-specific summaries.

## Output Exclusivity

This skill handles untailored CV delivery. Once invoked, deliver output directly -- never delegate to another skill except cv-tailoring when the user introduces a job description mid-conversation. Do not read or invoke any other skill (including frontend, design, or HTML skills) -- all templates, CSS, and JS are bundled in this skill's `references/` directory. The only supported output formats are `markdown`, `plain text`, `pdf`, `html`, and `latex`. If the user asks for a format not in this list (e.g., docx, slides), tell them it is not supported and offer the five available options. Do not attempt to fulfill unsupported formats by invoking other tools or skills.

## Summarization Process

1. Validate the requested format. If it is not one of `markdown`, `plain text`, `pdf`, `html`, or `latex`, respond that the format is not supported and list the five available options. Do not invoke any other skill or tool to produce an alternative format. Do not proceed further
2. **LaTeX shortcut**: If the requested format is `latex`, call `get_cv(format="latex")`. Save the returned LaTeX source to `tmp/FranciscoPerezSorrosal_CV.tex`. Inform the user that the `.tex` file is ready and can be compiled with `pdflatex FranciscoPerezSorrosal_CV.tex` or `latexmk -pdf FranciscoPerezSorrosal_CV.tex`. LaTeX always renders the complete CV document -- summarization parameters are ignored. Skip all remaining steps
3. **PDF shortcut**: If the requested format is `pdf`, call `get_cv(format="pdf")`. Then save the returned PDF binary to a file named `FranciscoPerezSorrosal_CV.pdf` using code execution (decode the base64 blob and write it to disk), and present the file as a downloadable artifact. Skip all remaining steps. **Failover**: If `get_cv(format="pdf")` returns an error or the response indicates that `application/pdf` objects are not supported, fall back to: (a) call `get_link("CV PDF")` to obtain the PDF URL, (b) download the PDF from that URL, (c) save it as `FranciscoPerezSorrosal_CV.pdf`, and (d) present the file as a downloadable artifact. Skip all remaining steps
4. **HTML generation**: If the requested format is `html` (everything needed is in this skill's `references/` — do NOT read or invoke any other skill):
   a. Call `get_cv()` to retrieve the full CV markdown
   b. If the user also requested summarization (any depth other than `full`), apply steps 6-7 to the markdown first to produce a summary. Otherwise use the full markdown
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
      - **Data sourcing for expandable lists**: call `get_link("Google Scholar")` and visit the profile page to obtain real publication data. Use this data to populate the expandable bullet-point lists in the generated HTML:
        - **Publications stat**: one `<li>` per paper — wrap title in `<a>` linking to its Google Scholar citation page, show venue, year, and citation count in `<small>`. Omit author lists for cleanliness
        - **Citations stat**: top-cited papers as bullet points — `<strong>` citation count + `<a>` linked short title in `<em>` + venue in `<small>`. Include h-index and a link to the full Google Scholar profile at the bottom
        - **Patents stat**: one `<li>` per patent — wrap title in `<a>` linking to its Google Scholar page, show patent app number and year in `<small>`
        - The template shows the HTML pattern for each list item type; populate with real data from the profile
   g. Replace everything inside `<main>` (`<!-- BODY_CONTENT -->`) with the generated section HTML
   h. Call `get_cv_pdf_link()` and replace `<!-- PDF_LINK -->` with the URL (all occurrences)
   i. Write the completed HTML to `tmp/FranciscoPerezSorrosal_CV.html` (full CV) or `tmp/FranciscoPerezSorrosal_CV_Summary.html` (summary)
   j. Open the file in the default browser: `open tmp/<filename>.html`
   k. Skip all remaining steps
5. Call `get_cv()` (defaults to markdown) to retrieve the full CV content
6. Determine the target profile: match the user's request to a [preset](references/summary-presets.md) or build custom parameters
7. If depth is **full**: return the CV content as-is (skip summarization and restructuring). Otherwise: generate the summary following the summarization parameters below
8. Append the PDF link (from `get_link("CV PDF")`) at the end of the output
9. If citation analysis is requested, fetch the Google Scholar profile via `get_link("Google Scholar")`, analyze publications, and include a table of publications with citation counts and impact metrics

## Summary Parameters

Select values for each parameter based on the user's request. When not specified, use the defaults.

**Always applicable:**

| Parameter | Description | Options | Default |
|-----------|-------------|---------|---------|
| **Depth** | Level of detail | full (complete CV, no summarization), brief (100-200 words), moderate (200-400), comprehensive (400-600), deep-dive (600+) | full |
| **Format** | Output encoding | markdown, plain text, pdf, html, latex | markdown |

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

**Full CV** -- Complete CV content without summarization. Returns the full markdown rendered from the structured data layer.

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
- "Give me the CV in LaTeX" / "Generate a .tex file" / "moderncv version" -> format: latex (full CV only, summarization parameters ignored)
- "Give me the CV as HTML" / "HTML version" -> format: html, depth: full
- "Quick Hiring Screen in HTML" -> apply Quick Hiring Screen preset, format: html
- "Summarize for hiring managers as an HTML page" -> depth: brief, audience: technical hiring manager, format: html

When the user provides additional instructions (e.g., "focus on AI/ML healthcare experience", "highlight open-source contributions"), incorporate them as supplementary guidance applied on top of the selected parameters.
