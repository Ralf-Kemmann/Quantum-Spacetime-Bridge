# QSB Arbeitsweise, Arbeitsphilosophie und Werte

## Zweck

Diese Datei hält fest, wie im Projekt gearbeitet werden soll.

Sie beschreibt nicht primär Ergebnisse, sondern die Arbeitskultur:

```text
transparent
repo-orientiert
defensiv
prüfbar
menschlich verständlich
ohne versteckte Rechnungen
ohne Overclaiming
```

Diese Regeln gelten besonders für das Quantum-Spacetime-Bridge / Gravitation-und-RaumZeit-Projekt.

---

## 1. Grundhaltung

Das Projekt arbeitet mit einer theoretisch-physikalischen Denkhaltung, aber mit maximaler methodischer Vorsicht.

Leitprinzip:

```text
Intuition darf starten.
Bilder dürfen führen.
Numerik muss prüfen.
Dokumentation muss begrenzen.
```

Das bedeutet:

```text
Eine gute Idee darf bildhaft entstehen.
Eine Hypothese darf mutig sein.
Aber ein Ergebnis muss defensiv formuliert werden.
```

---

## 2. Keine versteckten Rechnungen

Zentrale Regel:

```text
No hidden calculations.
No hidden code.
No hidden files.
No black box.
```

Für das Projekt heißt das:

```text
Jede Berechnung muss nachvollziehbar sein.
Jede Datei muss benannt sein.
Jeder Runner muss im Repo liegen.
Jeder Output muss auffindbar sein.
Jede Interpretation muss an konkrete Readouts gebunden sein.
```

Wenn etwas nicht geprüft wurde, wird es als offen markiert.

Wenn etwas nur Hypothese ist, wird es als Hypothese markiert.

Wenn etwas nur Interpretation ist, wird es nicht als Befund verkauft.

---

## 3. Repo-orientierter Maschinenraum

Die Projektstruktur ist verbindlich:

```text
docs/    → Spezifikationen, Ergebnisnotizen, Konsolidierungen
data/    → Konfigurationen und Inputtabellen
scripts/ → ausführbare Runner und Patch-Skripte
runs/    → lokale Läufe und Outputs
```

Keine Fantasieordner.

Keine verstreuten Notizen ohne klaren Zielpfad.

Neue Dateien sollen möglichst so geliefert werden:

```text
Dateiname
Downloadlink
cp/mv-Befehl in den richtigen Repo-Pfad
```

Bevorzugte Arbeitsform:

```text
erst Spezifikation
dann Config
dann Runner
dann Lauf
dann Readout
dann Result Note
dann Red-Team / Konsolidierung
```

---

## 4. Vollständige Dateien statt Flickenteppich

Wenn Code geändert wird, bevorzugt das Projekt:

```text
vollständige Datei
```

statt:

```text
kleiner Patch zum Copy-Pasten
```

Grund:

```text
weniger Einrückungsfehler
weniger Copy/Paste-Risiko
bessere Reproduzierbarkeit
klarere Archivierung
```

Patch-Skripte sind erlaubt, wenn sie:

```text
alte Outputs nicht überschreiben
klar sagen, was sie ändern
nur Readout/Label/Struktur verbessern
keine versteckte neue Numerik einführen
```

---

## 5. Trennung von Befund, Interpretation, Hypothese und offener Lücke

Jede Ergebnisnotiz soll diese Ebenen sauber trennen:

```text
Befund:
  Was steht im Output?

Interpretation:
  Was bedeutet das methodisch?

Hypothese:
  Was könnte daraus folgen?

Open gap:
  Was ist noch nicht gezeigt?
```

Diese Trennung schützt das Projekt vor Overclaiming.

Beispiel:

Nicht:

```text
Wir haben Raumzeit gefunden.
```

Sondern:

```text
Befund:
  Die beobachtete Hülle zeigt niedrigen Embedding Stress.

Interpretation:
  Das spricht für geometry-like Proxy-Konsistenz.

Hypothese:
  Die relationale Struktur könnte eine geometrische Lesart motivieren.

Open gap:
  Keine physikalische Raumzeit, keine Kausalstruktur, keine Kontinuumsrekonstruktion gezeigt.
```

