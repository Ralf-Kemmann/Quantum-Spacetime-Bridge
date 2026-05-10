# QSB FU02g4c Stage 3 — Execution-Path Implementation Specification

**Date:** 2026-05-10  
**Project:** Quantum–Spacetime Bridge / Gravitation und RaumZeit  
**Block:** FU02g4c / C60 carrier-patch genericity control  
**Document role:** Implementation specification for a guarded Stage-3 execution-path runner  
**Intended repository location:** `docs/QSB_FU02G4C_STAGE3_IMPLEMENTATION_SPEC_2026-05-10.md`  
**Depends on:** `docs/QSB_FU02G4C_STAGE3_EXECUTION_PATH_SPEC_2026-05-10.md`

---

## 1. Ziel

Diese Spezifikation beschreibt den ersten kontrollierten Implementierungsschritt für FU02g4c Stage 3.

Ziel ist **nicht** der Full Raw-Order Replay. Ziel ist ein kleiner, prüfbarer, disabled-by-default Execution-Gate-Runner, der nachweist, dass der Stage-3-Ausführungspfad technisch sauber vorbereitet ist und bei fehlender Freigabe korrekt blockiert.

Der Runner soll:

1. eine Stage-3-Konfiguration laden,
2. Kandidatenrollen explizit prüfen,
3. die Execution-Gate-Logik auswerten,
4. einen negativen Gate-Test als erwartetes Verhalten dokumentieren,
5. ausschließlich unter `runs/` schreiben,
6. keine bestehenden FU02-Ankerdateien verändern,
7. keine wissenschaftliche Claim-Hochstufung erzeugen.

---

## 2. Nicht-Ziel

Dieser Implementierungsschritt ist ausdrücklich **kein**:

1. Full Raw-Order Replay,
2. Orbit-Zertifizierung,
3. globaler Nicht-Generizitätsnachweis,
4. Kandidatenentscheidung zwischen `candidate_008` und `candidate_005`,
5. Änderung geschlossener FU02-Ankerdateien,
6. Repo-Reorganisation,
7. stiller Übergang von Dry-Run zu echter Ausführung.

Stage 3 bleibt in diesem Schritt: **execution_path_only**.

---

## 3. Zu erstellende Dateien

Codex darf in diesem Schritt nur die folgenden Dateien erstellen, falls sie noch nicht existieren:

```text
scripts/fu02g4c_stage3_execution_gate_runner.py
data/fu02g4c_stage3_execution_gate_config.yaml
```

Falls eine der Dateien bereits existiert, darf Codex sie **nicht eigenmächtig überschreiben**, sondern muss den vorhandenen Zustand melden und eine Rückfrage bzw. einen Änderungsvorschlag liefern.

---

## 4. Verbotene Aktionen

Codex darf nicht:

1. bestehende FU02-Ankerdateien ändern,
2. Dateien löschen,
3. neue Top-Level-Ordner erzeugen,
4. `git add`, `git commit`, `git reset` oder `git push` ausführen,
5. Full-Replay-Logik starten,
6. stillschweigend alternative Input-Dateien verwenden,
7. `candidate_005` als Reference-Smoke-Kandidat behandeln,
8. erfolgreiche Gate-Tests als Zertifizierung formulieren.

---

## 5. Default-Konfiguration

Die YAML-Konfiguration muss disabled-by-default sein.

```yaml
stage_id: FU02g4c_stage3
candidate_id: candidate_008
expected_reference_candidate: candidate_008
degeneracy_stress_candidate: candidate_005
execution_enabled: false
dry_run: true
allow_anchor_mutation: false
claim_mode: execution_path_only
run_label: stage3_execution_gate_dry_run
output_dir: runs/FU02g4c_stage3_execution_gate_dry_run
command_template: "python scripts/fu02g4c_stage3_execution_gate_runner.py --config data/fu02g4c_stage3_execution_gate_config.yaml --dry-run"
```

---

## 6. Konfigurationsfelder

| Field name | Field type | Field description |
|---|---:|---|
| `stage_id` | string | Workflow-Stage; erwarteter Wert: `FU02g4c_stage3`. |
| `candidate_id` | string | Kandidat für den aktuellen Gate-Test; Default: `candidate_008`. |
| `expected_reference_candidate` | string | Referenzkandidat des Reference-Smoke-Pfads; muss `candidate_008` sein. |
| `degeneracy_stress_candidate` | string | Degeneracy-Stressfall; muss `candidate_005` sein. |
| `execution_enabled` | boolean | Harte Ausführungsfreigabe; Default und Pflicht in Erstfassung: `false`. |
| `dry_run` | boolean | Dry-run-Schalter; Default: `true`. |
| `allow_anchor_mutation` | boolean | Schutz gegen Änderung geschlossener FU02-Anker; Default: `false`. |
| `claim_mode` | string | Claim-Grenze; in diesem Schritt ausschließlich `execution_path_only`. |
| `run_label` | string | Lesbarer Laufname für Reports und Manifeste. |
| `output_dir` | path/string | Zielverzeichnis unter `runs/`; keine Top-Level-Ausgabe. |
| `command_template` | string | Dokumentierte Kommandozeile bzw. Kommando-Vorlage. |

