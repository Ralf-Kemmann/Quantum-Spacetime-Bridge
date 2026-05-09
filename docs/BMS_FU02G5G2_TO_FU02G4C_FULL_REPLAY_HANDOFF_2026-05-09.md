# BMS/FU02g5g2 Abschluss- und Übergabe-Notiz für den nächsten FU02g4c Full Replay

**Datum:** 2026-05-09  
**Projekt:** QSB / Gravitation-und-RaumZeit  
**Arbeitsblock:** FU02g5g2 → FU02g4c Full Replay Handoff  
**Status:** Abschlussnotiz für lokalen Replay-Stand; Full-Raw-Order-Zertifizierung weiterhin offen

---

## 1. Zweck der Notiz

Diese Notiz konserviert den aktuellen Stand des FU02g5g2-Replay-Blocks und formuliert die Übergabe an den nächsten methodischen Schritt: einen vollständigen FU02g4c raw-order Replay / Certification Pass.

Die Notiz ist bewusst defensiv formuliert. Sie soll verhindern, dass der lokale scaffold/FU02g4c-style Replay-Erfolg versehentlich als vollständige Rohordnungszertifizierung gelesen wird.

---

## 2. Rollen- und Workflow-Rahmen

Der eingefrorene Maschinenraum-Workflow gilt für diesen Block:

- **Nova:** methodisches Klemmbrett; Spezifikation, Logik, Claim-Bremse, Red-Team-Synthese, Interpretation.
- **Codex:** lokaler Schraubenschlüssel; Dateien, Skripte, Configs, Tests, Outputs, nur mit kurzer Leine.
- **Ralf:** kreativer Kopf, Forschungsarchitekt, finale Kontrollinstanz; entscheidet Forschungsrichtung, Terminal-/Git-Kontrolle und Claim-Freigabe.

Arbeitsregeln:

- repo-orientiert
- transparent
- keine hidden files
- kein hidden code
- keine hidden calculations
- keine hidden assumptions
- keine Overclaims
- Trennung von Befund / Interpretation / Hypothese / Offene Lücke / Claim Boundary

---

## 3. Aktueller Stand: FU02g5g2

FU02g5g2 hat im aktuellen scaffold/FU02g4c-style Replay alle **11 scaffold-localized near candidates** per-index reproduziert.

Dieser Befund betrifft die getestete Replay-Logik und den aktuellen Kandidatenraum. Er ist ein lokaler Reproduzierbarkeitsbefund innerhalb der aktuell verwendeten scaffold/FU02g4c-style Replay-Konfiguration.

Wichtig: Dieser Befund ersetzt nicht die vollständige FU02g4c raw-order Replay Certification.

---

## 4. Besonders markierte Kandidaten

### 4.1 candidate_005

**Arbeitsstatus:** direkt fotografierter coarse-signature degeneracy stress case.

candidate_005 ist als Stressfall für coarse-signature-Degeneracy zu behandeln. Der Kandidat ist methodisch wertvoll, weil er prüft, ob die Replay-Logik bei grob ähnlichen Signaturen stabil bleibt oder ob mehrere strukturell verschiedene Fälle auf derselben groben Signatur zusammenfallen können.

Defensive Lesart:

- candidate_005 ist kein alleiniger Strukturbeweis.
- candidate_005 ist ein Diagnostikfall für Degeneracy-Handling.
- candidate_005 sollte im Full Replay besonders darauf geprüft werden, ob seine per-index-Reproduktion auch unter Rohordnungsbedingungen stabil bleibt.

### 4.2 candidate_008

**Arbeitsstatus:** reproduzierter Spiegelklunker / positive control.

candidate_008 ist als positiver Kontrollfall zu behandeln. Die Reproduktion dieses Spiegelklunkers spricht dafür, dass die aktuelle Replay-Logik zumindest bekannte bzw. erwartete Strukturmerkmale wiederfindet.

Defensive Lesart:

- candidate_008 stützt die interne Plausibilität des Replay-Mechanismus.
- candidate_008 beweist allein keine globale Nicht-Generizität.
- candidate_008 ist als positive control nützlich, aber kein Ersatz für den vollständigen raw-order Pass.

---

## 5. Befund

Im getesteten FU02g5g2-Replay wurden alle 11 scaffold-localized near candidates per-index reproduziert.

Zusätzlich wurden zwei methodisch wichtige Sonderfälle markiert:

1. candidate_005 als coarse-signature degeneracy stress case.
2. candidate_008 als Spiegelklunker / positive control.

Der aktuelle Stand stützt damit die interne Reproduzierbarkeit der Kandidatenliste innerhalb der getesteten scaffold/FU02g4c-style Replay-Logik.

---

## 6. Interpretation

Die per-index-Reproduktion aller 11 Kandidaten ist ein methodisch relevanter Zwischenbefund. Sie spricht dagegen, dass die aktuelle Kandidatenliste bloß ein flüchtiges Artefakt eines einzelnen lokalen Durchlaufs ist.

Die beiden Sonderfälle ergänzen diese Lesart:

- candidate_005 testet die Empfindlichkeit gegenüber grober Signaturdegeneracy.
- candidate_008 dient als positive Kontrolle für eine reproduzierte Spiegelstruktur.

