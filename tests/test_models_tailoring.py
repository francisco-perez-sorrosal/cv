"""Tests for TailoringSpec Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from cv_mcp_server.models.tailoring import (
    EntryEmphasis,
    KeywordHighlight,
    SectionDirective,
    TailoringSpec,
)


# --- KeywordHighlight ---


class TestKeywordHighlight:
    def test_default_weight(self):
        kw = KeywordHighlight(term="machine learning")
        assert kw.weight == 1.0

    def test_custom_weight(self):
        kw = KeywordHighlight(term="NLP", weight=2.0)
        assert kw.weight == 2.0

    def test_weight_zero_valid(self):
        kw = KeywordHighlight(term="irrelevant", weight=0.0)
        assert kw.weight == 0.0

    def test_weight_above_max_rejected(self):
        with pytest.raises(ValidationError):
            KeywordHighlight(term="x", weight=2.1)

    def test_weight_negative_rejected(self):
        with pytest.raises(ValidationError):
            KeywordHighlight(term="x", weight=-0.1)


# --- SectionDirective ---


class TestSectionDirective:
    def test_include_defaults_true(self):
        sd = SectionDirective(section_name="Skills", position=0)
        assert sd.include is True

    def test_exclude_section(self):
        sd = SectionDirective(section_name="Hobbies", include=False, position=5)
        assert sd.include is False
        assert sd.position == 5


# --- EntryEmphasis ---


class TestEntryEmphasis:
    def test_default_weight_and_reason(self):
        ee = EntryEmphasis(entry_id="work-acme-2023")
        assert ee.weight == 1.0
        assert ee.reason == ""

    def test_weight_zero_omit(self):
        ee = EntryEmphasis(entry_id="work-old-job", weight=0.0, reason="Not relevant")
        assert ee.weight == 0.0
        assert ee.reason == "Not relevant"

    def test_weight_above_max_rejected(self):
        with pytest.raises(ValidationError):
            EntryEmphasis(entry_id="x", weight=2.5)

    def test_weight_negative_rejected(self):
        with pytest.raises(ValidationError):
            EntryEmphasis(entry_id="x", weight=-1.0)


# --- TailoringSpec ---


MINIMAL_SECTION_ORDER = [
    {"section_name": "Professional Experience", "position": 0},
    {"section_name": "Skills", "position": 1},
]


class TestTailoringSpecDefaults:
    def test_required_fields_only(self):
        spec = TailoringSpec(
            job_title="ML Engineer",
            section_order=MINIMAL_SECTION_ORDER,
        )
        assert spec.job_title == "ML Engineer"
        assert spec.company == ""
        assert len(spec.section_order) == 2
        assert spec.entry_emphasis == []
        assert spec.keywords == []
        assert spec.profile_override == ""
        assert spec.max_pages == 2

    def test_missing_job_title_rejected(self):
        with pytest.raises(ValidationError):
            TailoringSpec(section_order=MINIMAL_SECTION_ORDER)

    def test_missing_section_order_rejected(self):
        with pytest.raises(ValidationError):
            TailoringSpec(job_title="Engineer")


class TestTailoringSpecMaxPages:
    def test_max_pages_one_valid(self):
        spec = TailoringSpec(
            job_title="Engineer",
            section_order=MINIMAL_SECTION_ORDER,
            max_pages=1,
        )
        assert spec.max_pages == 1

    def test_max_pages_three_valid(self):
        spec = TailoringSpec(
            job_title="Engineer",
            section_order=MINIMAL_SECTION_ORDER,
            max_pages=3,
        )
        assert spec.max_pages == 3

    def test_max_pages_zero_rejected(self):
        with pytest.raises(ValidationError):
            TailoringSpec(
                job_title="Engineer",
                section_order=MINIMAL_SECTION_ORDER,
                max_pages=0,
            )

    def test_max_pages_four_rejected(self):
        with pytest.raises(ValidationError):
            TailoringSpec(
                job_title="Engineer",
                section_order=MINIMAL_SECTION_ORDER,
                max_pages=4,
            )


class TestTailoringSpecRoundTrip:
    def test_dict_roundtrip(self):
        data = {
            "job_title": "Senior ML Engineer",
            "company": "Acme Corp",
            "section_order": [
                {"section_name": "Professional Experience", "include": True, "position": 0},
                {"section_name": "Skills", "include": True, "position": 1},
                {"section_name": "Education", "include": True, "position": 2},
                {"section_name": "Hobbies", "include": False, "position": 3},
            ],
            "entry_emphasis": [
                {"entry_id": "work-acme-2023", "weight": 2.0, "reason": "Direct match"},
                {"entry_id": "work-old-2015", "weight": 0.0, "reason": "Irrelevant"},
            ],
            "keywords": [
                {"term": "machine learning", "weight": 2.0},
                {"term": "python", "weight": 1.0},
            ],
            "profile_override": "Experienced ML engineer with 10 years in NLP.",
            "max_pages": 2,
        }
        spec = TailoringSpec.model_validate(data)
        assert spec.job_title == "Senior ML Engineer"
        assert spec.company == "Acme Corp"
        assert len(spec.section_order) == 4
        assert spec.section_order[3].include is False
        assert spec.entry_emphasis[0].weight == 2.0
        assert spec.entry_emphasis[1].weight == 0.0
        assert len(spec.keywords) == 2
        assert spec.profile_override.startswith("Experienced")
        assert spec.max_pages == 2

    def test_json_roundtrip(self):
        spec = TailoringSpec(
            job_title="Data Scientist",
            company="BigCo",
            section_order=[
                SectionDirective(section_name="Skills", position=0),
                SectionDirective(section_name="Education", position=1),
            ],
            keywords=[KeywordHighlight(term="statistics", weight=1.5)],
            max_pages=3,
        )
        json_str = spec.model_dump_json()
        restored = TailoringSpec.model_validate_json(json_str)
        assert restored.job_title == spec.job_title
        assert restored.company == spec.company
        assert len(restored.section_order) == 2
        assert restored.section_order[0].section_name == "Skills"
        assert restored.keywords[0].term == "statistics"
        assert restored.keywords[0].weight == 1.5
        assert restored.max_pages == 3

    def test_model_dump_structure(self):
        spec = TailoringSpec(
            job_title="Engineer",
            section_order=[
                SectionDirective(section_name="Skills", position=0),
            ],
        )
        dumped = spec.model_dump()
        assert isinstance(dumped, dict)
        assert dumped["job_title"] == "Engineer"
        assert isinstance(dumped["section_order"], list)
        assert dumped["section_order"][0]["section_name"] == "Skills"