---

## 7. Runner-Verhalten

Der Runner soll als kleine, transparente Prüfkomponente implementiert werden.

### 7.1 CLI

Minimal erwarteter Aufruf:

```bash
python scripts/fu02g4c_stage3_execution_gate_runner.py \
  --config data/fu02g4c_stage3_execution_gate_config.yaml \
  --dry-run
```

Optional darf ein `--output-dir`-Argument unterstützt werden. Wenn es unterstützt wird, muss es weiterhin unter `runs/` liegen.

### 7.2 Ablauf

Der Runner soll folgende Schritte ausführen:

1. Repository-Root bestimmen.
2. Konfigurationsdatei laden.
3. Pflichtfelder validieren.
4. Kandidatenrollen prüfen.
5. Claim-Modus prüfen.
6. Output-Verzeichnis unter `runs/` anlegen.
7. Execution-Gate auswerten.
8. Gate-Report schreiben.
9. Command-Manifest schreiben.
10. Input-Manifest schreiben.
11. Output-Manifest schreiben.
12. Markdown-Readout schreiben.
13. Exit-Code setzen.

---

## 8. Gate-Logik

### 8.1 Erwarteter negativer Gate-Fall

Für die Default-Konfiguration gilt:

```yaml
execution_enabled: false
dry_run: true
allow_anchor_mutation: false
claim_mode: execution_path_only
```

Erwartetes Ergebnis:

```text
stage3_negative_execution_gate_pass
```

Der Runner muss klar dokumentieren, dass die echte Ausführung blockiert wurde und dass diese Blockade in diesem Schritt ein erwarteter PASS ist.

### 8.2 Verbotene echte Ausführung

Wenn `execution_enabled: false`, darf keine echte Replay-Logik ausgeführt werden.

Falls irgendein Codepfad dennoch versucht, echte Ausführung zu starten, muss der Runner mit einem Fehlerstatus abbrechen:

```text
stage3_unexpected_execution_fail
```

### 8.3 Positive Gate-Reserve

Eine positive Gate-Öffnung wird in dieser Implementierung höchstens als logisch erkannter, aber nicht voll genutzter Zustand vorgesehen. Sie wird nicht zur Full-Replay-Ausführung verwendet.

Für später wäre mindestens erforderlich:

```yaml
execution_enabled: true
dry_run: false
allow_anchor_mutation: false
claim_mode: execution_path_only
```

Auch dann bleibt Anchor-Mutation verboten.

---

## 9. Statuslabels

| Field name | Field type | Field description |
|---|---:|---|
| `stage3_negative_execution_gate_pass` | string/status | Defaultfall: Execution blockiert korrekt, PASS für Gate-Verhalten. |
| `stage3_dry_run_gate_behavior_pass` | string/status | Dry-run validiert Konfiguration, Pfad und Reports ohne echte Replay-Ausführung. |
| `stage3_execution_blocked_by_gate` | string/status | Blockierter Execution-Status; korrekt, wenn `execution_enabled=false`. |
| `stage3_unexpected_execution_fail` | string/status | Fehler: echte Ausführung trotz geschlossener Gate-Logik. |
| `stage3_anchor_mutation_fail` | string/status | Fehler: geschlossene Anchor-Datei wurde verändert oder Mutation erlaubt. |
| `stage3_candidate_role_confusion_fail` | string/status | Fehler: Kandidatenrollen wurden verwechselt. |
| `stage3_claim_boundary_fail` | string/status | Fehler: Readout impliziert Certification oder globalen Claim. |
| `stage3_output_location_fail` | string/status | Fehler: Output außerhalb erlaubter Repo-Struktur. |
| `stage3_missing_required_field_fail` | string/status | Fehler: Pflichtfeld fehlt in der YAML-Konfiguration. |
| `stage3_hidden_fallback_fail` | string/status | Fehler: fehlender Input wurde still ersetzt. |

---

## 10. Output-Dateien

Der Default-Lauf soll unter diesem Verzeichnis schreiben:

```text
runs/FU02g4c_stage3_execution_gate_dry_run/
```

Erwartete Dateien:

```text
stage3_execution_gate_report.json
stage3_execution_gate_report.md
stage3_command_manifest.txt
stage3_input_manifest.json
stage3_output_manifest.json
```

---

## 11. Output-Felder

### 11.1 `stage3_execution_gate_report.json`

