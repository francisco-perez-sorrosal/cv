"""Template-based renderers for the Resume model.

Uses Jinja2 templates to generate markdown and LaTeX output from structured
CV data. Supports both full-document and per-section rendering for markdown,
and full-document rendering for LaTeX.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from cv_mcp_server.models.resume import InstitutionType, Resume, WorkEntry
from cv_mcp_server.store import ResumeStore

TEMPLATES_DIR = Path(__file__).parent / "templates"


def render_markdown(store: ResumeStore, *, enrich: bool = True) -> str:
    """Render a complete Resume as markdown."""
    sections = render_sections(store, enrich=enrich)
    return "\n\n".join(sections.values()) + "\n"


def render_sections(store: ResumeStore, *, enrich: bool = True) -> OrderedDict[str, str]:
    """Render the Resume into named sections, preserving order.

    Returns an OrderedDict mapping section name -> rendered markdown.
    Only non-empty sections are included.
    """
    env = _create_env(store)
    template = env.get_template("cv.md.j2")
    context = _template_context(store, enrich)
    raw = template.render(**context)
    return _parse_sections(raw)


def section_names(store: ResumeStore, *, enrich: bool = True) -> list[str]:
    """Return available section names for this resume."""
    return list(render_sections(store, enrich=enrich).keys())


def get_section(store: ResumeStore, name: str, *, enrich: bool = True) -> str | None:
    """Look up a section by name (case-insensitive, '&'-insensitive)."""
    normalized = _normalize(name)
    for key, content in render_sections(store, enrich=enrich).items():
        if _normalize(key) == normalized:
            return content
    return None


def render_work_entry(w: WorkEntry, store: ResumeStore, *, enrich: bool = True) -> str:
    """Render a single work entry with its nested projects."""
    env = _create_env(store)
    template = env.get_template("_work_entry.md.j2")
    context: dict = {"w": w}
    context["project_links"] = _build_project_links(store) if enrich else {}
    return _clean_whitespace(template.render(**context))


# --- Internal ---


def _create_env(store: ResumeStore) -> Environment:
    """Create a Jinja2 environment with custom filters."""
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=False,
    )
    env.filters["inst_name"] = _make_inst_name_filter(store.resume)
    env.filters["period"] = _period_filter
    env.filters["patent_status"] = _patent_status_filter
    return env


def _template_context(store: ResumeStore, enrich: bool) -> dict:
    """Build template context with pre-filtered lists and optional semantic data."""
    resume = store.resume
    industry, academic = [], []
    for w in resume.work:
        if _is_academic_work(w, store):
            academic.append(w)
        else:
            industry.append(w)

    # Conferences: consolidate reviewers by name, combine speaker/attendee list
    reviewer_map: dict[str, list[str]] = {}
    for c in resume.conferences:
        if c.role == "reviewer":
            reviewer_map.setdefault(c.name, []).append(c.date)
    reviewer_groups = [
        {"name": name, "years": " and ".join(sorted(years))}
        for name, years in reviewer_map.items()
    ]

    non_reviewers = [c for c in resume.conferences if c.role != "reviewer"]
    conference_list = sorted(non_reviewers, key=lambda c: c.date, reverse=True)

    # Memberships: separate committer contributions from organizational affiliations
    committers = [m for m in resume.memberships if m.role and m.role.lower() == "committer"]
    members = [m for m in resume.memberships if not m.role or m.role.lower() != "committer"]

    # Publications: sorted chronologically descending, with total citations
    sorted_publications = sorted(
        resume.publications, key=lambda p: p.release_date, reverse=True,
    )
    total_citations = sum(p.citations for p in resume.publications)

    # Academic publications: those published within academic work date ranges
    academic_years: set[int] = set()
    for w in academic:
        s = int(w.start_date[:4])
        e = int(w.end_date[:4]) if w.end_date else s
        academic_years.update(range(s, e + 1))
    academic_publications = [
        p for p in sorted_publications
        if int(p.release_date[:4]) in academic_years
    ]

    b = resume.personal_info
    contact_parts = []
    if b.location.city:
        loc = b.location.city
        if b.location.region:
            loc += f", {b.location.region}"
        contact_parts.append(loc)
    if b.email:
        contact_parts.append(b.email)
    if b.phone:
        contact_parts.append(b.phone)

    profile_links = [f"[{p.network}]({p.url})" for p in b.profiles if p.url]

    if enrich:
        project_links = _build_project_links(store)
        skill_levels = _build_skill_levels(store)
    else:
        project_links = {}
        skill_levels = {}

    return {
        "resume": resume,
        "industry_work": industry,
        "academic_work": academic,
        "reviewer_groups": reviewer_groups,
        "conference_list": conference_list,
        "committers": committers,
        "members": members,
        "sorted_publications": sorted_publications,
        "academic_publications": academic_publications,
        "total_citations": total_citations,
        "contact_parts": contact_parts,
        "profile_links": profile_links,
        "project_links": project_links,
        "skill_levels": skill_levels,
    }


def _is_academic_work(w: WorkEntry, store: ResumeStore) -> bool:
    """Classify a work entry as academic research.

    Academic = university institution + Researcher or PhD Candidate role.
    University entries with other roles (lecturer, sysadmin) stay in industry.
    """
    inst = store.resume.institution_by_id(w.institution_id)
    if not inst or inst.type != InstitutionType.university:
        return False
    academic_roles = {"researcher", "phd candidate"}
    return any(r.lower() in academic_roles for r in w.roles)


def _build_project_links(store: ResumeStore) -> dict[str, list[dict]]:
    """Build project ID -> related entries (publications, patents, conferences)."""
    displayable = {"published-as", "patented-as", "presented-at"}
    project_links: dict[str, list[dict]] = {}
    for rel in store.semantics.relationships:
        if rel.type.value in displayable:
            target = store.entry_by_id(rel.target_id)
            if target:
                project_links.setdefault(rel.source_id, []).append({
                    "type": rel.type.value,
                    "label": store.entry_label(rel.target_id),
                    "target": target,
                })
    return project_links


def _build_skill_levels(store: ResumeStore) -> dict[str, str]:
    """Build normalized skill name -> proficiency level string."""
    skill_levels: dict[str, str] = {}
    for sp in store.semantics.skill_proficiency:
        topic = store.semantics.taxonomy.topic_by_id(sp.topic_id)
        if topic:
            skill_levels[topic.label.lower()] = sp.level.value.title()
            for alias in topic.aliases:
                skill_levels[alias.lower()] = sp.level.value.title()
    return skill_levels


def _parse_sections(raw: str) -> OrderedDict[str, str]:
    """Parse section markers from rendered output into an OrderedDict."""
    sections: OrderedDict[str, str] = OrderedDict()
    pattern = re.compile(
        r"<!-- SECTION: (.+?) -->\n(.*?)<!-- END_SECTION: \1 -->",
        re.DOTALL,
    )
    for match in pattern.finditer(raw):
        name = match.group(1).strip()
        content = _clean_whitespace(match.group(2))
        if content:
            sections[name] = content
    return sections


def _clean_whitespace(text: str) -> str:
    """Normalize excessive blank lines and strip edges."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _normalize(name: str) -> str:
    """Lowercase, strip '&', and collapse whitespace for fuzzy matching."""
    return re.sub(r"\s+", " ", name.lower().replace("&", "").strip())


