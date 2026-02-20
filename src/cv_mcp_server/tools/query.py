"""Structured query tools: filter and retrieve resume entries."""

import json

from pydantic import BaseModel, Field

from cv_mcp_server.server import mcp, store
from cv_mcp_server.renderers import render_work_entry


@mcp.tool(
    description="Filter work entries by company, date range, or topic. Returns matching entries as markdown."
)
def query_work(
    company: str = "",
    start_year: str = "",
    end_year: str = "",
    topic: str = "",
    enrich: bool = Field(
        default=True,
        description="Include semantic enrichments (cross-references to publications/patents)"
    ),
) -> str:
    """Filter work entries by company, date range, or topic. Returns matching entries as markdown."""
    results = list(store.resume.work)

    if company:
        company_lower = company.lower()
        filtered = []
        for w in results:
            inst = store.institution_by_id(w.institution_id)
            if inst is None:
                continue
            names = [inst.name.lower()] + [a.lower() for a in inst.aliases]
            if any(company_lower in n for n in names):
                filtered.append(w)
        results = filtered

    if start_year and end_year:
        results = [
            w for w in results
            if w.start_date <= end_year and (w.end_date >= start_year or w.end_date == "")
        ]

    if topic:
        topic_entry_ids = {e["id"] for e in store.entries_by_topic(topic)}
        results = [
            w for w in results
            if w.id in topic_entry_ids or any(p.id in topic_entry_ids for p in w.projects)
        ]

    if not results:
        return "No matching work entries found."

    return "\n\n".join(render_work_entry(w, store, enrich=enrich) for w in results)


@mcp.tool(description="Retrieve a specific resume entry by its stable ID. Returns JSON representation.")
def get_entry(entry_id: str) -> str:
    entry = store.entry_by_id(entry_id)
    if entry is None:
        return f"Entry '{entry_id}' not found."
    if isinstance(entry, BaseModel):
        return json.dumps(entry.model_dump(by_alias=True), indent=2, default=str)
    return str(entry)


@mcp.tool(
    description="List all entry IDs with labels, optionally filtered by section type (work, patents, publications, education, certificates, conferences, memberships, skills)."
)
def list_entry_ids(section: str = "") -> str:
    lines = []
    r = store.resume

    section_map = {
        "work": [(w.id, f"{w.position} at {store.institution_name(w.institution_id)}") for w in r.work]
                + [(p.id, f"  Project: {p.name}") for w in r.work for p in w.projects],
        "institutions": [(i.id, f"{i.name} ({i.type.value})") for i in r.institutions],
        "patents": [(p.id, p.title) for p in r.patents],
        "publications": [(p.id, p.name) for p in r.publications],
        "education": [(e.id, f"{e.study_type} at {store.institution_name(e.institution_id)}") for e in r.education],
        "certificates": [(c.id, c.name) for c in r.certificates],
        "conferences": [(c.id, c.name) for c in r.conferences],
        "memberships": [(m.id, m.organization) for m in r.memberships],
        "skills": [(s.id, s.name) for s in r.skills],
    }

    if section:
        section_lower = section.lower()
        if section_lower not in section_map:
            return f"Unknown section '{section}'. Available: {', '.join(section_map.keys())}"
        entries = section_map[section_lower]
        for eid, label in entries:
            lines.append(f"- {eid}: {label}")
    else:
        for sec_name, entries in section_map.items():
            if entries:
                lines.append(f"\n## {sec_name}")
                for eid, label in entries:
                    lines.append(f"- {eid}: {label}")

    return "\n".join(lines) if lines else "No entries found."
