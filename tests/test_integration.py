"""Integration tests using real YAML data files."""

from __future__ import annotations

import pytest

from cv_mcp_server.renderers import (
    get_section,
    render_latex,
    render_markdown,
    render_sections,
    render_tailored_latex,
)
from cv_mcp_server.models.tailoring import SectionDirective, TailoringSpec

pytestmark = pytest.mark.integration


class TestDataLoading:
    def test_work_entry_count(self, real_store):
        assert len(real_store.resume.work) >= 16

    def test_publication_count(self, real_store):
        assert len(real_store.resume.publications) >= 10

    def test_patent_count(self, real_store):
        assert len(real_store.resume.patents) >= 2

    def test_institutions_non_empty(self, real_store):
        assert len(real_store.resume.institutions) > 0

    def test_semantics_loaded(self, real_store):
        assert len(real_store.semantics.annotations) > 0


class TestEntryIds:
    def test_count(self, real_store):
        ids = real_store.resume.all_entry_ids()
        assert len(ids) >= 140

    def test_known_entries_exist(self, real_store):
        assert real_store.entry_by_id("inst-yahoo") is not None
        assert real_store.entry_by_id("inst-upm") is not None

    def test_labels_non_empty(self, real_store):
        for entry_id in list(real_store.resume.all_entry_ids())[:20]:
            label = real_store.entry_label(entry_id)
            assert label and len(label) > 0


class TestSemanticQueries:
    def test_entries_by_topic_ai(self, real_store):
        results = real_store.entries_by_topic("ai")
        assert len(results) >= 2

    def test_relationships_for_known_project(self, real_store):
        all_rels = real_store.semantics.relationships
        assert len(all_rels) > 0

    def test_skill_proficiency_non_empty(self, real_store):
        assert len(real_store.semantics.skill_proficiency) > 0

    def test_taxonomy_topic_count(self, real_store):
        assert len(real_store.semantics.taxonomy.topics) >= 33


class TestRendering:
    def test_full_markdown_length(self, real_store):
        md = render_markdown(real_store)
        assert len(md) > 1000

    def test_section_count(self, real_store):
        sections = render_sections(real_store)
        assert len(sections) >= 13

    def test_case_insensitive_section_lookup(self, real_store):
        s = get_section(real_store, "skills")
        assert s is not None


class TestRenderLatexRealData:
    def test_render_latex_real_data(self, real_store):
        latex = render_latex(real_store)
        assert len(latex) > 1000
        assert r"\section{Professional Experience}" in latex
        assert "Francisco" in latex


class TestEnrichmentToggle:
    def test_enrich_true_contains_published(self, real_store):
        md = render_markdown(real_store, enrich=True)
        assert "Published:" in md or "Patent:" in md

    def test_enrich_false_no_published(self, real_store):
        md = render_markdown(real_store, enrich=False)
        assert "Published:" not in md


class TestCrossReferences:
    def test_no_dangling_warnings(self, real_store):
        warnings: list[str] = []
        from loguru import logger
        handler_id = logger.add(lambda msg: warnings.append(str(msg)), level="WARNING")
        try:
            real_store._validate_cross_references()
        finally:
            logger.remove(handler_id)
        assert not any("unknown entry IDs" in w for w in warnings)


class TestWorkQueries:
    def test_work_by_company_yahoo(self, real_store):
        results = real_store.work_by_company("Yahoo")
        assert len(results) >= 1

    def test_work_by_alias_verizon(self, real_store):
        results = real_store.work_by_company("Verizon Media")
        assert len(results) >= 1


class TestGetTailoredCvTool:
    def test_invalid_json_returns_schema(self):
        from cv_mcp_server.tools.data import get_tailored_cv

        result = get_tailored_cv('{"not": "a valid spec"}')
        assert "Invalid TailoringSpec" in result
        assert "json_schema" in result.lower() or "properties" in result

    def test_empty_string_returns_schema(self):
        from cv_mcp_server.tools.data import get_tailored_cv

        result = get_tailored_cv("")
        assert "Invalid TailoringSpec" in result


class TestRenderTailoredLatexRealData:
    def test_render_tailored_latex_real_data(self, real_store):
        spec = TailoringSpec(
            job_title="Senior ML Engineer",
            company="Test Corp",
            section_order=[
                SectionDirective(section_name="Professional Experience", include=True, position=0),
                SectionDirective(section_name="Skills", include=True, position=1),
                SectionDirective(section_name="Education", include=True, position=2),
            ],
        )
        tailored = render_tailored_latex(real_store, spec)
        full = render_latex(real_store)

        assert r"\section{Professional Experience}" in tailored
        assert r"\section{Skills}" in tailored
        assert r"\section{Education}" in tailored
        assert len(tailored) < len(full)

    def test_section_names_match_list_cv_sections(self, real_store):
        """Regression test for F-02: section names in tailored template must match
        the names returned by list_cv_sections (markdown renderer)."""
        from cv_mcp_server.renderers import section_names

        md_names = section_names(real_store)
        # These three sections had mismatched names before the fix
        previously_mismatched = [
            "Courses and Certifications",
            "Leadership & Communication",
            "Other Activities Related to CS",
        ]
        for name in previously_mismatched:
            assert name in md_names, f"'{name}' not in list_cv_sections output"
            spec = TailoringSpec(
                job_title="Test",
                section_order=[SectionDirective(section_name=name, include=True, position=0)],
            )
            tailored = render_tailored_latex(real_store, spec)
            # Each section renders its LaTeX \section{} -- verify it appears
            assert r"\section{" in tailored, f"Section '{name}' not rendered in tailored output"
