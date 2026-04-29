# BMC-15e menschlich lesbar — Geometry-Control Nulls, Ergebnis und Mathematik

## Zweck dieser Datei

Diese Datei fasst den BMC-15e-Lauf in menschlich lesbarer Form zusammen.

Sie ist bewusst so geschrieben, dass man den roten Faden versteht:

```text
Warum wurde BMC-15e gemacht?
Was wurde gerechnet?
Welche Ergebnisse kamen heraus?
Welche Mathematik steckt dahinter?
Was darf man daraus sagen?
Was darf man nicht daraus sagen?
```

Wichtig:

```text
BMC-15e ist ein Geometry-Proxy-Test.
BMC-15e ist kein Beweis physikalischer Raumzeit.
BMC-15e zeigt keine Kausalstruktur.
BMC-15e zeigt keine Lorentz-Signatur.
BMC-15e rekonstruiert keine physikalische Metrik.
```

---

## 1. Ausgangslage vor BMC-15e

Vor BMC-15e hatten wir aus BMC-15b diesen Stand:

```text
Gegen Graph-Rewire-Nulls:
  observed ist deutlich günstiger / geometry-proxy-kompatibler.

Gegen Feature-/Family-/Copula-Nulls:
  observed ist oft null-typisch.

Gesamt:
  informativ, aber nicht eindeutig spezifisch.
```

Das war methodisch gut, aber es fehlte ein Vergleichsanker:

```text
Wie sieht observed im Vergleich zu absichtlich geometrisch erzeugten Kontrollgraphen aus?
```

Genau diese Lücke füllt BMC-15e.

---

## 2. Leitfrage von BMC-15e

BMC-15e fragt nicht:

```text
Ist das Raumzeit?
```

BMC-15e fragt:

```text
Wo liegt der beobachtete relationale Graph im Diagnostikraum,
wenn wir ihn nicht nur gegen geschüttelte Graphen,
sondern auch gegen absichtlich geometrisch erzeugte Kontrollgerüste halten?
```

Interne Kurzform:

```text
Der Klunker wurde nicht nur gegen Graph-Geschüttel gehalten,
sondern gegen einfache geometrische Kontrollgerüste.
```

---

## 3. Geladene observed Graphobjekte

Der MVP-Lauf hat drei beobachtete Graphobjekte geladen:

| Graphobjekt | Knoten | Kanten | Zusammenhängend |
|---|---:|---:|---|
| `N81_full_baseline` | 22 | 81 | ja |
| `maximum_spanning_tree_envelope` | 22 | 21 | ja |
| `mutual_kNN_k3_envelope` | 22 | 23 | nein |

Wichtiger Dämpfer:

```text
mutual_kNN_k3_envelope ist nicht zusammenhängend.
Daher müssen dessen distanzbasierte Diagnostiken vorsichtig gelesen werden.
```

Der Runner verwendet für nicht zusammenhängende Graphen eine Policy auf der größten Komponente.

---

## 4. Geometry-Control-Familien

BMC-15e hat zwei einfache Geometrie-Kontrollfamilien verwendet:

```text
random_geometric_graph
soft_geometric_kernel
```

### 4.1 Random Geometric Graph

Idee:

```text
Punkte werden in einem geometrischen Raum erzeugt.
Knoten werden nach geometrischer Nähe verbunden.
```

Das ist ein einfacher Euclid-artiger Kontrollgraph.

### 4.2 Soft Geometric Kernel

Idee:

```text
Punkte werden in einem geometrischen Raum erzeugt.
Abstände werden über einen weichen Kernel in Ähnlichkeiten/Gewichte übersetzt.
```

Ein typischer Kernel ist:

```text
w_ij = exp(-d_ij / s)
```

wobei:

```text
w_ij = Gewicht / Ähnlichkeit zwischen i und j
d_ij = geometrischer Abstand zwischen i und j
s    = Skalenparameter
```

---

## 5. Parameter des MVP-Laufs

Verwendete Dimensionen:

```text
2
3
4
```

