"""Tests for SemanticOverlay Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from cv_mcp_server.models.resume import EntryId
from cv_mcp_server.models.semantics import (
    EntryAnnotations,
    ProficiencyLevel,
    Provenance,
    Relationship,
    RelationshipType,
    RelevanceLevel,
    SemanticOverlay,
    TopicAnnotation,
    TopicTaxonomy,
)


# --- Enum values ---


class TestEnums:
    def test_provenance_values(self):
        assert {p.value for p in Provenance} == {"human", "llm", "derived"}

    def test_relationship_type_values(self):
        expected = {
            "relates-to", "derived-from", "resulted-in", "uses-skill",
            "published-as", "patented-as", "presented-at",
            "supervised-by", "continuation-of",
        }
        assert {r.value for r in RelationshipType} == expected

    def test_proficiency_level_values(self):
        expected = {
            "novice", "beginner", "intermediate",
            "advanced", "expert", "thought-leader",
        }
        assert {p.value for p in ProficiencyLevel} == expected

    def test_relevance_level_values(self):
        expected = {"primary", "secondary", "tertiary", "exclude"}
        assert {r.value for r in RelevanceLevel} == expected


# --- TopicAnnotation confidence bounds ---


class TestTopicAnnotation:
    def test_confidence_zero_valid(self):
        ta = TopicAnnotation(
            topic_id="ai", confidence=0.0, provenance=Provenance.human,
        )
        assert ta.confidence == 0.0

    def test_confidence_one_valid(self):
        ta = TopicAnnotation(
            topic_id="ai", confidence=1.0, provenance=Provenance.human,
        )
        assert ta.confidence == 1.0

    def test_confidence_above_one_rejected(self):
        with pytest.raises(ValidationError):
            TopicAnnotation(
                topic_id="ai", confidence=1.5, provenance=Provenance.human,
            )

    def test_confidence_negative_rejected(self):
        with pytest.raises(ValidationError):
            TopicAnnotation(
                topic_id="ai", confidence=-0.1, provenance=Provenance.human,
            )

    def test_camel_case_topic_id(self):
        ta = TopicAnnotation(
            **{"topicId": "ai.ml", "confidence": 0.5, "provenance": "human"},
        )
        assert ta.topic_id == "ai.ml"


# --- TopicTaxonomy ---


class TestTopicTaxonomy:
    def test_topic_by_id_found(self, minimal_taxonomy):
        topic = minimal_taxonomy.topic_by_id("ai.ml")
        assert topic is not None
        assert topic.label == "Machine Learning"

    def test_topic_by_id_not_found(self, minimal_taxonomy):
        assert minimal_taxonomy.topic_by_id("nonexistent") is None

    def test_descendants_returns_self_and_children(self, minimal_taxonomy):
        desc = minimal_taxonomy.descendants("ai")
        assert "ai" in desc
        assert "ai.ml" in desc
        assert "ai.ml.classification" in desc
        assert "systems" not in desc

    def test_descendants_leaf_returns_self(self, minimal_taxonomy):
        desc = minimal_taxonomy.descendants("systems")
        assert desc == ["systems"]

    def test_descendants_no_match(self, minimal_taxonomy):
        assert minimal_taxonomy.descendants("nonexistent") == []


# --- Relationship ---


class TestRelationship:
    def test_camel_case_aliases(self):
        r = Relationship(
            **{
                "sourceId": "proj-a",
                "targetId": "pub-b",
                "type": "published-as",
            },
        )
        assert r.source_id == "proj-a"
        assert r.target_id == "pub-b"
        assert r.type == RelationshipType.published_as

    def test_enum_from_string(self):
        r = Relationship(
            source_id=EntryId("a"),
            target_id=EntryId("b"),
            type="patented-as",
        )
        assert r.type == RelationshipType.patented_as


# --- SemanticOverlay ---


class TestSemanticOverlay:
    def test_annotations_for_found(self, minimal_semantics):
        ann = minimal_semantics.annotations_for("work-acme-2023")
        assert ann is not None
        assert len(ann.topics) == 1

    def test_annotations_for_not_found(self, minimal_semantics):
        assert minimal_semantics.annotations_for("nonexistent") is None

    def test_relationships_for_as_source(self, minimal_semantics):
        rels = minimal_semantics.relationships_for("proj-widget")
        assert len(rels) == 2

    def test_relationships_for_as_target(self, minimal_semantics):
        rels = minimal_semantics.relationships_for("pub-nlp-2019")
        assert len(rels) == 1
        assert rels[0].source_id == "proj-widget"

    def test_relationships_for_empty(self, minimal_semantics):
        assert minimal_semantics.relationships_for("nonexistent") == []

    def test_entries_by_topic_with_descendants(self, minimal_semantics):
        entries = minimal_semantics.entries_by_topic("ai")
        assert "work-acme-2023" in entries
        assert "proj-widget" in entries

    def test_entries_by_topic_without_descendants(self, minimal_semantics):
        entries = minimal_semantics.entries_by_topic("ai.ml", include_descendants=False)
        assert "work-acme-2023" in entries
        assert "proj-widget" not in entries

    def test_all_referenced_ids(self, minimal_semantics):
        ids = minimal_semantics.all_referenced_ids()
        assert "work-acme-2023" in ids
        assert "proj-widget" in ids
        assert "pub-nlp-2019" in ids
        assert "patent-widget-2022" in ids
