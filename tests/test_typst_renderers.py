"""Tests for Typst rendering: filters, full CV, and tailored CV."""

from __future__ import annotations

from types import SimpleNamespace

from cv_mcp_server.renderers import (
    _typst_escape_filter,
    _typst_period_filter,
    render_typst,
    render_tailored_typst,
)
from cv_mcp_server.models.tailoring import (
    EntryEmphasis,
    SectionDirective,
    TailoringSpec,
)


# --- Typst escape filter ---


class TestTypstEscapeFilter:
    def test_escapes_hash(self):
        assert _typst_escape_filter("#set") == "\\#set"

    def test_escapes_dollar(self):
        assert _typst_escape_filter("$x$") == "\\$x\\$"

    def test_escapes_at(self):
        assert _typst_escape_filter("@ref") == "\\@ref"

    def test_escapes_angle_brackets(self):
        assert _typst_escape_filter("<label>") == "\\<label\\>"

    def test_plain_text_unchanged(self):
        assert _typst_escape_filter("Hello world") == "Hello world"

    def test_mixed_special_chars(self):
        result = _typst_escape_filter("Use #func with $math and @cite")
        assert "\\#func" in result
        assert "\\$math" in result
        assert "\\@cite" in result

    def test_empty_string(self):
        assert _typst_escape_filter("") == ""


# --- Typst period filter ---


class TestTypstPeriodFilter:
    def test_year_range(self):
        obj = SimpleNamespace(start_date="2020", end_date="2023")
        assert _typst_period_filter(obj) == "2020--2023"

    def test_no_end_date(self):
        obj = SimpleNamespace(start_date="2020", end_date="")
        assert _typst_period_filter(obj) == "2020--Now"

    def test_no_start_date(self):
        obj = SimpleNamespace(start_date="", end_date="2023")
        assert _typst_period_filter(obj) == ""

    def test_same_year_only(self):
        obj = SimpleNamespace(start_date="2022", end_date="2022")
        assert _typst_period_filter(obj) == "2022"

    def test_same_year_with_months(self):
        obj = SimpleNamespace(start_date="2022-06", end_date="2022-12")
        assert _typst_period_filter(obj) == "Jun--Dec 2022"

    def test_cross_year_with_months(self):
        obj = SimpleNamespace(start_date="2021-03", end_date="2023-09")
        assert _typst_period_filter(obj) == "Mar 2021--Sep 2023"

    def test_start_month_end_year_only(self):
        obj = SimpleNamespace(start_date="2021-06", end_date="2023")
        assert _typst_period_filter(obj) == "Jun 2021--2023"


# --- render_typst ---


class TestRenderTypst:
    def test_render_typst_produces_output(self, minimal_store):
        output = render_typst(minimal_store)
        assert len(output) > 0

    def test_render_typst_has_moderner_cv_import(self, minimal_store):
        output = render_typst(minimal_store)
        assert '#import "@preview/moderner-cv' in output

    def test_render_typst_has_candidate_name(self, minimal_store):
        output = render_typst(minimal_store)
        first_name = minimal_store.resume.personal_info.name.split()[0]
        last_name = minimal_store.resume.personal_info.name.split()[-1]
        assert first_name in output
        assert last_name in output

    def test_render_typst_has_sections(self, minimal_store):
        output = render_typst(minimal_store)
        assert "= Professional Experience" in output

    def test_render_typst_enrich_default(self, minimal_store):
        output = render_typst(minimal_store, enrich=True)
        # Enriched output includes project cross-references (published-as, patented-as)
        assert "Published:" in output or "Patent:" in output

    def test_render_typst_enrich_false(self, minimal_store):
        output = render_typst(minimal_store, enrich=False)
        # Non-enriched output omits project cross-references
        assert "Published:" not in output
        assert "Patent:" not in output


# --- render_tailored_typst ---


class TestRenderTailoredTypst:
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

    def test_render_tailored_typst_basic(self, minimal_store):
        spec = self._make_spec()
        output = render_tailored_typst(minimal_store, spec)
        assert len(output) > 0
        assert '#import "@preview/moderner-cv' in output
        assert "= Professional Experience" in output

    def test_render_tailored_typst_section_filtering(self, minimal_store):
        spec = self._make_spec()
        output = render_tailored_typst(minimal_store, spec)
        assert "= Skills" not in output
        assert "= Education" not in output
        assert "= Languages" not in output

    def test_render_tailored_typst_profile_override(self, minimal_store):
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
        output = render_tailored_typst(minimal_store, spec)
        assert "Custom profile text for testing" in output

    def test_render_tailored_typst_entry_omission(self, minimal_store):
        spec = self._make_spec(
            entry_emphasis=[
                EntryEmphasis(entry_id="work-acme-2023", weight=0, reason="Not relevant"),
            ],
        )
        output = render_tailored_typst(minimal_store, spec)
        # "Acme Corp" is unique to the work entry (not in preamble personal data)
        assert "Acme Corp" not in output
        # The work entry's project should also be absent
        assert "Widget Builder" not in output