Verwendete Weight-Modes:

```text
unweighted
observed_rank_remap
```

Replikate:

```text
200 pro Graphobjekt / Kontrollfamilie / Dimension / Weight-Mode
```

Gesamtergebnis des Laufs:

```text
Control metric rows:       7200
Family summary rows:       36
Observed-position rows:    288
Warnings:                  none
```

Technische Abhängigkeiten:

```text
sklearn_available: true
scipy_available: true
```

---

## 6. Wichtigste Mathematik

### 6.1 Graph und Kantengewichte

Ein beobachteter oder kontrollierter Graph wird als gewichteter ungerichteter Graph gelesen:

```text
G = (V, E, w)
```

mit:

```text
V = Knotenmenge
E = Kantenmenge
w_ij = Kantengewicht zwischen i und j
```

Im Projektkontext wird ein höheres Gewicht als stärkere Nähe / stärkere Relation gelesen.

Für Distanzdiagnostik wird daraus eine einfache Kostenfunktion:

```text
c_ij = 1 / |w_ij|
```

mit numerischer Sicherung gegen Division durch Null.

Das ist keine physikalische Metrik, sondern ein Proxy-Abstand für Graphdiagnostik.

---

### 6.2 Kürzeste-Wege-Distanzen

Aus den Kantenkosten wird eine Graphdistanz berechnet:

```text
D_ij = kürzeste Pfadlänge zwischen i und j
```

Formal:

```text
D_ij = min_P sum_(a,b in P) c_ab
```

wobei `P` über alle Pfade von `i` nach `j` läuft.

Diese Distanzen sind die Grundlage für mehrere Geometry-Proxys.

---

### 6.3 Triangle Defects

Die Dreiecksungleichung lautet:

```text
D_ij <= D_ik + D_kj
```

Ein Triangle Defect liegt vor, wenn:

```text
D_ij > D_ik + D_kj + tolerance
```

BMC-15e behandelt all-zero Tie Cases korrekt:

```text
observed = 0
control_min = 0
control_max = 0
→ observed_geometry_control_equivalent
```

Im refined readout waren alle Triangle-Defect-Vergleiche äquivalent:

```text
triangle_defects:
  observed_geometry_control_equivalent = 36
```

Lesart:

```text
Die getesteten observed- und Kontrollgraphen sind in diesem Sanity-Check gleichwertig.
Das beweist keine physikalische Metrik.
```

---

### 6.4 Embedding Stress

Embedding Stress misst, wie gut die Graphdistanzen in einen niedrigdimensionalen euklidischen Raum eingebettet werden können.

Ziel:

```text
Finde Koordinaten x_i in R^d,
sodass ||x_i - x_j|| ungefähr D_ij ist.
```

Der normalisierte Stress wird im Runner sinngemäß als:

```text
stress = sqrt( sum_ij (D_ij - ||x_i - x_j||)^2 / sum_ij D_ij^2 )
```

gelesen.

Interpretation:

```text
niedriger Stress = bessere niedrigdimensionale Einbettungskompatibilität
höherer Stress   = schlechtere Einbettungskompatibilität
```

Wichtig:

```text
niedriger Stress bedeutet nicht physikalische Geometrie.
Er bedeutet nur bessere Proxy-Einbettbarkeit unter dieser Diagnostik.
```

Der erste BMC-15e-Readout hatte `embedding_stress_2d/3d/4d` irrtümlich als `not_directional` einsortiert.

Der Refinement-Patch korrigierte das:

```text
embedding_stress_2d: lower_is_more_geometry_like
embedding_stress_3d: lower_is_more_geometry_like
embedding_stress_4d: lower_is_more_geometry_like
```

Das war ein Label-Patch, keine neue Numerik.

---

### 6.5 Negative Eigenvalue Burden

Aus der Distanzmatrix wird über klassische MDS-Logik eine Gram-artige Matrix konstruiert.

Dazu wird die quadrierte Distanzmatrix doppelt zentriert:

```text
B = -1/2 * J D^2 J
```

mit:

```text
J = I - (1/n) 11^T
```

Wenn `B` eine saubere euklidische Gram-Matrix wäre, sollten keine starken negativen Eigenwerte auftreten.

Der Runner misst:

```text
negative_eigenvalue_burden =
  sum(|negative eigenvalues|) / sum(|all eigenvalues|)
```

Interpretation:

```text
niedriger negative_eigenvalue_burden = weniger spektrale Verletzung der euklidischen Gram-Lesart
höherer negative_eigenvalue_burden   = stärkere Abweichung von dieser Proxy-Lesart
```

Wichtig:

```text
Das ist kein universeller Geometriebeweis.
In Lorentzianen oder hyperbolischen Kontexten können indefinite Strukturen physikalisch sinnvoll sein.
Hier ist es nur ein euklidisch orientierter Geometry-Proxy.
```

---

### 6.6 Geodesic Consistency Error

Der Runner verwendet als einfache Geodesic-Consistency-Diagnostik eine Streuungsgröße der endlichen, nicht-null Geodäsie-Distanzen.

Sinngemäß:

```text
geodesic_consistency_error = std(D_ij) / mean(D_ij)
```

für endliche, positive Paarabstände.

Interpretation:

```text
niedriger Wert = homogenere geodätische Distanzstruktur
höherer Wert   = stärkere Streuung
```

Auch das ist nur ein Proxy.

---

### 6.7 Local Dimension Proxy

Der Runner berechnet eine vorsichtige dimensionsartige Graphgröße, sinngemäß:

```text
local_dimension_proxy ≈ log(n) / log(avg_distance + 1)
```

Das ist ausdrücklich keine physikalische Dimension.

Im Readout wird diese Größe als `not_directional` behandelt.

---

## 7. Originaler BMC-15e Readout

Vor dem Label-Refinement waren die Position-Label-Counts:

| Label | Count |
|---|---:|
| `not_directional` | 180 |
| `observed_within_geometry_control_range` | 66 |
| `observed_geometry_control_equivalent` | 36 |
| `observed_more_geometry_like_than_geometry_controls` | 6 |

Die 6 favorable cases lagen vollständig bei:

```text
negative_eigenvalue_burden
```

---

## 8. Label Refinement Patch

Der Patch änderte nur Labels für Embedding Stress.

Er änderte nicht:

```text
geometry_control_metrics.csv
Kontrollgraphen
Graphmetriken
Distanzen
MDS-Ergebnisse
negative-eigenvalue-Werte
triangle-defect-Werte
geodesic-Werte
```

Patch-Ergebnis:

```text
Rows total:   288
Rows changed: 108
```

Vorher:

| Label | Count |
|---|---:|
| `not_directional` | 180 |
| `observed_within_geometry_control_range` | 66 |
| `observed_geometry_control_equivalent` | 36 |
| `observed_more_geometry_like_than_geometry_controls` | 6 |

Nachher:

| Label | Count |
|---|---:|
| `observed_within_geometry_control_range` | 159 |
| `not_directional` | 72 |
| `observed_geometry_control_equivalent` | 36 |
| `observed_more_geometry_like_than_geometry_controls` | 21 |

Interpretation:

```text
Die meisten gerichteten Vergleiche liegen innerhalb des Bereichs einfacher Geometry Controls.
Ein kleiner, aber sichtbarer Block liegt observed-günstiger als die getesteten Geometry Controls.
```

---

## 9. Was wurde durch den Patch sichtbar?

Durch die korrekte Directionalität von Embedding Stress kamen hinzu:

```text
embedding_stress_2d:
  5 observed_more_geometry_like_than_geometry_controls
  31 observed_within_geometry_control_range

embedding_stress_3d:
  5 observed_more_geometry_like_than_geometry_controls
  31 observed_within_geometry_control_range

embedding_stress_4d:
  5 observed_more_geometry_like_than_geometry_controls
  31 observed_within_geometry_control_range
```

Zusammen:

