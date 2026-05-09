# BMS FU02g4c Full Raw-Order Replay: Stage-3 Wrapper/Runner Specification

## 1. Zweck der Spezifikation

Diese Spezifikation reagiert auf den Stage-3 Command-Gate-Befund BLOCKED.

Der BLOCKED-Befund entstand, weil aus vorhandenen Skripten kein eindeutig sicherer, isolierter Full-Replay-Certification-Befehl ableitbar war.

Ziel ist die spaetere Implementierung eines dedizierten Stage-3 Wrappers/Runners.

Diese Spezifikation ist kein Lauf, kein Certification Output und keine Full-Coverage-Zertifizierung.

## 2. Ausgangslage

- Stage 0 input-path validation: PASS.
- Stage 1 disabled run config exists.
- Stage 2 candidate_008 reference smoke check: PASS.
- Stage 3 disabled full-replay config exists.
- Stage 3 command gate: BLOCKED.
- full FU02g4c raw-order replay certification remains open.

## 3. Ziel des spaeteren Stage-3 Wrappers/Runners

Der spaetere Wrapper/Runner muss:

- vollstaendige FU02g4c raw-order coverage ausfuehren oder einen vollstaendigen Gap-Report erzeugen.
- alle 11 Kandidaten aus den Kandidatentabellen pruefen.
- raw_index-Semantik auditierbar dokumentieren.
- candidate_005 separat berichten.
- candidate_008 separat berichten.
- missing/additional candidates berichten.
- alle Outputs in ein isoliertes Stage-3-Verzeichnis schreiben.
- keine FU02g4c-Ankeroutputs ueberschreiben.
- Command Log und Manifest schreiben.
- Claim Boundary schreiben.

## 4. Technische Mindestanforderungen

Der spaetere Wrapper/Runner muss default disabled sein:

- execution_enabled: false
- full_replay_enabled: false
- dry_run/default_gate_mode: true
- allow_existing_output_overwrite: false
- allow_existing_fu02g4c_anchor_mutation: false
- unbounded_execution_requires_explicit_ralf_approval: true
- full_certification default: false

Aktivierung nur mit expliziten Flags, zum Beispiel:

- `--enable-stage3-full-replay`
- `--confirm-full-raw-order-coverage`
- `--candidate-count-expected 11`
- `--output-dir <fresh isolated output dir>`
- `--write-claim-boundary`
- `--require-stage2-candidate008-pass`

## 5. Input-Anforderungen

Muss pruefen:

- Stage-3 disabled full-replay config YAML parsbar.
- Original FU02g4c config vorhanden.
- Original FU02g4c enumerator script vorhanden.
- Kandidatentabellen vorhanden:
  - g5e1 candidates
  - g5e2 classification
  - g5f revalidation
  - g5g replay certification
  - g5g2 per-index photo certification
- alle Kandidatentabellen enthalten 11 Kandidaten oder Abweichung wird BLOCKED.
- candidate_005 vorhanden mit raw_index 26157530.
- candidate_008 vorhanden mit raw_index 26187175.
- Stage-2 candidate_008 reference smoke PASS Result Note vorhanden.
- Output-Verzeichnis ist frisch oder explizit freigegeben.

## 6. Coverage-Anforderungen

- Full raw-order coverage darf nicht durch window-only, scaffold-only oder candidate-only replay ersetzt werden.
- Coverage muss zaehlbar und auditierbar sein.
- Wenn vollstaendige Coverage nicht erreichbar ist, muss ein explicit gap report erzeugt werden.
- Gap report darf nicht als Full Certification gelesen werden.
- Der spaetere Runner muss klar unterscheiden:
  - full_raw_order_coverage_complete
  - explicit_gap_report_generated
  - window_or_scaffold_support_only
  - blocked

## 7. Candidate Handling

Alle 11 Kandidaten:

- muessen aus Tabellen geladen werden.
- muessen per raw_index geprueft oder als nicht pruefbar dokumentiert werden.
- muessen in `candidate_replay_certification.csv` erscheinen.
- fehlende oder zusaetzliche Kandidaten muessen in `missing_or_additional_candidates.csv` erscheinen.

candidate_005:

- candidate_id: candidate_005
- raw_index: 26157530
- role: coarse_signature_degeneracy_stress_case
- expected_exact_match: false
- expected_near_distance: 0
- muss separate Detaildatei `candidate_005_detail.json` bekommen.
- near_distance=0 darf nicht als identity/isomorphism gelesen werden.
- darf nicht als exact relabelt werden.

candidate_008:

- candidate_id: candidate_008
- raw_index: 26187175
- role: positive_control_known_exact / Spiegelklunker
- Stage-2 reference smoke check: PASS
- muss separate Detaildatei `candidate_008_detail.json` bekommen.
- Positive control ist kein Ersatz fuer Full Coverage.

## 8. Erlaubte technische Strategie

Option A:

