#!/usr/bin/env python3
"""Render the CV from YAML data to a chosen output format."""

import argparse
from pathlib import Path

from cv_mcp_server.renderers import (
    render_html,
    render_latex,
    render_markdown,
    render_typst,
)
from cv_mcp_server.store import ResumeStore

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FORMATS = {
    "tex": ("tex", "FranciscoPerezSorrosal_CV_English.tex", render_latex),
    "md": ("md", "FranciscoPerezSorrosal_CV_English.md", render_markdown),
    "html": ("html", "FranciscoPerezSorrosal_CV_English.html", render_html),
    "typst": ("typst", "FranciscoPerezSorrosal_CV_English.typ", render_typst),
}


def default_output(fmt: str) -> Path:
    subdir, filename, _ = FORMATS[fmt]
    return PROJECT_ROOT / "rendered-cv" / subdir / filename


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render CV from YAML data to a chosen format"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=list(FORMATS),
        default="tex",
        dest="fmt",
        help="Output format (default: tex)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output file path (default: rendered-cv/<format>/<filename>)",
    )
    args = parser.parse_args()

    _, _, render_fn = FORMATS[args.fmt]
    output_path = Path(args.output) if args.output else default_output(args.fmt)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    store = ResumeStore.load(PROJECT_ROOT / "cv-data")
    output_path.write_text(render_fn(store), encoding="utf-8")
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