# --- Jinja2 filters ---


def _make_inst_name_filter(resume: Resume):
    """Create an inst_name filter bound to a specific resume."""
    def inst_name(inst_id: str) -> str:
        inst = resume.institution_by_id(inst_id)
        return inst.name if inst else inst_id
    return inst_name


def _period_filter(obj) -> str:
    """Format a date range from an object with start_date/end_date."""
    start = getattr(obj, "start_date", "")
    end = getattr(obj, "end_date", "")
    if not start:
        return ""
    return f"{start}–{end}" if end else f"{start}–Present"


def _patent_status_filter(status) -> str:
    """Format patent status."""
    return f" ({status.value})" if status else ""


# --- LaTeX rendering ---

_LATEX_SPECIAL = re.compile(r"([\\{}$&#%_])")
_LATEX_TILDE = re.compile(r"~")
_LATEX_CARET = re.compile(r"\^")


def render_latex(store: ResumeStore) -> str:
    """Render a complete Resume as LaTeX."""
    env = _create_latex_env(store)
    template = env.get_template("cv.tex.j2")
    context = _template_context(store, enrich=False)
    return template.render(**context)


def _create_latex_env(store: ResumeStore) -> Environment:
    """Create a Jinja2 environment configured for LaTeX output."""
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters["inst_name"] = _make_inst_name_filter(store.resume)
    env.filters["latex_period"] = _latex_period_filter
    env.filters["patent_status"] = _patent_status_filter
    env.filters["latex_escape"] = _latex_escape_filter
    env.filters["strip_period"] = _strip_trailing_period
    env.filters["employer_name"] = _make_employer_name_filter(store.resume)
    return env


