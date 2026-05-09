# BMS FU02g4c Full Raw-Order Replay: Stage-3 Command Gate Plan

## 1. Zweck des Command Gate Plans

Dieser Plan konstruiert nur moegliche Stage-3-Befehle.

Er fuehrt keinen Full Replay aus. Er ist kein Certification Output. Er entscheidet, ob Stage 3 ausfuehrbar, blockiert oder nur nach weiterer Wrapper-/Runner-Spezifikation moeglich ist.

## 2. Ausgangslage

- Stage 0 input-path validation: PASS.
- Stage 1 disabled config exists.
- Stage 2 candidate_008 reference smoke check: PASS.
- Stage 3 disabled full-replay config exists.
- Full FU02g4c raw-order replay certification remains open.

## 3. Read-only CLI / Runner Inventory

### scripts/run_bms_fu02g4c_orbit_reduced_resumable_connected_patch_enumeration.py

- Pfad: `scripts/run_bms_fu02g4c_orbit_reduced_resumable_connected_patch_enumeration.py`
- Erkennbare CLI-Argumente: `--config` ist required.
- Zweck laut Code/Kommentaren: Orbit-reduced / resumable connected patch enumeration; ein einzelner Lauf ist ein Chunk, ausser `enumeration_status == complete`.
- Output-Verhalten: schreibt in `cfg["run"]["output_dir"]` unter anderem Chunk Summary, Run Manifest, Warnings, resolved Config, Match Examples und Signature Counts.
- Risiko: startet echte Enumeration; ein einzelner Lauf ist chunk-orientiert und nicht automatisch ein Stage-3 Full-Replay-Certification-Lauf mit allen 11 Kandidaten, Detail-Reports und Claim Boundary.
- Eignung fuer Stage 3: potentially suitable after config clarification, aber nicht allein ausreichend.

### scripts/run_bms_fu02g5g_fu02g4c_raw_order_replay_certification.py

- Pfad: `scripts/run_bms_fu02g5g_fu02g4c_raw_order_replay_certification.py`
- Erkennbare CLI-Argumente: `--config` ist required.
- Zweck laut Code/Kommentaren: Recovery/Audit vorhandener FU02g4c Logs und Configs; prueft, ob g5e/g5f Kandidaten-Rohindices durch FU02g4c Fenster-/Log-Artefakte gestuetzt werden.
- Output-Verhalten: schreibt `summary.json`, `fu02g4c_log_inventory.csv`, `candidate_window_crosscheck.csv`, `candidate_replay_certification.csv`, `result_note.md`.
- Risiko: laut Code re-exekutiert der Runner den Original-Enumerator nicht; Scaffold-Indizes werden nicht still als FU02g4c raw-order Indizes behandelt. Er ist Recovery-/Support-Audit, nicht Full Raw-Order Coverage.
- Eignung fuer Stage 3: not suitable als alleiniger Stage-3 Full-Replay-Befehl; potentially useful als Audit-/Candidate-Table-Komponente.

### scripts/aggregate_bms_fu02g4c_chunk_outputs.py

- Pfad: `scripts/aggregate_bms_fu02g4c_chunk_outputs.py`
- Erkennbare CLI-Argumente: `--project-root`, wiederholbares `--log-dir`, `--out-dir`.
- Zweck laut Code/Kommentaren: Coverage and Log Audit fuer FU02g4c Chunk Outputs; parst Chunk-/Segment-Logs, klassifiziert Coverage-Ketten und schreibt Audit-Artefakte.
- Output-Verhalten: schreibt unter anderem `chunk_log_audit.csv`, `chunk_log_audit.json`, `coverage_intervals_primary.csv`, `coverage_gaps_primary.csv`, `aggregate_counts_primary.json` und eine Result Note in `--out-dir`.
- Risiko: aggregiert bestehende Logs, startet keinen Full Replay und prueft nicht selbst alle 11 Kandidaten per raw_index.
- Eignung fuer Stage 3: potentially suitable after config clarification als Coverage-Audit-Komponente, nicht als Full-Replay-Runner.

### scripts/run_bms_fu02g4c_remaining_chunks.sh

- Pfad: `scripts/run_bms_fu02g4c_remaining_chunks.sh`
- Erkennbare Nutzungsmuster: Umgebungsvariablen `REPO_ROOT`, `CONFIG_PATH`, `RUNNER_PATH`, `CHUNK_SIZE`, `START_SKIP`, `MAX_CHUNKS`, `LOG_DIR_REL`; Beispielaufruf `bash scripts/run_bms_fu02g4c_remaining_chunks.sh`.
- Zweck laut Kommentaren: Remaining chunk runner; aktiviert `.venv`, veraendert YAML-Config-Felder `chunk_id`, `skip_first_raw_patches`, `max_raw_patches_this_run`, startet den vorhandenen Enumerator und schreibt Logs unter `runs/BMS-FU02g4c/chunk_batch_logs/`.
- Risiko: veraendert die Original-Config, startet echte Enumeration und schreibt in bestehende FU02g4c-Strukturen. Das kollidiert mit Stage-3-Isolierung und Anker-/Output-Schutz.
- Eignung fuer Stage 3: not suitable fuer diese Gate-Ausfuehrung.

