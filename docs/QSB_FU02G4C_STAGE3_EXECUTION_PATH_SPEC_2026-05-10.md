# QSB FU02g4c Stage 3 — Execution-Path Implementation Specification

**Date:** 2026-05-10  
**Project:** Quantum–Spacetime Bridge / Gravitation und RaumZeit  
**Block:** FU02g4c / C60 carrier-patch genericity control  
**Status:** Specification draft for controlled Stage-3 implementation path  
**Intended repository location:** `docs/QSB_FU02G4C_STAGE3_EXECUTION_PATH_SPEC_2026-05-10.md`

---

## 1. Purpose

This document specifies the controlled implementation path for **FU02g4c Stage 3**.

Stage 3 is not a certification run and not a scientific result by itself. Its purpose is to define and implement a guarded execution path that can later run the orbit-reduced / resumable connected-patch replay workflow under explicit gates, reproducibility constraints, and conservative claim boundaries.

The immediate goal is to make the execution path technically testable while preserving the current scientific status:

- Stage 0: `PASS`
- Stage 1: disabled configuration exists
- Stage 2: `candidate_008` reference-smoke `PASS`
- Stage 3: scaffold exists; dry-run ready; negative execution gate blocks correctly
- Full raw-order replay: not executed
- Full certification: not available
- Global non-genericity claim: not available

---

## 2. Non-goals

Stage 3 must not be treated as any of the following:

1. A full replay of the raw connected-patch enumeration.
2. A certification of the FU02f1-C60 carrier region.
3. A proof of global non-genericity.
4. A replacement for Stage 0, Stage 1, or Stage 2.
5. A permission slip for overwriting closed FU02 anchor files.
6. A silent migration or restructuring of the repository.

Stage 3 is only an execution-path implementation and control layer.

---

## 3. Current status basis

The current working basis is the FU02g4c Stage-3 relocation package dated 2026-05-09.

The relevant project-internal state is:

- `candidate_008` remains the reference-smoke candidate.
- `candidate_005` remains a degeneracy stress case and must not be silently promoted to reference status.
- Existing FU02 anchor files are treated as closed unless explicitly reopened by Ralf.
- The disabled-by-default principle remains active.
- The negative execution gate must continue to block execution when the required permission state is absent.

No implementation step may blur the distinction between scaffold readiness and certified replay completion.

---

## 4. Required implementation principle

The Stage-3 execution path must be implemented as a **guarded, disabled-by-default pathway**.

The implementation must satisfy four basic principles:

1. **No hidden execution:** any run path must be explicit in command, config, and output.
2. **No hidden mutation:** existing anchor files must not be modified unless explicitly instructed.
3. **No hidden claim upgrade:** successful dry-runs or scaffold tests must not be reported as certification.
4. **No hidden fallback:** missing inputs or blocked gates must fail clearly rather than silently switching to a different mode.

---

## 5. Input assumptions

The implementation may assume that the repository contains the existing FU02g4c Stage-3 scaffold and related configs from the relocation package.

However, the implementation must not assume that a full raw-order replay has already been completed.

Expected input categories:

| Field name | Field type | Field description |
|---|---:|---|
| `stage_id` | string | Identifier for the current workflow stage; expected value: `FU02g4c_stage3`. |
| `candidate_id` | string | Candidate identifier under test; `candidate_008` for reference-smoke path, `candidate_005` for degeneracy stress path. |
| `execution_enabled` | boolean | Hard gate for real execution; default must be `false`. |
| `dry_run` | boolean | Whether the path validates commands/configs without executing full replay logic. |
| `allow_anchor_mutation` | boolean | Must default to `false`; protects closed FU02 anchor files. |
| `input_config_path` | path/string | Path to the Stage-3 configuration file. |
| `output_dir` | path/string | Run output directory under `runs/`, not a top-level folder. |
| `run_label` | string | Human-readable label for the run attempt. |
| `expected_reference_candidate` | string | Reference candidate expected for the reference-smoke path; normally `candidate_008`. |
| `degeneracy_stress_candidate` | string | Candidate reserved for degeneracy stress behavior; normally `candidate_005`. |
| `claim_mode` | string | Explicit claim mode; must remain `execution_path_only` for this stage. |

---

## 6. Execution gate

The execution gate is the central safety mechanism of Stage 3.

### 6.1 Default behavior

By default, Stage 3 must not execute the real replay path.

Expected default state:

```yaml
execution_enabled: false
dry_run: true
allow_anchor_mutation: false
claim_mode: execution_path_only
```

### 6.2 Negative gate requirement

When `execution_enabled: false`, any attempt to start the real replay path must terminate with a clear blocked status.

Expected blocked status wording:

```text
stage3_execution_blocked_by_gate
```

The blocked state is a correct and expected behavior, not a failure of the scaffold.

### 6.3 Positive gate requirement

A positive gate may only be introduced later by explicit instruction.

A positive gate must require at least:

```yaml
execution_enabled: true
dry_run: false
allow_anchor_mutation: false
claim_mode: execution_path_only
```

Even with a positive execution gate, anchor mutation remains disallowed unless separately authorized.

---

## 7. Expected outputs

Stage 3 should produce explicit, reviewable outputs in a run directory under `runs/`.

Expected output files:

| Field name | Field type | Field description |
|---|---:|---|
| `stage3_execution_gate_report.json` | JSON file | Machine-readable gate decision, input config summary, and blocked/allowed state. |
| `stage3_execution_gate_report.md` | Markdown file | Human-readable readout with Befund / Interpretation / Hypothese / Offene Lücke / Claim Boundary. |
| `stage3_command_manifest.txt` | text file | Exact command or command template that would be executed, including dry-run status. |
| `stage3_input_manifest.json` | JSON file | Explicit list of input files and candidate identifiers used by the path. |
| `stage3_output_manifest.json` | JSON file | Explicit list of files written by the Stage-3 check itself. |