| Field name | Field type | Field description |
|---|---:|---|
| `stage_id` | string | Stage-Kennung aus der Konfiguration. |
| `run_label` | string | Laufname aus der Konfiguration. |
| `candidate_id` | string | Aktuell getesteter Kandidat. |
| `expected_reference_candidate` | string | Erwarteter Reference-Smoke-Kandidat. |
| `degeneracy_stress_candidate` | string | Degeneracy-Stresskandidat. |
| `execution_enabled` | boolean | Wert des Execution-Gates. |
| `dry_run` | boolean | Dry-run-Status. |
| `allow_anchor_mutation` | boolean | Anchor-Mutation-Schalter. |
| `claim_mode` | string | Claim-Modus. |
| `gate_decision` | string | Gate-Entscheidung, z. B. `blocked`. |
| `status_label` | string | Maschinenlesbarer PASS/FAIL/blocked-Status. |
| `is_pass` | boolean | Ob der Gate-Test als PASS gilt. |
| `is_certification` | boolean | Muss in dieser Stufe `false` sein. |
| `full_replay_executed` | boolean | Muss in dieser Stufe `false` sein. |
| `anchor_mutation_performed` | boolean | Muss `false` sein. |
| `created_at_utc` | string | ISO-Zeitstempel der Reporterzeugung. |
| `claim_boundary` | string | Kurzer Claim-Boundary-Satz. |

### 11.2 `stage3_input_manifest.json`

| Field name | Field type | Field description |
|---|---:|---|
| `config_path` | path/string | Geladene YAML-Konfiguration. |
| `repo_root` | path/string | Erkannter Repository-Root. |
| `candidate_id` | string | Aktueller Kandidat. |
| `reference_candidate_role` | string | Kandidatenrolle für Reference-Smoke. |
| `degeneracy_candidate_role` | string | Kandidatenrolle für Degeneracy-Stress. |
| `input_files_checked` | list[string] | Liste explizit geprüfter Eingaben. |
| `hidden_fallback_used` | boolean | Muss `false` sein. |

### 11.3 `stage3_output_manifest.json`

| Field name | Field type | Field description |
|---|---:|---|
| `output_dir` | path/string | Laufverzeichnis unter `runs/`. |
| `files_written` | list[string] | Explizit geschriebene Dateien. |
| `files_modified_outside_output_dir` | list[string] | Muss leer sein. |
| `anchor_files_modified` | list[string] | Muss leer sein. |
| `top_level_dirs_created` | list[string] | Muss leer sein. |

---

## 12. Markdown-Readout-Struktur

`stage3_execution_gate_report.md` muss diese Abschnitte enthalten:

```markdown
# FU02g4c Stage 3 — Execution Gate Report

## Befund

## Interpretation

## Hypothese

## Offene Lücke

## Claim Boundary
```

Pflichtinhalt Claim Boundary:

```text
This Stage-3 result only validates the guarded execution path or gate behavior. It does not constitute a full raw-order replay, a full certification, or evidence for global non-genericity.
```

---

## 13. Minimaltests

Codex soll nach Erstellung mindestens diese Checks ausführen:

```bash
python scripts/fu02g4c_stage3_execution_gate_runner.py \
  --config data/fu02g4c_stage3_execution_gate_config.yaml \
  --dry-run

python -m py_compile scripts/fu02g4c_stage3_execution_gate_runner.py

git status --short
```

Der erste Lauf muss einen blockierten Gate-Zustand als erwarteten PASS erzeugen.

---

## 14. Erwartete Konsolenausgabe

Die Konsolenausgabe soll kurz und eindeutig sein, z. B.:

```text
FU02g4c Stage 3 execution gate runner
config: data/fu02g4c_stage3_execution_gate_config.yaml
output_dir: runs/FU02g4c_stage3_execution_gate_dry_run
gate_decision: blocked
status_label: stage3_negative_execution_gate_pass
full_replay_executed: false
is_certification: false
```

---

## 15. Minimaler Codex-Auftrag

```text
Create the FU02g4c Stage-3 execution-path gate implementation exactly as specified in docs/QSB_FU02G4C_STAGE3_IMPLEMENTATION_SPEC_2026-05-10.md.

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

The runner must write explicit reports under runs/FU02g4c_stage3_execution_gate_dry_run/ and must treat blocked execution under execution_enabled=false as the expected negative gate PASS.

Run these checks:
- python scripts/fu02g4c_stage3_execution_gate_runner.py --config data/fu02g4c_stage3_execution_gate_config.yaml --dry-run
- python -m py_compile scripts/fu02g4c_stage3_execution_gate_runner.py
- git status --short

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

## 16. Zulässiger Claim nach diesem Schritt

Nach erfolgreicher Implementierung und Dry-run-Ausführung ist nur folgender Claim zulässig:

> The FU02g4c Stage-3 execution gate path has been implemented and dry-run checked. The negative execution gate blocks real replay execution as intended. This is not a full raw-order replay, not a certification, and not evidence for global non-genericity.

Nicht zulässig bleiben:

1. `FU02g4c is certified`,
2. `candidate_008 proves non-genericity`,
3. `candidate_005 is resolved`,
4. `full replay completed`,
5. `C60 carrier patch is globally non-generic`.

---

## 17. Offene Punkte

1. Nach Codex-Lauf muss geprüft werden, ob bereits vorhandene Stage-3-Scaffold-Dateien existieren.
2. Falls vorhandene Runner-Dateien existieren, darf nicht ungefragt überschrieben werden.
3. Der positive Execution-Gate-Pfad bleibt für einen späteren, expliziten Block reserviert.
4. Die Full-Replay-Ausführung bleibt geschlossen, bis Ralf sie separat freigibt.
