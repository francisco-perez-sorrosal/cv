# CLAUDE.md

## Repository Overview

This repository is the single source of truth for Francisco Perez-Sorrosal's CV content. It contains only data (YAML), schema definitions, and CI workflows that validate and publish. All tooling (rendering, serving, editing) lives in the [`cv-forge`](https://github.com/francisco-perez-sorrosal/cv-forge) repository.

## Data Files

- `cv-data/resume.yaml` — the primary CV data (experience, education, skills, patents, publications, languages)
- `cv-data/resume-semantics.yaml` — semantic overlay (topics, relationships, cross-entry annotations)
- `schemas/` — JSON Schema files (`resume.schema.json`, `semantics.schema.json`) mirrored from `cv-forge@v1`

## Editing Conventions

**Entry IDs** — every entry that can be referenced carries an `id` field in the form `<type>-<slug>`, e.g. `work-yahoo-kgs-2023`, `pub-htl-acl-2019`, `patent-em-2019`.

**Cross-references** — entries with an `institution_id` field (work, education, certificates) must name a declared institution from `institutions[]`. The schema enforces this; `cv-forge validate` flags unknown references with hints.

**Chronological order** — within `work`, `education`, and `certificates`: list most recent first.

**Date format** — `YYYY` or `YYYY-MM` for start/end dates on work, education, certificates. Conferences use full `YYYY-MM-DD` (different family — do not reuse their format elsewhere).

**Semantic overlay references** — every `entry_id` in `resume-semantics.yaml` must name an actual entry in `resume.yaml`. Edit both files together when removing an entry.

## Validation

Validate before every PR:

```bash
check-jsonschema --schemafile schemas/resume.schema.json cv-data/resume.yaml
check-jsonschema --schemafile schemas/semantics.schema.json cv-data/resume-semantics.yaml
```

The CI workflow runs these checks automatically; local validation catches issues faster.

## Publishing

Push a CalVer tag (`YYYY.MM.DD`) and the publishing workflow runs automatically, rendering all formats and creating a GitHub Release.

```bash
git tag 2026.09.13
git push origin 2026.09.13
```

All assets are published at stable, version-free URLs under `releases/latest/download/`.

## No tooling here

Do not add render logic, CLI commands, or scripting to this repository. This is a data-only repo; machinery (rendering, validation, serving, editing) lives in [`cv-forge`](https://github.com/francisco-perez-sorrosal/cv-forge).

## Rendered artifacts are release assets

Never commit PDF, LaTeX, HTML, or Typst output to this repository. Rendered artifacts are generated at publish time and distributed as GitHub Release assets.

## Personal information

This repository contains Francisco's real professional information (work history, projects, contact links). Handle appropriately.
