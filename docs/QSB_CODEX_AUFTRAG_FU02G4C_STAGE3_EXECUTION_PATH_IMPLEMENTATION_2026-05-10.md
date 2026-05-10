# QSB Codex-Auftrag — FU02g4c Stage 3 Execution Path Implementation

Date: 2026-05-10  
Scope: C60 / FU02g4c Stage 3  
Mode: Maschinenraum, short leash, disabled-by-default

## Ziel

Implementiere den ausführbaren Stage-3-Pfad als eng begrenzten Scaffold.

Stage 3 darf nur zeigen, dass der Execution Path technisch kontrolliert erreichbar ist und dass das negative Execution Gate korrekt blockiert, solange die Stage-3-Ausführung nicht explizit aktiviert wurde.

## Nicht-Ziel

Nicht ausführen:

- kein Full Raw-Order Replay
- keine Full Certification
- keine globale Nicht-Generizität behaupten
- keine bestehenden FU02-Anchor-Dateien ändern
- keine geschlossenen Dateien anfassen
- keine Git-Operationen ausführen: kein add, commit, reset, push
- keine Top-Level-Ordner erzeugen
- keine Dateien löschen

## Arbeitsbasis

Bitte zuerst lesen:

- `docs/QSB_FU02G4C_STAGE3_EXECUTION_PATH_SPEC_2026-05-10.md`
- `docs/QSB_FU02G4C_STAGE3_IMPLEMENTATION_SPEC_2026-05-10.md`
- vorhandene FU02g4c Stage-0/1/2/3 Scaffold-Dateien im Repo

Bekannte Statusgrenzen:

- Stage 0: PASS
- Stage 1: disabled config vorhanden
- Stage 2: `candidate_008` Reference-Smoke PASS
- Stage 3: Scaffold vorhanden, dry-run ready, negative execution gate blockiert korrekt
- `candidate_005`: Degeneracy-Stressfall
- Full Raw-Order Replay: nicht ausgeführt

## Erlaubte Änderungen

Erstelle nur die minimal notwendigen neuen Dateien oder eng begrenzten Runner-/Config-Ergänzungen für Stage 3.

Zielstruktur:

- Config unter `data/`
- ausführbarer Runner unter `scripts/`
- Laufartefakte ausschließlich unter `runs/`
- kurze Readout-/Manifest-Dateien im jeweiligen `runs/`-Unterordner

Bestehende Dateien nur ändern, wenn es für die Stage-3-Execution-Path-Implementierung zwingend nötig ist. Jede Änderung einzeln begründen.

## Required behavior

Der Runner muss mindestens zwei Modi sauber trennen:

### 1. Negative gate / default mode

Default bleibt disabled.

Erwartung:

- Runner startet kontrolliert
- erkennt disabled Stage-3-Ausführung
- schreibt einen negativen Gate-Readout
- beendet ohne Replay
- Status muss sinngemäß sein: `execution_gate_blocked_as_expected`

### 2. Dry-run / path-validation mode

Dry-run darf den Pfad prüfen, aber keine Replay-Arbeit starten.

Erwartung:

- Inputs werden validiert
- candidate IDs werden sichtbar geloggt
- `candidate_008` bleibt Reference-Smoke-Kontext
- `candidate_005` bleibt Degeneracy-Stressfall
- keine Certification
- kein Full Replay
- Status muss sinngemäß sein: `dry_run_path_validated`

## Required outputs

Unter `runs/` soll ein Stage-3-Unterordner entstehen, der mindestens enthält:

- `readout.md`
- `summary.json`
- optional `manifest.json`

Readout muss die Abschnitte enthalten:

- Befund
- Interpretation
- Hypothese
- Offene Lücke
- Claim Boundary

## Tests / checks

Führe nur sichere, kurze Checks aus:

- Syntax-/Importcheck für neue oder geänderte Python-Dateien
- negativer Gate-Test
- Dry-run-Test, falls vollständig safe und disabled-by-default-konform

Keine langen Enumerationen starten.

## Reporting

Am Ende bitte berichten:

1. `git status --short`
2. erstellte Dateien
3. geänderte Dateien
4. ausgeführte Befehle
5. erzeugte Outputs
6. Checks und Ergebnis
7. Limitations / nicht ausgeführte Dinge

## Claim Boundary für alle Ausgaben

Nur sagen:

Stage 3 validates a controlled execution path scaffold.

Nicht sagen:

- Stage 3 certifies FU02g4c
- Full Raw-Order Replay has been executed
- C60 carrier regions are globally non-generic
- candidate_008 is fully certified
