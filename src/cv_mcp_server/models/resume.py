"""Structured CV data models based on JSON Resume schema with custom extensions.

Uses snake_case field names natively; camelCase aliases for JSON Resume export
via model_dump(by_alias=True).

Custom extensions beyond JSON Resume:
- work[].projects: nested projects within positions
- work[].roles: role tags per position
- patents[]: patent section
- conferences[]: conference attendance and reviewer roles
- memberships[]: professional memberships
- leadership[]: leadership & communication section
- publications[].citations: citation count
- publications[].authors: author list
- book_reviews[]: technical book reviewer credits
- All entry types have an 'id' field for semantic overlay references
"""

from __future__ import annotations

from enum import Enum
from typing import NewType

from pydantic import BaseModel, ConfigDict, Field

# Semantic type for entry identifiers. Distinguishes cross-reference fields
# from plain strings at the type level. Convention: <type>-<slug>.
EntryId = NewType("EntryId", str)


# --- Enums ---


class PatentStatus(str, Enum):
    application = "application"
    granted = "granted"


class LanguageFluency(str, Enum):
    native = "native"
    fluent = "fluent"
    professional = "professional"
    intermediate = "intermediate"
    beginner = "beginner"


class InstitutionType(str, Enum):
    company = "company"
    university = "university"
    research_institution = "research_institution"
    education_platform = "education_platform"
    government = "government"
    consortium = "consortium"
    cooperative = "cooperative"
    independent = "independent"


# --- Shared base ---


class ResumeEntry(BaseModel):
    """Base for all entries that participate in the semantic overlay."""

    model_config = ConfigDict(populate_by_name=True)

    id: EntryId = Field(
        description="Stable identifier for semantic overlay references. "
        "Convention: <type>-<slug> (e.g., 'work-yahoo-kgs-2023', 'patent-em-2019')."
    )


# --- Institution ---


class Institution(ResumeEntry):
    """An organization (company, university, education provider)."""

    name: str = Field(description="Canonical name")
    type: InstitutionType
    location: str = Field("", description="Primary location")
    url: str = ""
    aliases: list[str] = Field([], description="Former/alternative names")
    description: str = Field("", description="Brief description")


# --- PersonalInfo (JSON Resume 'basics') ---


class Location(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    address: str = ""
    city: str = ""
    region: str = Field("", alias="state")
    country_code: str = Field("", alias="countryCode")
    postal_code: str = Field("", alias="postalCode")


class Profile(BaseModel):
    """Social/professional profile link."""

    model_config = ConfigDict(populate_by_name=True)

    network: str = Field(description="Platform name (e.g., 'LinkedIn', 'GitHub')")
    url: str = ""
    username: str = ""


class PersonalInfo(BaseModel):
    """Candidate identity and contact info. Maps to JSON Resume 'basics'."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = ""
    label: str = Field(
        "", description="Professional title (e.g., 'Principal Research Engineer')"
    )
    email: str = ""
    phone: str = ""
    url: str = ""
    summary: str = ""
    location: Location = Location()
    profiles: list[Profile] = []


# --- Work ---


class Project(ResumeEntry):
    """A named project within a work position or standalone."""

    name: str
    start_date: str = Field("", alias="startDate")
    end_date: str = Field("", alias="endDate")
    description: str = ""
    description_label: str = Field(
        "",
        description="Label for description (e.g., 'Approach', 'Method'); when absent, description is plain text",
    )
    goal: str = Field("", description="Project goal statement")
    highlights: list[str] = []
    achievements: list[str] = Field(
        [], description="Outcomes distinct from goal and general highlights"
    )
    keywords: list[str] = []
    roles: list[str] = []
    entity: str = Field("", description="Parent company/org (for top-level projects)")
    type: str = ""
    url: str = ""


class WorkEntry(ResumeEntry):
    """A professional position. Projects are nested, not flat."""

    institution_id: EntryId = Field(description="Reference to institution")
    location: str = ""
    department: str = Field("", description="Team or department")
    employer_display: str = Field(
        "", description="Overrides default 'department @ institution' display name"
    )
    position: str = ""
    start_date: str = Field("", alias="startDate")
    end_date: str = Field("", alias="endDate")
    summary: str = ""
    roles: list[str] = Field(
        [], description="Role tags (e.g., 'ML/AI Expert', 'Tech Lead')"
    )
    highlights: list[str] = []
    url: str = ""
    projects: list[Project] = Field(
        [], description="Named projects within this position"
    )


# --- Patents (custom section) ---


class Patent(ResumeEntry):
    """Patent entry (not in JSON Resume)."""

    number: str = Field(description="Patent application or grant number")
    title: str
    date: str = Field(description="Year filed or granted")
    status: PatentStatus
    url: str = ""
    inventors: list[str] = []


# --- Publications ---


class Publication(ResumeEntry):
    """Academic publication. Extends JSON Resume with citations and authors."""

    name: str
    publisher: str = Field("", description="Venue (conference, journal)")
    release_date: str = Field("", alias="releaseDate")
    url: str = ""
    summary: str = ""
    authors: list[str] = []
    citations: int = Field(0, description="Citation count")


# --- Education ---


class Education(ResumeEntry):
    institution_id: EntryId = Field(description="Reference to institution")
    department: str = Field(
        "", description="School or institute within the institution"
    )
    area: str = Field("", description="Field of study")
    study_type: str = Field("", alias="studyType", description="Degree type")
    start_date: str = Field("", alias="startDate")
    end_date: str = Field("", alias="endDate")
    location: str = ""
    score: str = ""
    courses: list[str] = []


# --- Skills ---


class Skill(BaseModel):
    """A skill subcategory with keyword list."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(
        description="Subcategory name (e.g., 'Languages', 'ML Frameworks')"
    )
    keywords: list[str] = []