Optional later outputs, only if the positive gate is explicitly opened:

| Field name | Field type | Field description |
|---|---:|---|
| `stage3_replay_progress.jsonl` | JSONL file | Resumable progress records for replay execution. |
| `stage3_replay_summary.json` | JSON file | Summary of replay status, timeout behavior, and orbit/signature counters. |
| `stage3_replay_readout.md` | Markdown file | Human-readable run result, still without certification claim unless full criteria are met. |

---

## 8. Pass / fail criteria

### 8.1 Dry-run pass

A Stage-3 dry-run can be marked `PASS` only if all of the following hold:

1. The config is found and parsed.
2. Candidate identifiers are explicit.
3. The command path is explicit.
4. The real execution path remains blocked when `execution_enabled: false`.
5. No closed anchor file is modified.
6. Output manifests are written under `runs/`.
7. The readout clearly states that this is not certification.

Recommended status label:

```text
stage3_dry_run_gate_behavior_pass
```

### 8.2 Negative gate pass

A blocked execution attempt is a pass when it blocks for the correct reason.

Recommended status label:

```text
stage3_negative_execution_gate_pass
```

### 8.3 Fail conditions

Stage 3 must fail if any of the following occur:

1. The real replay path executes while `execution_enabled: false`.
2. An anchor file is modified without explicit authorization.
3. `candidate_005` is silently treated as the reference candidate.
4. Missing input is silently replaced by another path.
5. The output readout implies full certification.
6. The run writes outside approved repository subdirectories.
7. The implementation changes unrelated project files.

Recommended fail labels:

```text
stage3_unexpected_execution_fail
stage3_anchor_mutation_fail
stage3_candidate_role_confusion_fail
stage3_hidden_fallback_fail
stage3_claim_boundary_fail
stage3_output_location_fail
stage3_unrequested_file_mutation_fail
```

---

## 9. Readout structure

Every Stage-3 readout must use the following sections:

```markdown
## Befund

## Interpretation

## Hypothese

## Offene Lücke

## Claim Boundary
```

### Required claim boundary wording

The readout must include wording equivalent to:

> This Stage-3 result only validates the guarded execution path or gate behavior. It does not constitute a full raw-order replay, a full certification, or evidence for global non-genericity.

---

## 10. Repository constraints

Codex or any implementation assistant must obey the following constraints:

1. Create only the explicitly requested files.
2. Do not edit closed FU02 anchor files.
3. Do not delete files.
4. Do not create new top-level directories.
5. Do not run `git add`, `git commit`, `git reset`, or `git push`.
6. Always report:
   - files created,
   - files modified,
   - commands run,
   - tests/checks performed,
   - outputs produced,
   - limitations.
7. Always show `git status --short` at the end of the local work block.

---

## 11. Suggested implementation target

The preferred next implementation step is a small guarded runner or runner extension that only validates the Stage-3 execution path first.

Suggested file target, if not already present:

```text
scripts/fu02g4c_stage3_execution_gate_runner.py
```

Suggested config target, if not already present:

```text
data/fu02g4c_stage3_execution_gate_config.yaml
```

The runner should initially support:

```bash
python scripts/fu02g4c_stage3_execution_gate_runner.py \
  --config data/fu02g4c_stage3_execution_gate_config.yaml \
  --dry-run
```

The first implementation pass should not execute the full replay.

---

## 12. Minimal Codex Auftrag

Use the following short-leash task text for Codex:

```text
Create the Stage-3 execution-path gate implementation for FU02g4c exactly as specified in docs/QSB_FU02G4C_STAGE3_EXECUTION_PATH_SPEC_2026-05-10.md.

Create only these files if they do not already exist:
- scripts/fu02g4c_stage3_execution_gate_runner.py
- data/fu02g4c_stage3_execution_gate_config.yaml

Do not edit existing FU02 anchor files.
Do not delete files.
Do not create top-level folders.
Do not run git add, git commit, git reset, or git push.

The default config must be disabled-by-default:
- execution_enabled: false
- dry_run: true
- allow_anchor_mutation: false
- expected_reference_candidate: candidate_008
- degeneracy_stress_candidate: candidate_005
- claim_mode: execution_path_only

The runner must write explicit reports under runs/ and must treat blocked execution under execution_enabled=false as the expected negative gate pass.

At the end, report:
- files created
- files modified
- commands run
- tests/checks performed
- output files produced
- limitations
- git status --short
```

---

## 13. Scientific claim boundary

At the present stage, the only admissible claim is:

> A guarded Stage-3 execution path is being specified and prepared. The scaffold and gate behavior may be tested, but no full raw-order replay and no full FU02g4c certification have yet been completed.

The following claims are not admissible:

- The C60 carrier patch is globally non-generic.
- FU02g4c is fully certified.
- Stage 3 proves the FU02f1-C60 carrier region.
- The replay has been completed.
- Candidate degeneracy has been resolved globally.

---

## 14. Open items

1. Confirm the exact existing Stage-3 scaffold filenames in the repository.
2. Confirm whether a runner file already exists and should be extended rather than newly created.
3. Confirm the intended run directory naming scheme under `runs/`.
4. Confirm whether Stage-3 should write JSON-only first or JSON + Markdown readouts immediately.
5. Confirm whether the first Codex pass should be limited to dry-run reporting only.

Until these are resolved, Stage 3 remains an implementation-path specification, not a replay result.