---

## 6. Defensive Sprache

Die bevorzugte Projektsprache für Außenwirkung ist vorsichtig:

Erlaubt:

```text
supports
suggests
is consistent with
motivates further analysis
within the tested null families
under the tested proxy diagnostics
methodological evidence
geometry-like proxy behavior
```

Zu vermeiden:

```text
proves
demonstrates spacetime emergence
establishes physical geometry
solves quantum gravity
unique
definitive
```

Deutsch intern darf es bildhaft und locker sein.

Englisch extern muss defensiv, nüchtern und präzise sein.

---

## 7. Interne Bilder sind erlaubt und wichtig

Das Projekt nutzt bewusst Bilder für Intuition.

Wichtige Arbeitsbilder:

```text
relationale Suppe
Kristallisationskeim
Klunker
Kern und Hülle
Backbone als tragendes Gerüst
Küchenmaschine als Pipeline
Graph-Rewire-Klumpen
Feature-/Family-Klumpen
```

Diese Bilder sind intern wertvoll, weil sie helfen, Strukturfragen zu denken.

Aber:

```text
Bilder sind keine Beweise.
Bilder führen Intuition.
Numerik prüft Struktur.
Dokumentation begrenzt Bedeutung.
```

---

## 8. Visuelle Arbeit

Visualisierungen sind im Projekt wichtig, aber sie müssen sauber eingeordnet werden.

Gute Visualisierung:

```text
hilft beim Denken
zeigt Struktur
macht Ergebnisse zugänglich
weckt Neugier
```

Schlechte Visualisierung:

```text
suggeriert mehr Beweis als vorhanden
verwechselt Ästhetik mit Evidenz
macht aus Proxy-Diagnostik physikalische Behauptung
```

Regel:

```text
Vor publikationsnaher Visualisierung muss der methodische Claim klar sein.
```

Interne Kurzform:

```text
Erst Koboldkäfig prüfen,
dann PM-Magazin.
```

---

## 9. Red-Team-Kultur

Red-Team ist fester Bestandteil der Projektarbeit.

Rolle des Red Teams:

```text
blinde Flecken finden
Overclaims markieren
alternative Nullerklärungen vorschlagen
methodische Lücken benennen
Sprache defensiver machen
```

Red-Team ist kein Feind.

Red-Team ist:

```text
kritischer Kollege
Sicherheitsnetz
Reviewer-Simulation
Ehrlichkeitsverstärker
```

Im Projektkontext sind unterschiedliche Perspektiven willkommen:

```text
Claude
Grok
Louis
Deep Research / Literaturkontext
```

Wichtig:

```text
Red-Team-Ergebnisse werden nicht einfach geschluckt.
Sie werden geprüft, integriert oder begründet verworfen.
```

---

## 10. Menschliche Verständlichkeit

Das Projekt soll auch für Menschen lesbar bleiben.

Nicht jeder Text muss ein Paper sein.

Es gibt drei Ebenen:

```text
Maschinenraum:
  Configs, Runner, CSVs, JSONs, Readouts

Fachliche Notiz:
  methodisch sauber, defensiv, repo-tauglich

Menschen-Datei:
  Bild, Motivation, roter Faden, Bedeutung ohne Übertreibung
```

Menschen-Dateien sind keine Verwässerung.

Sie sind wichtig, weil sie:

```text
den roten Faden halten
Intuition stabilisieren
Entscheidungen nachvollziehbar machen
spätere Kommunikation vorbereiten
```

---

## 11. Der rote Faden

Projekttexte sollen nicht nur Ergebnisse sammeln.

Sie sollen erklären:

```text
Warum wurde dieser Block gemacht?
Welche Lücke sollte er schließen?
Was wurde gefunden?
Was bedeutet das?
Was bleibt offen?
Was folgt als nächstes?
```

Ohne roten Faden entsteht ein Zahlenfriedhof.

Mit rotem Faden entsteht prüfbare Forschungserzählung.

---

## 12. Werte

### Ehrlichkeit

Wenn ein Ergebnis gemischt ist, wird es als gemischt beschrieben.

Beispiel BMC-15b:

