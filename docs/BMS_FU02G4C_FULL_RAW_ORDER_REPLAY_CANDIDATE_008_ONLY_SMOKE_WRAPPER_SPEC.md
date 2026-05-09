# BMS FU02g4c Full Raw-Order Replay: candidate_008-only Smoke Wrapper Specification

## 1. Zweck der Spezifikation

Diese Spezifikation reagiert auf den Stage-2 BLOCKED-Befund.

Der BLOCKED-Befund entstand, weil kein eindeutig sicherer candidate_008-only Befehl vorhanden war. Ziel ist die spaetere Implementierung eines minimalen Wrappers, der genau candidate_008 prueft.

Diese Spezifikation ist kein Lauf, kein Result Output und keine Certification.

## 2. Ausgangslage

- Stage 0 input-path validation: PASS.
- Stage 1 execution-ready disabled config liegt vor.
- Stage 2 bounded smoke-check plan liegt vor.
- Stage 2 candidate_008 disabled smoke config liegt vor.
- Stage 2 execution gate wurde geprueft.
- Stage 2 execution result: BLOCKED.
- full FU02g4c raw-order replay certification remains open.

## 3. Zielkandidat

candidate_008:

- candidate_id: candidate_008
- raw_index: 26187175
- role: positive_control_known_exact / Spiegelklunker
- expected_exact_match: true
- expected_near_distance: 0
- purpose: bounded positive-control technical smoke check
- claim boundary: positive control is not full coverage and not global non-genericity proof

## 4. Ausgeschlossener Kandidat

candidate_005:

- candidate_id: candidate_005
- raw_index: 26157530
- role: coarse_signature_degeneracy_stress_case
- expected_exact_match: false
- expected_near_distance: 0
- status: explicitly excluded from candidate_008-only wrapper
- claim boundary: near_distance=0 is not identity or isomorphism; candidate_005 must not be relabeled exact

## 5. Wrapper-Anforderungen

Der spaetere Wrapper muss:

- genau einen Kandidaten akzeptieren oder hart auf candidate_008 fixiert sein
- candidate_id == candidate_008 pruefen
- raw_index == 26187175 pruefen
- candidate_005 aktiv blockieren
- alle anderen Kandidaten aktiv blockieren
- execution nur ausfuehren, wenn explizit enabled
- default: disabled
- full_replay_allowed: false
- unbounded_enumeration_allowed: false
- existing_output_overwrite_allowed: false
- fu02g4c_anchor_mutation_allowed: false
- git_operations_allowed: false

## 6. Erlaubte technische Strategie

Option A:

Wrapper nutzt vorhandene patch photo / exact patch JSON als read-only reference und prueft nur Konsistenz gegen candidate_008-Metadaten.

Option B:

Wrapper nutzt `inspect_bms_fu02g4c_single_exact_patch.py` nur dann, wenn ein klarer no-anchor, single-index, max_raw_patches=1, isolated-output Modus sicher nachgewiesen ist.

Option C:

Wrapper bleibt BLOCKED, falls ein vorhandenes Skript nur ueber Enumerator-Wrapper oder Multi-Kandidaten-Logik erreichbar ist.

Option C ist vorzuziehen, wenn Sicherheitslage unklar ist.

## 7. Verbotene technische Strategie

Der spaetere Wrapper darf nicht:

- g5g2 full candidate table laufen lassen
- alle 11 Kandidaten pruefen
- candidate_005 mitpruefen
- FU02g4c Enumerator unbounded starten
- FU02g4c-Ankerverzeichnisse beschreiben
- bestehende FU02g4c patch photos ueberschreiben
- near_distance=0 als exact identity interpretieren
- candidate_008 als Full-Coverage-Beweis interpretieren

## 8. Vorgeschlagene spaetere CLI

Nur als Spezifikation, nicht ausfuehren:

```bash
python scripts/run_bms_fu02g4c_candidate008_only_smoke_wrapper.py \
  --config data/bms_fu02g4c_full_raw_order_replay_stage2_candidate_008_disabled_smoke_config.yaml \
  --enable-candidate-008-smoke \
  --candidate-id candidate_008 \
  --raw-index 26187175 \
  --output-dir runs/BMS-FU02g4c-full-replay/stage2_bounded_smoke_check_candidate_008/
```

Festzuhalten:

- Dieses Skript existiert noch nicht.
- Der Befehl ist ein Zielbild, kein aktueller ausfuehrbarer Befehl.
- Vor Ausfuehrung muesste Ralf explizit freigeben.

## 9. Erwartete spaetere Outputs

Falls der Wrapper spaeter implementiert und freigegeben wird:

- summary.json
- readout.md
- candidate_008_smoke_check.json
- candidate_008_reference_check.json
- optional: candidate_008_patch_photo_reference.json

Alle Outputs muessen enthalten:

- stage: 2
- candidate_id: candidate_008
- raw_index: 26187175
- candidates_checked_count: 1
- candidate_005_checked: false
- full_replay_started: false
- full_certification: false
- smoke_check_status: PASS / FAIL / BLOCKED
- claim_boundary

## 10. PASS / FAIL / BLOCKED Kriterien

PASS nur, wenn:

- exactly candidate_008 checked
- candidate_005_checked == false
- full_replay_started == false
- full_certification == false
- isolated output directory used
- expected positive-control condition satisfied or explicitly validated
- claim boundary written

FAIL wenn:

- candidate_008 check runs but expected condition fails
- candidate_008 mapping mismatch occurs
- output incomplete but execution occurred

BLOCKED wenn:

- command would check more than candidate_008
- command would include candidate_005
- command would start full replay
- command would start unbounded enumeration
- command would mutate FU02g4c anchors
- command safety cannot be proven

## 11. Claim Boundary

Nach dieser Spezifikation erlaubt:

- A candidate_008-only smoke-wrapper specification exists.
- The previous Stage-2 BLOCKED result has been translated into wrapper requirements.
- candidate_008 remains the selected positive-control target.
- candidate_005 remains excluded and reserved for later degeneracy handling.

Nach dieser Spezifikation nicht erlaubt:

- Wrapper was implemented.
- Smoke check was executed.
- candidate_008 was newly checked.
- FU02g4c full raw-order replay was started.
- FU02g4c full raw-order replay certification is complete.
- candidate_008 proves global non-genericity.
- candidate_005 is exact.
- near_distance=0 implies identity or isomorphism.

## 12. Naechster Schritt

Create the candidate_008-only smoke-wrapper as a new script, disabled by default, after explicit Ralf approval.
