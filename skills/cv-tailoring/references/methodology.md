# CV Tailoring Methodology

## Objective

Analyze a target job posting and strategically reposition Francisco's CV to showcase his most relevant qualifications while maintaining complete content integrity. Approach this as a senior technical recruiter specializing in CS, ML, and AI roles -- evaluate from the hiring side, not the candidate side. Focus on strategic presentation rather than content modification.

## Phase 1: Strategic Analysis

### Job Deconstruction
Extract from the job description:
- Key requirements and responsibilities
- Technical stack and tools
- Company culture indicators
- Seniority expectations

### Candidate Mapping
Identify Francisco's experiences that align with job priorities. Focus on:
- Direct technical skill matches
- Transferable experience from distributed systems, ML/AI, and software engineering
- Leadership and collaboration evidence

### Initial Fit Assessment
Evaluate compatibility on a 1-10 scale based on:
- Technical skills overlap
- Experience level alignment
- Role compatibility

**Scoring Guide:**
- 1-3: Poor fit (missing core requirements)
- 4-6: Moderate fit (some alignment, significant gaps)
- 7-8: Strong fit (most requirements met)
- 9-10: Excellent fit (near-perfect match)

### Gap Assessment
Recognize misalignments or areas requiring strategic positioning. Be specific about what is missing vs. what can be positioned differently.

## Phase 2: Strategic CV Repositioning

### Content Organization
- Reorder CV sections to lead with most relevant qualifications
- Restructure bullet points to emphasize job-relevant achievements first
- Position key technical skills prominently when they match requirements
- Elevate distributed systems and software engineering experience when relevant

### Strategic Emphasis
- Highlight terminology and keywords that mirror job posting language
- Emphasize quantifiable achievements that relate to role expectations
- Spotlight technologies and methodologies mentioned in job requirements
- Showcase distributed systems expertise (scalability, performance, architecture) when applicable
- Feature software engineering best practices and development experience for technical roles
- Connect AI/ML work with underlying software engineering and systems foundations

### Professional Formatting
- Use H2 headers for major sections (Summary, Experience, Skills, Education)
- Apply H3 headers for job titles and educational institutions
- Maintain consistent bullet point structure with action verbs
- Ensure clean hierarchy and scannable layout
- Create clear connections between diverse technical backgrounds (AI/ML, distributed systems, software engineering)

## Phase 3: Alignment Evaluation

### Scoring Matrix (0-10 scale)

Produce a table with columns: Competency Area, Score, Strategic Rationale

| Competency Area | What to Assess |
|----------------|----------------|
| Core Technical Skills | Alignment between technical expertise and job requirements |
| Experience Depth | How experience level matches role seniority |
| Domain Knowledge | Relevance of industry background to target company/sector |
| Role-Specific Capabilities | Match between demonstrated abilities and job responsibilities |
| Technology Stack Alignment | Overlap between technical tools and job requirements |
| Growth Trajectory | Potential to advance within role and company |
| Cultural Integration | Likelihood of fitting company culture from available indicators |

## Phase 4: Rendered Output

### TailoringSpec Generation
Construct a TailoringSpec JSON object from the Phase 2 analysis:
- `job_title`: Target position title
- `company`: Target company name
- `job_id`: Job posting identifier (LinkedIn job ID, requisition number, or short slug). Used in output filenames to distinguish multiple applications to the same company.
- `section_order`: Ordered list of sections to include. Each has `section_name`, `include` (true/false), `position` (0-indexed render order). Omit sections that add no value for this role.
- `entry_emphasis`: Per-entry weight assignments. Use `weight: 0` to omit irrelevant entries. Use `weight: 2` to highlight the most relevant ones. Include `reason` for audit trail.
- `keywords`: Job-relevant terms to bold in the output. Extract from Phase 1 job deconstruction.
- `profile_override`: Tailored professional summary rewritten from existing CV content (never fabricate).
- `max_pages`: Target page count (2 or 3). Use 2 for focused roles, 3 when broader experience is relevant.

### LaTeX Rendering
Call `get_tailored_cv` with the TailoringSpec JSON to get compilable LaTeX source.

### Compilation
1. Save the LaTeX source to `tmp/FranciscoPerezSorrosal_CV_<Company>_<JobID>.tex`
2. Run `pdflatex` twice (second pass resolves cross-references)
3. Check the `.log` file for errors
4. On error: read the log, identify the issue, fix the LaTeX source, save, and recompile (max 2 retries)
5. On success: verify page count is within `max_pages` budget

### Content Integrity Check
Before delivering, verify:
- No information was fabricated during transformation
- All content in the rendered document exists in the original CV data
- The profile_override only rephrases existing content

## Deliverables Specification

### 1. Job Intelligence Brief

**Header:** Job ID with clickable URL link and complete job title

**Initial Fit Assessment:** Overall compatibility score (1-10) with brief justification
- Overall Fit Score: X/10 - One sentence explaining the primary reasons for this initial assessment

**Metadata Table:**
- Company name and industry
- Location and remote options
- Employment type
- Experience level required
- Salary range (if disclosed)
- Key technical requirements
- Application deadline (if specified)
- Direct application URL

### 2. Strategically Repositioned CV

Full CV in markdown format optimized for the specific role:
- Contact information prominently displayed
- Professional summary tailored to role (if applicable)
- Experience section ordered by relevance to target position
- Skills section highlighting job-relevant technologies
- Consistent formatting with clear visual hierarchy

### 3. Strategic Alignment Assessment

Scoring matrix table as described in Phase 3.

### 4. Strategic Positioning Summary (400-600 words)

- **Competitive Advantages** (150-200 words): Strongest qualifications directly addressing role requirements
- **Strategic Challenges** (100-150 words): Gaps and recommended mitigation strategies
- **Value Proposition** (150-250 words): Unique combination of skills and experience for this opportunity

### 5. Compiled PDF

LaTeX-rendered CV (moderncv format) compiled to PDF, constrained to 2-3 pages. Sections reordered by job relevance, entries filtered for fit, keywords highlighted.

## Methodology Notes

- **Strategic Focus**: Prioritize job description alignment above all. Every positioning decision should demonstrate fit for this specific role.
- **Honest Assessment**: Provide realistic scores. Acknowledge limitations while highlighting genuine strengths.
