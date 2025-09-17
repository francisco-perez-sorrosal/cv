# Francisco Perez-Sorrosal CV

This repository contains Francisco Perez-Sorrosal's CV in multiple formats:

- **Main branch (`main`)**: Contains the LaTeX source CV and generated PDF
- **MCP branch (`mcp`)**: Contains a Python-based MCP (Model Context Protocol) server that serves the CV as a resource for AI systems

## LaTeX CV (Main Branch)

### Requirements (macOS)

- LaTeX distribution (MacTeX recommended)

MacTeX includes:

1. `pdflatex` a common compiler for converting LaTeX files into PDF
2. `latexmk` a Perl script that runs pdflatex plus other necessary tools like BibTeX or Biber

### Installing MacTeX with Homebrew

```bash
brew install --cask mactex
```

Or download from https://tug.org/mactex/

### CV Compilation

```bash
# Compile CV to PDF with latexmk (recommended) (-c cleans auxiliary files)
latexmk -pdf -c 2025_FranciscoPerezSorrosal_CV_English.tex

# or compile it with pdflatex
pdflatex 2025_FranciscoPerezSorrosal_CV_English.tex
```

## MCP Server (MCP Branch)

Refer to the documentation below:

1. [User Guide](https://github.com/francisco-perez-sorrosal/cv/blob/mcp/README_USER.md)
2. [Dev Documentation](https://github.com/francisco-perez-sorrosal/cv/blob/mcp/README_DEV.md)
3. [CI/CD Documentation](https://github.com/francisco-perez-sorrosal/cv/blob/mcp/README_CICD.md)
