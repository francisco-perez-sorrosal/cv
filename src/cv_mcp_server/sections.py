"""CV content parsed into structured sections for targeted retrieval."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

import pymupdf4llm
from loguru import logger

_SECTION_HEADING = re.compile(r"^### \*\*(.+?)\*\*\s*$", re.MULTILINE)
_PAGE_MARKER = re.compile(r"^\*\d+/\d+\*\s*$", re.MULTILINE)


def _normalize(name: str) -> str:
    """Lowercase, strip '&', and collapse whitespace for fuzzy matching."""
    return re.sub(r"\s+", " ", name.lower().replace("&", "").strip())


def _parse_sections(markdown: str) -> dict[str, str]:
    """Split markdown by heading boundaries into named sections.

    Text before the first heading is stored under key "header".
    Page markers (*N/M*) are stripped from all content.
    """
    cleaned = _PAGE_MARKER.sub("", markdown)
    matches = list(_SECTION_HEADING.finditer(cleaned))

    sections: dict[str, str] = {}

    if matches:
        header_text = cleaned[: matches[0].start()].strip()
        if header_text:
            sections["header"] = header_text

    for i, match in enumerate(matches):
        key = match.group(1)  # preserve original heading (e.g. "Leadership & Communication")
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned)
        sections[key] = cleaned[start:end].strip()

    return sections


@dataclass(frozen=True)
class CvContent:
    """Immutable snapshot of parsed CV content: full markdown and named sections.

    Create a new instance to get fresh content (e.g. after the PDF changes on disk).
    """

    markdown: str
    sections: MappingProxyType[str, str] = field(default_factory=lambda: MappingProxyType({}))

    @classmethod
    def from_pdf(cls, cv_path: Path) -> "CvContent":
        """Parse a PDF file into a CvContent snapshot."""
        if not cv_path.exists():
            logger.warning(f"CV not found at {cv_path}")
            return cls(markdown="There's no CV found!")

        logger.info(f"Parsing CV from {cv_path}...")
        markdown = pymupdf4llm.to_markdown(str(cv_path))
        sections = MappingProxyType(_parse_sections(markdown))
        logger.info(f"Parsed {len(sections)} CV sections")
        return cls(markdown=markdown, sections=sections)

    def get_section(self, name: str) -> str | None:
        """Look up a section by name (case-insensitive, '&'-insensitive)."""
        normalized = _normalize(name)
        for key, content in self.sections.items():
            if _normalize(key) == normalized:
                return content
        return None

    def section_names(self) -> list[str]:
        """Return available section names."""
        return list(self.sections.keys())
