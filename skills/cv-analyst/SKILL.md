---
name: cv-analyst
description: >
  Handler for general CV retrieval, summarization, rendering, and formatting
  requests about Francisco Perez-Sorrosal's professional background. Supported
  output formats are markdown (default), plain text, PDF, HTML, LaTeX, and Typst.
  Do NOT use for job-specific tailoring -- use the cv-tailoring skill instead
  when the user provides a job description or wants to adapt the CV for a
  specific role. Do NOT delegate CV output to document-generation tools
  (no docx, no slides). HTML output is server-rendered via
  get_cv(format="html") -- do NOT read or invoke any frontend, design, or
  HTML skill. Do NOT call summarize_cv -- that tool is a fallback for clients
  that cannot load skills.
  Trigger phrases: "LaTeX", "tex", "moderncv", "typeset CV", "generate .tex",
  "Typst", "typst", "moderner-cv", "generate .typ".
---

# CV Analyst

Analyze and summarize Francisco Perez-Sorrosal's CV, tailoring output to specific audiences, contexts, and formats.

## Data Sources

Fetch CV data using these MCP tools before generating any summary. The CV data comes from a structured YAML data layer with a semantic overlay, rendered to markdown via Jinja2 templates. For targeted questions, prefer section-specific or structured query tools over `get_cv` to save tokens.

### Full CV tools

1. **`get_cv(format, enrich)`** -- Full CV content. `format`: `"markdown"` (default, for analysis), `"pdf"` (returns the original PDF binary), `"latex"` (returns LaTeX source using moderncv package), or `"html"` (returns a self-contained interactive HTML document with theme switching, expandable cards, and print CSS), or `"typst"` (returns Typst source using moderner-cv package). `enrich` (default `true`): when enabled, the markdown, HTML, and Typst output includes semantic enrichments -- cross-references to related publications/patents and skill proficiency levels from the semantic overlay. Use when the full CV is needed or when the question spans multiple sections.
2. **`get_link(name)`** -- Returns a profile or document link by name. Available: `CV PDF` (shareable CV URL), `Google Scholar`, `LinkedIn`, `GitHub`, `Twitter`. Primary use for `CV PDF`: when the user explicitly asks for a link to share. Secondary use: failover for PDF delivery when `get_cv(format="pdf")` fails -- call `get_link("CV PDF")`, download from that URL, save locally, and present as artifact.

### Section tools (preferred for targeted queries)

1. **`list_cv_sections`** -- Lists available section names with line counts. Call first when unsure which section contains the answer. Current sections: header, quote, Profile and Goals, Professional Experience, Patents, Academic Research Experience, Skills, Courses and Certifications, Education, Leadership & Communication, Languages, Other Activities Related to CS, Hobbies and Interests.
2. **`get_cv_sections(section_names, enrich)`** -- Retrieve one or more sections in a single call. `section_names` is a list of strings (case-insensitive, `&` ignored). `enrich` (default `true`): include semantic enrichments. Reports unrecognized names with the list of available sections.

### Structured query tools (for precise, token-efficient answers)

Prefer these over `get_cv` when the user asks about a specific company, time period, topic, or entry. They return focused results without loading the entire CV.

1. **`query_work(company, start_year, end_year, topic, enrich)`** -- Filter work entries by company name, date range, or semantic topic. Returns matching entries as markdown. All parameters are optional.
2. **`get_entry(entry_id)`** -- Retrieve any resume entry by its stable ID as JSON. Entry IDs follow the `<type>-<slug>` convention (e.g., `work-yahoo-kgs-2023`, `pub-htl-acl-2019`).
3. **`list_entry_ids(section)`** -- List all entry IDs with labels, optionally filtered by section type (work, patents, publications, education, certificates, conferences, memberships, skills, book_reviews).

### Semantic query tools (for topic-based and cross-reference queries)

Use these when the user asks about themes, skill proficiency, or connections between CV entries.

1. **`query_by_topic(topic, include_subtopics)`** -- Find entries annotated with a topic from the semantic taxonomy. Returns entry IDs with labels.
2. **`get_relationships(entry_id)`** -- Get cross-references between entries (e.g., which publications came from which work experience).
3. **`get_skill_profile(topic)`** -- Get skill proficiency levels with evidence, optionally filtered by topic.
4. **`get_entry_context(entry_id)`** -- Full semantic context for an entry: topics, relationships, impact metrics, and audience-specific summaries.

## Workflow

### Step 1: Validate format

Supported formats: `markdown`, `plain text`, `pdf`, `html`, `latex`, `typst`. If the user requests anything else (docx, slides, etc.), decline and list the six available options.

