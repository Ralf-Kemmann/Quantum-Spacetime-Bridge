# QSB Umzugsdatei 3 — Codex-Regeln / Lehrlingszettel

**Date:** 2026-05-09  
**Project:** Quantum–Spacetime Bridge / Gravitation und RaumZeit  
**Purpose:** Regeln für Codex als lokalen Implementierungsassistenten.

---

## 1. Rolle

```text
Codex:
lokaler Schraubenschlüssel.
```

Codex darf:

```text
Dateien erzeugen
Skripte implementieren
Configs schreiben
Tests ausführen
Runs ausführen
Outputs berichten
Git-Status zeigen
```

Codex entscheidet nicht über wissenschaftliche Claims.

---

## 2. Harte Verbote

Codex darf nicht:

```text
bestehende Dateien ändern, außer explizit erlaubt
closed FU02 anchor files anfassen
git add ausführen
git commit ausführen
git reset ausführen
git push ausführen
Dateien löschen
Top-Level-Ordner erzeugen
hidden code erzeugen
hidden calculations machen
hidden files anlegen
stille Algorithmusänderungen durchführen
stille Feldnamenänderungen durchführen
```

---

## 3. Standardauftrag

```text
Repo:
/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

Task:
...

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

---

## 4. Nach jedem Codex-Task

Immer prüfen:

```bash
git status --short --untracked-files=no
```

Erwartung:

```text
leer
```

Dann scoped prüfen:

```bash
git status --short \
  docs/<new_doc>.md \
  data/<new_config>.yaml \
  scripts/<new_script>.py
```

Erwartung:

```text
nur die ausdrücklich gewünschten neuen Dateien als ??
```

---

## 5. Reporting-Pflicht

Codex muss berichten:

```text
files created
files modified
commands run
tests/checks passed or failed
output directory
git status
limitations / uncertainties
```

---

## 6. Wissenschaftliche Result Notes

Jede Result Note braucht:

```text
Befund
Interpretation
Hypothese
Offene Lücke
Claim Boundary
```

Keine Overclaims.

Nicht behaupten:

```text
physical emergence
spacetime emergence
global uniqueness
global rarity
Lorentz compatibility
full FU02g4c certification
```

außer exakt belegt und von Ralf freigegeben.

---

## 7. Interne Kurzform

```text
Codex darf schrauben.
Aber nur am markierten Bauteil.

Schnell ja.
Blackbox nein.
```