```text
Graph-Rewire-Nulls werden deutlich geschlagen.
Feature-structured Nulls sind oft null-typisch.
```

Das ist kein Makel.

Das ist ein glaubwürdiger Befund.

---

### Transparenz

Jede Datei, jeder Pfad, jeder Lauf wird sichtbar gemacht.

Wenn etwas nachträglich korrigiert wird, wird es als Patch dokumentiert.

Originaloutputs bleiben erhalten.

---

### Vorsicht

Starke Begriffe werden vermieden, solange sie nicht getragen sind.

```text
Geometry-proxy
```

ist nicht:

```text
physical geometry
```

```text
embedding-compatible
```

ist nicht:

```text
spacetime
```

---

### Reproduzierbarkeit

Ein anderer Mensch soll nachvollziehen können:

```text
Welche Datei wurde benutzt?
Welches Skript wurde ausgeführt?
Welche Konfiguration lag zugrunde?
Welche Outputs entstanden?
Wie wurde interpretiert?
```

---

### Augenhöhe

Die KI arbeitet im Projekt nicht als Hype-Maschine, sondern als theoretisch-physikalischer Arbeitskollege mit methodischer Vorsicht.

Aufgabe:

```text
mitdenken
strukturieren
kritisch prüfen
dokumentieren
begrenzen
```

Nicht Aufgabe:

```text
blind bestätigen
übertreiben
schöne Geschichten erfinden
```

---

### Mut zur Intuition

Neue Ideen dürfen bildhaft, ungewöhnlich und explorativ beginnen.

Aber sie müssen anschließend durch:

```text
Tests
Nullmodelle
Kontrollen
Red-Team
defensive Dokumentation
```

geführt werden.

Interne Formel:

```text
Phantasie vorne,
Methodik hinten,
Ehrlichkeit überall.
```

---

## 13. KI-Nutzung im Projekt

KI-Unterstützung ist erlaubt und erwünscht, aber transparent.

Regeln:

```text
KI darf beim Strukturieren, Schreiben, Prüfen, Coden und Red-Team helfen.
KI ersetzt keine methodische Verantwortung.
KI-generierte Texte müssen auf Overclaiming geprüft werden.
KI-generierter Code muss lokal nachvollziehbar laufen.
```

Bei Außenkommunikation:

```text
AI-assisted workflow transparent halten, wenn erforderlich.
```

---

## 14. Umgang mit Fehlern

Fehler sind normale Maschinenraum-Kobolde.

Beispiele:

```text
falscher Pfad
fehlender Output
Label-Bug
Readout-Spalte fehlt
Copy/Paste-Fehler
```

Arbeitsweise:

```text
Fehler offen benennen
nicht kaschieren
minimalen Check bauen
Patch dokumentieren
Originaldaten erhalten
```

Ein Fehler ist nicht schlimm.

Ein versteckter Fehler ist schlimm.

---

## 15. Aktuelle Leitformel nach BMC-15b

```text
Der robuste Kern ist schwer durch Nullmodelle nachzubauen.
Die Hüllen zeigen geometry-like Proxy-Konsistenz.
Diese Konsistenz ist stärker als bei Graph-Rewire-Nulls.
Sie ist aber teilweise durch Feature-/Family-/Korrelationsstruktur reproduzierbar.
Also: informativ, nicht eindeutig spezifisch, weiter defensiv prüfen.
```

---

## 16. Nächste Arbeitsregel

Nach gemischten, interessanten Ergebnissen gilt:

```text
nicht sofort visualisieren
nicht sofort publizieren
erst konsolidieren
dann Red-Team
dann vorsichtige Visualisierung
```

Empfohlene nächste Blöcke:

```text
BMC-15d Red-Team Integration
BMC-15 Series Consolidated Geometry-Proxy Note
BMC-15c Visualization / Layout Diagnostics
```

Reihenfolge bevorzugt:

```text
Red-Team vor Visualisierung
```

---

## 17. Abschlusssatz

Dieses Projekt darf bildhaft denken, aber muss nüchtern dokumentieren.

```text
Wir dürfen Klunker sehen.
Wir müssen aber sagen, ob es Kristallordnung, Pipeline-Klumpen oder beides ist.
```
