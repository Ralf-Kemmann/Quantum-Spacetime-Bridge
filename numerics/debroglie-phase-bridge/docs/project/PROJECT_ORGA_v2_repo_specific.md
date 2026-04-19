# PROJECT_ORGA.md
## Gravitation und RaumZeit — Organisations- und Arbeitsstruktur (Version 2, repo-spezifisch)

### Version
2026-03-30

---

## 1. Zweck

Dieses Dokument beschreibt die **konkret auf das bestehende Repo zugeschnittene** Organisations- und Arbeitsstruktur des Projekts.

Ziel ist:

- die **bewährte reale Repo-Struktur** beizubehalten
- keine unnötigen Umzüge oder Totalumbauten zu erzwingen
- Forschungsraum, Werkbank, Recherche und Gegenprüfung klar zu trennen
- den Projektfluss auch bei Chat-Überlastung stabil zu halten
- Masterchat, Reviews und aktive Arbeitsblöcke sauber in die vorhandene Struktur einzubetten

Leitgedanke:

> Physik führt, Werkzeuge dienen.

---

## 2. Grundprinzip

Die vorhandene Struktur ist bereits in weiten Teilen tragfähig.  
Deshalb gilt ab jetzt ausdrücklich:

> **Die bestehende operative Repo-Struktur bleibt der Kern des Projekts.**

Es wird **kein künstlicher Komplettumbau** erzwungen.  
Stattdessen wird die vorhandene Struktur **offiziell gemappt** und nur dort ergänzt, wo Ordnung und Stabilität klar gewinnen.

---

## 3. Reale Kernstruktur des Projekts

Die aktuelle Struktur zeigt bereits mehrere funktionale Räume:

```text
project_root/
├── archive/
├── configs/
├── data/
├── docs/
├── m33_v0_scaffold/
├── notebooks/
├── results/
├── scripts/
├── src/
├── tests/
└── .venv/
```

Diese Struktur wird wie folgt gelesen.

### 3.1 Stabiler Stamm

Der stabile Stamm des Projekts liegt in:

- `src/dpb/`
- `scripts/`
- `configs/`
- `tests/`

Bedeutung:

- `src/dpb/`  
  produktiver Paket-/Bibliothekskern

- `scripts/`  
  operative Skripte, historische und produktive Laufroutinen

- `configs/`  
  globale Konfigurationen, Referenzen, Nullmodelle, Experimente

- `tests/`  
  formale Tests für Kernkomponenten

### 3.2 Aktive Audit-Werkbank

Die aktive Werkbank für neue Audit- und Runner-Blöcke liegt in:

- `m33_v0_scaffold/`

mit den Unterräumen:

- `m33_v0_scaffold/src/`
- `m33_v0_scaffold/configs/`
- `m33_v0_scaffold/scripts/`
- `m33_v0_scaffold/runs/`

Diese Struktur ist **der bevorzugte Ort für neue Blockarbeit** wie:

- M.3.9a.1
- M.3.9a.2
- Folgeblöcke im Audit-/Branch-/Dispersion-Strang

### 3.3 Dokumentationsraum

Die Dokumentation liegt bereits sinnvoll in:

- `docs/project/`
- `docs/reviews/`
- `docs/theory/`

Diese Struktur wird **offiziell übernommen** und nicht ersetzt.

### 3.4 Evidenzräume

Es existieren zwei Evidenzräume:

- `runs/`
- `results/`

Diese werden **nicht gewaltsam zusammengeführt**.

Stattdessen gilt:

- `runs/`  
  bevorzugter Output-Raum neuer strukturierter Auditblöcke und Runnerläufe

- `results/`  
  historisch gewachsener Ergebnisraum, publikationsnahe Resultate, ältere oder phänomenspezifische Ergebnisbäume

### 3.5 Weitere Räume

- `archive/`  
  Altlasten, stillgelegte oder frühere Stände

- `data/`  
  Rohdaten, Zwischenstände, verarbeitete Daten

- `notebooks/`  
  explorative und publikationsnahe Notebook-Arbeit

- `.venv/`  
  lokale Laufumgebung

---

## 4. Offizielle Funktionszuordnung der echten Ordner

### 4.1 Forschungsraum / Nova

Der Forschungsraum arbeitet primär in:

- `docs/project/`
- `docs/theory/`

