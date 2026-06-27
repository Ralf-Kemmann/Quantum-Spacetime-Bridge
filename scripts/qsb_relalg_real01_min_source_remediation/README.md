# QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION

Bounded remediation pass for the 13 sources previously classified as
`ambiguous_requires_human_review` by
`QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY`.

This package creates a sandbox-only run under
`runs/QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION/`. It reads prior eligibility
outputs and small samples from the ambiguous files. It does not modify
prerequisite runs or source files.

## Purpose

The run decides whether each ambiguous source can be routed to C-layer staging,
phase-source authorization, export-contract preparation, repair actions, final
exclusion, or human decision.

## Prerequisites

Required prerequisite validations must pass through:

- `QSB-RELALG-PREAX01-SYNTH`
- `QSB-RELALG-AX01-TERM`
- `QSB-RELALG-AX01`
- `QSB-RELALG-GAUGE01`
- `QSB-RELALG-LOOP01-MIN`
- `QSB-RELALG-NULL01-MIN`
- `QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY`

The previous eligibility gate must authorize
`QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION`.

## How To Run

```bash
python scripts/qsb_relalg_real01_min_source_remediation/real01_min_source_remediation.py
```

## Replay Protection

The default command refuses to overwrite an existing
`runs/QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION/` directory.

```bash
python scripts/qsb_relalg_real01_min_source_remediation/real01_min_source_remediation.py --force
```

The `--force` option replaces only the remediation output directory.

## Input Ambiguous Candidates

The builder reads the previous ambiguous report, candidate classification,
candidate evidence, source inventory, and next-step gate from
`runs/QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY/`.

## Remediation Classes

- `remediated_eligible_c_layer`
- `conditional_phase_source_requires_authorization`
- `requires_export_contract`
- `requires_provenance_repair`
- `requires_unit_or_angle_convention`
- `requires_source_coherence_mapping`
- `reclassified_k_layer_only_not_eligible`
- `reclassified_metadata_only_not_eligible`
- `reclassified_visual_only_not_eligible`
- `reclassified_not_relevant`
- `unresolved_requires_human_decision`

## C-Layer Evidence

C-layer evidence requires ordered pair identifiers, complex relation fields or
an equivalent representation, source/provenance evidence, source-space
coherence, threshold/magnitude information, and any required unit or angle
convention.

## Authorization

Phase-derived construction requires explicit human authorization before any
later construction of `C_AB = exp(i * delta_phi_AB)`.

## Export Contract

An export contract is required when plans, configs, or upstream artifacts point
to phase/delta-phi logic but no eligible ordered C-layer export file exists.

## Blocked

REAL01 staging, execution, interpretation, and physics-claim steps remain
blocked unless a later gate explicitly authorizes staging.

## Outputs

The run writes remediation review tables, file inspection records, decision
tables, authorization/export/repair action lists, reclassified exclusions,
summary metrics, a human review packet, claim boundary, gate, manifest,
validation report, and run summary.

## Validation

Validation checks prerequisite pass states, candidate coverage, one final class
per candidate, no immediate phase computation, safe upgrade rules, human packet
coverage, blocked gate status, manifest hashes, replay protection, and summary
presence.

## Next-Step Gate

The gate is conditional. In the expected remediation-only case, export-contract
targets authorize `QSB-RELALG-REAL01-MIN-EXPORT-CONTRACT` while staging,
execution, interpretation, and claim steps remain blocked.

## Claim Boundaries

This run is source remediation only. It performs no C-layer loop diagnostic,
no real-data staging, no real-data interpretation, no plotting, and no
production mutation.
