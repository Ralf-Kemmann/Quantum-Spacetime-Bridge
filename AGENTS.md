# AGENTS.md — QSB / Quantum–Spacetime Bridge Working Rules

## Role

You are working in the Quantum–Spacetime Bridge / Gravitation und RaumZeit research repository.

Treat this repository as a scientific audit trail, not as a generic coding sandbox.

## Core principles

- No hidden code.
- No hidden calculations.
- No hidden generated files.
- No hidden assumptions.
- No overclaiming.
- Preserve the distinction between:
  - Befund
  - Interpretation
  - Hypothese
  - Offene Lücke
  - Claim Boundary

## Repository structure

Use only the established project folders:

- `docs/` for specifications, result notes, context notes, field lists.
- `data/` for configs, manifests, input tables, YAML/CSV/JSON inputs.
- `scripts/` for executable scripts.
- `runs/` for generated run outputs.
- Do not create new top-level folders unless explicitly instructed.

## Editing rules

- Do not edit existing files unless explicitly instructed.
- If the user asks to create exactly N files, create exactly those files.
- Do not modify closed anchor files from earlier blocks unless explicitly instructed.
- Do not modify FU02g4c/FU02g5/FU02g5b/FU02g5c/FU02g5d files unless the task explicitly names them.
- Never run `git add`, `git commit`, `git push`, `git reset`, or destructive git commands.
- Always report `git status --short` after file creation or edits.
- Do not delete files unless explicitly instructed.

## Scientific writing rules

For result notes, use this structure:

- Befund
- Interpretation
- Hypothese
- Offene Lücke
- Claim Boundary

Use defensive scientific language.

Never claim:
- physical emergence
- spacetime emergence
- Lorentz compatibility
- global uniqueness
- global rarity proof
- proof of dynamics
unless the task explicitly provides validated evidence for that claim.

## QSB current FU02 boundaries

Current safe statements:

- The localized FU02g4c exact candidate is automorphic to the FU02f1 reference carrier.
- Under automorphy-only role transport, that candidate admits exactly one face-type-preserving mapping and receives unique transported roles.
- FU02g5e1 provides a scaffold-localization inventory of 11 near-match candidates, including the known exact candidate.
- FU02g5e1 does not certify exact FU02g4c raw-order replay.

Current unsafe statements:

- QSB proves spacetime emergence.
- QSB proves global uniqueness.
- QSB proves global rarity.
- QSB is a spacetime-quasicrystal model.
- Non-isomorphic patches may receive reference roles by analogy.

## Coding rules

- Prefer deterministic outputs.
- Include explicit config paths in result notes.
- Include stop reasons for long-running scripts.
- Include warnings in JSON/CSV outputs.
- If enumeration order cannot be guaranteed to match an earlier runner, label the run as scaffold/localization and say the replay order is not certified.
- Do not silently change algorithms.
- Do not silently change field names.
- If adding CSV/JSON outputs, also create or update a field list when requested.

## Reporting after task completion

Always report:

1. Files created
2. Files modified
3. Commands run
4. Output directory
5. Tests/checks
6. Git status
7. Any uncertainty or limitation

## Internal shorthand

Codex may act as the local implementation assistant, but the scientific claim boundary is strict.

No labels on foreign Klunker.
Only mirror Klunker may carry reference labels.