Hierhin gehören:

- Masterchat
- Projektregeln
- Workflow-Dokumente
- Theorieblöcke
- Begriffsarbeit
- Milestones
- physikalische Lesarten
- strategische Synthesen

### 4.2 Gegnerraum / Reviews

Der Gegnerraum arbeitet primär in:

- `docs/reviews/`

Hierhin gehören:

- Claude / Team-Red
- Deep-Research-Auswertungen
- Perplexity- oder andere externe Rückmeldungen
- eigene Reaktionsnotizen
- Review-Synthesen

### 4.3 Werkbank / Codex

Die Werkbank arbeitet primär in:

- `m33_v0_scaffold/src/`
- `m33_v0_scaffold/configs/`
- `m33_v0_scaffold/scripts/`
- `m33_v0_scaffold/runs/`

Das ist die bevorzugte aktive Umgebung für neue Auditblöcke und laufende Implementierung.

### 4.4 Stabiler Produktivkern

Der stabile Produktivkern bleibt:

- `src/dpb/`
- `scripts/`
- `configs/`
- `tests/`

Er wird nicht ohne guten Grund durch jede neue Audit-Idee umgebaut.

---

## 5. Rollen und Tools

### 5.1 Nova / Forschungsraum

Nova ist die konzeptionelle Leitstelle.

Im Forschungsraum bleiben:

- Physik
- Mechanismusfragen
- Begriffsarbeit
- Pflichtenhefte
- Runner-Spezifikationen
- Masterchat
- Befund vs. Deutung
- Synthese
- Priorisierung
- Entscheidung über nächste Schritte

Nova ist **nicht** die primäre Repo-Werkbank.

### 5.2 Codex / Werkbank

Codex ist die bevorzugte technische Werkbank.

Codex übernimmt:

- Runner-Implementierung
- YAML-Konfigurationen
- Bootstrap-Skripte
- Refactoring
- Tests
- Diffs
- Repo-Navigation
- strukturierte Ausgaben

Festlegung für dieses Projekt:

> **VS Code mit Codex IDE Extension ist die Standard-IDE.**

Codex arbeitet bevorzugt in:

- `m33_v0_scaffold/` für aktive neue Blöcke
- `src/dpb/` nur dann, wenn klar ist, dass die Änderung den stabilen Kern betrifft

### 5.3 Deep Research / Recherche- und Aufklärungsraum

Deep Research wird fest genutzt für:

- Literaturrecherche
- Standardverfahren
- Referenzfamilien
- Vergleich mit Standardphysik
- bekannte Modellklassen
- Gegenargumente
- theoretische Baukästen
- Vorstrukturierung externer Testfelder

Deep Research sammelt und strukturiert.  
Die physikalische Bewertung erfolgt anschließend im Forschungsraum.

### 5.4 Claude / Team-Red / Gegnerraum

Claude wird als kritischer Gegenprüfer genutzt für:

- skeptische Reviews
- Overclaiming-Prüfung
- Konstruktionsbias-Kritik
- Falsifikationsdruck
- methodische Nachschärfung
- stärkere Testvorschläge

---

## 6. Dokumentationsstruktur in `docs/`

### 6.1 `docs/project/`

Dies ist der offizielle Leitstandraum für Projektdokumente.

Ist-Zustand:

```text
docs/project/
├── CHANGELOG_PROJECT.md
├── MASTERCHAT_CANONICAL.md
├── PROJECT_NORMS.md
└── WORKFLOW.md
```

Empfohlene Ergänzung:

```text
docs/project/
├── CHANGELOG_PROJECT.md
├── MASTERCHAT_CANONICAL.md
├── PROJECT_NORMS.md
├── PROJECT_ORGA.md
├── WORKFLOW.md
└── WORKFLOW_ACTIVE_BLOCK.md
```

Bedeutung:

- `MASTERCHAT_CANONICAL.md`  
  kanonischer Masterchat / zentraler Projektstand

- `PROJECT_NORMS.md`  
  feste Projektregeln, Schreibweise, Arbeitsprinzipien

- `WORKFLOW.md`  
  allgemeiner Workflow des Projekts

- `PROJECT_ORGA.md`  
  dieses Dokument: Rollen, Räume, Toolstruktur, echte Ordnerlogik