class SkillGroup(ResumeEntry):
    """Top-level skill category (e.g., 'Programming', 'Data Infrastructure')."""

    name: str = Field(description="Category name")
    skills: list[Skill] = Field([], description="Subcategories within this group")


# --- Certificates ---


class Certificate(ResumeEntry):
    name: str
    date: str = ""
    institution_id: EntryId = Field(description="Reference to institution (issuer)")
    url: str = ""
    location: str = Field("", description="Where the course took place")
    format: str = Field(
        "", description="Delivery format (e.g., 'In-Person', 'Remote', 'Online')"
    )


# --- Languages ---


class Language(ResumeEntry):
    language: str
    fluency: str = ""


# --- Conferences (custom section) ---


class Conference(ResumeEntry):
    """Conference attendance/participation (not in JSON Resume)."""

    name: str
    start_date: str = Field(
        "",
        alias="startDate",
        description="First day (YYYY-MM-DD) or year only for reviewer entries",
    )
    end_date: str = Field(
        "",
        alias="endDate",
        description="Last day (YYYY-MM-DD); equals start_date for single-day events",
    )
    location: str = ""
    role: str = Field("", description="attendee, speaker, organizer, reviewer")
    url: str = ""


# --- Memberships (custom section) ---


class Membership(ResumeEntry):
    """Professional membership (not in JSON Resume)."""

    organization: str
    role: str = ""
    start_date: str = Field("", alias="startDate")
    end_date: str = Field("", alias="endDate")
    url: str = ""


# --- Book Reviews (custom section) ---


class BookReview(ResumeEntry):
    """Technical book reviewer credit (not in JSON Resume)."""

    title: str = Field(description="Book title")
    author: str = Field("", description="Book author(s)")
    publisher: str = Field("", description="Publisher name")
    date: str = Field("", description="Publication year or date")
    url: str = ""


# --- Leadership & Communication ---


class LeadershipItem(BaseModel):
    """A single leadership/communication item (e.g., a cvitem in LaTeX)."""

    model_config = ConfigDict(populate_by_name=True)

    label: str = Field(description="Category label (e.g., 'Research', 'Apache')")
    description: str = ""


class LeadershipCategory(BaseModel):
    """A subsection within Leadership & Communication."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(
        description="Subsection name (e.g., 'Mentoring & Team Leadership')"
    )
    items: list[LeadershipItem] = []


# --- Interests ---


class Interest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: str = Field(
        "", description="Narrative description of the interest area"
    )
    keywords: list[str] = []


# --- Meta ---


class Meta(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    version: str = Field("1.0.0", description="Schema version (semver)")
    canonical: str = Field(
        "", description="URL to the canonical version of this resume"
    )
    last_modified: str = Field("", alias="lastModified")


# --- Top-level Resume ---


class Resume(BaseModel):
    """JSON Resume-compatible schema with custom extensions.

    Custom extensions beyond JSON Resume:
    - work[].projects: nested projects within positions
    - work[].roles: role tags per position
    - patents[]: patent section
    - conferences[]: conference attendance and reviewer roles
    - memberships[]: professional memberships
    - book_reviews[]: technical book reviewer credits
    - leadership[]: leadership & communication section
    - publications[].citations: citation count
    - publications[].authors: author list
    - All entry types have an 'id' field for semantic overlay references
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    personal_info: PersonalInfo = Field(PersonalInfo(), alias="basics")
    quote: str = ""
    institutions: list[Institution] = Field(
        [], description="Organizations referenced by work, education, certificates"
    )
    work: list[WorkEntry] = []
    education: list[Education] = []
    publications: list[Publication] = []
    skills: list[SkillGroup] = []
    languages: list[Language] = []
    certificates: list[Certificate] = []
    interests: list[Interest] = []
    projects: list[Project] = Field(
        [], description="Standalone projects not tied to a specific position"
    )
    patents: list[Patent] = []
    conferences: list[Conference] = []
    memberships: list[Membership] = []
    book_reviews: list[BookReview] = Field(
        [], description="Technical book reviewer credits"
    )
    leadership: list[LeadershipCategory] = []
    meta: Meta = Meta()

    def institution_by_id(self, inst_id: str) -> Institution | None:
        """Look up an institution by ID."""
        return next((i for i in self.institutions if i.id == inst_id), None)

    def all_entry_ids(self) -> set[EntryId]:
        """Collect all entry IDs across all sections for overlay validation."""
        ids: set[EntryId] = set()
        for inst in self.institutions:
            ids.add(inst.id)
        for work in self.work:
            ids.add(work.id)
            for project in work.projects:
                ids.add(project.id)
        for section in [
            self.education,
            self.publications,
            self.skills,
            self.languages,
            self.certificates,
            self.projects,
            self.patents,
            self.conferences,
            self.memberships,
            self.book_reviews,
        ]:
            for entry in section:
                ids.add(entry.id)
        return ids
