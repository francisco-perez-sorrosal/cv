"""Semantic overlay models for CV annotation, classification, and querying.

The semantic overlay lives in a separate file from the resume data, enabling
clean separation of facts (human-authored) from annotations (LLM-refinable).
All annotations reference resume entries by their stable IDs.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from cv_mcp_server.models.resume import EntryId


# --- Enums ---

class Provenance(str, Enum):
    """Who authored this annotation."""
    human = "human"
    llm = "llm"
    derived = "derived"  # Computed from other annotations


class RelationshipType(str, Enum):
    """Types of cross-entry relationships."""
    relates_to = "relates-to"
    derived_from = "derived-from"
    resulted_in = "resulted-in"
    uses_skill = "uses-skill"
    published_as = "published-as"       # work project -> publication
    patented_as = "patented-as"         # work project -> patent
    presented_at = "presented-at"       # work/publication -> conference
    supervised_by = "supervised-by"     # project -> education/research
    continuation_of = "continuation-of"  # project -> earlier project


class ProficiencyLevel(str, Enum):
    """Skill proficiency on a standardized scale."""
    novice = "novice"
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"
    thought_leader = "thought-leader"


class RelevanceLevel(str, Enum):
    """How relevant an entry is for a given audience."""
    primary = "primary"       # Must include
    secondary = "secondary"   # Include if space allows
    tertiary = "tertiary"     # Omit unless specifically asked
    exclude = "exclude"       # Never include for this audience


# --- Topic Taxonomy ---

class Topic(BaseModel):
    """A topic in the hierarchical taxonomy.

    Topics form a tree via dot-separated IDs:
    'ai.ml.nlp.entity-matching'

    The ID encodes the hierarchy — 'ai.ml' is the parent of 'ai.ml.nlp'.
    """
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(
        description="Dot-separated hierarchical path (e.g., 'ai.ml.nlp'). "
        "This IS the topic identity."
    )
    label: str = Field(description="Human-readable display name")
    description: str = ""
    aliases: list[str] = Field(
        [], description="Alternative names (e.g., ['NLP', 'natural language processing'])"
    )


class TopicTaxonomy(BaseModel):
    """The full topic taxonomy. Defined once, referenced by annotations."""
    model_config = ConfigDict(populate_by_name=True)

    version: str = "1.0.0"
    topics: list[Topic] = []

    def topic_by_id(self, topic_id: str) -> Topic | None:
        for t in self.topics:
            if t.id == topic_id:
                return t
        return None

    def descendants(self, topic_id: str) -> list[str]:
        """Return all topic IDs that are descendants of (or equal to) the given ID."""
        return [t.id for t in self.topics if t.id.startswith(topic_id)]


# --- Per-entry annotations ---

class TopicAnnotation(BaseModel):
    """A topic assigned to a resume entry."""
    model_config = ConfigDict(populate_by_name=True)

    topic_id: str = Field(alias="topicId", description="Reference to taxonomy topic ID")
    confidence: float = Field(ge=0.0, le=1.0, description="Classification certainty")
    provenance: Provenance
    rationale: str = Field("", description="Why this topic was assigned")
    primary: bool = Field(False, description="Primary topic for the entry (vs supporting)")


class TemporalRelevance(BaseModel):
    """How a topic's relevance to the candidate changes over time."""
    model_config = ConfigDict(populate_by_name=True)

    topic_id: str = Field(alias="topicId")
    period: str = Field(description="Date range (e.g., '2010-2015', '2020-present')")
    weight: float = Field(
        ge=0.0, le=1.0,
        description="Relevance weight during this period (1.0 = primary focus)"
    )
    note: str = ""


class SkillProficiency(BaseModel):
    """Track skill proficiency at a specific entry/time."""
    model_config = ConfigDict(populate_by_name=True)

    topic_id: str = Field(alias="topicId", description="Skill as topic ID")
    level: ProficiencyLevel
    entry_id: EntryId = Field(
        EntryId(""), alias="entryId",
        description="Resume entry where this was demonstrated. Empty = overall/current level."
    )
    evidence: str = Field("", description="What demonstrates this proficiency level")
    provenance: Provenance = Provenance.human


