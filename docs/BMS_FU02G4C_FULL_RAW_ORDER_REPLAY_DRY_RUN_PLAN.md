# BMS-FU02g4c Full Raw-Order Replay Certification Dry-Run Plan

**Date:** 2026-05-09
**Project:** Quantum-Spacetime Bridge / Gravitation und RaumZeit
**Block:** FU02g4c Full Raw-Order Replay Certification
**Plan status:** dry-run / execution plan only
**Starting config:** `data/bms_fu02g4c_full_raw_order_replay_certification_preflight_config.yaml`

## 1. Purpose

This document is a dry-run and execution plan for a later FU02g4c full raw-order
replay certification pass.

It is not a replay run.

It is not certification output.

It only documents the conditions, inputs, staged execution path, audit outputs,
risks, and claim boundary required before a later full raw-order replay can be
started and interpreted.

No long enumeration or replay run is authorized by this plan.

## 2. Relevant Existing Files

Read-only inspection found the expected preflight config, prior configs, and
runner scripts present.

### Configs

- `data/bms_fu02g4c_full_raw_order_replay_certification_preflight_config.yaml`
  - New preflight-only config.
  - Sets `allow_long_replay_run: false`.
  - Sets `allow_existing_fu02g4c_anchor_mutation: false`.
  - Sets `claim_full_certification_after_preflight: false`.

- `data/bms_fu02g4c_orbit_reduced_resumable_config.yaml`
  - FU02g4c orbit-reduced/resumable connected-patch enumeration config.
  - Declares FU02g4c input bundle paths and enumeration controls.

- `data/bms_fu02g5f_raw_order_replay_certification_config.yaml`
  - FU02g5f revalidation / candidate_005 inspection config.
  - Notes that this block does not reuse the original FU02g4c enumerator/input
    bundle and therefore does not certify full raw order.

- `data/bms_fu02g5g_fu02g4c_raw_order_replay_certification_config.yaml`
  - FU02g5g recovery/crosscheck config.
  - Inventories existing FU02g4c artifacts and keeps `allow_replay_rerun: false`.

- `data/bms_fu02g5g2_narrow_per_index_replay_photo_certification_config.yaml`
  - FU02g5g2 narrow per-index photo certification config.
  - Sets `full_fu02g4c_replay_certification: false`.

### Scripts

- `scripts/run_bms_fu02g4c_orbit_reduced_resumable_connected_patch_enumeration.py`
  - FU02g4c connected-patch enumerator.
  - This is the script whose exact replay semantics must be verified before
    claiming full raw-order certification.

- `scripts/run_bms_fu02g5g_fu02g4c_raw_order_replay_certification.py`
  - FU02g5g artifact inventory / recovery runner.
  - Useful for crosschecking existing FU02g4c windows, but not sufficient by
    itself as a full replay.

- `scripts/run_bms_fu02g5g2_narrow_per_index_replay_photo_certification.py`
  - Narrow per-index scaffold/FU02g4c-style photo runner.
  - Useful as prior evidence, but explicitly not full FU02g4c replay
    certification unless exact original reuse is certified.

- `scripts/inspect_bms_fu02g4c_single_exact_patch.py`
  - Single exact-patch inspection script.
  - Useful for bounded inspection and positive-control support.

## 3. Candidate and Mapping State

A later full replay must check all 11 candidates per-index:

- `candidate_000`, raw index `2338804`
- `candidate_001`, raw index `2338805`
- `candidate_002`, raw index `2839553`
- `candidate_003`, raw index `18575893`
- `candidate_004`, raw index `26157529`
- `candidate_005`, raw index `26157530`
- `candidate_006`, raw index `26161006`
- `candidate_007`, raw index `26167866`
- `candidate_008`, raw index `26187175`
- `candidate_009`, raw index `26187327`
- `candidate_010`, raw index `26328307`

The later run must not silently collapse scaffold-style per-index reproduction
into full FU02g4c raw-order certification. The mapping from candidate id to raw
index must be carried explicitly into the full replay output.

### candidate_005

- `candidate_id`: `candidate_005`
- `raw_index`: `26157530`
- role: coarse-signature degeneracy stress case
- `expected_exact_match`: `false`
- `near_distance`: `0`
- Required interpretation: `near_distance=0` must not be read as identity,
  exactness, role-transport eligibility, or isomorphism.

This candidate is a diagnostic stress case for coarse-signature degeneracy. It
must have a separate row and separate readout paragraph in the final audit.

