#!/usr/bin/env python3
"""Generate LaTeX CV from YAML data."""

import argparse
from pathlib import Path

from cv_mcp_server.renderers import render_latex
from cv_mcp_server.store import ResumeStore


def main():
    parser = argparse.ArgumentParser(description="Generate LaTeX CV from YAML data")
    parser.add_argument(
        "--output", "-o",
        default="2026_FranciscoPerezSorrosal_CV_English.tex",
        help="Output .tex file path",
    )
    args = parser.parse_args()

    data_dir = Path(__file__).resolve().parent.parent / "src" / "cv_mcp_server" / "data"
    store = ResumeStore.load(data_dir)
    output_path = Path(args.output)
    output_path.write_text(render_latex(store))
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