def _strip_trailing_period(text: str) -> str:
    """Strip trailing period from text (for items joined with semicolons)."""
    return text.rstrip(".")


def _latex_escape_filter(text: str) -> str:
    """Escape LaTeX special characters and convert Unicode symbols."""
    text = _LATEX_SPECIAL.sub(r"\\\1", text)
    text = _LATEX_TILDE.sub(r"\\textasciitilde{}", text)
    text = _LATEX_CARET.sub(r"\\textasciicircum{}", text)
    text = text.replace("≈", "$\\simeq$")
    text = text.replace("é", "\\'e")
    text = text.replace("ó", "\\'o")
    text = text.replace("í", "\\'i")
    text = text.replace("ñ", "\\~n")
    return text


_MONTH_NAMES = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
    "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
    "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}


def _latex_period_filter(obj) -> str:
    """Format a date range with LaTeX en-dash.

    Handles: year-only (2023), year-month (2022-06), same-year ranges,
    and month-level ranges like 'Jun--Dec 2022'.
    """
    start = getattr(obj, "start_date", "")
    end = getattr(obj, "end_date", "")
    if not start:
        return ""
    if not end:
        return f"{start}--Now"

    s_year, s_month = _parse_date(start)
    e_year, e_month = _parse_date(end)

    if s_year == e_year and not s_month and not e_month:
        return s_year
    if s_year == e_year and s_month and e_month:
        return f"{_MONTH_NAMES[s_month]}--{_MONTH_NAMES[e_month]} {s_year}"
    if s_month:
        start_fmt = f"{_MONTH_NAMES[s_month]} {s_year}" if s_month else s_year
    else:
        start_fmt = s_year
    if e_month:
        end_fmt = f"{_MONTH_NAMES[e_month]} {e_year}" if e_month else e_year
    else:
        end_fmt = e_year
    return f"{start_fmt}--{end_fmt}"


def _parse_date(date_str: str) -> tuple[str, str]:
    """Parse 'YYYY' or 'YYYY-MM' into (year, month) tuple."""
    parts = date_str.split("-")
    year = parts[0]
    month = parts[1] if len(parts) > 1 else ""
    return year, month


def _make_employer_name_filter(resume: Resume):
    """Create an employer_name filter that respects employer_display overrides."""
    def employer_name(w: WorkEntry) -> str:
        if w.employer_display:
            return w.employer_display
        inst = resume.institution_by_id(w.institution_id)
        inst_name = inst.name if inst else w.institution_id
        if w.department:
            return f"{w.department} @ {inst_name}"
        return inst_name
    return employer_name
