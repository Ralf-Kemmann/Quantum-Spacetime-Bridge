# debroglie_matter_signature_isotope_carbon_srontium_plan_v1

## 1. Ziel

Dieses Dokument formuliert den unmittelbaren Arbeitsplan für die nächste Isotopen-Erweiterung
über den erfolgreichen H/D/T-Minimaltest hinaus.

Im Fokus stehen zwei neue Felder:

- **Kohlenstoff** als inhaltlich zentrale Atomsorte
- **Strontium** als methodisch starke kleine Isotopenserie

Ja, der Titel trägt bewusst den charmanten Tippfehler **„Srontium“**.
Er bleibt hier als interner Werkstattgruß stehen.

Leitfrage:

> Wie setzen wir den nächsten Isotopenblock so auf, dass sowohl inhaltliche Relevanz
als auch methodische Staffelstärke sauber geprüft werden?

---

## 2. Ausgangslage

Der erste Isotopenblock H/D/T hat gezeigt:

- die Wellenachse reagiert sauber auf isotopische Massenvariation
- die Strukturachse bleibt im Minimalfall invariant
- die kombinierte Signatur reagiert kontrolliert
- Wellen- und Strukturanteil lassen sich damit erstmals hart trennen

Darauf baut der vorliegende Plan direkt auf.

---

## 3. Warum Kohlenstoff?

Kohlenstoff wird als erster Generalisierungsschritt gewählt, weil er:

- für organische Materie strukturell zentral ist
- vier Valenzelektronen trägt
- als kovalente Grundspezies im Projektkontext inhaltlich deutlich relevanter ist als Wasserstoff allein
- zugleich eine saubere erste Isotopenpaarung erlaubt

Minimaler Start:

- `12C`
- `13C`

Arbeitsziel:

> Prüfen, ob die H/D/T-Logik auch bei einer chemisch zentralen, strukturell reicheren Atomsorte trägt.

---

## 4. Warum Strontium?

Strontium wird nicht primär aus inhaltlicher, sondern aus methodischer Stärke gewählt.

Wichtige Punkte:

- mehrere stabile Isotope
- damit mehr als nur ein Zweiervergleich
- gestufte Massenskala innerhalb gleicher Elektronenstruktur
- guter Staffeltest für systematische Wellenverschiebung

Arbeitsziel:

> Prüfen, ob die Wellenachse über mehrere Isotopenstufen sauber und geordnet reagiert, während die Strukturachse invariant bleibt.

---

## 5. Arbeitsaufteilung

### 5.1 Kohlenstoff-Block
Rolle:
- inhaltlich relevanter Generalisierungstest

Minimaler Satz:
- `12C`
- `13C`

Optional später:
- `14C` nur mit expliziter Kennzeichnung, da radioaktiv

### 5.2 Strontium-Block
Rolle:
- methodisch starker Serien- und Staffeltest

Minimaler Satz:
- stabile Sr-Isotope in einer ersten kleinen Serie

Wichtig:
Noch keine tiefere Kernphysik erzwingen, sondern zunächst:
- gleiche Elektronenstruktur annehmen
- Valenz-/Closure-Deskriptoren konstant halten
- Massenskala als gezielte Variable auslesen

---

## 6. Erwartete Befunde

### 6.1 Für Kohlenstoff
Erwartet wird:

- systematische Wellenverschiebung zwischen `12C` und `13C`
- konstante Strukturdeskriptoren
- kontrollierte kombinierte Signatur
- Bestätigung, dass der H/D/T-Befund nicht bloß ein Wasserstoff-Spezialfall war

### 6.2 Für Strontium
Erwartet wird:

- geordnete Staffelung der Wellenachse über mehrere Isotope
- Strukturinvarianz über die Serie
- keine chaotische kombinierte Ordnung
- stärkerer methodischer Achsentrennungstest als beim Zweierpaar

---

## 7. Konkreter Ausbauplan

### Schritt 1
Dokumentationsschicht bauen:

- `debroglie_matter_signature_isotope_cn_sr_io_v1.md`
- `debroglie_matter_signature_isotope_cn_sr_tests_v1.md`

### Schritt 2
Runner erweitern:

- Isotopen-Datensätze für `12C`, `13C`
- Isotopen-Datensätze für stabile Sr-Isotope
- Invarianzdiagnostik beibehalten

### Schritt 3
Config-Serie aufsetzen:

- Carbon Run A: Welle
- Carbon Run B: Welle + Valenz
- Carbon Run C: Welle + Valenz + Closure

- Sr Run A: Welle
- Sr Run B: Welle + Valenz
- Sr Run C: Welle + Valenz + Closure

### Schritt 4
Readout-Vergleich:

- H/D/T gegen C-Isotopenpaar
- H/D/T gegen Sr-Serie
- Carbon gegen Strontium
- prüfen, ob Generalisierung und Staffelung beide tragen

---

## 8. Methodische Leitlinien

### 8.1 Erst Generalisierung, dann Komplexität
Nicht sofort zu viele neue Freiheitsgrade hineinwerfen.

Erst prüfen:
- trägt die H/D/T-Logik bei Kohlenstoff?
- trägt sie als Serienlogik bei Strontium?

### 8.2 Struktur konstant halten
Im ersten Wurf gilt:

- gleiche Elektronenstruktur
- gleiche Valenzlogik
- gleiche Closure-Logik

Isotopie wird zunächst als Massentest gelesen.

### 8.3 Keine voreilige Kernphysik
Kernspin, Quadrupolmomente oder Hyperfein-Effekte werden erst später relevant, falls der Grundblock trägt.

---

## 9. Erfolgsbedingungen

Der Ausbau gilt als gelungen, wenn:

1. der H/D/T-Befund sauber auf Kohlenstoff generalisiert
2. Strontium eine geordnete Staffelreaktion zeigt
3. Strukturinvarianz über beide Felder stabil bleibt
4. die kombinierte Signatur kontrolliert reagiert
5. Generalisierung und Staffelung gemeinsam die Achsentrennung härten

---

## 10. Risiken

### 10.1 Kohlenstoff
Das Paar `12C`/`13C` könnte zu wenig Spreizung liefern, um einen optisch starken Effekt zu zeigen.
Das wäre aber nicht automatisch ein Gegenbefund, sondern eventuell nur ein kleiner Massenschritt.

### 10.2 Strontium
Mit mehreren Isotopen steigt die Chance auf methodische Inkonsistenzen im Input oder in der Readout-Logik.
Die Logbuchdisziplin muss hier besonders sauber bleiben.

### 10.3 Überinterpretation
Auch wenn C und Sr tragen, ist damit noch keine endgültige Theorie gewonnen.
Der Block bleibt ein Achsentrennungstest, kein Endbeweis.

---

## 11. Projektlogik

Der Plan folgt einer sauberen internen Treppe:

1. **H/D/T**
   - Minimaltest
   - erster harter Trennbefund

2. **Kohlenstoff**
   - inhaltliche Generalisierung

3. **Strontium**
   - methodische Staffelhärtung

Das ist eine gute Reihenfolge, weil sie den Maschinenraum weder überlädt noch zu früh in Spezialfälle kippt.

---

## 12. Bottom line

Die operative Leitformel dieses Plans lautet:

> Nach dem erfolgreichen H/D/T-Minimaltest wird die Isotopenlogik nun über Kohlenstoff generalisiert und über Strontium als Serienfeld methodisch verschärft.

Oder noch knapper:

> C prüft, ob es relevant ist.  
> Srontium prüft, ob es in Serie trägt.