Damit entsteht ein stärkeres Bild interner Konsistenz, aber noch kein abgeschlossener globaler Zertifizierungsbefund.

---

## 7. Hypothese

Arbeitshypothese für den nächsten Schritt:

Wenn die 11 scaffold-localized near candidates auch im vollständigen FU02g4c raw-order Replay stabil per-index reproduziert werden, dann wäre der Status der Kandidatenliste deutlich stärker als nur ein lokaler scaffold-style Replay-Befund.

Insbesondere wäre dann zu prüfen, ob:

- candidate_005 seine Rolle als Degeneracy-Stressfall robust behält,
- candidate_008 weiterhin als positiver Spiegelklunker reproduzierbar bleibt,
- keine zusätzlichen raw-order-Abweichungen auftreten,
- die Reihenfolge und Indizierung der Rohenumeration sauber mit der bisherigen Kandidatenliste zusammengeführt werden kann.

---

## 8. Offene Lücke

Die zentrale offene Lücke bleibt:

**full FU02g4c raw-order replay certification is not yet complete.**

Das bedeutet:

- Die lokale FU02g5g2-Reproduktion ist abgeschlossen.
- Die vollständige Rohordnungszertifizierung ist nicht abgeschlossen.
- Ein globaler Claim zur vollständigen FU02g4c-Replay-Zertifizierung wäre aktuell verfrüht.

---

## 9. Claim Boundary

### Zulässige defensive Formulierung

> FU02g5g2 reproduced all 11 scaffold-localized near candidates per-index in the current scaffold/FU02g4c-style replay. candidate_005 is retained as a coarse-signature degeneracy stress case, and candidate_008 is retained as a reproduced mirror-clunker positive control. The full FU02g4c raw-order replay certification remains open.

### Nicht zulässige stärkere Formulierung

> The FU02g4c replay certification is complete.

### Ebenfalls nicht zulässig

> The candidate structure is globally proven to be non-generic.

### Ebenfalls nicht zulässig

> The C60 carrier-region specificity has been fully certified by raw-order replay.

---

## 10. Übergabe an den nächsten Maschinenraum-Block

Nächster Block:

**FU02g4c Full Raw-Order Replay Certification**

Ziel:

Vollständige Prüfung, ob die bisher lokal reproduzierten 11 scaffold-localized near candidates auch im vollständigen FU02g4c raw-order Replay stabil, eindeutig und nachvollziehbar reproduziert werden.

Minimal erwartete Outputs:

- vollständiger Run- oder Replay-Readout
- Kandidaten-Mapping per-index
- explizite Markierung von candidate_005
- explizite Markierung von candidate_008
- Abweichungsliste, auch wenn leer
- Summary JSON oder Markdown-Readout
- Claim-Boundary-Abschnitt
- Git-Status nach Erstellung der Outputs

---

## 11. Codex-Auftrag für den nächsten lokalen Lauf

Codex darf im nächsten Schritt nur mit einem expliziten Auftrag arbeiten.

Vorgeschlagener Auftrag:

```text
Arbeite im Repo:

/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

Ziel:
Bereite den vollständigen FU02g4c raw-order replay certification pass vor oder führe ihn aus, falls die dafür nötigen Skripte und Configs bereits eindeutig vorhanden sind.

Regeln:
- keine bestehenden FU02-Ankerdateien ändern
- keine bestehenden Skripte ändern, außer ausdrücklich beauftragt
- keine Dateien löschen
- keine Top-Level-Ordner erzeugen
- keine git add/commit/reset/push Kommandos
- nur git status ist erlaubt
- alle erzeugten Dateien melden
- alle ausgeführten Befehle melden
- alle Checks und Fehlermeldungen melden
- candidate_005 separat als coarse-signature degeneracy stress case markieren
- candidate_008 separat als Spiegelklunker / positive control markieren
- full raw-order replay certification nur dann als abgeschlossen bezeichnen, wenn der vollständige Rohordnungsdurchlauf tatsächlich abgeschlossen und dokumentiert ist

Erwartete Abschlussmeldung:
- Befund
- Interpretation
- Offene Lücke
- Claim Boundary
- git status --short
```

---

## 12. Minimaler nächster Prüfpunkt

Vor jedem stärkeren Claim muss mindestens geklärt sein:

1. Wurde die komplette FU02g4c-Rohordnung durchlaufen?
2. Wurden alle 11 Kandidaten per-index wiedergefunden?
3. Sind candidate_005 und candidate_008 korrekt wiedererkannt?
4. Gibt es zusätzliche oder fehlende Treffer?
5. Ist die Mapping-Logik zwischen scaffold-style Replay und raw-order Replay dokumentiert?
6. Liegt ein reproduzierbarer Readout im Repo vor?
7. Ist die Claim Boundary im Output enthalten?

---

## 13. Kurzfazit

FU02g5g2 ist ein sauberer lokaler Replay-Abschluss: alle 11 scaffold-localized near candidates wurden per-index reproduziert.

Der Block stärkt die interne Konsistenz der Kandidatenliste und bewahrt zwei methodisch wichtige Marker:

- candidate_005: Degeneracy-Stressfall
- candidate_008: Spiegelklunker / positive control

Die eigentliche FU02g4c full raw-order replay certification bleibt offen und ist der nächste zwingende Maschinenraum-Schritt.
