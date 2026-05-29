# QSB-ST-SHAPIROINFO11 -- Correction-State Sidecar Template

## Current anchor

`81f6949 Add QSB-ST ShapiroInfo interface lab handoff`

## Purpose

SHAPIROINFO11 erzeugt ein konkretes, leeres YAML-Template fuer den
verpflichtenden Correction-State-Sidecar.

Das Template darf noch keinen echten Datensatz behaupten. Alle unbekannten
Werte sollen explizit als `unknown`, `not_applicable` oder
`manual_review_required` markiert werden.

Correction-State is not metadata decoration. Correction-State is a blocking
interpretability layer.

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO10_CORRECTION_STATE_FIELD_SCHEMA.md`
- `docs/QSB_ST_SHAPIROINFO09_TARGETED_BINARY_PULSAR_PILOT_PLAN.md`
- `docs/QSB_ST_SHAPIROINFO08_TOY_TO_SEMI_REAL_ADAPTER_PLAN.md`
- `docs/QSB_ST_SHAPIROINFO02_MINIMAL_SIGNAL_RECORD_SCHEMA_SPEC.md`

## Scope

- template/specification only
- no data download
- no real dataset selection
- no `.par` / `.tim` ingestion
- no parsing
- no PINT / tempo2 execution
- no residual calculation
- no empirical result
- no Bridge claim
- no Shapiro modification claim

## Files Created By This Block

| path | role | status |
|---|---|---|
| `data/QSB-ST-SHAPIROINFO/correction_state_sidecar_template.yaml` | Empty Correction-State sidecar template. | created as template only |
| `docs/QSB_ST_SHAPIROINFO11_CORRECTION_STATE_SIDECAR_TEMPLATE_SPEC.md` | Human-readable template specification. | created as spec only |

No run output, script, downloaded data, parsed timing file, or empirical result
is created by SHAPIROINFO11.

## Template Rule

The YAML file is a scaffold for later review. It is not a populated sidecar.
Unknown or not-yet-reviewed values remain explicit blockers.

Allowed placeholder markers in the empty template:

- `unknown`
- `not_applicable`
- `manual_review_required`

The template may later be copied into a dataset-specific sidecar only after a
future block explicitly authorizes that step.

## Initial Gate State

The empty template starts blocked:

- `adapter_readiness_label: blocked_missing_correction_state`
- `go_no_go_status: NO_GO`
- `go_no_go_reason: empty template; central correction-state fields are unknown`

This is intentional. A blank sidecar must not unlock a semi-real adapter run.

## Field Coverage

The template contains the SHAPIROINFO10 field groups:

- core identity/provenance fields
- timing-model fields
- binary-model fields
- clock correction fields
- ephemeris fields
- DM / ISM / plasma fields
- solar-wind fields
- backend / instrument fields
- noise-model fields
- QC / outlier fields
- window/control fields
- mapping/readiness fields
- claim-boundary fields

The field names are kept as direct YAML keys so later checks can grep, parse,
or map them without hidden translation.

## Claim Flags

All claim flags in the template must be `false`:

- `bridge_confirmation_flag: false`
- `physical_validation_flag: false`
- `new_shapiro_effect_claim_flag: false`
- `gr_incomplete_claim_flag: false`
- `residual_implies_qsb_flag: false`
- `dataset_specific_evidence_claim_flag: false`
- `real_data_result_claim_flag: false`
- `candidate_residual_claim_flag: false`
- `derivation_of_c_claim_flag: false`
- `numerical_c_explanation_claim_flag: false`

Any future sidecar with one of these flags set to `true` is outside this
workflow and must be treated as `NO_GO`.

## Relation To SHAPIROINFO10

SHAPIROINFO10 defined the Correction-State field schema. SHAPIROINFO11 turns
that schema into an empty YAML template with explicit blocker defaults.

SHAPIROINFO11 does not change field names, allowed status vocabulary, or
Go/No-Go logic from SHAPIROINFO10.

## Relation To SHAPIROINFO09

SHAPIROINFO09 planned a targeted binary pulsar pilot, for example a public
package such as NANOGrav J0740+6620. SHAPIROINFO11 does not select, inspect,
download, or parse that candidate. It only prepares the sidecar shape required
before a later dry-run adapter can be considered.

## Relation To SHAPIROINFO02

SHAPIROINFO02 defines the signal-record layer. SHAPIROINFO11 supplies the
companion Correction-State layer that must be present before semi-real records
can be mapped or blocked.

## Befund

The repository now has a concrete empty Correction-State sidecar template.
It is intentionally blocked until provenance, timing model, clock, ephemeris,
DM/ISM, backend, noise, QC, controls, and mapping state are reviewed.

## Interpretation

The template makes missing correction-state information visible at the first
file boundary. Unknown state is not hidden in prose, code, defaults, or later
adapter behavior.

## Hypothese

A strict empty-template starting point may reduce false-positive risk by making
central unknowns block semi-real use before any data ingestion or residual
calculation exists.

## Offene Luecke

- no real sidecar populated
- no dataset selected
- no source URL reviewed
- no citation reviewed
- no `.par` / `.tim` files inspected
- no PINT / tempo2 run
- no adapter implemented
- no dry-run preview executed
- no empirical result

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no candidate residual claim from template creation
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO12 Public Source and Citation Checklist
- SHAPIROINFO13 Targeted Binary Pulsar Dry-Run Adapter Spec
- SHAPIROINFO14 Cassini Feasibility Study Plan
- SHAPIROINFO15 VLBI Feasibility Study Plan

## Acceptance Checks

- Datei `data/QSB-ST-SHAPIROINFO/correction_state_sidecar_template.yaml`
  existiert
- Datei `docs/QSB_ST_SHAPIROINFO11_CORRECTION_STATE_SIDECAR_TEMPLATE_SPEC.md`
  existiert
- Template enthaelt `correction_state_schema_version`
- Template enthaelt `clock_correction_state`
- Template enthaelt `ephemeris_state`
- Template enthaelt `dm_ism_state`
- Template enthaelt `backend_instrument_state`
- Template enthaelt `noise_model_state`
- Template enthaelt `qc_state`
- Template enthaelt `adapter_readiness_label: blocked_missing_correction_state`
- Template enthaelt `go_no_go_status: NO_GO`
- Template enthaelt `bridge_confirmation_flag: false`
- Template enthaelt `numerical_c_explanation_claim_flag: false`
- Spec enthaelt Correction-State is not metadata decoration
- risk grep clean
- git diff --check clean
- git status --short reported