```text
15 Stress-Fälle observed_more_geometry_like_than_geometry_controls
93 Stress-Fälle observed_within_geometry_control_range
```

Mit den ursprünglichen 6 Spektral-Fällen ergibt das:

```text
observed_more_geometry_like_than_geometry_controls = 21
```

---

## 10. Die favorable cases

Die ursprünglichen 6 favorable cases aus dem ersten Readout lagen bei:

```text
negative_eigenvalue_burden
```

Besonders wichtig:

```text
N81_full_baseline
unweighted
3D / 4D Controls
```

Beispielwerte:

| Observed object | Control family | Dimension | Weight mode | Observed | Control min | Control median | Control max |
|---|---|---:|---|---:|---:|---:|---:|
| `N81_full_baseline` | `random_geometric_graph` | 3 | `unweighted` | 0.086625 | 0.108481 | 0.206169 | 0.247944 |
| `N81_full_baseline` | `random_geometric_graph` | 4 | `unweighted` | 0.086625 | 0.118654 | 0.216387 | 0.252915 |
| `N81_full_baseline` | `soft_geometric_kernel` | 3 | `unweighted` | 0.086625 | 0.129127 | 0.205171 | 0.259886 |
| `N81_full_baseline` | `soft_geometric_kernel` | 4 | `unweighted` | 0.086625 | 0.133147 | 0.219173 | 0.264106 |

Lesart:

```text
Der beobachtete N81_full_baseline hat in diesen Fällen einen niedrigeren negative_eigenvalue_burden
als alle getesteten einfachen Geometrie-Kontrollen.
```

Aber:

```text
Das ist ein spektraler Proxy-Befund, kein Beweis physikalischer Geometrie.
```

---

## 11. Gesamtbefund

### Befund

```text
BMC-15e MVP completed successfully.

Die beobachteten Graphobjekte wurden gegen einfache geometrische Kontrollgraphen positioniert.

Nach Readout-Refinement liegen die meisten gerichteten Vergleiche innerhalb des Geometry-Control-Bereichs.

Ein kleiner Block liegt observed-günstiger als die getesteten Geometry Controls,
insbesondere bei Embedding Stress und Negative Eigenvalue Burden.
```

### Interpretation

```text
Die observed Graphobjekte sind nicht nur besser als einfache Graph-Rewire-Nulls,
sondern bei vielen Geometry-Proxys kompatibel mit einfachen geometrisch erzeugten Kontrollgerüsten.

Das stärkt die geometry-proxy Lesart.

Es macht den Befund aber nicht eindeutig spezifisch,
weil Feature-/Family-/Copula-Nulls weiterhin viele ähnliche Proxy-Werte erzeugen können.
```

### Hypothese

```text
Die beobachteten relationalen Strukturen könnten in einem geometry-proxy-kompatiblen Regime liegen,
das nicht bloß graph-rewire-artig ist und in Teilen einfache geometrische Kontrollsignaturen berührt.

Die günstigen Stress-/Spektralstellen könnten auf eine spezifische Einbettungs-/Spektralstruktur
des N81_full_baseline hinweisen.
```

### Offene Lücken

```text
Keine physikalische Raumzeit gezeigt.
Keine physikalische Metrik rekonstruiert.
Keine Kausalstruktur getestet.
Keine Lorentz-Signatur getestet.
Keine Lichtkegelstruktur gezeigt.
Kein Kontinuumslimit gezeigt.
Feature-/Family-/Copula-Nulls bleiben ernsthafte alternative Erklärungsebene.
mutual_kNN_k3_envelope ist disconnected und vorsichtig zu lesen.
Hyperbolische Kontrollen sind im MVP noch nicht aktiv.
```

---

## 12. Verhältnis zu BMC-15b

BMC-15b sagte:

```text
Gegen Graph-Rewire-Nulls ist observed deutlich günstiger.
Gegen Feature-/Family-/Copula-Nulls ist observed oft null-typisch.
```

BMC-15e ergänzt:

```text
Gegen einfache Geometry Controls liegt observed häufig im Control-Bereich
und an einigen Stress-/Spektralstellen sogar günstiger.
```