- `WORKFLOW_ACTIVE_BLOCK.md`  
  nur der aktuell laufende Block mit:
  - Ziel
  - Nicht-Ziel
  - Runner
  - Config
  - Outputs
  - offene Punkte
  - nächstem Schritt

### 6.2 `docs/reviews/`

Ist-Zustand:

```text
docs/reviews/
├── claude_redteam.md
├── perplexity_feedback.md
└── response_notes.md
```

Diese Struktur ist brauchbar und kann zunächst so bleiben.

Optional spätere Unterteilung:

```text
docs/reviews/
├── claude/
├── deep_research/
├── perplexity/
└── response_notes/
```

Nur wenn das Volumen steigt; kein Muss für jetzt.

### 6.3 `docs/theory/`

Dieser Ordner ist der Theoriebaukasten des Projekts.

Hierhin gehören:

- Axiome / Definitionen
- Spezifitätstests
- Massen-/Zeit-Blöcke
- Kraftblöcke
- Referenzimplementationen
- Metrikstatus
- Theta-Map-Logik
- später:
  - minimaler dynamischer Kern
  - Operator-/Spektralsprache
  - Streu-/Transportandockung
  - Floquet-/Spektralflussideen

---

## 7. Masterchat-Regelung

### 7.1 Offizielle Regel

Der Masterchat lebt primär in:

- `docs/project/MASTERCHAT_CANONICAL.md`

Optional können zusätzlich Sicherungskopien oder Versionssnapshots separat abgelegt werden.  
Aber **die kanonische Arbeitsreferenz** bleibt im `docs/project/`-Raum.

### 7.2 Ziel

So wird vermieden, dass Masterchat und Projektorga aus dem Dokumentationskern herauswandern und bei Chatwechseln unauffindbar werden.

---

## 8. Werkbank-Regelung für `m33_v0_scaffold/`

### 8.1 Status

`m33_v0_scaffold/` ist offiziell die **aktive Audit-Werkbank**.

Das gilt insbesondere für:

- neue Runner
- neue Auditblöcke
- Familien-/Branch-/Dispersion-Experimente
- Bootstrap-Skripte
- blocknahe Configs
- blocknahe Läufe

### 8.2 Konsequenz

Neue Blöcke wie:
- `m39a_family_full_audit_runner.py`
- `config_m39a_family_full_audit.yaml`
- passende Bootstrap-Skripte

gehören bevorzugt nach:

- `m33_v0_scaffold/src/`
- `m33_v0_scaffold/configs/`
- `m33_v0_scaffold/scripts/`

nicht sofort in den stabilen Produktivkern.

### 8.3 Vorteil

So bleibt:

- der Produktivkern stabil
- die Werkbank beweglich
- neue Blöcke testbar
- Codex-Arbeit klar lokalisiert

---

## 9. Evidenzräume: `runs/` und `results/`

### 9.1 `m33_v0_scaffold/runs/`

Dieser Bereich ist der bevorzugte Laufraum für neue Auditblöcke aus der Werkbank.

### 9.2 Top-Level `results/`

Dieser Bereich bleibt bestehen als historischer und publikationsnaher Ergebnisraum.

### 9.3 Regel

- **Neue strukturierte Auditläufe** bevorzugt nach `m33_v0_scaffold/runs/`
- **Bestehende Ergebnisbäume** in `results/` bleiben unberührt
- keine erzwungene Zusammenführung
- keine hektische Migration alter Ergebnisse

---

## 10. Standard-Workflow pro Arbeitsblock im echten Repo

### Schritt 1 — Forschungsfrage klären
Mit Nova:

- Ziel
- Nicht-Ziel
- Hypothese
- Gegenhypothese
- erwartete Outputs
- Erfolgskriterien
- Gegenkriterien

Ergebnis:
- Pflichtenheft
- Runner-Spezifikation

Ablage:
- in Chat
- später komprimiert nach `docs/project/WORKFLOW_ACTIVE_BLOCK.md`

### Schritt 2 — Recherche
Falls nötig:
- Deep Research
- Literatur
- Referenzfamilien
- Standardverfahren
- Einordnung

Ablage:
- `docs/reviews/` oder zugehörige Review-Unterstruktur

### Schritt 3 — Implementierung
Codex baut im bevorzugten Fall in:

- `m33_v0_scaffold/src/`
- `m33_v0_scaffold/configs/`
- `m33_v0_scaffold/scripts/`

