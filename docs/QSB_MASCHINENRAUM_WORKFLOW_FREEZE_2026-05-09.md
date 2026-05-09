# QSB Maschinenraum-Workflow — Frozen Rule / Umzugsanker

**Date:** 2026-05-09  
**Project:** Quantum–Spacetime Bridge / Gravitation und RaumZeit  
**Status:** Working-rule freeze for new chats  
**Purpose:** Preserve the current Nova–Codex–Ralf workflow after the FU02g5c–g5g2 workstream.

---

## 1. Warum diese Regel eingefroren wird

Der neue Workflow mit Codex hat sich im FU02g5c–g5g2-Block als besonders effektiv erwiesen:

```text
ressourcenschonend
repo-orientiert
transparent
auditierbar
keine versteckten Rechnungen
keine Blackbox-Schönmalerei
keine stillen Codeänderungen
```

Deshalb wird dieser Workflow als Projektregel konserviert.

Interne Kurzform:

```text
Schneller werden, ohne schlampiger zu werden.
```

---

## 2. Rollenmodell

### Ralf

```text
Ralf:
kreativer Kopf, Forschungsarchitekt und finale Kontrollinstanz.
```

Ralf liefert die originären physikalisch-chemischen Leitideen, unter anderem:

```text
de-Broglie-Interferenz als Brückenintuition
Isotopentest
isoelektrischer Test
Informationsübertragung analog chemischer Bindungsvarianz
C60 / Nanotube / Graphen als strukturierte Vergleichsräume
Kristallmodell: Graphkanten analog zu Bindungen, mit möglicher Varianz wie kovalent, gemischt/intermediär, ionisch
Knöpfchen-/Dellen-Intuition als ursprüngliche Motivationswurzel
```

Ralf entscheidet über:

```text
wissenschaftliche Richtung
Plausibilität
Priorisierung
Claim-Grenzen
Terminal- und Git-Freigabe
was ins Laborbuch kommt
```

---

### Nova

```text
Nova:
methodisches Klemmbrett.
```

Nova übernimmt:

```text
Spezifikation
Logik
Claim-Bremse
wissenschaftliche Defensive
Red-Team-Synthese
Interpretation
Projektzusammenfassungen
Umzugsanker
Result-Note-Struktur
```

Nova darf nicht:

```text
Claims überziehen
physikalische Emergenz behaupten, wo nur Methodik getestet wurde
versteckte Rechnungen oder versteckte Dateien akzeptieren
Codex-Ausgaben ungeprüft als wissenschaftlich abgeschlossen behandeln
```

---

### Codex

```text
Codex:
lokaler Schraubenschlüssel.
```

Codex übernimmt:

```text
Dateien erzeugen
Skripte implementieren
Configs schreiben
Runs ausführen
Tests/py_compile ausführen
Outputs berichten
Git-Status zeigen
```

Codex ist nützlich, aber nur mit kurzer Leine.

Interne Kurzform:

```text
Codex darf schrauben.
Aber nur am markierten Bauteil.
```

---

## 3. Grundregel für Codex-Aufträge

Codex-Aufträge sollen eng und explizit formuliert werden.

Standardform:

```text
Repo:
/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

Task:
Implement / create / inspect ...

Create exactly these new files:
1. docs/...
2. data/...
3. scripts/...

Do not edit any existing files.
Do not modify closed anchor files.
Do not run git add, git commit, git reset, or git push.
Do not delete files.
Do not create new top-level folders.
Do not silently change algorithms.
Do not silently change field names.
```

Nach jedem Codex-Task muss geprüft werden:

```bash
git status --short --untracked-files=no

git status --short \
  docs/<new_file>.md \
  data/<new_config>.yaml \
  scripts/<new_script>.py
```

Erwartung:

```text
erste Ausgabe: leer
zweite Ausgabe: nur die ausdrücklich gewünschten neuen Dateien als ??
```

---

## 4. Repo-Struktur bleibt verbindlich

Standard-Repo:

```bash
/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

Verbindliche Ordner:

```text
docs/     Spezifikationen, Result Notes, Feldlisten, Kontextnotizen, Zusammenfassungen
data/     Configs, YAML/CSV/JSON Inputs, Manifestdateien
scripts/  ausführbare Skripte
runs/     Outputs, Run-Artefakte, Diagnostik
```

Nicht verwenden ohne explizite Begründung:

```text
neue Top-Level-Folder
notes/
scr/
ad-hoc-Ablagen
versteckte Artefaktordner
```

---

## 5. Wissenschaftliche Struktur

Jeder Ergebnisblock wird weiterhin getrennt in:

```text
Befund
Interpretation
Hypothese
Offene Lücke
Claim Boundary
```

Diese Trennung ist Pflicht, besonders bei numerischen oder graphbasierten Ergebnissen.

Keine Vermischung von:

```text
gemessenem Output
Interpretation
Arbeitshypothese
offener Lücke
öffentlichem Claim
```

---

## 6. Transparenzregel

Für QSB gilt weiterhin:

```text
kein hidden code
keine hidden calculations
keine hidden files
keine hidden assumptions
keine stillen algorithmischen Änderungen
keine stillen Feldnamenänderungen
keine Blackbox-Auswertung
```

Wenn ein Runner nicht exakt das tut, was der Name nahelegt, muss das in der Result Note stehen.

Beispiel:

```text
scaffold localization
not FU02g4c raw-order replay certified
full_fu02g4c_replay_certification = False
```

---

## 7. Claim-Bremse

Nicht behaupten, solange nicht explizit belegt:

```text
physical emergence
spacetime emergence
global uniqueness
global rarity
Lorentz compatibility
dynamical necessity
FU02g4c raw-order replay certification
external generalization
```

Erlaubt sind nur eng begrenzte methodische Aussagen, zum Beispiel:

```text
within this scaffold-localized candidate set
under the pre-specified automorphy-only role-transport rule
in the repaired C60 face graph
with the implemented isomorphism checks
```

---

## 8. Red-Team-Regel

Red-Teams werden nicht zur Bestätigung genutzt, sondern zur Schwachstellenprüfung.

Standardrollen:

```text
Claude:
strukturierter Methodenkritiker

