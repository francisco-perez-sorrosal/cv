"""Tests for Resume Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from cv_mcp_server.models.resume import (
    EntryId,
    Institution,
    InstitutionType,
    LanguageFluency,
    PatentStatus,
    Project,
    Publication,
    Resume,
    ResumeEntry,
    WorkEntry,
)


# --- Enum values ---


class TestEnums:
    def test_patent_status_values(self):
        assert PatentStatus.application.value == "application"
        assert PatentStatus.granted.value == "granted"

    def test_language_fluency_values(self):
        expected = {"native", "fluent", "professional", "intermediate", "beginner"}
        assert {f.value for f in LanguageFluency} == expected

    def test_institution_type_values(self):
        expected = {
            "company", "university", "research_institution",
            "education_platform", "government", "consortium",
            "cooperative", "independent",
        }
        assert {t.value for t in InstitutionType} == expected


# --- camelCase alias roundtrip ---


class TestCamelCaseAliases:
    def test_start_date_alias(self):
        w = WorkEntry(
            id="w1",
            institution_id="inst-1",
            **{"startDate": "2020", "endDate": "2023"},
        )
        assert w.start_date == "2020"
        assert w.end_date == "2023"

    def test_release_date_alias(self):
        p = Publication(id="p1", name="Paper", **{"releaseDate": "2021"})
        assert p.release_date == "2021"

    def test_country_code_alias(self):
        from cv_mcp_server.models.resume import Location
        loc = Location(**{"countryCode": "US"})
        assert loc.country_code == "US"

    def test_study_type_alias(self):
        from cv_mcp_server.models.resume import Education
        e = Education(id="e1", institution_id="i1", **{"studyType": "Ph.D."})
        assert e.study_type == "Ph.D."

    def test_roundtrip_by_alias(self):
        w = WorkEntry(
            id="w1",
            institution_id="inst-1",
            start_date="2020",
            end_date="2023",
        )
        dumped = w.model_dump(by_alias=True)
        assert dumped["startDate"] == "2020"
        assert dumped["endDate"] == "2023"
        roundtripped = WorkEntry.model_validate(dumped)
        assert roundtripped.start_date == "2020"


# --- ResumeEntry ---


class TestResumeEntry:
    def test_requires_id(self):
        with pytest.raises(ValidationError):
            ResumeEntry()

    def test_with_id(self):
        entry = ResumeEntry(id="test-entry")
        assert entry.id == "test-entry"


# --- Project / WorkEntry defaults ---


class TestProjectAndWorkDefaults:
    def test_project_empty_collections(self):
        p = Project(id="p1", name="Test")
        assert p.highlights == []
        assert p.keywords == []
        assert p.roles == []

    def test_work_entry_defaults(self):
        w = WorkEntry(id="w1", institution_id="inst-1")
        assert w.highlights == []
        assert w.roles == []
        assert w.projects == []
        assert w.position == ""

    def test_nested_projects_preserve_ids(self):
        w = WorkEntry(
            id="w1",
            institution_id="inst-1",
            projects=[
                Project(id="p1", name="Proj A"),
                Project(id="p2", name="Proj B"),
            ],
        )
        assert [p.id for p in w.projects] == ["p1", "p2"]


# --- Publication ---


class TestPublication:
    def test_citations_default_zero(self):
        p = Publication(id="p1", name="Paper")
        assert p.citations == 0

    def test_citations_custom(self):
        p = Publication(id="p1", name="Paper", citations=100)
        assert p.citations == 100


# --- Resume methods ---


class TestResumeMethods:
    def test_institution_by_id_found(self, minimal_resume):
        inst = minimal_resume.institution_by_id("inst-acme")
        assert inst is not None
        assert inst.name == "Acme Corp"

    def test_institution_by_id_not_found(self, minimal_resume):
        assert minimal_resume.institution_by_id("inst-nonexistent") is None

    def test_all_entry_ids_completeness(self, minimal_resume):
        ids = minimal_resume.all_entry_ids()
        expected = {
            "inst-acme", "inst-testuni",
            "work-acme-2023", "work-testuni-2020",
            "proj-widget",
            "pub-nlp-2019",
            "patent-widget-2022",
            "edu-testuni-phd",
            "skill-programming",
            "lang-en",
            "conf-icml-2019", "conf-acl-review-2020",
            "member-asf", "member-acm",
        }
        assert ids == expected


# --- Resume construction ---


class TestResumeConstruction:
    def test_empty_resume_valid(self):
        r = Resume()
        assert r.work == []
        assert r.publications == []

    def test_extra_fields_ignored(self):
        r = Resume(**{"work": [], "unknown_field": "ignored"})
        assert not hasattr(r, "unknown_field")
