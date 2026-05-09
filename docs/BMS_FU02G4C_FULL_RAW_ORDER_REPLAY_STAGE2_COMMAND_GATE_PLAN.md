# BMS-FU02g4c Full Raw-Order Replay - Stage 2 Command Gate Plan

**Date:** 2026-05-09
**Project:** Quantum-Spacetime Bridge / Gravitation und RaumZeit
**Block:** FU02g4c Full Raw-Order Replay Certification
**Stage:** 2
**Plan status:** command-construction / execution-gate plan only

## 1. Zweck des Gate-Plans

Dieser Plan konstruiert und prueft nur den spaeter moeglichen Stage-2-Befehl.

Er fuehrt den Befehl nicht aus.

Er hebt keine disabled Flags auf.

Er ist kein Smoke-Check-Output.

Er ist kein Certification Output.

Der Stage-2 Smoke Check bleibt disabled. Kein Smoke Check wurde durch diesen
Plan ausgefuehrt.

## 2. Ausgangslage

- Stage 0 input-path validation: `PASS`
- Stage 1 disabled run config liegt vor:
  `data/bms_fu02g4c_full_raw_order_replay_stage1_disabled_run_config.yaml`
- Stage 2 candidate_008 disabled smoke config liegt vor:
  `data/bms_fu02g4c_full_raw_order_replay_stage2_candidate_008_disabled_smoke_config.yaml`
- Full FU02g4c raw-order replay certification remains open.

Die Stage-2-Config bleibt disabled:

- `execution_enabled: false`
- `smoke_check_enabled: false`
- `allow_long_replay_run: false`
- `replay_started: false`
- `full_certification: false`

## 3. Zielkandidat

### candidate_008

- `candidate_id`: `candidate_008`
- `raw_index`: `26187175`
- role: positive_control_known_exact / Spiegelklunker
- `expected_exact_match`: `true`
- `expected_near_distance`: `0`
- purpose: bounded positive-control smoke check
- Claim Boundary: positive control is not full coverage.

### Nicht ausfuehren / nicht pruefen in diesem Gate

`candidate_005` bleibt ausgeschlossen:

- `candidate_id`: `candidate_005`
- `raw_index`: `26157530`
- role: coarse_signature_degeneracy_stress_case
- `expected_exact_match`: `false`
- Claim Boundary: near_distance=0 is not identity or isomorphism.

## 4. Zu konstruierender spaeterer Befehl

Die CLI-Strukturen wurden nur read-only inspiziert. Es wurde kein Runner
ausgefuehrt.

### Erkennbare CLI-Signaturen

`scripts/run_bms_fu02g5g_fu02g4c_raw_order_replay_certification.py`

- erkennbar: `python scripts/run_bms_fu02g5g_fu02g4c_raw_order_replay_certification.py --config <config>`
- Zweck im Gate: Candidate-Replay-/Recovery-Logik als spaeterer
  command-construction-Kandidat.

`scripts/run_bms_fu02g5g2_narrow_per_index_replay_photo_certification.py`

- erkennbar: `python scripts/run_bms_fu02g5g2_narrow_per_index_replay_photo_certification.py --config <config>`
- Zweck im Gate: narrow per-index photo/replay logic as spaeterer
  smoke-check-Kandidat, nur mit isolierter und enabled Stage-2-Config.

`scripts/inspect_bms_fu02g4c_single_exact_patch.py`

- erkennbar:
  `python scripts/inspect_bms_fu02g4c_single_exact_patch.py --repo-root <path> --runner <path> --base-config <path> --skip <raw_index> --max-raw-patches <n> --chunk-id <id> --timeout-seconds <seconds> --output-dir <path>`
- Zweck im Gate: spaeterer begrenzter Single-Patch-/positive-control
  Inspector-Kandidat, wenn ein bounded smoke technisch so freigegeben wird.

### Spaeter moegliche Befehle - NICHT AUSFUEHREN

Diese Befehle sind nur Text fuer eine spaetere Freigabe. Sie duerfen aus diesem
Plan heraus nicht ausgefuehrt werden.

```bash
python scripts/run_bms_fu02g5g2_narrow_per_index_replay_photo_certification.py \
  --config data/bms_fu02g4c_full_raw_order_replay_stage2_candidate_008_enabled_smoke_config.yaml
```

oder, falls der Single-Patch-Inspector als bounded positive-control smoke
freigegeben wird:

```bash
python scripts/inspect_bms_fu02g4c_single_exact_patch.py \
  --repo-root /home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge \
  --runner scripts/run_bms_fu02g4c_orbit_reduced_resumable_connected_patch_enumeration.py \
  --base-config data/bms_fu02g4c_orbit_reduced_resumable_config.yaml \
  --skip 26187175 \
  --max-raw-patches 1 \
  --chunk-id stage2_candidate_008_bounded_smoke \
  --timeout-seconds 120 \
  --output-dir runs/BMS-FU02g4c-full-replay/stage2_bounded_smoke_check_candidate_008
```

The current disabled config path
`data/bms_fu02g4c_full_raw_order_replay_stage2_candidate_008_disabled_smoke_config.yaml`
must not be treated as an executable config unless a later explicit approval
creates an enabled config or provides an explicit terminal enable gate.

## 5. Execution Gate

Before Stage 2 may run later, all of the following must be true:

- Ralf gibt explizit frei.
- disabled Config wird nicht heimlich geaendert.
- Es wird entweder eine neue enabled Stage-2 Config erstellt oder im Terminal
  explizit ein Freigabe-Flag gesetzt.
- Es wird maximal `candidate_008` geprueft.
- Output geht ausschliesslich nach:
  `runs/BMS-FU02g4c-full-replay/stage2_bounded_smoke_check_candidate_008/`
- Keine FU02g4c-Ankeroutputs werden beschrieben.
- Kein Full Replay wird gestartet.
- Kein unbounded Enumerator wird gestartet.
- `git status --short` wird vor und nach einem spaeteren Lauf geprueft.
- Claim Boundary wird in Output geschrieben.

## 6. Blockierende Bedingungen

Stage 2 muss `BLOCKED` bleiben, wenn:

- command would process more than candidate_008
- command would start full replay or unbounded enumeration
- command would write into existing FU02g4c anchor directories
- command would overwrite existing outputs
- candidate_008 mapping is ambiguous
- candidate_005 would be included accidentally
- execution_enabled remains false and no explicit Ralf approval exists
- no isolated output directory is declared
- no Claim Boundary output would be written

## 7. Erwartete spaetere Outputs, falls Ralf Stage 2 freigibt

- `summary.json`
- `readout.md`
- `candidate_008_smoke_check.json`
- `candidate_008_replay_or_photo_reference.json`
- claim_boundary section in `readout.md`

## 8. Claim Boundary

### Nach diesem Gate-Plan erlaubt

- A Stage-2 command-construction / execution-gate plan exists.
- candidate_008 remains the selected bounded positive-control target.
- required pre-execution safety gates are documented.
- Stage 2 remains disabled until explicit Ralf approval.

### Nach diesem Gate-Plan nicht erlaubt

- Stage-2 smoke check was executed.
- FU02g4c full raw-order replay was started.
- FU02g4c full raw-order replay certification is complete.
- All 11 candidates are raw-order certified.
- candidate_008 proves global non-genericity.
- candidate_005 is exact.
- near_distance=0 implies identity or isomorphism.

## 9. Naechster Schritt

Commit this Stage-2 command-gate plan.
