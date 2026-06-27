# QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY

Minimal real-source eligibility check after `QSB-RELALG-NULL01-MIN`.

This package creates a sandbox-only run under
`runs/QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY/`. It inspects candidate
repository sources using file names, headers, small samples, manifests, and
metadata. It does not modify prerequisite runs or production project files.

## Purpose

The run answers one narrow question: which existing project sources, if any,
are eligible for a later minimal REAL01 C-layer staging step.

## Prerequisites

Required prerequisite files:

- `runs/QSB-RELALG-PREAX01-SYNTH/qsb_relalg_preax01_synth_validation_report.json`
- `runs/QSB-RELALG-AX01-TERM/qsb_relalg_ax01_term_validation_report.json`
- `runs/QSB-RELALG-AX01/qsb_relalg_ax01_validation_report.json`
- `runs/QSB-RELALG-GAUGE01/qsb_relalg_gauge01_validation_report.json`
- `runs/QSB-RELALG-LOOP01-MIN/qsb_relalg_loop01_min_validation_report.json`
- `runs/QSB-RELALG-NULL01-MIN/qsb_relalg_null01_min_validation_report.json`
- `runs/QSB-RELALG-NULL01-MIN/qsb_relalg_null01_min_next_step_gate.json`

The NULL01-MIN gate must authorize
`QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY`.

## How To Run

```bash
python scripts/qsb_relalg_real01_min_source_eligibility/real01_min_source_eligibility.py
```

## Replay Protection

The default command refuses to overwrite an existing
`runs/QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY/` directory. To regenerate only
this run directory:

```bash
python scripts/qsb_relalg_real01_min_source_eligibility/real01_min_source_eligibility.py --force
```

## Candidate Discovery

The builder inspects likely files under `runs/`, `data/`, `docs/`, and
`scripts/`. It prioritizes RELALG/QSB-related source names and C/K/phase/pair
relation keywords. Inspection is limited to file metadata, hashes, headers, and
small text samples.

## Eligibility Classes

- `eligible_c_layer`
- `conditional_authorized_c_from_phase`
- `k_layer_only_not_eligible`
- `visual_only_not_eligible`
- `metadata_only_not_eligible`
- `mixed_source_not_eligible`
- `missing_provenance_not_eligible`
- `ambiguous_requires_human_review`
- `not_relevant`

## C-Layer Evidence

C-layer evidence requires ordered pair identifiers plus complex relation data
or an explicitly authorized phase-difference source with provenance,
source-space, and convention evidence.

## Excluded Evidence

K-layer magnitudes, scores, graph distances, heatmaps, visual artifacts,
metadata-only reports, and mixed-source tables do not qualify as C-layer
eligibility evidence.

## Outputs

- `qsb_relalg_real01_min_source_eligibility_config.json`
- `qsb_relalg_real01_min_source_eligibility_prerequisite_report.json`
- `qsb_relalg_real01_min_source_inventory.csv`
- `qsb_relalg_real01_min_candidate_evidence.csv`
- `qsb_relalg_real01_min_candidate_classification.csv`
- `qsb_relalg_real01_min_c_layer_eligibility_report.csv`
- `qsb_relalg_real01_min_k_layer_exclusion_report.csv`
- `qsb_relalg_real01_min_ambiguous_sources_report.csv`
- `qsb_relalg_real01_min_recommended_next_action.csv`
- `qsb_relalg_real01_min_claim_boundary_report.md`
- `qsb_relalg_real01_min_next_step_gate.json`
- `qsb_relalg_real01_min_manifest.json`
- `qsb_relalg_real01_min_validation_report.json`
- `QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY_RUN_SUMMARY.md`

## Validation

Validation checks prerequisite pass states, required outputs, candidate
classification completeness, K-layer exclusion, ambiguous-source reporting,
gate blocking, manifest hashes, replay protection, and run summary presence.

## Next-Step Gate

The gate is conditional:

- eligible C-layer source found: authorize `QSB-RELALG-REAL01-MIN-STAGING`
- only conditional phase source found: authorize `QSB-RELALG-REAL01-MIN-AUTHORIZATION`
- no eligible source found: authorize `QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION`

REAL01 execution, interpretation, and physics-claim steps remain blocked.

## Claim Boundaries

This run is source eligibility only. It performs no C-layer loop diagnostic,
no real-data interpretation, no plotting, and no production mutation.
