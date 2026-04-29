# Archive Policy

## Purpose of this document

This document defines the current archive and quarantine policy for the **Quantum–Spacetime Bridge** repository.

Its purpose is to ensure that cleanup, reduction, and structural maintenance follow explicit rules rather than ad hoc decisions. In a research repository that combines active numerics, historical notes, structured runs, and outward-facing scientific documentation, archive policy is part of scientific hygiene.

This policy is therefore not only about tidiness. It is about preserving transparency, reproducibility, and interpretive clarity.

## Scope

This policy applies to the repository as a whole, with particular relevance to the consolidated numerics subtree:

```text
numerics/debroglie-phase-bridge/
```

It also applies to documentation-side archival decisions under `docs/` where non-canonical drafts, obsolete companion texts, or historically useful but non-active files need to be retained without confusing the active structure.

## Governing principle

The repository follows a strict transparency rule:

> no hidden calculations, no hidden files, no hidden code, and no opaque result handling

The archive policy must therefore support two goals at the same time:

1. keep the active repository structure readable  
2. preserve historical and technical traceability

This means that the preferred cleanup action is usually:

> classify first, relocate second, delete only when clearly justified

## Archive location classes

The current repository uses several clearly named non-active location classes.

### 1. `_quarantine/`

**Purpose:**  
For malformed, misnamed, accidental, structurally unsafe, or non-canonical active-tree artifacts.

**Typical use cases:**
- malformed filenames
- accidental source files with wrong names
- backup files inside active source directories
- files that should not remain in active paths but may still have diagnostic value

**Interpretation:**  
A file in `_quarantine/` is not active. It is also not assumed to be authoritative. It is being preserved because deletion without review would be too aggressive.

### 2. `_archive_heavy/`

**Purpose:**  
For legitimate but very large or detail-heavy artifacts that reduce readability when kept in the most visible active layer of a run or work directory.

**Typical use cases:**
- large CSV grids
- detailed intermediate matrices
- heavy parameter sweeps
- bulky run artifacts that are supported by smaller summaries nearby

**Interpretation:**  
A file in `_archive_heavy/` is valid project material, but no longer part of the most visible active run surface.

### 3. `_archive_masterchat_noncanonical/`

**Purpose:**  
For non-canonical masterchat and masterchat-like files once a single canonical masterchat has been identified.

**Typical use cases:**
- backup masterchat files
- outdated current-status snapshots
- relocation notes
- bridge insert pieces
- parallel masterchat copies outside the canonical location

**Interpretation:**  
These files are preserved for provenance and project history, but they must not compete with the single active canonical masterchat.

### 4. `docs/_archive/`

**Purpose:**  
For non-canonical or superseded documentation drafts on the outward-facing documentation side.

**Typical use cases:**
- draft core texts
- superseded overview variants
- working text bundles no longer treated as active public-facing documents

**Interpretation:**  
Files in `docs/_archive/` remain available for reference, but they are not part of the active curated documentation set.

## Canonical vs. non-canonical rule

Before a file is moved into any archive class, its status should be assessed in terms of repository role.

### Canonical file
A canonical file is:
- the active reference version
- the file that should be cited, used, or followed
- the file that defines the current project state in its category

### Non-canonical file
A non-canonical file is:
- a backup
- a snapshot
- a previous stage
- a draft
- a parallel version
- or a working artifact that should not remain part of the active reference layer

The archive policy exists to keep these two categories visibly distinct.

## Deletion policy

Deletion is allowed only under stricter conditions than relocation.

A file may be deleted only when at least one of the following is clearly true:

1. it is a pure technical accident with no diagnostic value  
2. it is a malformed duplicate whose content is safely preserved elsewhere  
3. it is reproducible and documented, and its removal does not reduce transparency  
4. it has already been reviewed and explicitly judged irrelevant for provenance

When there is doubt, the preferred action is:

- move to archive
or
- move to quarantine

not:
- immediate deletion

## Special rule for numerics and result files

For numerics-heavy project material, deletion thresholds must be stricter.

This is because numerical traces, run outputs, and structured intermediate artifacts may later matter for:

- provenance
- reviewer questions
- reproducibility checks
- interpretation of earlier decisions

Therefore:
- summaries may be favored for visibility
- heavy detail artifacts may be archived
- but calculation-relevant material should not be silently removed

## Special rule for masterchat material

There must be exactly one active canonical masterchat for any given working line.

Once that canonical file has been identified:
- all other masterchat-like variants should be treated as non-canonical
- these may be archived if historically useful
- they must not remain scattered across the active tree in ways that create ambiguity

This rule is organizationally important, not only cosmetically important.

## Documentation requirement

Whenever a meaningful cleanup or archive action changes the visibility of project material, it should be documented in at least one of the following ways:

- short cleanup summary note
- archive summary note
- quarantine summary note
- commit message with clear archival rationale

The goal is that later readers can reconstruct not only what changed, but why it changed.

## What this policy forbids

The following behaviors are explicitly discouraged or forbidden:

- silent hiding of computationally relevant files
- deleting historical artifacts only because they are visually inconvenient
- leaving multiple canonical-looking files active without clarification
- moving files into obscure side locations without documentation
- using archive areas as a substitute for actual classification

## Practical working rule

The practical archive workflow is:

1. identify candidate  
2. classify role  
3. decide whether active / archive / quarantine / delete  
4. move or retain  
5. document the decision

This sequence should be preferred over improvised cleanup.

## Relation to repository cleanliness

A clean repository is **not** defined here as the smallest possible repository.

Instead, a clean repository is one that is:

- readable
- structurally honest
- non-ambiguous
- documented
- recoverable where needed

This policy therefore favors **transparent order** over aggressive shrinking.

## Field list

1. `scope` — String — area of the repository to which the policy applies  
2. `governing_principle` — String — core transparency rule that constrains cleanup and archiving  
3. `archive_location_class` — String — named non-active storage class such as `_quarantine` or `_archive_heavy`  
4. `archive_location_purpose` — String — reason why a given archive class exists  
5. `typical_use_case` — String — example type of file appropriate for a given archive class  
6. `canonical_file` — String — file currently treated as the active reference version in its class  
7. `noncanonical_file` — String — file preserved but not treated as active reference  
8. `deletion_condition` — String — condition under which deletion may be justified  
9. `numerics_special_rule` — String — stricter handling rule for numerics and result artifacts  
10. `masterchat_special_rule` — String — rule for maintaining exactly one active masterchat  
11. `documentation_requirement` — String — requirement that archive-relevant cleanup actions remain documented  
12. `forbidden_behavior` — String — cleanup behavior explicitly rejected by project policy  
13. `practical_workflow_step` — String — one step in the preferred classify-before-delete workflow  
14. `repository_cleanliness_definition` — String — project-specific interpretation of what a “clean” repository means

## Bottom line

The archive policy of **Quantum–Spacetime Bridge** is based on one simple idea:

> preserve traceability while reducing ambiguity

Files should not disappear just to make the repository look neat. Instead, they should be classified, relocated, and documented in ways that keep the active project structure readable without damaging scientific transparency.
