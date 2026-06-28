# QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT

Minimal upstream-export work package after
`QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT`.

This package creates a sandbox-only run under
`runs/QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT/`. It creates exporter registries,
feasibility records, manifest templates, validation rules, status tables, and
header-only export templates. It does not export real rows unless an explicit
local authorization artifact exists.

## Purpose

Prepare the upstream export layer that would later allow contract-compliant
C-layer files to be produced.

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

The export-contract gate must authorize
`QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT`.

## How To Run

```bash
python scripts/qsb_relalg_real01_min_upstream_export/real01_min_upstream_export.py
```

## Replay Protection

The default command refuses to overwrite an existing
`runs/QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT/` directory.

```bash
python scripts/qsb_relalg_real01_min_upstream_export/real01_min_upstream_export.py --force
```

## Input Export Contracts

The run reads contract specs, required fields, statuses, authorization
templates, manifest requirements, validation rules, and the export-contract
gate from `runs/QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT/`.

## Authorization Artifact Behavior

The builder looks for:

`runs/QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT/input/upstream_export_authorization.json`

If it is absent, authorization status is `not_authorized`, real-row export is
not allowed, and only header templates/stubs are created.

## Header-Only Export Templates

One CSV template is created per export contract under `export_templates/`. The
templates contain only the schema header. They contain no `Phi_ABC`, loop, or
triple fields.

## Allowed Outputs

Allowed outputs include registries, feasibility tables, exporter stubs,
header-only templates, manifest templates, validation rules, blocked-reason
reports, hygiene reports, and human review packets.

## Forbidden Outputs

Without explicit local authorization, no real C-layer rows are exported. The run
does not compute loop products, does not compute `Phi_ABC`, does not stage
REAL01, and does not interpret data.

## Public/GitHub Hygiene

The script and README use source IDs, paths, field names, hashes, and summaries.
They do not embed credentials, tokens, raw payload rows, large samples, or
environment dumps. They do not recommend `git add .`.

## Blocked

REAL01 staging, execution, interpretation, and physics-claim steps remain
blocked unless a later gate explicitly authorizes them.

## Outputs

The run writes the required upstream-export config, prerequisite report,
contract input registry, authorization report, feasibility table, exporter
registry, schema templates table, manifest templates, validation rules, status
table, blocked reasons, hygiene report, human packet, claim boundary, gate,
manifest, validation report, run summary, and one header-only CSV template per
contract.

## Validation

Validation checks prerequisites, contract coverage, one status per contract,
template presence, absence of prohibited fields, zero real rows without
authorization, safe authorization constraints, hygiene, blocked gate status,
manifest hashes, replay protection, and summary presence.

## Next-Step Gate

The default gate authorizes `QSB-RELALG-REAL01-MIN-AUTHORIZATION` while keeping
staging, execution, interpretation, and claim steps blocked.

## Claim Boundaries

This is an upstream export work package only. No C-layer row export, REAL01
staging, loop diagnostic, interpretation, plotting, or production mutation is
performed by default.
