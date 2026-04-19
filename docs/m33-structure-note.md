# M33 Structure Note

## Purpose of this document

This note records the current structural understanding of the `m33_v0_scaffold` area inside the consolidated numerics subtree.

Its purpose is to prevent premature cleanup decisions in a part of the project that already shows signs of internal structural branching rather than simple accidental duplication.

## Location

The relevant area is located under:

```text
numerics/debroglie-phase-bridge/m33_v0_scaffold/
```

This subtree appears to contain the M33-related scaffold and associated implementation, run material, and patch-like branches.

## Why this note is necessary

During the numerics cleanup inventory, several apparently duplicated M33-related files were identified by basename, including:

- `bootstrap_m33_v0.sh`
- `config_m33_v0.yaml`
- `columns_m33_v0.py`
- `config_schema.py`
- `m33_v0_runner.py`

At first glance, these looked like possible duplication candidates. However, additional inspection showed that at least part of the structure is **not** a trivial mirror.

This means that the M33 area must currently be treated as a **branching structure requiring interpretation**, not as a simple cleanup target.

## Observed structural branches

The current M33-related structure includes at least the following visible branches:

### 1. Root-level M33 bootstrap

```text
numerics/debroglie-phase-bridge/bootstrap_m33_v0.sh
```

This appears to be a higher-level bootstrap entry point.

### 2. Main scaffold area

```text
numerics/debroglie-phase-bridge/m33_v0_scaffold/
```

This is the core M33 scaffold area and contains:

- `configs/`
- `docs/`
- `logs/`
- `notes/`
- `runs/`
- `scripts/`
- `src/`

### 3. Patch / local candidate branch

```text
numerics/debroglie-phase-bridge/m33_v0_scaffold/m33_v0_patch_local_candidates/
```

This appears to be a patch-like or local-candidate branch with its own:

- `configs/`
- `scripts/`
- `src/`

This suggests that the subtree contains not only a main scaffold, but also an explicit candidate or patch branch.

## Key current finding

A direct comparison between M33 files under `src/` and `scripts/` showed that they are **not simply identical duplicates**.

At least one inspected file pair showed real content divergence:

- `m33_v0_scaffold/src/columns_m33_v0.py`
- `m33_v0_scaffold/scripts/columns_m33_v0.py`

The observed differences were not merely cosmetic. They affected structural field definitions and output column groupings, indicating that these two locations may reflect different development states, usage roles, or logic branches.

## Consequence for cleanup

Because the M33-related branches are not yet proven to be redundant, the following cleanup rule now applies:

> No automatic deletion, deduplication, or archive move of M33 scaffold duplicates should be performed until their functional role is clarified.

This is especially important for:

- `src/`
- `scripts/`
- `m33_v0_patch_local_candidates/`

## Current interpretation

The current best interpretation is:

- `m33_v0_scaffold/src/` may represent a main implementation branch
- `m33_v0_scaffold/scripts/` may represent runner-facing or script-oriented variants
- `m33_v0_patch_local_candidates/` may represent a patch or candidate-development branch

This interpretation is provisional and still requires confirmation.

## What is already known

The following is already known with sufficient confidence:

- the M33 area contains multiple structurally similar files
- at least some of these files are not identical
- therefore, basename duplication alone is not a sufficient cleanup criterion here
- this area must be documented before it is reduced

## Recommended next step

Before any structural reduction in the M33 subtree, a dedicated classification pass should be performed.

That pass should answer:

1. Which M33 branch is currently canonical?
2. Which files are active implementation files?
3. Which files are script mirrors, compatibility layers, or transitional variants?
4. Which branch is historical, experimental, or patch-specific?
5. Which parts may later be archived without harming reproducibility?

## Suggested future follow-up document

If the M33 area remains an active focus, a follow-up document would be useful:

- `docs/m33-canonical-structure.md`

That file could later define:

- canonical branch
- supporting branch
- historical branch
- cleanup-safe archive candidates

## What should not happen

The following actions should be avoided for now:

- deleting `src/` vs `scripts/` duplicates solely based on filename
- collapsing the patch-local-candidates branch without inspection
- assuming that repeated M33 basenames imply redundancy
- moving M33 files into quarantine unless they are clearly malformed or accidental

## Bottom line

The `m33_v0_scaffold` area is currently best understood as a **branched internal structure**, not as a simple duplication artifact.

At least part of the apparent duplication reflects real content divergence. Therefore this area should remain intact for now, while its internal roles are documented and later clarified in a dedicated canonical-structure pass.
