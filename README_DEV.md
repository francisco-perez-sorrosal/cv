# Francisco Perez-Sorrosal CV

This repository contains Francisco Perez-Sorrosal's CV in LaTeX format.

## Requirements (macOS)

- LaTeX distribution (MacTeX recommended)

MacTeX includes:

1. `pdflatex` a common compiler for converting LaTeX files into PDF
2. `latexmk` a Perl script that runs pdflatex plus other necessary tools like BibTeX or Biber

### Installing MacTeX with Homebrew

```bash
brew install --cask mactex
```

Or download from https://tug.org/mactex/

## CV Compilation

```bash
# Compile CV to PDF with latexmk (recommended) (-c cleans auxiliary files)
latexmk -pdf -c 2025_FranciscoPerezSorrosal_CV_English.tex

# or compile it with pdflatex
pdflatex 2025_FranciscoPerezSorrosal_CV_English.tex
```

## Dev
1. [Dev Doc](https://github.com/francisco-perez-sorrosal/cv/blob/mcp/README_DEV.md)
2. [CICD Doc](https://github.com/francisco-perez-sorrosal/cv/blob/mcp/README_CICD.md)
