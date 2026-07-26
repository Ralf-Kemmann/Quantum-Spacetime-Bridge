# Repository Guide

## Recommended reading order

The repository is large because it preserves a detailed audit trail. For orientation, use this order:

1. [`README.md`](../../README.md)
2. [`CURRENT_STATUS.md`](CURRENT_STATUS.md)
3. [`CLAIM_BOUNDARIES.md`](CLAIM_BOUNDARIES.md)
4. [`RESEARCH_INFRASTRUCTURE.md`](RESEARCH_INFRASTRUCTURE.md)
5. the specific run, model, or publication strand of interest

Do not infer the current project position from an arbitrary historical result note.

## Main directories

### `docs/`

Specifications, status notes, result discussions, field lists, public orientation, and methodological records.

`docs/public/` is the outward-facing entry layer. Older documents elsewhere in `docs/` may describe historical stages and retain their original claim status.

### `data/`

Controlled input tables, configuration files, manifests, metadata seeds, and source-linked records.

Raw third-party material may remain local when licensing or size prevents repository publication.

### `scripts/`

Executable research, import, validation, and reporting scripts.

### `runs/`

Run-specific records, outputs, validations, review decisions, and lineage material that are tracked as part of the audit history.

Some local generated run outputs may be ignored. The presence or absence of a directory alone is not a publication claim.

### `numerics/`

Model-specific numerical work, configurations, and analysis components.

### `validation/` and `tests/`

Cross-project checks, validation logic, and test cases.

### `results/`

Selected compact public-facing summaries. This is not a replacement for detailed run lineage.

### `figures/`

Scientific figures and conceptual editorial illustrations. Their roles must remain clearly labelled.

### `artifacts/`

Packaged research artifacts, hand-offs, and reproducibility material.

### `exports/`

Local generated exports. This directory is ignored by Git and should not be used as a canonical public source.

## Public and historical layers

The repository contains several generations of research:

- early wave-based and pair-H3 work;
- topology and structure-memory diagnostics;
- causal-structure candidates;
- observational and timing-data investigations;
- PostgreSQL DWH and metadata development;
- Planck Bridge Resonator work;
- coupled matter–edge-field graph dynamics;
- publication and research-infrastructure work.

These strands are connected historically, but their scientific claims are not automatically interchangeable.

## Canonicality

A file is not canonical merely because it is recent or prominently named.

Canonical status depends on:

- source identity;
- version and lineage;
- run and review status;
- validation outcome;
- explicit freeze or release decision;
- applicable claim boundary.

The metadata and run records should be consulted before reusing a value or statement.

## Local exports and working-tree cleanliness

Generated snapshot packages and database exports belong under `exports/` and are intentionally ignored. Public release artifacts should be created through a deliberate versioned release process rather than by committing a local export directory.

## Contributions and feedback

The project is maintained as an independent research programme.

Reproducibility reports, source corrections, and clearly scoped scientific comments are welcome. Proposed changes should identify the affected file, run, source, or claim boundary and should not silently rewrite historical records.
