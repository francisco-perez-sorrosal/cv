"""Template-based markdown renderer for the Resume model.

Uses Jinja2 templates to generate markdown matching the LaTeX CV structure.
Supports both full-document and per-section rendering.
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
