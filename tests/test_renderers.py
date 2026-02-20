"""Tests for markdown, LaTeX, and HTML rendering."""

from __future__ import annotations

from collections import OrderedDict
from types import SimpleNamespace

from cv_mcp_server.renderers import (
    _build_project_links,
    _build_skill_levels,
    _clean_whitespace,
    _is_academic_work,
    _make_inst_name_filter,
    _normalize,
    _parse_sections,
    _patent_status_filter,
    _period_filter,
    get_section,
    render_html,
    render_latex,
    render_markdown,
    render_sections,
    render_tailored_latex,
    render_work_entry,
)
from cv_mcp_server.models.resume import PatentStatus
from cv_mcp_server.models.tailoring import (
    EntryEmphasis,
    SectionDirective,
    TailoringSpec,
)


# --- render_markdown ---


class TestRenderMarkdown:
    def test_returns_non_empty(self, minimal_store):
        md = render_markdown(minimal_store)
        assert len(md) > 0

    def test_contains_candidate_name(self, minimal_store):
        md = render_markdown(minimal_store)
        assert "Test Candidate" in md

    def test_trailing_newline(self, minimal_store):
        md = render_markdown(minimal_store)
        assert md.endswith("\n")


# --- render_latex ---


class TestRenderLatex:
    def test_render_latex_produces_output(self, minimal_store):
        latex = render_latex(minimal_store)
        assert len(latex) > 0

    def test_render_latex_has_document_structure(self, minimal_store):
        latex = render_latex(minimal_store)
        assert r"\documentclass" in latex
        assert r"\begin{document}" in latex
        assert r"\end{document}" in latex

    def test_render_latex_has_candidate_name(self, minimal_store):
        latex = render_latex(minimal_store)
        first_name = minimal_store.resume.personal_info.name.split()[0]
        last_name = minimal_store.resume.personal_info.name.split()[-1]
        assert first_name in latex
        assert last_name in latex

    def test_render_latex_has_sections(self, minimal_store):
        latex = render_latex(minimal_store)
        assert r"\section{Professional Experience}" in latex


# --- render_sections ---


class TestRenderSections:
    def test_returns_ordered_dict(self, minimal_store):
        sections = render_sections(minimal_store)
        assert isinstance(sections, OrderedDict)

    def test_expected_sections(self, minimal_store):
        sections = render_sections(minimal_store)
        names = set(sections.keys())
        assert "header" in names
        assert "Professional Experience" in names
        assert "Skills" in names

    def test_empty_sections_omitted(self, minimal_store):
        sections = render_sections(minimal_store)
        for content in sections.values():
            assert content.strip() != ""


# --- get_section ---


class TestGetSection:
    def test_case_insensitive(self, minimal_store):
        s = get_section(minimal_store, "professional experience")
        assert s is not None

    def test_ampersand_insensitive(self, minimal_store):
        s1 = get_section(minimal_store, "Leadership & Communication")
        s2 = get_section(minimal_store, "Leadership Communication")
        assert s1 == s2

    def test_not_found(self, minimal_store):
        assert get_section(minimal_store, "Nonexistent Section") is None


# --- render_work_entry ---


class TestRenderWorkEntry:
    def test_contains_position_and_institution(self, minimal_store):
        w = minimal_store.resume.work[0]
        md = render_work_entry(w, minimal_store)
        assert "Senior Engineer" in md
        assert "Acme Corp" in md

    def test_enrich_shows_published(self, minimal_store):
        w = minimal_store.resume.work[0]
        md = render_work_entry(w, minimal_store, enrich=True)
        assert "Published:" in md or "Patent:" in md

    def test_enrich_false_no_enrichment(self, minimal_store):
        w = minimal_store.resume.work[0]
        md = render_work_entry(w, minimal_store, enrich=False)
        assert "Published:" not in md
        assert "Patent:" not in md


# --- _build_project_links ---


class TestBuildProjectLinks:
    def test_returns_dict_keyed_by_project_id(self, minimal_store):
        links = _build_project_links(minimal_store)
        assert "proj-widget" in links

    def test_published_and_patented(self, minimal_store):
        links = _build_project_links(minimal_store)
        types = {link["type"] for link in links["proj-widget"]}
        assert "published-as" in types
        assert "patented-as" in types


# --- _build_skill_levels ---


class TestBuildSkillLevels:
    def test_maps_labels(self, minimal_store):
        levels = _build_skill_levels(minimal_store)
        assert levels["machine learning"] == "Expert"

    def test_maps_aliases(self, minimal_store):
        levels = _build_skill_levels(minimal_store)
        assert levels["ml"] == "Expert"


# --- _is_academic_work ---


class TestIsAcademicWork:
    def test_university_researcher(self, minimal_store):
        w = minimal_store.resume.work[1]  # work-testuni-2020 with role=Researcher
        assert _is_academic_work(w, minimal_store)

    def test_company_not_academic(self, minimal_store):
        w = minimal_store.resume.work[0]
        assert not _is_academic_work(w, minimal_store)


# --- _parse_sections ---