Dedizierter Orchestrator nutzt bestehenden FU02g4c Enumerator nur in explizit freigegebenem Stage-3-Modus und schreibt ausschliesslich in isoliertes Stage-3-Verzeichnis.

Option B:

Dedizierter Orchestrator ruft vorhandene Chunk-Enumeration kontrolliert auf, sammelt Coverage-Logs, aggregiert Outputs und prueft danach alle 11 Kandidaten.

Option C:

Falls vollstaendige Ausfuehrung zu lang oder nicht eindeutig ist, erzeugt der Runner einen explicit gap report und Status BLOCKED oder GAP_REPORTED, aber keine Full Certification.

Jede Strategie muss Claim Boundary schreiben.

## 9. Verbotene technische Strategie

Der spaetere Wrapper/Runner darf nicht:

- nur vorhandene Window-/Inspect-Logs als Full Coverage ausgeben.
- nur candidate_008 pruefen.
- candidate_005 auslassen.
- alle 11 Kandidaten pruefen, aber Coverage nicht auditieren.
- bestehende FU02g4c-Ankeroutputs ueberschreiben.
- patch_photos oder alte FU02g4c logs veraendern.
- near_distance=0 als exact identity/isomorphism interpretieren.
- Stage-2 positive control als Full-Replay-Beweis interpretieren.
- bei unklarem Zustand PASS schreiben.

## 10. Vorgeschlagene spaetere CLI

Nur als Spezifikation, nicht ausfuehren:

```bash
python scripts/run_bms_fu02g4c_stage3_full_replay_wrapper.py \
  --config data/bms_fu02g4c_full_raw_order_replay_stage3_disabled_full_replay_config.yaml \
  --enable-stage3-full-replay \
  --confirm-full-raw-order-coverage \
  --candidate-count-expected 11 \
  --require-stage2-candidate008-pass \
  --output-dir runs/BMS-FU02g4c-full-replay/stage3_full_raw_order_replay_certification_001/ \
  --write-claim-boundary
```

Festhalten:

- Dieses Skript existiert noch nicht.
- Der Befehl ist ein Zielbild.
- Vor Ausfuehrung muss Ralf explizit freigeben.
- Vor Ausfuehrung muss geprueft werden, dass Output-Verzeichnis nicht existiert oder explizit freigegeben ist.

## 11. Erwartete Outputs

Der spaetere Stage-3 Wrapper/Runner muss schreiben:

- summary.json
- readout.md
- coverage_report.csv
- candidate_replay_certification.csv
- missing_or_additional_candidates.csv
- candidate_005_detail.json
- candidate_008_detail.json
- run_manifest.json
- command_log.txt
- claim_boundary section in readout.md

`summary.json` muss enthalten:

- stage: 3
- mode
- full_replay_started
- full_raw_order_coverage_complete
- explicit_gap_report_generated
- full_certification
- candidate_count_expected
- candidate_count_checked
- candidate_005_reported
- candidate_008_reported
- fu02g4c_anchor_files_mutated: false
- output_dir
- warnings
- blocked_reasons
- claim_boundary

## 12. PASS / FAIL / BLOCKED / GAP_REPORTED Kriterien

PASS nur, wenn:

- full raw-order coverage completed.
- all 11 candidates checked.
- candidate_005 separately reported.
- candidate_008 separately reported.
- no FU02g4c anchor files modified.
- isolated output directory used.
- required outputs complete.
- claim boundary written.
- full_certification true only under these conditions.

FAIL wenn:

- Full replay starts but candidate checks fail.
- expected candidate mappings fail.
- outputs are inconsistent.
- candidate_005/candidate_008 reports missing.

BLOCKED wenn:

- command safety or isolation cannot be proven.
- coverage cannot be audited.
- runner would overwrite anchor outputs.
- runner would only perform window/scaffold replay.
- candidate tables are incomplete.
- output directory collision occurs without explicit approval.

GAP_REPORTED wenn:

- full coverage cannot complete but the gap is explicitly documented.
- full_certification remains false.
- readout.md clearly says certification remains open.

## 13. Claim Boundary

Nach dieser Spezifikation erlaubt:

- A dedicated Stage-3 full-replay wrapper/runner specification exists.
- The Stage-3 BLOCKED command-gate result has been translated into wrapper requirements.
- Full Coverage, candidate handling, outputs, and safety gates are specified.
- candidate_005 and candidate_008 are separately protected in the future design.

Nach dieser Spezifikation nicht erlaubt:

- Stage-3 wrapper was implemented.
- Stage-3 Full Replay was executed.
- FU02g4c full raw-order replay certification is complete.
- All 11 candidates are raw-order certified.
- candidate_005 is exact.
- candidate_008 proves global non-genericity.
- near_distance=0 implies identity or isomorphism.

## 14. Naechster Schritt

Create the Stage-3 full-replay wrapper as a new script, disabled by default, after explicit Ralf approval.
