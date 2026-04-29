"""Shared test fixtures: synthetic (Tier 1) and real-data (Tier 2)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cv_mcp_server.models.resume import (
    Conference,
    Education,
    EntryId,
    Institution,
    InstitutionType,
    Language,
    Membership,
    Patent,
    PatentStatus,
    PersonalInfo,
    Profile,
    Project,
    Publication,
    Resume,
    SkillGroup,
    Skill,
    WorkEntry,
)
from cv_mcp_server.models.semantics import (
    AudienceRelevance,
    EntryAnnotations,
    ProficiencyLevel,
    Provenance,
    Relationship,
    RelationshipType,
    RelevanceLevel,
    SemanticOverlay,
    SkillProficiency,
    Topic,
    TopicAnnotation,
    TopicTaxonomy,
)
from cv_mcp_server.store import ResumeStore


DATA_DIR = Path(__file__).parent.parent / "cv-data"


# --- Tier 1: Synthetic fixtures (no disk I/O) ---


@pytest.fixture
def minimal_institutions() -> list[Institution]:
    return [
        Institution(
            id=EntryId("inst-acme"),
            name="Acme Corp",
            type=InstitutionType.company,
            location="San Francisco",
            aliases=["Acme", "Acme Inc."],
        ),
        Institution(
            id=EntryId("inst-testuni"),
            name="Test University",
            type=InstitutionType.university,
            location="Boston",
        ),
    ]


@pytest.fixture
def minimal_work() -> list[WorkEntry]:
    return [
        WorkEntry(
            id=EntryId("work-acme-2023"),
            institution_id=EntryId("inst-acme"),
            position="Senior Engineer",
            start_date="2021",
            end_date="2023",
            roles=["Tech Lead", "ML Engineer"],
            highlights=["Led team of 5", "Built ML pipeline"],
            projects=[
                Project(
                    id=EntryId("proj-widget"),
                    name="Widget Builder",
                    start_date="2022",
                    end_date="2023",
                    description="A widget building tool",
                    highlights=["Launched v1.0"],
                    keywords=["python", "ml"],
                ),
            ],
        ),
        WorkEntry(
            id=EntryId("work-testuni-2020"),
            institution_id=EntryId("inst-testuni"),
            position="Researcher",
            start_date="2018",
            end_date="2020",
            roles=["Researcher"],
            summary="NLP research",
        ),
    ]


@pytest.fixture
def minimal_publications() -> list[Publication]:
    return [
        Publication(
            id=EntryId("pub-nlp-2019"),
            name="Deep NLP for Widgets",
            publisher="ACL 2019",
            release_date="2019",
            authors=["A. Test", "B. Author"],
            citations=42,
        ),
    ]


@pytest.fixture
def minimal_patents() -> list[Patent]:
    return [
        Patent(
            id=EntryId("patent-widget-2022"),
            number="US1234567",
            title="Widget Generation Method",
            date="2022",
            status=PatentStatus.granted,
            inventors=["A. Test"],
        ),
    ]


@pytest.fixture
def minimal_education() -> list[Education]:
    return [
        Education(
            id=EntryId("edu-testuni-phd"),
            institution_id=EntryId("inst-testuni"),
            area="Computer Science",
            study_type="Ph.D.",
            start_date="2014",
            end_date="2018",
        ),
    ]


@pytest.fixture
def minimal_skills() -> list[SkillGroup]:
    return [
        SkillGroup(
            id=EntryId("skill-programming"),
            name="Programming",
            skills=[
                Skill(name="Languages", keywords=["Python", "Java"]),
                Skill(name="ML Frameworks", keywords=["PyTorch", "TensorFlow"]),
            ],
        ),
    ]


@pytest.fixture
def minimal_resume(
    minimal_institutions,
    minimal_work,
    minimal_publications,
    minimal_patents,
    minimal_education,
    minimal_skills,
) -> Resume:
    return Resume(
        personal_info=PersonalInfo(
            name="Test Candidate",
            label="Senior Engineer",
            email="test@example.com",
            profiles=[
                Profile(network="GitHub", url="https://github.com/test"),
                Profile(network="LinkedIn", url="https://linkedin.com/in/test"),
            ],
        ),
        institutions=minimal_institutions,
        work=minimal_work,
        publications=minimal_publications,
        patents=minimal_patents,
        education=minimal_education,
        skills=minimal_skills,
        languages=[
            Language(id=EntryId("lang-en"), language="English", fluency="native"),
        ],
        conferences=[
            Conference(
                id=EntryId("conf-icml-2019"),
                name="ICML",
                date="2019",
                role="attendee",
            ),
            Conference(
                id=EntryId("conf-acl-review-2020"),
                name="ACL",
                date="2020",
                role="reviewer",
            ),
        ],
        memberships=[
            Membership(
                id=EntryId("member-asf"),
                organization="Apache Software Foundation",
                role="committer",
                start_date="2015",
                url="https://apache.org",
            ),
            Membership(
                id=EntryId("member-acm"),
                organization="ACM",
                role="",
                start_date="2010",
            ),
        ],
    )


@pytest.fixture
def minimal_taxonomy() -> TopicTaxonomy:
    return TopicTaxonomy(
        topics=[
            Topic(id="ai", label="Artificial Intelligence", aliases=["AI"]),
            Topic(id="ai.ml", label="Machine Learning", aliases=["ML"]),
            Topic(
                id="ai.ml.classification",
                label="Text Classification",
                aliases=["text classification"],
            ),
            Topic(id="systems", label="Systems Engineering"),
        ],
    )


@pytest.fixture
def minimal_semantics(minimal_taxonomy) -> SemanticOverlay:
    return SemanticOverlay(
        taxonomy=minimal_taxonomy,
        annotations=[
            EntryAnnotations(
                entry_id=EntryId("work-acme-2023"),
                topics=[
                    TopicAnnotation(
                        topic_id="ai.ml",
                        confidence=0.9,
                        provenance=Provenance.human,
                        primary=True,
                    ),
                ],
                audience_relevance=[
                    AudienceRelevance(
                        entry_id=EntryId("work-acme-2023"),
                        audience="hiring-manager",
                        relevance=RelevanceLevel.primary,
                        reason="Recent industry role",
                    ),
                ],
            ),
            EntryAnnotations(
                entry_id=EntryId("proj-widget"),
                topics=[
                    TopicAnnotation(
                        topic_id="ai.ml.classification",
                        confidence=0.8,
                        provenance=Provenance.llm,
                    ),
                ],
            ),
        ],
        relationships=[
            Relationship(
                source_id=EntryId("proj-widget"),
                target_id=EntryId("pub-nlp-2019"),
                type=RelationshipType.published_as,
                description="Widget project paper",
            ),
            Relationship(
                source_id=EntryId("proj-widget"),
                target_id=EntryId("patent-widget-2022"),
                type=RelationshipType.patented_as,
                description="Widget patent",
            ),
        ],
        skill_proficiency=[
            SkillProficiency(
                topic_id="ai.ml",
                level=ProficiencyLevel.expert,
                provenance=Provenance.human,
            ),
            SkillProficiency(
                topic_id="systems",
                level=ProficiencyLevel.advanced,
                provenance=Provenance.human,
            ),
        ],
    )


@pytest.fixture
def minimal_store(minimal_resume, minimal_semantics, tmp_path) -> ResumeStore:
    semantics_path = tmp_path / "resume-semantics.yaml"
    return ResumeStore(minimal_resume, minimal_semantics, semantics_path)


# --- Tier 2: Real data fixtures (session-scoped) ---


@pytest.fixture(scope="session")
def real_store() -> ResumeStore:
    return ResumeStore.load(DATA_DIR)