class TestParseSections:
    def test_single_section(self):
        raw = "<!-- SECTION: header -->\n# Name\n<!-- END_SECTION: header -->"
        sections = _parse_sections(raw)
        assert "header" in sections
        assert "# Name" in sections["header"]

    def test_multiple_sections(self):
        raw = (
            "<!-- SECTION: A -->\nContent A\n<!-- END_SECTION: A -->\n"
            "<!-- SECTION: B -->\nContent B\n<!-- END_SECTION: B -->"
        )
        sections = _parse_sections(raw)
        keys = list(sections.keys())
        assert keys == ["A", "B"]

    def test_empty_content_omitted(self):
        raw = "<!-- SECTION: Empty -->\n   \n<!-- END_SECTION: Empty -->"
        sections = _parse_sections(raw)
        assert "Empty" not in sections


# --- _clean_whitespace ---


class TestCleanWhitespace:
    def test_collapses_triple_newlines(self):
        assert _clean_whitespace("a\n\n\nb") == "a\n\nb"

    def test_strips_edges(self):
        assert _clean_whitespace("  hello  ") == "hello"


# --- _normalize ---


class TestNormalize:
    def test_lowercases(self):
        assert _normalize("HELLO") == "hello"

    def test_strips_ampersand(self):
        assert _normalize("A & B") == "a b"

    def test_collapses_whitespace(self):
        assert _normalize("a   b") == "a b"


# --- Jinja2 filters ---


class TestPeriodFilter:
    def test_both_dates(self):
        obj = SimpleNamespace(start_date="2020", end_date="2023")
        assert _period_filter(obj) == "2020\u20132023"

    def test_no_end(self):
        obj = SimpleNamespace(start_date="2020", end_date="")
        assert _period_filter(obj) == "2020\u2013Present"

    def test_no_start(self):
        obj = SimpleNamespace(start_date="", end_date="2023")
        assert _period_filter(obj) == ""


class TestPatentStatusFilter:
    def test_with_value(self):
        assert _patent_status_filter(PatentStatus.granted) == " (granted)"

    def test_none(self):
        assert _patent_status_filter(None) == ""


class TestInstNameFilter:
    def test_found(self, minimal_resume):
        filt = _make_inst_name_filter(minimal_resume)
        assert filt("inst-acme") == "Acme Corp"

    def test_unknown(self, minimal_resume):
        filt = _make_inst_name_filter(minimal_resume)
        assert filt("nonexistent") == "nonexistent"


# --- render_tailored_latex ---


class TestRenderTailoredLatex:
    def _make_spec(self, **overrides) -> TailoringSpec:
        """Build a TailoringSpec with sensible defaults, overridable per-test."""
        defaults = {
            "job_title": "Test Role",
            "section_order": [
                SectionDirective(
                    section_name="Professional Experience",
                    include=True,
                    position=0,
                ),
            ],
        }
        defaults.update(overrides)
        return TailoringSpec(**defaults)

    def test_render_tailored_latex_basic(self, minimal_store):
        spec = self._make_spec()
        output = render_tailored_latex(minimal_store, spec)
        assert len(output) > 0
        assert r"\documentclass" in output
        assert r"\begin{document}" in output
        assert r"\section{Professional Experience}" in output

    def test_render_tailored_latex_section_filtering(self, minimal_store):
        spec = self._make_spec()
        output = render_tailored_latex(minimal_store, spec)
        assert r"\section{Skills}" not in output
        assert r"\section{Education}" not in output
        assert r"\section{Languages}" not in output

    def test_render_tailored_latex_profile_override(self, minimal_store):
        spec = self._make_spec(
            section_order=[
                SectionDirective(
                    section_name="Profile and Goals",
                    include=True,
                    position=0,
                ),
            ],
            profile_override="Custom profile text for testing",
        )
        output = render_tailored_latex(minimal_store, spec)
        assert "Custom profile text for testing" in output

    def test_render_tailored_latex_entry_omission(self, minimal_store):
        spec = self._make_spec(
            entry_emphasis=[
                EntryEmphasis(entry_id="work-acme-2023", weight=0, reason="Not relevant"),
            ],
        )
        output = render_tailored_latex(minimal_store, spec)
        # "Acme Corp" is unique to the work entry (not in preamble personal data)
        assert "Acme Corp" not in output
        # The work entry's project should also be absent
        assert "Widget Builder" not in output


# --- render_html ---


class TestRenderHtml:
    def test_returns_non_empty(self, minimal_store):
        html = render_html(minimal_store)
        assert len(html) > 0

    def test_has_html_document_structure(self, minimal_store):
        html = render_html(minimal_store)
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html
        assert "<head>" in html
        assert "<body>" in html

    def test_contains_candidate_name(self, minimal_store):
        html = render_html(minimal_store)
        assert "Test" in html
        assert "Candidate" in html

    def test_self_contained_css(self, minimal_store):
        html = render_html(minimal_store)
        assert "<style>" in html
        assert "--bg:" in html

    def test_self_contained_js(self, minimal_store):
        html = render_html(minimal_store)
        assert "<script>" in html
        assert "applyTheme" in html

    def test_has_interactive_features(self, minimal_store):
        html = render_html(minimal_store)
        assert "expandable" in html
        assert "data-label" in html

    def test_enrichment_toggle(self, minimal_store):
        html = render_html(minimal_store, enrich=False)
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
