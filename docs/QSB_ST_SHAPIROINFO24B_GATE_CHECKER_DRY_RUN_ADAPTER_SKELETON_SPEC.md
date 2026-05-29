# QSB-ST-SHAPIROINFO24B -- Gate-Checker / Dry-Run Adapter Skeleton Without Real Data

## Current Anchor

Local anchor:

`9dbbd51 Add QSB-ST ShapiroInfo local storage raw data policy`

Public anchor, falls der lokale Commit noch nicht gepusht ist:

`40e3808 Update QSB-ST ShapiroInfo J0740 manifest after README release inspection`

## Purpose

SHAPIROINFO24B erzeugt ein kleines technisches Gate-Checker-Script. Das Script
liest das J0740-Manifest und das Correction-State-Sidecar-Template, prueft
zentrale Gate-Felder und erzeugt einen maschinenlesbaren Dry-Run-Status.

Der erste erfolgreiche Lauf soll nicht `GO` sein. Der erste erfolgreiche Lauf
soll kontrolliert bestaetigen:

`BLOCKED_EXPECTED`

Das heisst: Der Gate-Checker funktioniert, weil er die geschlossenen Gates
erkennt.

## Scope

- gate-checker / dry-run adapter skeleton only
- no download
- no PINT / tempo2 installation
- no PINT / tempo2 execution
- no real pulsar evaluation
- no `.par` / `.tim` ingestion
- no linked timing-data file opened
- no linked parameter file opened
- no real data parsing
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Files Created

| path | role | status |
|---|---|---|
| `scripts/run_qsb_st_shapiroinfo24b_gate_checker.py` | dry-run gate-checker skeleton | created |
| `docs/QSB_ST_SHAPIROINFO24B_GATE_CHECKER_DRY_RUN_ADAPTER_SKELETON_SPEC.md` | specification note | created |

No existing file is modified by SHAPIROINFO24B.

## Inputs Read By The Script

| input | path | allowed_contact | note |
|---|---|---|---|
| J0740 manifest draft | `data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml` | yes, existing YAML only | Existing blocked manifest; no raw data. |
| Correction-State sidecar template | `data/QSB-ST-SHAPIROINFO/correction_state_sidecar_template.yaml` | yes, existing YAML only | Empty template; no dataset-specific sidecar. |

The script refuses `.par` and `.tim` inputs. It does not open linked timing-data
or parameter files.

## Script Behaviour

The script performs a conservative scalar-field scan of the existing YAML files.
It does not attempt a timing-model parse and does not interpret scientific
content.

Checks include:

- top-level manifest gate status
- `download_allowed`
- `sidecar_population_allowed`
- `dry_run_preview_allowed`
- `download_plan.download_gate_status`
- `download_plan.raw_data_tracking_status`
- `download_plan.downloaded_files`
- `downstream_gate.sidecar_gate_status`
- `downstream_gate.dry_run_gate_status`
- unresolved file-level documentation, data-use/license, and correction context
- manifest claim flags
- sidecar central blocking placeholders
- sidecar claim flags

Missing or unexpected fields are not treated as permissive. They produce
`UNEXPECTED_GATE_STATE`.

## Expected Dry-Run Output

Default output directory:

`runs/QSB-ST-SHAPIROINFO24B/gate_checker_dry_run_open/`

Default machine-readable output:

`runs/QSB-ST-SHAPIROINFO24B/gate_checker_dry_run_open/gate_checker_status.json`

Expected first successful decision:

`gate_decision = BLOCKED_EXPECTED`

Exit semantics:

| exit_code | meaning |
|---|---|
| `0` | Gates are closed in the expected way: `BLOCKED_EXPECTED`. |
| `2` | Gate fields are missing or unexpectedly open: `UNEXPECTED_GATE_STATE`. |
| other | Input/output or execution error. |

## Why BLOCKED_EXPECTED Is Success Here

SHAPIROINFO24B is not a data-analysis block. A successful run means the checker
can verify that download, raw-data tracking, sidecar population, and dry-run
preview remain closed.

The dry-run status is therefore a gate-health artifact, not a scientific result.

## Relation To SHAPIROINFO23

SHAPIROINFO23 defined the local storage and raw-data policy. SHAPIROINFO24B is
the bounded technical step after that policy note: it checks the current gates
without extending the policy chain indefinitely.

## Relation To SHAPIROINFO22

SHAPIROINFO22 updated the J0740 manifest after page-level README / Release-Note
inspection. SHAPIROINFO24B reads that manifest state and confirms the unresolved
fields still block operational access.

## Relation To SHAPIROINFO11

SHAPIROINFO11 created the empty Correction-State sidecar template. SHAPIROINFO24B
uses that template only as an input to confirm that central Correction-State
fields remain unresolved and blocking.

## Befund

A minimal gate-checker skeleton can verify the present blocked state without
touching real timing data.

## Interpretation

The project now has a small technical control point between documentation gates
and any later data-contact step. This control point should fail closed if a gate
is missing, ambiguous, or unexpectedly open.

## Hypothese

A machine-readable `BLOCKED_EXPECTED` dry-run can reduce ambiguity before any
future controlled source or file-contact operation.

## Offene Luecke

- no download
- no linked timing-data file opened
- no linked parameter file opened
- no `.par` parsed
- no `.tim` parsed
- no PINT / tempo2 execution
- no Correction-State sidecar population
- no adapter over real timing data
- no residual calculation
- no empirical result

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no candidate residual claim from gate checking
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO25 Gate-Checker Result Note
- SHAPIROINFO26 File-Link Metadata Review Plan
- SHAPIROINFO27 Controlled Download Gate Proposal
- SHAPIROINFO28 Targeted Binary Pulsar Dry-Run Adapter Spec

## Acceptance Checks

- Script exists
- Spec exists
- Script reads only existing manifest/template YAML by default
- Script refuses `.par` / `.tim` inputs
- Script output contains `BLOCKED_EXPECTED`
- Script output contains `download_performed: false`
- Script output contains `par_tim_ingestion_performed: false`
- Script output contains `pint_or_tempo2_execution_performed: false`
- Script output contains `residual_calculation_performed: false`
- Script output contains `no_bridge_confirmation`
- Run output may exist under `runs/QSB-ST-SHAPIROINFO24B/gate_checker_dry_run_open/`
- no download
- no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
