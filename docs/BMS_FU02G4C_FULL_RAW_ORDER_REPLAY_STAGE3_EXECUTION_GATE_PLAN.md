# BMS FU02g4c Full Raw-Order Replay: Stage-3 Execution Gate Plan

## 1. Zweck des Gate-Plans

Dies ist nur ein Execution Gate Plan.

Er startet keinen Full Replay. Er ist kein Certification Output. Er definiert Bedingungen, Stop-Regeln, Outputs und Claim Boundary fuer einen spaeteren Stage-3 Full Raw-Order Replay.

## 2. Ausgangslage

- Stage 0 input-path validation: PASS.
- Stage 1 disabled run config exists.
- Stage 2 candidate_008 reference smoke check: PASS.
- candidate_005 remains unresolved degeneracy-stress case.
- full FU02g4c raw-order replay certification remains open.

## 3. Full-Replay-Ziel

Ziel eines spaeteren Stage-3-Laufs:

- vollstaendige FU02g4c raw-order coverage pruefen oder expliziten Gap-Report erzeugen
- alle 11 Kandidaten per raw_index pruefen
- candidate_005 separat als degeneracy-stress case ausweisen
- candidate_008 separat als positive-control PASS/anchor ausweisen
- fehlende oder zusaetzliche Kandidaten dokumentieren
- keine FU02g4c-Ankeroutputs ueberschreiben

## 4. Required Preconditions

Der spaetere Full Replay darf nur laufen, wenn:

- Ralf explizit Stage 3 freigibt.
- Stage 0 PASS dokumentiert ist.
- Stage 1 disabled config dokumentiert ist.
- Stage 2 candidate_008 reference smoke PASS dokumentiert ist.
- original FU02g4c config existiert.
- original FU02g4c enumerator script existiert.
- alle 11 Kandidaten-Tabellen existieren und 11 Zeilen enthalten.
- isoliertes Output-Verzeichnis noch nicht existiert oder eindeutig freigegeben ist.
- git status vor dem Lauf dokumentiert wurde.
- keine bestehenden FU02g4c-Ankerdateien beschrieben werden.

## 5. Proposed Isolated Output Directory

Vorschlag:

```text
runs/BMS-FU02g4c-full-replay/stage3_full_raw_order_replay_certification_001/
```

## 6. Candidate Handling

Alle 11 Kandidaten:

- aus g5e1/g5e2/g5f/g5g/g5g2 Tabellen referenzieren
- candidate_count_expected: 11

candidate_005:

- raw_index: 26157530
- role: coarse_signature_degeneracy_stress_case
- expected_exact_match: false
- near_distance=0 darf nicht als identity/isomorphism gelesen werden
- muss separate Detailsektion bekommen

candidate_008:

- raw_index: 26187175
- role: positive_control_known_exact / Spiegelklunker
- Stage-2 reference smoke PASS vorhanden
- muss separate Detailsektion bekommen
- Positive control ersetzt keine Full Coverage

## 7. Execution Gate / Stop Conditions

Stage 3 muss BLOCKED bleiben, wenn:

- Befehl nicht eindeutig Full Replay isoliert ausfuehrt
- Befehl bestehende FU02g4c-Ankeroutputs ueberschreiben wuerde
- Befehl unklar zwischen window/scaffold replay und raw-order full replay unterscheidet
- raw-order coverage nicht gezaehlt oder nicht auditierbar ist
- nur Kandidatenfenster statt Full Coverage geprueft wuerden
- candidate_005 nicht separat ausgewiesen wuerde
- candidate_008 nicht separat ausgewiesen wuerde
- Output-Verzeichnis existiert und Ueberschreibung nicht explizit freigegeben ist
- Claim Boundary nicht geschrieben wuerde

## 8. Required Outputs for Stage 3

Ein spaeterer Full Replay muss mindestens schreiben:

- summary.json
- readout.md
- coverage_report.csv
- candidate_replay_certification.csv
- missing_or_additional_candidates.csv
- candidate_005_detail.json
- candidate_008_detail.json
- run_manifest.json
- command_log.txt oder equivalent
- claim_boundary section in readout.md

## 9. PASS / FAIL / BLOCKED Criteria

PASS nur, wenn:

- full raw-order coverage completed oder explicit complete gap report erzeugt
- alle 11 Kandidaten geprueft
- candidate_005 separat berichtet
- candidate_008 separat berichtet
- keine FU02g4c-Ankerdateien veraendert
- isolated output dir verwendet
- full_replay_started true, full_certification true nur bei erfuellten Kriterien
- Claim Boundary geschrieben

FAIL wenn:

- Full Replay laeuft, aber Kandidaten fehlen oder erwartete Checks fehlschlagen
- Coverage unvollstaendig ohne akzeptierten Gap-Report
- Output inkonsistent

BLOCKED wenn:

- Sicherheit/Isolierung/Command nicht eindeutig
- Gefahr von Ankerueberschreibung
- Runner startet nicht eindeutig den geplanten Modus
- Coverage nicht auditierbar

## 10. Claim Boundary

Nach diesem Gate Plan erlaubt:

- Stage-3 Full Replay Execution Gate ist spezifiziert.
- Voraussetzungen, Outputs und Stop-Bedingungen sind dokumentiert.
- candidate_008 Stage-2 positive-control PASS ist als Vorbedingung dokumentiert.
- candidate_005 bleibt als Degeneracy-Stressfall separat zu behandeln.

Nicht erlaubt:

- Stage-3 Full Replay wurde ausgefuehrt.
- Full Certification ist abgeschlossen.
- Alle 11 Kandidaten sind raw-order certified.
- candidate_005 ist exact.
- global non-genericity is proven.

## 11. Naechster Schritt

Create a Stage-3 disabled full-replay config, not executable by default.