## 4. Command Construction

BLOCKED: Aus den vorhandenen Skripten ist kein eindeutig sicherer Stage-3 Full-Replay-Certification-Befehl ableitbar.

Nicht auszufuehrende, nur konzeptionelle Fragmente:

```bash
python scripts/run_bms_fu02g4c_orbit_reduced_resumable_connected_patch_enumeration.py \
  --config data/bms_fu02g4c_full_raw_order_replay_stage3_disabled_full_replay_config.yaml
```

Dieses Fragment ist nicht ausfuehrbar als Stage-3 Full Replay, weil die Stage-3 Config ein Gate-/Planungsformat ist und nicht nachgewiesen ist, dass sie der Enumerator-Config-Signatur entspricht. Ausserdem waere ein einzelner Enumerator-Lauf chunk-orientiert und wuerde nicht automatisch die Stage-3 Required Outputs erzeugen.

```bash
python scripts/run_bms_fu02g5g_fu02g4c_raw_order_replay_certification.py \
  --config data/bms_fu02g4c_full_raw_order_replay_stage3_disabled_full_replay_config.yaml
```

Dieses Fragment ist nicht ausfuehrbar als Stage-3 Full Replay, weil der g5g Runner einen Recovery-/Window-Audit durchfuehrt und laut Code nicht den Original-Enumerator re-exekutiert.

```bash
python scripts/aggregate_bms_fu02g4c_chunk_outputs.py \
  --out-dir runs/BMS-FU02g4c-full-replay/stage3_full_raw_order_replay_certification_001/coverage_audit
```

Dieses Fragment waere nur ein Aggregations-/Coverage-Audit ueber bestehende Logs, kein Full Replay.

Gruende fuer BLOCKED:

- Full raw-order coverage ist mit einem einzelnen vorhandenen Befehl nicht auditierbar.
- Der Enumerator ist chunk/resumable und kein kompletter Stage-3 Certification-Orchestrator.
- Der g5g Runner prueft Kandidaten-/Fenster-/Recovery-Tabellen und re-exekutiert den Enumerator nicht.
- Der Aggregator arbeitet auf vorhandenen Logs.
- Das Shell-Skript veraendert die FU02g4c Config und schreibt in bestehende FU02g4c Chunk-Log-Strukturen.
- Kein vorhandener Befehl erzeugt eindeutig alle Stage-3 Required Outputs im isolierten Output-Verzeichnis.
- Keine klare Trennung zwischen window/scaffold/full raw-order ist fuer einen einzelnen Stage-3 Befehl nachgewiesen.

## 5. Execution Gate Conditions

Stage 3 darf spaeter nur laufen, wenn:

- Ralf explizit Stage 3 freigibt.
- Befehl eindeutig dokumentiert ist.
- Output-Verzeichnis frisch und isoliert ist.
- keine FU02g4c-Ankeroutputs ueberschrieben werden.
- full raw-order coverage auditierbar ist.
- alle 11 Kandidaten geprueft werden.
- candidate_005 separat ausgewiesen wird.
- candidate_008 separat ausgewiesen wird.
- missing/additional candidates report erzeugt wird.
- `summary.json`, `readout.md`, `coverage_report.csv`, `candidate_replay_certification.csv`, `run_manifest.json` und `command_log.txt` erzeugt werden.
- Claim Boundary im `readout.md` steht.

## 6. BLOCKED Conditions

Stage 3 muss BLOCKED bleiben, wenn:

- kein eindeutig sicherer Full-Replay-Befehl ableitbar ist.
- ein Befehl nur window/scaffold/kandidatenbezogen arbeitet.
- coverage nicht vollstaendig oder nicht auditierbar ist.
- candidate_005 nicht separat behandelt wird.
- candidate_008 nicht separat behandelt wird.
- bestehende Outputs ueberschrieben wuerden.
- FU02g4c-Ankerdateien veraendert wuerden.
- Output-Verzeichnis bereits existiert und keine explizite Freigabe vorliegt.
- Claim Boundary nicht geschrieben wuerde.

## 7. Required Future Outputs

Ein spaeterer Stage-3 Full Replay muss mindestens erzeugen:

- summary.json
- readout.md
- coverage_report.csv
- candidate_replay_certification.csv
- missing_or_additional_candidates.csv
- candidate_005_detail.json
- candidate_008_detail.json
- run_manifest.json
- command_log.txt

## 8. Claim Boundary

Nach diesem Command Gate Plan erlaubt:

- Stage-3 command-construction / execution gate exists.
- Candidate_008 positive-control PASS is available as prerequisite.
- Stage-3 command safety and BLOCKED conditions are documented.

Nach diesem Command Gate Plan nicht erlaubt:

- Stage-3 Full Replay was executed.
- FU02g4c full raw-order replay certification is complete.
- all 11 candidates are raw-order certified.
- candidate_005 is exact.
- candidate_008 proves global non-genericity.
- near_distance=0 implies identity or isomorphism.

## 9. Naechster Schritt

Create a dedicated Stage-3 full-replay wrapper/runner specification.