class Relationship(BaseModel):
    """A directed relationship between two resume entries."""
    model_config = ConfigDict(populate_by_name=True)

    source_id: EntryId = Field(alias="sourceId", description="From entry ID")
    target_id: EntryId = Field(alias="targetId", description="To entry ID")
    type: RelationshipType
    description: str = ""
    provenance: Provenance = Provenance.human
    confidence: float = Field(1.0, ge=0.0, le=1.0)


class ImpactIndicator(BaseModel):
    """Quantifiable impact beyond citations."""
    model_config = ConfigDict(populate_by_name=True)

    entry_id: EntryId = Field(alias="entryId")
    metric: str = Field(description="What is measured (e.g., 'team_size', 'users_served')")
    value: str = Field(description="The value (string to allow '50+', '$2M', etc.)")
    scope: str = Field("", description="Context (e.g., 'organization-wide', 'team-level')")
    provenance: Provenance = Provenance.human


class AudienceRelevance(BaseModel):
    """How relevant an entry is for a specific audience type."""
    model_config = ConfigDict(populate_by_name=True)

    entry_id: EntryId = Field(alias="entryId")
    audience: str = Field(
        description="Audience type (e.g., 'hiring-manager', 'academic-committee', "
        "'executive', 'startup-founder', 'peer-researcher')"
    )
    relevance: RelevanceLevel
    reason: str = ""
    provenance: Provenance = Provenance.human


class EntrySummary(BaseModel):
    """One-line summary of a resume entry, optionally audience-specific."""
    model_config = ConfigDict(populate_by_name=True)

    entry_id: EntryId = Field(alias="entryId")
    summary: str
    audience: str = Field("general", description="Which audience this summary targets")
    provenance: Provenance
    model: str = Field("", description="LLM model that generated this (empty if human)")


# --- Aggregated per-entry container ---

class EntryAnnotations(BaseModel):
    """All annotations for a single resume entry, keyed by entry ID."""
    model_config = ConfigDict(populate_by_name=True)

    entry_id: EntryId = Field(alias="entryId")
    topics: list[TopicAnnotation] = []
    summaries: list[EntrySummary] = []
    audience_relevance: list[AudienceRelevance] = Field([], alias="audienceRelevance")
    impact: list[ImpactIndicator] = []


# --- Top-level Semantic Overlay ---

class SemanticOverlay(BaseModel):
    """Semantic annotations for all resume entries.

    References entries in resume.yaml by their stable IDs.
    Designed to be sparse — entries without annotations are simply absent.
    LLMs populate this over time; humans can also edit directly.
    """
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    version: str = "1.0.0"
    taxonomy: TopicTaxonomy = TopicTaxonomy()
    annotations: list[EntryAnnotations] = []
    relationships: list[Relationship] = []
    temporal_relevance: list[TemporalRelevance] = Field([], alias="temporalRelevance")
    skill_proficiency: list[SkillProficiency] = Field([], alias="skillProficiency")

    def annotations_for(self, entry_id: str) -> EntryAnnotations | None:
        for a in self.annotations:
            if a.entry_id == entry_id:
                return a
        return None

    def relationships_for(self, entry_id: str) -> list[Relationship]:
        return [
            r for r in self.relationships
            if r.source_id == entry_id or r.target_id == entry_id
        ]

    def entries_by_topic(self, topic_id: str, include_descendants: bool = True) -> list[str]:
        """Return entry IDs annotated with this topic (or its descendants)."""
        match_ids = (
            set(self.taxonomy.descendants(topic_id))
            if include_descendants
            else {topic_id}
        )
        return [
            ann.entry_id
            for ann in self.annotations
            if any(ta.topic_id in match_ids for ta in ann.topics)
        ]

    def all_referenced_ids(self) -> set[EntryId]:
        """Collect all entry IDs referenced anywhere in the overlay."""
        ids: set[EntryId] = set()
        for ann in self.annotations:
            ids.add(ann.entry_id)
            for s in ann.summaries:
                ids.add(s.entry_id)
            for ar in ann.audience_relevance:
                ids.add(ar.entry_id)
            for imp in ann.impact:
                ids.add(imp.entry_id)
        for rel in self.relationships:
            ids.add(rel.source_id)
            ids.add(rel.target_id)
        for sp in self.skill_proficiency:
            if sp.entry_id:
                ids.add(sp.entry_id)
        return ids
