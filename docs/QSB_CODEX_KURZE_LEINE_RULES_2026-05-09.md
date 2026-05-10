# QSB Codex-Regeln – Kurze Leine

**Datum:** 2026-05-09  
**Projekt:** QSB / Gravitation und RaumZeit

## Grundsatz

Codex ist der lokale Schraubenschlüssel, nicht der Forschungsarchitekt.

Codex führt genau die spezifizierte Aufgabe aus und meldet danach:

- Dateien erstellt
- Dateien geändert
- Commands run
- Tests/checks
- Outputs
- Limitations
- `git status --short`

## Immer verboten ohne explizite Freigabe

- bestehende Dateien ändern
- bestehende Skripte ändern
- bestehende Configs ändern
- Dateien löschen
- Top-Level-Ordner erzeugen
- `git add .`
- `git commit`
- `git reset`
- `git push`
- FU02-Ankerdateien verändern
- bestehende Outputs überschreiben
- lange Enumeration-/Replay-Läufe starten
- Full Replay starten
- Full Certification behaupten

## Erlaubt, wenn ausdrücklich beauftragt

- genau eine neue Datei erstellen
- genau ein neues Skript erstellen
- genau eine neue Config erstellen
- read-only Inspektion
- YAML/JSON/CSV Header-Checks
- `py_compile`
- `--help`
- `sed -n`
- gezielter `git status --short`
- kleine Dry-Run-Gate-Checks, wenn explizit freigegeben

## Output-Regeln

Bei `runs/`-Outputs:

- `runs/` kann durch `.gitignore` ignoriert sein
- Resultate aus `runs/` müssen bei Relevanz zusätzlich in `docs/` als Result Note dokumentiert werden
- keine alten `runs/`-Outputs überschreiben, wenn nicht ausdrücklich freigegeben
- bei Output-Kollision lieber BLOCKED melden

## Stage-3-spezifische Sperren

Für FU02g4c Stage 3 gilt:

- kein Full Replay ohne explizite Ralf-Freigabe
- kein unbounded Enumerator
- keine FU02g4c-Ankeroutputs beschreiben
- keine Window-/Scaffold-Checks als Full Raw-Order Coverage ausgeben
- `candidate_005` separat schützen
- `candidate_008` separat als Positive-Control behandeln
- bei unklarem Command: BLOCKED melden

## Erwartete Abschlussmeldung

Codex soll knapp in dieser Form melden:

A) Befund  
B) Interpretation  
C) Offene Lücke  
D) Claim Boundary  
E) Nächster vorgeschlagener Schritt  
F) git status --short / Dateien / Commands
