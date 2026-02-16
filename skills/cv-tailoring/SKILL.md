---
name: cv-tailoring
description: >
  Tailors Francisco Perez-Sorrosal's CV to a specific job description.
  Produces a page-constrained (2-3 pages) compiled LaTeX/PDF CV optimized
  for the target role. Takes over from cv-analyst when a job description is
  provided. Orchestrates the CV MCP server (for CV content and rendering)
  and optionally the LinkedIn MCP server (for job data).
  Trigger terms: tailor CV, adapt resume, customize CV, CV for job,
  resume optimization, CV tailoring, match CV to job.
---

# CV Tailoring

Adapt Francisco's CV to a specific job description using a structured methodology that produces a compiled, page-constrained LaTeX/PDF CV.

## Prerequisites

Before starting, ensure access to:
1. A job description (provided by user, or retrieved via LinkedIn MCP tools)
2. Francisco's CV content (retrieved via the CV MCP server tools)

## Workflow

### Step 1: Obtain Job Context

One of:
- **Job description provided directly**: Use the text as-is.
- **Job search needed**: Call `explore_latest_jobs(location, keywords, distance, limit)` to scrape fresh LinkedIn results, or `query_jobs(...)` to search the cached job database with composable filters.
- **No job context**: Ask the user to either provide a job description or specify search criteria (keywords, location) to discover relevant postings.

### Step 2: Retrieve CV Content

Call the CV MCP server tools to retrieve Francisco's current CV content. Use targeted tools for efficient retrieval:
- `get_cv` -- full CV in markdown for comprehensive analysis
- `get_skill_profile` -- skill proficiency levels with evidence
- `query_by_topic` -- entries annotated with specific topics from the semantic taxonomy
- `get_entry_context` -- full semantic context for individual entries (topics, relationships, impact)

### Step 3: Apply Tailoring Methodology

Follow the full methodology in [references/methodology.md](references/methodology.md). The methodology has three analysis phases:

1. **Strategic Analysis** -- Deconstruct the job, map Francisco's experience, assess fit (1-10), identify gaps
2. **Strategic CV Repositioning** -- Reorder sections, emphasize relevant skills, mirror job language, apply professional formatting
3. **Alignment Evaluation** -- Score across 7 competency areas, produce strategic positioning summary

### Step 4: Generate TailoringSpec

Construct a `TailoringSpec` JSON from the Phase 2 analysis:

- **`job_title`**: target role title
- **`company`**: target company name
- **`job_id`**: job posting identifier -- use the LinkedIn job ID if available, otherwise a short slug derived from the role (e.g., `sr-ml-eng-2026`). Appears in the output filename to distinguish multiple applications to the same company
- **`section_order`**: list of `SectionDirective` objects -- only include sections relevant to the target role; set `include: false` for irrelevant sections. Each has `section_name`, `include` (bool), and `position` (int, controls rendering order)
- **`entry_emphasis`**: list of `EntryEmphasis` objects -- set `weight: 0` for entries that do not contribute to job fit (omitted from output), `weight: 1` for normal, `weight: 2` for highlighted. Each has `entry_id`, `weight`, and `reason`
- **`keywords`**: list of `KeywordHighlight` objects with `term` and `weight` -- terms from the job description to emphasize in the CV
- **`profile_override`**: tailored professional summary paragraph replacing the generic one (must use only existing CV content, rephrased for the role)
- **`max_pages`**: 2 or 3 -- the page budget for the compiled CV

### Step 5: Render and Compile

1. Call `get_tailored_cv(tailoring_config)` with the TailoringSpec JSON to get LaTeX source
2. Save the LaTeX source to `tmp/FranciscoPerezSorrosal_CV_<Company>_<JobID>.tex` (replace `<Company>` and `<JobID>` with values from the TailoringSpec, no spaces)
3. Compile with `pdflatex` (run twice for cross-references):
   ```
   cd tmp && pdflatex FranciscoPerezSorrosal_CV_<Company>_<JobID>.tex && pdflatex FranciscoPerezSorrosal_CV_<Company>_<JobID>.tex
   ```
4. Check the `.log` file for errors. On error: read the log, fix the LaTeX source, retry (max 2 retries)
5. On success: verify page count is within `max_pages` budget. If over budget, reduce content (increase `weight: 0` entries or tighten `profile_override`) and recompile

### Step 6: Content Integrity Check

Before delivering, verify:
- No information was fabricated during transformation
- All content in the rendered document exists in the original CV data
- The `profile_override` only rephrases existing content, never invents claims

### Step 7: Deliver Results

Produce six deliverables:
1. **Job Intelligence Brief** -- metadata table + fit score
2. **Strategically Repositioned CV (markdown)** -- full CV in markdown, reordered and emphasized for the target role. Serves as human-reviewable output before PDF compilation
3. **TailoringSpec** -- the JSON spec used for rendering (for reproducibility)
4. **Compiled PDF** -- the page-constrained tailored CV (`tmp/FranciscoPerezSorrosal_CV_<Company>_<JobID>.pdf`)
5. **Strategic Alignment Assessment** -- scoring matrix
6. **Strategic Positioning Summary** -- 400-600 words

## Tools Used

### CV MCP Server Tools

- `get_cv` -- full CV content in markdown for analysis
- `get_cv_sections` -- targeted section retrieval
- `get_skill_profile` -- skill proficiency levels with evidence
- `query_by_topic` -- find entries by semantic topic
- `get_entry_context` -- full semantic context for an entry
- `get_tailored_cv` -- render a tailored LaTeX CV from a TailoringSpec JSON

### LinkedIn MCP Tools (optional)

- `explore_latest_jobs(location, keywords, distance, limit)` -- scrape fresh LinkedIn job listings directly (no database, for exploration/testing)
- `query_jobs(company?, location?, keywords?, ...)` -- query cached job database with composable filters and configurable response sections

### Host Agent Tools

- **Write** -- save `.tex` files to `tmp/`
- **Bash** -- run `pdflatex` for compilation

## Important Constraints

- **Page constraint**: The tailored CV MUST fit within 2-3 pages. Use `max_pages` in the TailoringSpec and aggressively select content -- omit entries with `weight=0` that do not contribute to job fit.
- **Content integrity**: Never add, modify, or fabricate information not in Francisco's original CV. Only reorganize, emphasize, filter, and rephrase existing content.
- **Honest assessment**: Provide realistic scores. Acknowledge limitations while highlighting genuine strengths.
- **Professional formatting**: Use clean hierarchy and consistent structure in all deliverables.
