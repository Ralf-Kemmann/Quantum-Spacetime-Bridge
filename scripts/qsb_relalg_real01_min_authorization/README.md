# QSB-RELALG-REAL01-MIN-AUTHORIZATION

Human authorization-gate run after
`QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT`.

This package creates a sandbox-only run under
`runs/QSB-RELALG-REAL01-MIN-AUTHORIZATION/`. It checks whether a local human
authorization artifact exists and whether its scope is restrictive and valid.
It does not auto-authorize anything.

## Purpose

Determine whether contract-compliant upstream C-layer export creation is
authorized, pending, or invalid.

## Prerequisites

The builder requires pass states through:

- `QSB-RELALG-PREAX01-SYNTH`
- `QSB-RELALG-AX01-TERM`
- `QSB-RELALG-AX01`
- `QSB-RELALG-GAUGE01`
- `QSB-RELALG-LOOP01-MIN`
- `QSB-RELALG-NULL01-MIN`
- `QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY`
- `QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION`
- `QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT`
- `QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT`

The upstream-export gate must authorize
`QSB-RELALG-REAL01-MIN-AUTHORIZATION`.

## How To Run

```bash
python scripts/qsb_relalg_real01_min_authorization/real01_min_authorization.py
```

## Replay Protection

The default command refuses to overwrite an existing
`runs/QSB-RELALG-REAL01-MIN-AUTHORIZATION/` directory.

```bash
python scripts/qsb_relalg_real01_min_authorization/real01_min_authorization.py --force
```

## Input Upstream-Export Package

The run reads upstream-export contract registry, authorization report,
feasibility, exporter registry, schema templates, status, and next-step gate.

## Authorization Artifact Behavior

The run creates:

`runs/QSB-RELALG-REAL01-MIN-AUTHORIZATION/input/human_authorization_TEMPLATE.json`

It does not create:

`runs/QSB-RELALG-REAL01-MIN-AUTHORIZATION/input/human_authorization.json`

The active authorization file must be supplied by a human before rerun.

## Allowed Scope

A valid authorization may permit contract-compliant upstream C-layer export
creation for listed export contract IDs only.

## Forbidden Scope

The authorization must not permit `Phi_ABC` computation, loop/triple products,
REAL01 staging, REAL01 execution, REAL01 interpretation, or physics claims.

## Safety Flags

The active artifact must require contract compliance, no `Phi_ABC`, no loop or
triple products, and no physics claim.

## Public/GitHub Hygiene

The script and README use contract IDs, paths, field names, and summaries. They
do not embed credentials, tokens, raw payload rows, large samples, or
environment dumps. They do not recommend `git add .`.

## Blocked

Until a valid restrictive authorization exists, authorized upstream export,
staging, execution, interpretation, and physics-claim steps remain blocked.

## Outputs

The run writes config, prerequisite report, input status, authorization
template, contract registry, decisions, scope checks, safety flags, blocked
downstream steps, hygiene report, human packet, claim boundary, next-step gate,
manifest, validation report, and run summary.

## Validation

Validation checks prerequisites, template creation, no active authorization
auto-creation, contract coverage, one decision per contract, restrictive safety
flags, hygiene, blocked gate status, manifest hashes, replay protection, and
summary presence.

## Next-Step Gate

Without an active authorization file, the next step is
`QSB-RELALG-REAL01-MIN-HUMAN-AUTHORIZATION-INPUT`.

## Claim Boundaries

This is an authorization gate only. It performs no C-layer row export, no
`Phi_ABC` computation, no REAL01 staging, no loop diagnostic, no interpretation,
no plotting, and no production mutation.
