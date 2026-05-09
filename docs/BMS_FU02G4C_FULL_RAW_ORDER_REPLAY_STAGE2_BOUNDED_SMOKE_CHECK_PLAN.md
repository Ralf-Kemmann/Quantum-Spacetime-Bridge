# BMS-FU02g4c Full Raw-Order Replay - Stage 2 Bounded Smoke-Check Plan

**Date:** 2026-05-09
**Project:** Quantum-Spacetime Bridge / Gravitation und RaumZeit
**Block:** FU02g4c Full Raw-Order Replay Certification
**Stage:** 2
**Plan status:** bounded smoke-check plan only

## 1. Zweck des Plans

Stage 2 ist ein bounded smoke-check plan fuer den spaeteren FU02g4c Full
Raw-Order Replay Certification Block.

Stage 2 ist kein Full Replay.

Stage 2 ist kein Certification Output.

Stage 2 darf keine Full Coverage behaupten.

Stage 2 soll nur die spaetere Execution-Logik an einem begrenzten
Positivkontrollfall vorbereiten.

Dieser Plan startet keinen Smoke Check.

## 2. Ausgangslage

- Stage 0 input-path validation: `PASS`
- Stage 1 execution-ready disabled config liegt vor:
  `data/bms_fu02g4c_full_raw_order_replay_stage1_disabled_run_config.yaml`
- Full FU02g4c raw-order replay certification remains open.

Stage 1 ist disabled: `execution_enabled: false`, Stage 2 ist disabled, und
Stage 3 ist disabled. Ein echter Stage-2-Smoke-Check darf nur nach separater
Ralf-Freigabe laufen.

## 3. Empfohlener Smoke-Check-Kandidat

### candidate_008

- `candidate_id`: `candidate_008`
- `raw_index`: `26187175`
- role: positive_control_known_exact / Spiegelklunker
- `expected_exact_match`: `true`
- `expected_near_distance`: `0`
- purpose: positive-control technical smoke check
- claim boundary: positive control is not full coverage

`candidate_008` ist der geeignetere erste Smoke-Fall, weil er als
known-exact/positive-control dokumentiert ist. Er prueft technische
Anschlussfaehigkeit, nicht globale Spezifitaet.

## 4. Nicht als erster Smoke-Check-Kandidat

### candidate_005

- `candidate_id`: `candidate_005`
- `raw_index`: `26157530`
- role: coarse_signature_degeneracy_stress_case
- `expected_exact_match`: `false`
- `expected_near_distance`: `0`
- claim boundary: near_distance=0 is not identity or isomorphism

`candidate_005` ist wichtig, aber als erster Smoke Check methodisch ungeeignet.
Er gehoert in eine spaetere gezielte Degeneracy-Pruefung, nicht in den ersten
Positivkontroll-Smoke.

## 5. Vorgeschlagener spaeterer Stage-2-Modus

Der spaetere Smoke Check darf nur nach separater Ralf-Freigabe laufen.

Er soll:

- maximal einen Kandidaten pruefen
- `candidate_008` verwenden
- ein isoliertes Output-Verzeichnis verwenden:
  `runs/BMS-FU02g4c-full-replay/stage2_bounded_smoke_check_candidate_008/`
- keine FU02g4c-Ankerdateien aendern
- keine bestehenden Outputs ueberschreiben
- keine Full-Replay-Schleife starten
- kein unbounded enumeration/replay ausfuehren
- keine git operations ausfuehren

## 6. Erwartete spaetere Stage-2-Outputs

Fuer einen spaeteren echten Smoke Check, noch nicht jetzt, waeren sinnvoll:

- `summary.json`
- `readout.md`
- `candidate_008_smoke_check.json`
- `candidate_008_patch_photo_or_replay_reference.json`, falls erzeugt oder
  referenziert
- `claim_boundary.md` oder Claim-Boundary-Abschnitt im readout

Diese Outputs duerfen nur in das isolierte Stage-2-Verzeichnis geschrieben
werden und duerfen bestehende FU02g4c-Ankeroutputs nicht ueberschreiben.

## 7. Stage-2-Pass/Fail-Kriterien

### PASS nur, wenn

- `candidate_008` gezielt geprueft wurde
- Output isoliert geschrieben wurde
- kein Full Replay gestartet wurde
- keine FU02-Ankerdateien veraendert wurden
- expected exact-marker technisch wiedergefunden oder klar dokumentiert wurde
- Claim Boundary im Output steht

### FAIL oder BLOCKED, wenn

- Inputpfade fehlen
- Stage-1 disabled config nicht referenziert ist
- Smoke Check mehr als einen Kandidaten ausfuehren wuerde
- Full Replay versehentlich gestartet wuerde
- bestehende Outputs ueberschrieben wuerden
- `candidate_008` nicht eindeutig gemappt werden kann

## 8. Risiken

- Smoke Check wird als Full Certification missverstanden
- candidate_008 positive control wird ueberinterpretiert
- Stage-2-Output wird versehentlich in FU02g4c-Ankerverzeichnis geschrieben
- unbounded runner wird versehentlich gestartet
- candidate mapping raw_index/skip semantics nicht erneut sichtbar gemacht
- exact_match wird als globaler Strukturbeweis ueberinterpretiert

## 9. Claim Boundary

### Nach Stage-2-Plan erlaubt

- A bounded smoke-check plan exists.
- candidate_008 is selected as positive-control smoke candidate.
- candidate_005 is reserved for later degeneracy-stress handling.
- Stage 2 remains disabled until explicit Ralf approval.

### Nach Stage-2-Plan nicht erlaubt

- Smoke Check was executed.
- FU02g4c full raw-order replay was started.
- FU02g4c full raw-order replay certification is complete.
- All 11 candidates are raw-order certified.
- candidate_008 proves global non-genericity.
- candidate_005 is exact.
- near_distance=0 implies identity or isomorphism.

## 10. Naechster Schritt

Create a disabled Stage-2 candidate_008 smoke-check config.
