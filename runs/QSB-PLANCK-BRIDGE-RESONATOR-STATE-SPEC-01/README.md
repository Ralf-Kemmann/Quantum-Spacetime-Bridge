# QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01

**Status:** formal state specification candidate  
**Physical claim release:** `blocked_no_physics_claim`  
**Review status:** `requires_human_formal_review`  
**Purpose:** Define a minimal, testable Planck-Bridge-Resonator (PBR) candidate without asserting physical existence.

This package turns the PBR vocabulary (`phase-bearing`, `moded`, `coupling-capable`) into a minimal formal object and an admissibility gate.

## Core definition

A local PBR candidate is defined as:

```text
B_i = (H_i, Phi_i, M_i, gamma_i, sigma_i)
```

where:

- `H_i` is a complex internal state space.
- `Phi_i in H_i` is a candidate state.
- `M_i` is a registered mode / structure operator.
- `gamma_i` is a geometric or field-like boundary condition.
- `sigma_i` is the scale-gate status.

Relational coupling is not part of the local object. It is defined between candidates:

```text
K_ij(gamma) = <Phi_i, C_ij(gamma) Phi_j>
```

Minimal Gram interpretation:

```text
K_ij = <Phi_i, Phi_j>
```

This implies:

```text
K is Hermitian and positive semidefinite (PSD).
```

## Important claim boundary

PSD-pass does **not** validate QSB as physics. It only means the minimal Hilbert/Gram reading is not formally excluded.

PSD-fail does **not** refute QSB. It rejects or forces modification of this specific minimal interpretation.

## Folder contents

```text
data/       CSV and JSON registry data
sql/        PostgreSQL schema, import and validation queries
scripts/    local validation and PSD gate template
validation/ local package validation results
docs/       human-readable notes
```

## Suggested repository location

```text
runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01/
```

## Recommended next step

After importing this state spec, run an actual PSD test against the candidate matrix, likely from:

```text
runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv
```

if that matrix is confirmed as the intended PBR/Gram candidate input.
