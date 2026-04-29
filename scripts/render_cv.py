#!/usr/bin/env python3
"""Render the CV from YAML data to a chosen output format.

Quick render to rendered-cv/ (no compilation):
    python scripts/render_cv.py -f html
    python scripts/render_cv.py -f tex

Snapshot + compile + symlink (full pipeline via pixi run render-cv):
    python scripts/render_cv.py -f tex --snapshot --compile --symlink latest.pdf
"""

import argparse
import datetime
import shutil
import subprocess
import sys
from pathlib import Path

from cv_mcp_server.renderers import (
    render_html,
    render_latex,
    render_markdown,
    render_typst,
)
from cv_mcp_server.store import ResumeStore

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# (output-subdir, default-filename, render-function)
FORMATS = {
    "tex": ("tex", "FranciscoPerezSorrosal_CV_English.tex", render_latex),
    "md": ("md", "FranciscoPerezSorrosal_CV_English.md", render_markdown),
    "html": ("html", "FranciscoPerezSorrosal_CV_English.html", render_html),
    "typst": ("typst", "FranciscoPerezSorrosal_CV_English.typ", render_typst),
}


# --- Output path helpers ---


def _quick_output(fmt: str) -> Path:
    subdir, filename, _ = FORMATS[fmt]
    return PROJECT_ROOT / "rendered-cv" / subdir / filename


def _snapshot_output(fmt: str) -> Path:
    subdir, filename, _ = FORMATS[fmt]
    stem, suffix = Path(filename).stem, Path(filename).suffix
    date = datetime.date.today().strftime("%Y-%m-%d")
    return PROJECT_ROOT / "latest-cv" / subdir / f"{date}_{stem}{suffix}"


# --- Compiler implementations ---


def _compile_latex(source: Path) -> Path:
    """Compile .tex → PDF with latexmk; cleans aux files on success. Returns PDF path."""
    out_dir = source.parent
    result = subprocess.run(
        [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            f"-output-directory={out_dir}",
            str(source),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(f"latexmk failed (exit {result.returncode})")
    # Keep the PDF, remove aux files
    subprocess.run(
        ["latexmk", "-c", f"-output-directory={out_dir}", str(source)],
        capture_output=True,
    )
    return source.with_suffix(".pdf")


# Registry: format → compile callable, or None when not yet supported.
COMPILERS: dict[str, object] = {
    "tex": _compile_latex,
    "md": None,
    "html": None,
    "typst": None,  # future: typst compile <source> --output <pdf>
}


# --- Symlink helper ---


def _copy_pdf(dest: Path, source: Path) -> None:
    """Copy source PDF to dest so the file works as a direct GitHub download link.

    Removes an existing file or symlink at dest before copying.
    """
    if dest.is_symlink() or dest.exists():
        dest.unlink()
    shutil.copy2(source, dest)
    print(f"Copied    {source.name} -> {dest}")


# --- CLI ---


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render CV from YAML data to a chosen format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  quick preview (rendered-cv/html/):
    python scripts/render_cv.py -f html

  full pipeline — snapshot + PDF + symlink (default pixi run render-cv):
    python scripts/render_cv.py -f tex --snapshot --compile --symlink latest.pdf
""",
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
        help="Explicit output file path; overrides --snapshot and the default path",
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Write to latest-cv/<format>/<YYYY-MM-DD>_<name> instead of rendered-cv/",
    )
    parser.add_argument(
        "--compile",
        action="store_true",
        help="Compile rendered source to PDF (tex: latexmk; others: not yet supported)",
    )
    parser.add_argument(
        "--symlink",
        metavar="PATH",
        default=None,
        help="Copy compiled PDF to PATH (real file, not symlink — works as a direct GitHub link)",
    )
    args = parser.parse_args()

    if args.compile and COMPILERS[args.fmt] is None:
        raise SystemExit(f"--compile is not yet supported for format '{args.fmt}'")
    if args.symlink and not args.compile:
        raise SystemExit("--symlink requires --compile")

    # Resolve output path
    if args.output:
        output_path = Path(args.output)
    elif args.snapshot:
        output_path = _snapshot_output(args.fmt)
    else:
        output_path = _quick_output(args.fmt)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Render source
    _, _, render_fn = FORMATS[args.fmt]
    store = ResumeStore.load(PROJECT_ROOT / "cv-data")
    output_path.write_text(render_fn(store), encoding="utf-8")
    print(f"Rendered  {output_path}")

    # Compile to PDF
    if args.compile:
        compile_fn = COMPILERS[args.fmt]
        pdf_path = compile_fn(output_path)
        print(f"Compiled  {pdf_path}")

        if args.symlink:
            _copy_pdf(PROJECT_ROOT / args.symlink, pdf_path)


if __name__ == "__main__":
    main()
