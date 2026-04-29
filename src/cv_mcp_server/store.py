"""ResumeStore: unified access to structured CV data and semantic overlay.

Loads resume.yaml (required) and resume-semantics.yaml (optional),
validates cross-references, and provides query methods for MCP tools.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from loguru import logger

from cv_mcp_server.models.resume import Institution, Resume
from cv_mcp_server.models.semantics import (
    EntryAnnotations,
    Relationship,
    SemanticOverlay,
)


class ResumeStore:
    """Loads resume + semantic overlay, validates cross-references,
    and provides query methods for MCP tools.

    The resume data is read-only after load.
    The semantic overlay can be updated (LLM annotations) and persisted.
    """

    def __init__(
        self,
        resume: Resume,
        semantics: SemanticOverlay,
        semantics_path: Path,
    ) -> None:
        self._resume = resume
        self._semantics = semantics
        self._semantics_path = semantics_path
        self._entries_by_id: dict[str, object] = self._build_entry_index()

    @classmethod
    def load(cls, data_dir: Path) -> ResumeStore:
        """Load and validate resume + semantics from a directory."""
        resume_path = data_dir / "resume.yaml"
        semantics_path = data_dir / "resume-semantics.yaml"

        with open(resume_path, encoding="utf-8") as f:
            resume = Resume.model_validate(yaml.safe_load(f))
        logger.info(
            f"Loaded resume: {len(resume.work)} work entries, "
            f"{len(resume.publications)} publications"
        )

        if semantics_path.exists():
            with open(semantics_path, encoding="utf-8") as f:
                raw = yaml.safe_load(f)
            semantics = (
                SemanticOverlay.model_validate(raw) if raw else SemanticOverlay()
            )
            logger.info(
                f"Loaded semantic overlay: {len(semantics.annotations)} annotated entries"
            )
        else:
            semantics = SemanticOverlay()
            logger.info("No semantic overlay found; starting with empty annotations")

        store = cls(resume, semantics, semantics_path)
        store._validate_cross_references()
        return store

    @property
    def resume(self) -> Resume:
        return self._resume

    @property
    def semantics(self) -> SemanticOverlay:
        return self._semantics

    # --- Query methods ---

    def entry_by_id(self, entry_id: str) -> object | None:
        return self._entries_by_id.get(entry_id)

    def entry_label(self, entry_id: str) -> str:
        """Human-readable display name for an entry ID."""
        entry = self._entries_by_id.get(entry_id)
        if entry is None:
            return entry_id
        if hasattr(entry, "name"):
            return entry.name
        if hasattr(entry, "title"):
            return entry.title
        if hasattr(entry, "position"):
            return entry.position
        return entry_id

    def institution_by_id(self, inst_id: str) -> Institution | None:
        return self._resume.institution_by_id(inst_id)

    def institution_name(self, inst_id: str) -> str:
        """Resolve institution ID to display name."""
        inst = self._resume.institution_by_id(inst_id)
        return inst.name if inst else inst_id

    def work_by_company(self, company: str) -> list:
        """Find work entries matching a company name (case-insensitive substring).

        Searches institution name and aliases.
        """
        company_lower = company.lower()
        results = []
        for w in self._resume.work:
            inst = self._resume.institution_by_id(w.institution_id)
            if inst is None:
                continue
            names = [inst.name.lower()] + [a.lower() for a in inst.aliases]
            if any(company_lower in n for n in names):
                results.append(w)
        return results

    def work_by_date_range(self, start: str, end: str) -> list:
        """Find work entries overlapping a date range."""
        return [
            w
            for w in self._resume.work
            if w.start_date <= end and (w.end_date >= start or w.end_date == "")
        ]

    def entries_by_topic(self, topic_id: str) -> list[dict]:
        """Find resume entries annotated with a topic (including descendants)."""
        entry_ids = self._semantics.entries_by_topic(topic_id)
        return [
            {"id": eid, "entry": self._entries_by_id.get(eid)}
            for eid in entry_ids
            if eid in self._entries_by_id
        ]

    def relationships_for(self, entry_id: str) -> list[Relationship]:
        return self._semantics.relationships_for(entry_id)

    def audience_relevant_entries(self, audience: str) -> list[dict]:
        """Find entries most relevant for a given audience, sorted by relevance."""
        relevance_order = {"primary": 0, "secondary": 1, "tertiary": 2}
        results = []
        for ann in self._semantics.annotations:
            for ar in ann.audience_relevance:
                if ar.audience == audience and ar.relevance.value != "exclude":
                    results.append(
                        {
                            "entry_id": ann.entry_id,
                            "relevance": ar.relevance.value,
                            "reason": ar.reason,
                            "entry": self._entries_by_id.get(ann.entry_id),
                        }
                    )
        results.sort(key=lambda r: relevance_order.get(r["relevance"], 99))
        return results

    # --- Semantic write methods ---

    def annotate_entry(self, entry_id: str, annotations: EntryAnnotations) -> None:
        """Add or replace annotations for an entry. Persists to disk."""
        if entry_id not in self._entries_by_id:
            raise ValueError(f"Entry ID '{entry_id}' not found in resume")
        self._semantics.annotations = [
            a for a in self._semantics.annotations if a.entry_id != entry_id
        ]
        self._semantics.annotations.append(annotations)
        self._persist_semantics()

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a cross-entry relationship. Persists to disk."""
        for eid in [relationship.source_id, relationship.target_id]:
            if eid not in self._entries_by_id:
                raise ValueError(f"Entry ID '{eid}' not found in resume")
        self._semantics.relationships.append(relationship)
        self._persist_semantics()

    # --- Internal ---

    def _build_entry_index(self) -> dict[str, object]:
        index: dict[str, object] = {}
        for inst in self._resume.institutions:
            index[inst.id] = inst
        for w in self._resume.work:
            index[w.id] = w
            for p in w.projects:
                index[p.id] = p
        for section in [
            self._resume.education,
            self._resume.publications,
            self._resume.skills,
            self._resume.languages,
            self._resume.certificates,
            self._resume.projects,
            self._resume.patents,
            self._resume.conferences,
            self._resume.memberships,
            self._resume.book_reviews,
        ]:
            for entry in section:
                index[entry.id] = entry
        return index

    def _validate_cross_references(self) -> None:
        """Warn about dangling references in the semantic overlay."""
        valid_ids = self._resume.all_entry_ids()
        dangling = self._semantics.all_referenced_ids() - valid_ids
        if dangling:
            logger.warning(
                f"Semantic overlay references {len(dangling)} unknown entry IDs: "
                f"{sorted(dangling)[:10]}{'...' if len(dangling) > 10 else ''}"
            )

    def _persist_semantics(self) -> None:
        """Write semantic overlay back to YAML."""
        data = self._semantics.model_dump(by_alias=True, exclude_defaults=True)
        with open(self._semantics_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
            )
        logger.info("Semantic overlay persisted to disk")
