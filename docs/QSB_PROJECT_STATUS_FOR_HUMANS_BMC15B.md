# Quantum-Spacetime-Bridge — Projektstand für Menschen nach BMC-15b

## 1. Worum geht es gerade?

Wir untersuchen im Projekt eine relationale Struktur, die aus Merkmalen und Beziehungen zwischen Einheiten entsteht.

Die interne Leitidee ist:

```text
Aus einer relationalen Suppe bildet sich ein stabiler Kern.
Dieser Kern liegt in größeren, methodenabhängigen Hüllen.
Wir prüfen, ob dieser Kern robust ist und ob die Hüllen geometrieähnliche Ordnung zeigen.
```

Wichtig:

```text
Wir behaupten nicht:
Das ist physikalische Raumzeit.

Wir prüfen:
Gibt es robuste relationale Struktur?
Gibt es geometry-like Proxy-Verhalten?
Ist dieses Verhalten spezifisch oder nulltypisch?
```

---

## 2. Das Bild: Klunker, Keim, Hülle

Die beste interne Vorstellung ist die Festkörperchemie-Analogie:

```text
Eine Lösung wirkt zunächst homogen.
Dann bildet sich ein Kristallisationskeim.
Dieser Keim ist lokal stabil.
Danach wächst eine Hülle oder ein Gerüst.
```

Übertragen auf das Projekt:

```text
Klunker / Keim:
  der robuste N=81-Kern

Hülle:
  größere Backbone-/Envelope-Strukturen um den Kern

Kristallordnung:
  geometry-like Proxy-Konsistenz

Küchenmaschine:
  die Pipeline, die aus Daten Graphen und Hüllen extrahiert
```

Die entscheidende Frage ist nicht:

```text
Ist das schon Raumzeit?
```

Sondern:

```text
Ist der Keim robust?
Hat die Hülle innere Ordnung?
Ist diese Ordnung spezifisch oder macht die Pipeline solche Ordnung auch aus Nullmodellen?
```

---

## 3. Was wurde bis BMC-14 gezeigt?

Bis zur BMC-14-Serie haben wir geprüft, ob der beobachtete Kern einfach ein Artefakt verschiedener Nullmodelle sein könnte.

Der beobachtete Kern ist ein kompakter 6-Kanten-Kern im N=81-Regime.

Die Kontrollen fragten unter anderem:

```text
Kommt dieser Kern wieder, wenn wir Features schütteln?
Kommt er wieder, wenn wir Kovarianz erhalten?
Kommt er wieder, wenn wir Kantengewichtsränge erhalten?
Kommt er wieder, wenn wir Knotengrade erhalten?
Kommt er wieder, wenn wir Rangkorrelationen/Copula-Struktur erhalten?
```

Ergebnis:

```text
0 / 3300 getestete Null-Replikate rekonstruieren den beobachteten 6-Kanten-Kern vollständig.
```

Das ist ein starker methodischer Befund.

Aber:

```text
Family-/Feature-Struktur trägt Signalanteile.
Core-in-envelope-Verhalten ist teilweise pipeline-generisch.
```

Übersetzt:

```text
Der konkrete Klunker ist schwer nachzubauen.
Aber die Maschine baut grundsätzlich gern Keime in Hüllen.
```

---

## 4. Was hat BMC-15a geprüft?

BMC-15a war der erste Geometry-Proxy-Block.

Er fragte:

```text
Wenn der Kern robust ist:
zeigen Kern und Hüllen geometrieähnliche Konsistenzmerkmale?
```

Gemessen wurden unter anderem:

```text
Triangle inequality defects
Embedding stress
Shell growth
Local dimension proxy
Geodesic consistency
```

Ergebnis BMC-15a:

```text
Direkte Triangle defects: 0
Embedding stress: niedrig bis moderat niedrig
größere Hüllen: stabile sparse-scaffold shell-growth proxies
kompakter Core allein: zu klein und fragmentiert für standalone Geometry-Lesart
```

Bedeutung:

```text
Die Hüllen sehen geometry-like geordnet aus.
Der Kern allein ist zu klein, um daraus Geometrie abzuleiten.
```

Interne Kurzform:

```text
Der Klunker ist nicht nur hart.
In den Hüllen sieht man erste Kristallordnung.
Aber es ist noch kein fertiger Kristall und schon gar keine physikalische Raumzeit.
```

---

## 5. Warum brauchten wir BMC-15b?

BMC-15a zeigte nur den beobachteten Fall.

Die nächste Frage war:

```text
Ist diese geometry-like Ordnung besonders,
oder sehen Nullgraphen genauso aus?
```

Das ist entscheidend, weil eine Pipeline manchmal auch aus Zufall hübsche Ordnung erzeugen kann.

Interne Frage:

```text
Glitzert unser Klunker spezifisch,
oder glitzern Null-Klumpen genauso hübsch?
```

---

## 6. Was hat BMC-15b gemacht?

BMC-15b erzeugte Nullgraphen und berechnete dieselben Geometry-Proxys wie in BMC-15a.

Dabei wurden zwei Gruppen unterschieden.

### Graph-Rewire-Nulls

Diese Nullmodelle erhalten eher Graph-/Kanteneigenschaften, zerstören aber die konkrete relationale Feature-Identität:

```text
weight_rank_edge_rewire
degree_preserving_edge_rewire
degree_weightclass_edge_rewire
```

### Feature-structured Nulls

Diese Nullmodelle erhalten oder regenerieren Teile der Feature-/Family-/Korrelationsstruktur:

```text
global_covariance_gaussian
family_covariance_gaussian
gaussian_copula_feature_null
```

---

## 7. Wichtigster BMC-15b-Befund

Gegen Graph-Rewire-Nulls sieht der beobachtete Fall deutlich geordneter aus.

Besonders bei:

```text
embedding stress
negative eigenvalue burden
```

Beispiel:

```text
N81_full_baseline, degree_preserving_edge_rewire:

beobachtet:
  2D stress = 0.107
  3D stress = 0.063
  4D stress = 0.061

Null-Median:
  2D stress = 0.361
  3D stress = 0.234
  4D stress = 0.167
```

Das bedeutet:

```text
Der beobachtete Graph ist deutlich besser niedrigdimensional einbettbar
als grad-/gewichtsrang-erhaltene Rewire-Nullgraphen.
```

---

## 8. Der ehrliche Dämpfer

Gegen Feature-/Family-/Copula-Nulls ist das Bild gemischt.

Viele Geometry-Proxy-Werte sind dort:

```text
null_typical
```

Das bedeutet:

```text
Feature-/Family-/Korrelationsstruktur kann selbst geometry-like Proxy-Verhalten erzeugen.
```

Das ist keine Niederlage.

Es bedeutet:

```text
Die Geometry-like Ordnung kommt offenbar nicht aus beliebiger Graphstruktur,
sondern hängt stark mit der Feature-/Family-/Korrelationsstruktur zusammen.
```

Kurz:

```text
Gegen Graph-Rewire-Nulls: stark.
Gegen Feature-Nulls: gemischt / oft typisch.
```

---

## 9. Triangle-Label-Korrektur

Im ersten BMC-15b-Readout gab es einen Beschriftungsfehler.

Wenn beobachtet und Null beide exakt 0 Triangle-Defekte hatten, wurde das teils fälschlich als schlechter gelabelt.

Das wurde gepatcht.

Korrekte Lesart:

```text
observed = 0
null = 0
→ observed_null_equivalent
```

Interne Kurzform:

```text
Die alten all-zero Triangle-Labels waren ein Beschriftungskobold.
```

---

## 10. Aktueller Gesamtstand

Der aktuelle Stand lässt sich so zusammenfassen:

```text
Der beobachtete N=81-Kern ist gegen viele Nullmodelle robust.
Die größeren Hüllen zeigen geometry-like Proxy-Konsistenz.
Diese Geometry-Proxys sind gegenüber Graph-Rewire-Nulls deutlich günstiger.
Aber Feature-/Family-/Korrelationsstruktur kann ähnliche Geometry-Proxys erzeugen.
```

Das ist ein ehrlicher, guter Befund:

```text
nicht überzogen
nicht trivial
nicht endgültig
aber methodisch belastbar
```

---

## 11. Was dürfen wir daraus sagen?

Erlaubt:

```text
Der beobachtete Kern ist methodisch robust gegen die getesteten Nullfamilien.
Die beobachteten Hüllen zeigen geometry-like Proxy-Konsistenz.
Die Geometry-Proxys sind gegenüber Graph-Rewire-Nulls deutlich günstiger.
Feature-/Family-/Korrelationsstruktur trägt wesentlich zur geometry-like Ordnung bei.
```

Nicht erlaubt:

```text
Wir haben Raumzeit bewiesen.
Wir haben eine physikalische Metrik rekonstruiert.
Wir haben Kausalstruktur.
Wir haben eine Kontinuumsgeometrie.
Alle Nullerklärungen sind ausgeschlossen.
```

---

## 12. Der aktuelle Satz für Außenkommunikation

Sehr defensiv:

```text
The current diagnostics support a robust relational core identity and geometry-like proxy consistency at the envelope level. The geometry-proxy behavior is not merely reproduced by graph-rewiring controls, but feature/family/correlation-structured nulls can generate similar proxy values. The result is therefore informative but not uniquely specific, and it does not establish physical spacetime emergence.
```

Deutsch:

```text
Die aktuellen Diagnostiken stützen eine robuste relationale Kernidentität und geometrieähnliche Proxy-Konsistenz auf Hüllenebene. Dieses Verhalten wird nicht einfach durch Graph-Rewiring-Kontrollen reproduziert, kann aber durch Feature-/Family-/Korrelationsstruktur teilweise ebenfalls erzeugt werden. Der Befund ist daher informativ, aber nicht eindeutig spezifisch, und belegt keine physikalische Raumzeitentstehung.
```

---

## 13. Was steht als nächstes an?

Sinnvolle nächste Schritte:

```text
1. BMC-15d Red-Team Integration
2. BMC-15 Series Consolidated Geometry-Proxy Note
3. Danach erst vorsichtige Visualisierung / Layout Diagnostics
```

Warum nicht sofort hübsche Bilder?

```text
Weil BMC-15b gemischt ist.
Bilder wirken stark.
Vor Visualisierung sollte die defensive Interpretation festgezogen werden.
```

Interne Kurzform:

```text
Erst den Koboldkäfig prüfen,
dann PM-Magazin.
```

---

## 14. Letzter menschlicher Merksatz

```text
Der Klunker ist schwer nachzubauen.
Er zeigt in seinen Hüllen erste Ordnung.
Diese Ordnung ist mehr als bloß Graph-Geschüttel.
Aber sie ist teilweise aus Feature-/Family-Struktur erklärbar.
Also: interessant, robust, vorsichtig weiterprüfen.
```
