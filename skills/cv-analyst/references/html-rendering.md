# HTML Rendering Guide

Render CV content as a self-contained HTML page using the templates bundled in this skill's `references/` directory. Do NOT read or invoke any other skill for HTML output.

## Process

1. Call `get_cv()` to retrieve the full CV markdown
2. If the user requested summarization (depth other than `full`), apply summarization to the markdown first
3. Read the [HTML template](cv-template.html), [CSS](cv-template.css), and [JS](cv-template.js)
4. Inline assets to produce a self-contained HTML file (required for artifact sandboxes):
   - Replace `<link rel="stylesheet" href="cv-template.css">` with `<style>` + CSS contents + `</style>`
   - Replace `<script src="cv-template.js"></script>` with `<script>` + JS contents + `</script>`
5. Set `.hero-label` text: "Full CV" for depth full, "Candidate Summary" for summaries, or the preset name
6. Convert CV content into rich HTML using the template's component classes (see mapping below)
7. Replace everything inside `<main>` (`<!-- BODY_CONTENT -->`) with the generated HTML
8. Call `get_cv_pdf_link()` and replace `<!-- PDF_LINK -->` with the URL (all occurrences)
9. Write to `tmp/FranciscoPerezSorrosal_CV.html` (full) or `tmp/FranciscoPerezSorrosal_CV_Summary.html` (summary)
10. Open in browser: `open tmp/<filename>.html`

## Section-to-Component Mapping

| CV content | HTML component |
|------------|----------------|
| Profile/summary paragraph | `.profile-text`, key facts as `.tags > .tag` |
| Quantitative highlights (years, papers, citations, patents) | `.stats-row > .stat > .stat-number + .stat-label` |
| Skill categories | `.skills-grid > .skill-card > h3 + p` |
| Experience/achievements | `.achievements-list > .achievement > .achievement-meta + .achievement-title + p` |
| Education entries | `.edu-grid > .edu-card > .degree + .school + .year` |

Wrap each group in:
```html
<section data-label="Name">
  <div class="container">
    <div class="section-label">NN — Label</div>
    <h2 class="section-title">Title</h2>
    ...
  </div>
</section>
```

## Interactive Cards

Add class `expandable` to any stat, skill-card, achievement, or edu-card that has additional detail. Put detail inside `<div class="expand-content">` and add `<span class="expand-indicator"></span>`. The component shows a + icon and expands on click.

Use rich formatting inside expanded content: `<strong>` for titles/names, `<em>` for venues and the CV owner's name in author lists, `<small>` for metadata lines.

## Data Sourcing for Expandable Lists

Call `get_link("Google Scholar")` and visit the profile page to obtain real publication data:

- **Publications stat**: one `<li>` per paper — wrap title in `<a>` linking to its Google Scholar citation page, venue/year/citation count in `<small>`
- **Citations stat**: top-cited papers as bullet points — `<strong>` citation count + `<a>` linked title in `<em>` + venue in `<small>`. Include h-index and link to full profile
- **Patents stat**: one `<li>` per patent — wrap title in `<a>` linking to Google Scholar page, patent number and year in `<small>`