### Step 2: Route by format

| Format | Action |
|--------|--------|
| **LaTeX** | Call `get_cv(format="latex")`. Save to `tmp/FranciscoPerezSorrosal_CV.tex`. Inform user it can be compiled with `pdflatex` or `latexmk -pdf`. Always renders the complete CV — summarization parameters are ignored. **Done.** |
| **PDF** | Call `get_cv(format="pdf")`. Decode base64 blob, save to `FranciscoPerezSorrosal_CV.pdf`, present as downloadable artifact. **Failover**: if the call fails, use `get_link("CV PDF")` → download → save → present. **Done.** |
| **HTML** | Call `get_cv(format="html")`. Save to `tmp/FranciscoPerezSorrosal_CV.html`. Open in browser with `open tmp/FranciscoPerezSorrosal_CV.html`. Returns a self-contained interactive page with embedded CSS/JS, 5 color themes, expandable cards, and print CSS. Always renders the complete CV — summarization parameters are ignored. **Done.** |
| **Typst** | Call `get_cv(format="typst")`. Save to `tmp/FranciscoPerezSorrosal_CV.typ`. Inform user it can be compiled with `typst compile`. Always renders the complete CV — summarization parameters are ignored. **Done.** |
| **markdown / plain text** | Continue to step 3. |

### Step 3: Fetch and summarize

1. Call `get_cv()` to retrieve the full CV in markdown
2. Match the user's request to a [preset](references/summary-presets.md) or build custom parameters from the tables below
3. If depth is **full**: return the CV content as-is. Otherwise: generate the summary applying emphasis across these dimensions:
   - Technical skills and expertise areas
   - Research contributions and publications
   - Industry experience and impact
   - Academic background and achievements
   - Leadership and collaboration experience

### Step 4: Deliver

1. Append the PDF link (from `get_link("CV PDF")`) at the end of the output
2. If citation analysis is requested, fetch the Google Scholar profile via `get_link("Google Scholar")`, analyze publications, and include a table with citation counts and impact metrics

## Summary Parameters

Select values for each parameter based on the user's request. When not specified, use the defaults.

**Always applicable:**

| Parameter | Description | Options | Default |
|-----------|-------------|---------|---------|
| **Depth** | Level of detail | full (complete CV, no summarization), brief (100-200 words), moderate (200-400), comprehensive (400-600), deep-dive (600+) | full |
| **Format** | Output encoding | markdown, plain text, pdf, html, latex, typst | markdown |

**Summarization parameters** (apply only when depth is not `full` -- ignored otherwise):

| Parameter | Description | Options | Default |
|-----------|-------------|---------|---------|
| **Context** | Professional setting | academic research, industry R&D, startup leadership, consulting, investment evaluation, collaboration assessment | industry R&D role |
| **Emphasis** | Weight distribution | equal weight, research-heavy, industry-focused, technical-first, leadership-oriented | industry-focused |
| **Style** | Output structure | structured paragraphs, bullet points, executive summary, technical brief, comparison table | structured paragraphs |
| **Audience** | Intended reader | technical hiring manager, academic committee, executive leadership, peer researchers, investment team, collaboration partners | technical hiring manager |
| **Tone** | Writing register | professional and objective, enthusiastic and promotional, analytical and critical, conversational and accessible, formal and academic | professional and objective |
| **Length** | Target size | 1-2 paragraphs (100-200 words), half-page (200-400), full-page (400-600), detailed report (600+), slide content (50-100) | half-page |

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
- "Give me the CV as HTML" / "HTML version" -> format: html (full CV only, summarization parameters ignored)
- "Give me the CV in Typst" / "Typst version" / "moderner-cv" -> format: typst (full CV only, summarization parameters ignored)

When the user provides additional instructions (e.g., "focus on AI/ML healthcare experience", "highlight open-source contributions"), incorporate them as supplementary guidance applied on top of the selected parameters.

## Boundaries

- **Supported formats**: markdown, plain text, PDF, HTML, LaTeX, Typst — no others
- **Skill handoff**: delegates to cv-tailoring when the user introduces a job description mid-conversation
- **Self-contained**: HTML is server-rendered via `get_cv(format="html")` — never read or invoke any frontend, design, or HTML skill
- **`summarize_cv` tool**: fallback for MCP clients that cannot load Agent Skills. Exposes the same parameters as a tool-prompt pattern — the client calls the tool, receives a parameterized prompt, and processes it against CV data fetched via `get_cv`. Skill-capable clients should NOT call this tool