nur bei echter Kernrelevanz in:
- `src/dpb/`

### Schritt 4 — Lokaler Lauf
Du führst lokal aus.  
Outputs landen in:

- `m33_v0_scaffold/runs/...`
oder
- einem bewusst definierten Ergebnisraum

### Schritt 5 — Physikalische Auswertung
Die Outputs werden im Forschungsraum interpretiert.

### Schritt 6 — Kritische Gegenprüfung
Claude / Team-Red greift an.

### Schritt 7 — Rückintegration
Masterchat und `WORKFLOW_ACTIVE_BLOCK.md` werden aktualisiert.

---

## 11. Minimaler Standard pro Block

Ein Arbeitsblock gilt erst dann als sauber abgeschlossen, wenn mindestens vorliegt:

1. Pflichtenheft oder Runner-Spezifikation  
2. Implementierung  
3. reproduzierbarer Lauf  
4. strukturierte Outputs  
5. physikalische Auswertung  
6. kritische Gegenprüfung oder bewusste Entscheidung, warum sie noch nicht nötig ist  
7. Rückintegration in den Masterchat  

---

## 12. Konkrete Zuständigkeiten für Dateibereiche

### 12.1 Codex darf bevorzugt arbeiten in

- `m33_v0_scaffold/src/`
- `m33_v0_scaffold/configs/`
- `m33_v0_scaffold/scripts/`
- `src/dpb/` nur bei bewusstem Kernauftrag
- `configs/`
- `scripts/`
- `tests/`

### 12.2 Codex soll nicht stillschweigend ändern

Ohne expliziten Auftrag nicht ungefragt ändern:

- `docs/project/MASTERCHAT_CANONICAL.md`
- `docs/project/PROJECT_NORMS.md`
- `docs/project/PROJECT_ORGA.md`
- zentrale Review-Dokumente
- strategische Forschungsentscheidungen

### 12.3 Nova führt

Nova führt:

- Begriffe
- Lesarten
- Pflichtenhefte
- Masterchat
- Synthesen
- Milestones
- Priorisierung
- Brücken zwischen Befund und Theorie

---

## 13. Praktische Arbeitsumgebung

Eine frei arrangierbare Desktop-Oberfläche wie auf einem visuellen Betriebssystem-Schreibtisch existiert nicht als einzelnes Chat-Fenster.

Funktional wird die Arbeitsumgebung jedoch ab jetzt so verstanden:

- **ChatGPT-Projekt / Dokumentationsraum**  
  = Leitstand

- **`docs/project/` + Masterchat**  
  = kanonischer Projektkopf

- **Deep Research**  
  = Recherche- und Aufklärungsraum

- **VS Code + Codex IDE Extension**  
  = Werkbank

- **Claude / Team-Red**  
  = Gegnerraum

- **`m33_v0_scaffold/`**  
  = aktive Audit-Werkbank

Diese funktionale Kombination ersetzt den „Schreibtisch“ in einer Form, die sich in der Praxis bewährt und besser versionierbar ist als ein rein visuelles Dashboard.

---

## 14. Ziel dieser repo-spezifischen Struktur

Diese Struktur soll gleichzeitig leisten:

1. **Stabilität**  
   bewährte reale Repo-Struktur bleibt erhalten

2. **Klarheit**  
   echte vorhandene Ordner werden sauber funktional zugeordnet

3. **Entlastung**  
   Recherche und Reviews werden aus dem eigentlichen Forschungsraum ausgelagert

4. **Nachvollziehbarkeit**  
   keine unangenehmen Umzüge zwischen Chats ohne Referenzbasis

5. **Werkbankdisziplin**  
   neue Blöcke entstehen kontrolliert in der Audit-Werkbank, nicht ungeplant im Kern

---

## 15. Ein-Satz-Synthese

> Das Projekt behält seine reale bewährte Repo-Struktur bei und ordnet sie verbindlich in Leitstand (`docs/project/`), Theorie-Baukasten (`docs/theory/`), Gegnerraum (`docs/reviews/`), stabilem Produktivkern (`src/dpb/`) und aktiver Audit-Werkbank (`m33_v0_scaffold/`) ein, damit Forschung, Implementierung, Recherche und Gegenprüfung ohne unnötige Umzüge stabil zusammenarbeiten können.
