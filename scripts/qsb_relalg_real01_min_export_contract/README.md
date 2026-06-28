# QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT

Minimal export-contract specification run after
`QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION`.

This package creates a sandbox-only run under
`runs/QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT/`. It defines required export
fields, provenance, conventions, authorization text, validation rules, and
blocked downstream steps. It does not export, stage, or interpret data.

## Purpose

Define what an upstream source must provide before a later C-layer staging task
can be considered.

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

The remediation gate must authorize `QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT`.

## How To Run

```bash
python scripts/qsb_relalg_real01_min_export_contract/real01_min_export_contract.py
```

## Replay Protection

The default command refuses to overwrite an existing
`runs/QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT/` directory.

```bash
python scripts/qsb_relalg_real01_min_export_contract/real01_min_export_contract.py --force
```

## Input Candidates

The run reads the remediation decisions, export-contract candidates, remediation
summary, human packet, and remediation next-step gate.

## Export Contract Statuses

- `contract_ready_pending_human_authorization`
- `contract_ready_pending_upstream_export`
- `contract_blocked_missing_phase_or_complex_fields`
- `contract_blocked_missing_source_space`
- `contract_blocked_missing_unit_or_angle_convention`
- `contract_blocked_missing_lineage_or_hash`
- `contract_blocked_mixed_source_space`
- `contract_rejected_not_c_layer_exportable`

## Required C-Layer Export Fields

Required fields include source identifiers, ordered pair identifiers, endpoint
IDs, complex C fields or authorized phase-difference fields, magnitude reference
for thresholds, source-space ID, hashes, schema version, unit convention,
wrapping convention, orientation convention, and threshold policy.

## Authorization Templates

Each non-rejected candidate receives an authorization template. The template may
authorize a future C-layer export only. It does not authorize loop phase
computation or REAL01 execution.

## Manifest Requirements

Every contract requires source hash, config hash, source-space ID, angle and
wrapping conventions, threshold policy, schema version, claim boundary, and
authorization record.

## Validation Rules

Validation rules block missing ordered pair IDs, missing C-layer or phase-source
fields, missing provenance, missing source space, missing angle convention,
missing threshold policy, and magnitude-only exports.

## Public/GitHub Hygiene

The script and README use source IDs, paths, hashes, field names, and summaries.
They do not embed raw payloads, credentials, tokens, or large samples. Run
outputs stay under `runs/`.

## Blocked

REAL01 staging, execution, interpretation, and physics-claim steps remain
blocked by this run.

## Outputs

The run writes contract specs, required fields, statuses, authorization
templates, manifest requirements, validation rules, blocked downstream steps,
public-surface hygiene report, human review packet, claim boundary, gate,
manifest, validation report, and run summary.

## Claim Boundaries

This is an export-contract specification only. No C-layer staging, loop
diagnostic, interpretation, plotting, or production mutation is performed.
