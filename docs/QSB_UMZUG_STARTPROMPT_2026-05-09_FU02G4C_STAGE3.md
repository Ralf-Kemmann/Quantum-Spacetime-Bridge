# QSB Umzug Startprompt – FU02g4c Stage-3 Gate/Scaffold

**Datum:** 2026-05-09  
**Projekt:** QSB / Gravitation und RaumZeit  
**Repo:** `~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge`  
**Aktueller HEAD:** `a5fb658 Add FU02g4c stage3 gate status handoff`

Wir arbeiten im QSB / Gravitation-und-RaumZeit-Projekt weiter.

Bitte übernimm den eingefrorenen Maschinenraum-Workflow:

- **Nova = methodisches Klemmbrett**: Spezifikation, Logik, Claim-Bremse, Red-Team-Synthese, Interpretation.
- **Codex = lokaler Schraubenschlüssel**: Dateien, Skripte, Configs, Tests, Outputs, aber nur mit kurzer Leine.
- **Ralf = kreativer Kopf, Forschungsarchitekt und finale Kontrollinstanz**: originäre Leitideen, Forschungsrichtung, Terminal-/Git-Kontrolle, Claim-Freigabe.

## Projektregeln

- repo-orientiert und transparent arbeiten
- keine hidden files, hidden code, hidden calculations oder hidden assumptions
- keine Overclaims
- Befund / Interpretation / Hypothese / Offene Lücke / Claim Boundary trennen
- lange Inhalte als Dateien mit konkretem `cp`-Befehl nach `docs/`
- keine bestehenden Dateien ändern, wenn nicht explizit freigegeben
- keine Top-Level-Ordner erzeugen
- kein `git add .`
- kein `git commit`, `git reset`, `git push` durch Codex
- FU02-Ankerdateien nicht verändern
- bestehende Outputs nicht überschreiben
- `runs/` ist Maschinenraum; repo-sichtbare Resultate gehören zusätzlich als Result Note nach `docs/`

## Aktueller Stand

FU02g4c Full Raw-Order Replay ist noch nicht ausgeführt.

Versiegelt ist:

- Stage 0 input-path validation: `PASS`
- Stage 1 disabled run config: vorhanden
- Stage 2 `candidate_008` reference smoke check: `PASS`
- Stage 3 command gate: `BLOCKED`
- Stage 3 disabled full-replay config: vorhanden
- Stage 3 wrapper/runner spec: vorhanden
- Stage 3 wrapper scaffold: vorhanden, disabled-by-default
- Stage 3 dry-run gate: `DRY_RUN_READY`
- Stage 3 negative execution gate: `BLOCKED as intended`
- Stage 3 gate status handoff: committed

## Claim Boundary

Noch nicht passiert:

- FU02g4c Full Raw-Order Replay wurde nicht ausgeführt.
- Full Certification ist nicht abgeschlossen.
- Alle 11 Kandidaten sind nicht raw-order certified.
- `candidate_005` ist nicht exact.
- `candidate_008` bleibt Positive-Control und ist kein Full-Coverage-Beweis.
- `near_distance=0` bedeutet nicht Identität oder Isomorphie.
- globale Nicht-Generizität ist nicht gezeigt.

## Nächster sinnvoller Block

Nur nach expliziter Ralf-Freigabe:

**Stage-3 execution-path implementation specification**

Nicht direkt Full Replay starten.