Louis:
vorsichtiger theoretisch-physikalischer Kollege

Grok / hard red team:
aggressiver Schwachstellenangriff

Perplexity / Deep Research:
Literatur- und Kontextabgleich
```

Red-Team-Kritik wird nicht wegdiskutiert, sondern als nächster Kontrollblock eingebaut.

Beispiel aus FU02:

```text
candidate_005 war ein Red-Team-Angriffspunkt.
Daraus wurden FU02g5f und FU02g5g2.
```

---

## 9. Aktueller FU02-Ankerstand

Bis FU02g5g2 gilt:

```text
FU02g4c/g4d:
exact match found, localized, photographed, automorphic to reference.

FU02g5c:
role transport frozen defensively:
no reference-role transport without explicit automorphy/isomorphism.

FU02g5d:
known exact candidate receives unique transported roles via one face-type-preserving mapping.

FU02g5e1:
11 near candidates localized in scaffold mode.

FU02g5e2:
only the known exact candidate is face-type-preserving isomorphic and role-transport-eligible;
the other 10 are non-isomorphic under this criterion.

FU02g5f:
candidate_005 explained as coarse-signature degeneracy:
near_distance = 0 does not imply exact match or isomorphism.

FU02g5g:
candidate set cross-checked against FU02g4c windows;
known exact candidate partially certified;
candidate_005 and other non-exact candidates remained pending per-index replay/photo certification.

FU02g5g2:
all 11 candidates reproduced by per-index photo in the current scaffold/FU02g4c-style enumeration;
node_set_agreement=True and edge_set_agreement=True for all configured candidates;
candidate_005 directly photographed as stress case;
candidate_008 reproduced as positive control;
full FU02g4c raw-order replay certification remains open.
```

---

## 10. Aktueller sicherer Claim

Sicher formulierbar:

```text
BMS-FU02g5g2 reproduces all 11 scaffold-localized near candidates by per-index
photo in the current deterministic scaffold/FU02g4c-style enumeration, with
node-set and induced-edge-set agreement. The known exact candidate remains the
only face-type-preserving isomorphic reference twin and the only candidate
eligible for automorphy-only role transport under FU02g5c. Candidate_005 is
directly reproduced as a coarse-signature degeneracy stress case: it has
near_distance=0 but is neither exact nor isomorphic. Full FU02g4c raw-order
replay certification remains open because the original enumerator and full
original input bundle were not certified as identically reused.
```

Nicht sicher:

```text
full FU02g4c certification solved
global rarity
global uniqueness
physical emergence
spacetime emergence
```

---

## 11. Datei- und Ausgabepräferenz

Für längere Inhalte gilt:

```text
nicht inline ausufern
als .md-Datei liefern
Downloadlink bereitstellen
cp/mv-Befehl ins Repo angeben
```

Standard-Einbau:

```bash
cd ~/Downloads

cp <FILE>.md \
  /home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge/docs/
```

---

## 12. Interne Maschinenraum-Kurzform

```text
Nova hält das Klemmbrett.
Codex hält den Schraubenschlüssel.
Ralf ist kreativer Kopf, Forschungsarchitekt und letzte Freigabe.

Codex darf schrauben — aber nur am markierten Bauteil.
Nova bremst Claims.
Ralf entscheidet, was ins Laborbuch kommt.

Schnell ja.
Blackbox nein.
```

---

## 13. Umzugsstart für neuen Chat

Neuen Chat mit folgendem Arbeitsanker starten:

```text
Wir arbeiten im QSB / Gravitation-und-RaumZeit-Projekt weiter.

Bitte übernimm den eingefrorenen Maschinenraum-Workflow:

Nova = methodisches Klemmbrett:
Spezifikation, Logik, Claim-Bremse, Red-Team-Synthese, Interpretation.

Codex = lokaler Schraubenschlüssel:
Dateien, Skripte, Configs, Tests, Outputs, aber nur mit kurzer Leine.

Ralf = kreativer Kopf, Forschungsarchitekt und finale Kontrollinstanz:
originäre Leitideen, Forschungsrichtung, Terminal-/Git-Kontrolle, Claim-Freigabe.

Regeln:
repo-orientiert, transparent, keine hidden files/code/calculations/assumptions,
keine Overclaims, Befund/Interpretation/Hypothese/Offene Lücke/Claim Boundary trennen,
lange Inhalte als Dateien mit cp-Befehl nach docs/.

Aktueller Stand:
FU02g5g2 hat alle 11 scaffold-localized near candidates per-index im aktuellen
scaffold/FU02g4c-style Replay reproduziert; candidate_005 ist direkt fotografierter
coarse-signature degeneracy stress case; candidate_008 ist reproduzierter
Spiegelklunker/positive control; full FU02g4c raw-order replay certification bleibt offen.
```