### candidate_008

- `candidate_id`: `candidate_008`
- `raw_index`: `26187175`
- role: positive-control known-exact / Spiegelklunker
- `expected_exact_match`: `true`
- Required interpretation: positive-control support does not replace full
  raw-order coverage.

This candidate must have a separate row and separate readout paragraph in the
final audit.

## 4. Proposed Later Run Mode

### Stage 0 - Read-Only Validation

Purpose: validate config and input paths without running replay.

Allowed actions:

- parse the preflight config
- check that configured input files exist
- check that relevant scripts exist
- check that the intended output directory is isolated
- check that existing FU02g4c anchor paths are not selected as write targets
- read candidate tables and confirm that all 11 candidates are present
- confirm that candidate_005 and candidate_008 are separately targetable

Not allowed in Stage 0:

- no enumeration
- no replay
- no writing into FU02g4c anchor directories
- no modification of existing configs or scripts

### Stage 1 - Dry-Run Command Construction Only

Purpose: construct the exact future command(s) and output paths without
executing them.

Allowed actions:

- derive candidate target list from existing tables
- derive command strings for later replay
- derive expected output filenames
- verify that command construction does not target existing FU02g4c outputs

Not allowed in Stage 1:

- no replay command execution
- no smoke run
- no long enumeration
- no config mutation

### Stage 2 - Small Bounded Smoke Check

Purpose: test mechanics on a bounded window only if Ralf explicitly authorizes
it.

Possible scope:

- one very small configured window
- isolated output directory
- explicit timeout
- no overwrite of FU02g4c anchor outputs

Required condition:

- Stage 2 may only begin after a separate explicit approval from Ralf.

### Stage 3 - Full Raw-Order Replay / Certification Run

Purpose: execute the full FU02g4c raw-order replay/certification pass.

Required condition:

- Stage 3 may only begin after a separate explicit approval from Ralf.

The run must reuse the original FU02g4c enumerator and verified input bundle.
It must write only to an isolated output directory. It must not mutate existing
FU02g4c anchor files.

### Stage 4 - Post-Run Audit

Required post-run outputs:

- coverage report
- candidate replay table
- candidate_005 separate readout
- candidate_008 separate readout
- missing/additional candidate report
- `summary.json`
- `readout.md`
- Claim Boundary section

Required post-run checks:

- all 11 configured candidates were checked per-index
- raw-order coverage is complete, or an explicit gap report exists
- candidate_005 is reported without exactness overclaim
- candidate_008 is reported as positive control, not as full-coverage substitute
- final status only says certification complete if all criteria passed

## 5. Full-Certification Criteria

Full certification may only be claimed if all of the following are true:

- original FU02g4c enumerator reused
- original input bundle verified
- raw-order semantics verified
- full raw-order coverage completed or explicit gap report generated
- no existing FU02g4c anchor files mutated
- isolated output directory used
- all 11 candidates checked per-index
- candidate_005 separately reported
- candidate_008 separately reported
- no `near_distance=0 -> identity` overclaim
- `summary.json` created
- `readout.md` created
- final status explicitly says certification complete only if all criteria passed

If any criterion fails, the final status must remain bounded, for example:

- `not_certified`
- `partially_certified`
- `coverage_incomplete`
- `needs_mapping_clarification`
- `input_bundle_not_verified`

## 6. Risks

- unvollstaendige raw-order coverage
- scaffold/window replay wird versehentlich als full replay gelesen
- candidate mapping uneindeutig
- raw_index semantics falsch verstanden
- candidate_005 degeneracy wird ueberinterpretiert
- candidate_008 positive control wird ueberinterpretiert
- alte untracked Dateien beeinflussen Interpretation
- bestehende Outputs werden ueberschrieben
- langer Lauf wird versehentlich gestartet

## 7. Claim Boundary

### Nach Dry-Run-Plan erlaubt

- Der geplante Full Replay ist methodisch spezifiziert.
- Inputs, Runner, Risiken und Kriterien sind dokumentiert.
- candidate_005 und candidate_008 sind als Spezialfaelle im Plan enthalten.

### Nach Dry-Run-Plan nicht erlaubt

- Full Replay wurde ausgefuehrt.
- Full Certification ist abgeschlossen.
- Alle 11 Kandidaten sind raw-order certified.
- candidate_005 ist exact.
- global non-genericity is proven.

## 8. Next Step

Run only a read-only Stage 0 input-path validation.