Kombinierte konservative Lesart:

```text
Das observed geometry-proxy Verhalten ist nicht bloß Graph-Geschüttel.
Es ist oft kompatibel mit einfachen geometrischen Kontrollgerüsten.
Aber es ist weiterhin nicht eindeutig spezifisch,
weil strukturierte Feature-/Family-/Korrelations-Nulls ähnliche Werte erzeugen können.
```

---

## 13. Menschliche Kurzfassung

```text
Der Klunker liegt bei vielen Diagnostiken im Bereich absichtlich geometrischer Kontrollgerüste.

Das ist gut:
  Er sieht nicht nur besser aus als Graph-Geschüttel,
  sondern passt oft auch in den Bereich einfacher Geometrie-Kontrollen.

Und:
  An einigen Stress-/Spektralstellen liegt observed sogar günstiger
  als die getesteten Geometry Controls.

Aber:
  Das ist kein Alleinstellungsbeweis.
  Feature-/Family-/Copula-Nulls bleiben ernst.
  mutual-kNN ist disconnected.
  Hyperbolische Kontrollen fehlen noch.
  Causal/Lorentz ist nicht getestet.

Kurz:
  BMC-15e stärkt die geometry-proxy Lesart,
  aber nicht den Spacetime-Claim.
```

---

## 14. Reviewer-fähiger Absatz

```text
BMC-15e extends the BMC-15 comparison layer by adding explicitly geometry-generated control graph families. In the MVP run, the observed BMC-15 graph objects most often fall within the range of simple Euclidean-style geometry controls or show all-zero equivalence for triangle defects. After readout-label refinement, embedding-stress diagnostics are treated as directional lower-is-more-embedding-compatible proxies, increasing the number of favorable observed-vs-control comparisons. A subset of embedding-stress and negative-eigenvalue-burden comparisons is more favorable than the tested controls, especially for the N81 full baseline. This positions the observed structures as geometry-proxy compatible with simple geometry-generated scaffolds, but it does not establish physical geometry, causal structure, Lorentzian signature, or spacetime emergence. In combination with BMC-15b, the result remains informative but not uniquely specific, since feature-/family-/correlation-structured nulls can also produce similar proxy values.
```

---

## 15. Nächste sinnvolle Schritte

### 15.1 BMC-15e Result Note final aktualisieren

Die eigentliche Result Note sollte auf den refined readout umgestellt werden:

```text
observed_more_geometry_like_than_geometry_controls:
  6 → 21
```

mit klarer Angabe:

```text
15 zusätzliche Fälle stammen aus Embedding Stress.
6 Fälle stammen aus Negative Eigenvalue Burden.
```

### 15.2 Hyperbolische / hierarchische Controls prüfen

Noch nicht blind aktivieren.

Erst Spezifikation:

```text
Was genau ist der hyperbolische Kontrollgenerator?
Welche Parameter?
Wie wird Edge Count gematcht?
Wie wird Over-Tuning verhindert?
```

### 15.3 BMC-15f Envelope-Construction Sensitivity

Parallel sinnvoll:

```text
Prüfen, ob die geometry-proxy Lesart stabil bleibt,
wenn man die Hüllen-/Backbone-Konstruktion variiert.
```

### 15.4 Causal/Lorentz erst später

Causal-Set-Metriken wie Myrheim-Meyer erst nach sauberer Definition einer gerichteten Ordnung:

```text
Erst Pfeil definieren.
Dann Kausalintervalle zählen.
```

---

## 16. Abschlusssatz

```text
BMC-15e macht aus dem Klunker keine Raumzeit.
Aber BMC-15e zeigt:
Der Klunker liegt nicht nur jenseits von Graph-Geschüttel,
sondern in vielen Diagnostiken im Bereich einfacher geometrischer Kontrollgerüste
und in einigen Stress-/Spektralfällen sogar günstiger.

Das ist eine saubere, begrenzte und prüfbare Stärkung der Geometry-Proxy-Lesart.
```
