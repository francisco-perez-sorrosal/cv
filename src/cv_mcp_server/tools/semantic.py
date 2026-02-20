"""Semantic query tools: topic-based lookups, relationships, skill profiles."""

from cv_mcp_server.server import mcp, store


@mcp.tool(description="Find resume entries annotated with a topic. Returns entry IDs with labels.")
def query_by_topic(topic: str, include_subtopics: bool = True) -> str:
    results = store.entries_by_topic(topic) if include_subtopics else [
        {"id": eid, "entry": store.entry_by_id(eid)}
        for eid in store.semantics.entries_by_topic(topic, include_descendants=False)
    ]
    if not results:
        return f"No entries annotated with topic '{topic}'."
    lines = []
    for r in results:
        entry = r.get("entry") or r.get("entry")
        label = getattr(entry, "name", None) or getattr(entry, "title", None) or getattr(entry, "position", None) or str(r["id"])
        lines.append(f"- {r['id']}: {label}")
    return "\n".join(lines)


@mcp.tool(description="Get cross-references and relationships for a resume entry.")
def get_relationships(entry_id: str) -> str:
    rels = store.relationships_for(entry_id)
    if not rels:
        return f"No relationships found for '{entry_id}'."
    lines = []
    for r in rels:
        direction = "→" if r.source_id == entry_id else "←"
        other = r.target_id if r.source_id == entry_id else r.source_id
        lines.append(f"- {direction} {r.type.value} {other}: {r.description}")
    return "\n".join(lines)


@mcp.tool(description="Get skill proficiency levels across the career, optionally filtered by topic.")
def get_skill_profile(topic: str = "") -> str:
    profs = store.semantics.skill_proficiency
    if topic:
        match_ids = set(store.semantics.taxonomy.descendants(topic))
        profs = [p for p in profs if p.topic_id in match_ids]
    if not profs:
        return f"No skill proficiency data{' for topic ' + topic if topic else ''}."
    lines = []
    for p in profs:
        t = store.semantics.taxonomy.topic_by_id(p.topic_id)
        label = t.label if t else p.topic_id
        lines.append(f"- **{label}**: {p.level.value} — {p.evidence}")
    return "\n".join(lines)


@mcp.tool(description="Get full semantic context for an entry: topics, relationships, summaries, impact.")
def get_entry_context(entry_id: str) -> str:
    entry = store.entry_by_id(entry_id)
    if entry is None:
        return f"Entry '{entry_id}' not found."

    parts = [f"## Context for {entry_id}"]

    ann = store.semantics.annotations_for(entry_id)
    if ann:
        if ann.topics:
            parts.append("\n### Topics")
            for t in ann.topics:
                topic = store.semantics.taxonomy.topic_by_id(t.topic_id)
                label = topic.label if topic else t.topic_id
                primary = " (primary)" if t.primary else ""
                parts.append(f"- {label}{primary} — confidence: {t.confidence}, {t.rationale}")
        if ann.impact:
            parts.append("\n### Impact")
            for i in ann.impact:
                parts.append(f"- {i.metric}: {i.value} ({i.scope})")
        if ann.summaries:
            parts.append("\n### Summaries")
            for s in ann.summaries:
                parts.append(f"- [{s.audience}] {s.summary}")

    rels = store.relationships_for(entry_id)
    if rels:
        parts.append("\n### Relationships")
        for r in rels:
            direction = "→" if r.source_id == entry_id else "←"
            other = r.target_id if r.source_id == entry_id else r.source_id
            parts.append(f"- {direction} {r.type.value} {other}: {r.description}")

    return "\n".join(parts)
