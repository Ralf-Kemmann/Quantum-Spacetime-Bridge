\
# QSB / Gravitation und RaumZeit — Projektstand mit lesbarer Mathematik

Stand: 2026-05-04  
Arbeitsmodus: intern, defensiv, repo-orientiert  
Statusformel: **Welle → Beziehung → Rolle → Geometrie**

---

## 0. Kurzfassung

Der aktuelle Projektstand lässt sich so zusammenfassen:

> Wir haben noch keine fertige Gravitationstheorie.  
> Wir haben aber ein zunehmend gut kontrolliertes graphbasiertes Toy-Modell, in dem lokale relationale Strukturen nicht nur als „Flecken“, sondern als **rollenmarkierte Strukturklassen** untersucht werden.  
> Der bisherige C60/FU02g-Zweig zeigt: Der unkolorierte Carrier-Fleck ist selten, aber reproduzierbar; die exakte role-colored Signatur wurde in den gesicherten frühen Millionen-Patches bisher nicht reproduziert.  
> Die entscheidenden nächsten Tests sind: Coverage-Audit, Rollen-Sensitivität und externe Fullerene-/Planar-Kontrollen.

Interne Kurzform:

```text
Der Fleck ist selten.
Die Rollenfarbe ist störrischer.
Aber ob sie echter Klunker oder selbstgemalte Farbe ist,
müssen die nächsten adversarial Tests zeigen.
```

---

## 1. Die große Brückenidee

Die konzeptionelle Kette lautet:

```text
de-Broglie-artige Materiewellen
→ relationale Korrelationen
→ stabile Carrier-Patches
→ role-colored interne Struktur
→ Symmetrie-/Orbit-bewusste Strukturklasse
→ geometrisch lesbare Ordnung
```

In Kurzform:

```text
Welle → Beziehung → Rolle → Geometrie
```

Wichtig ist: Das ist derzeit **keine abgeschlossene physikalische Ableitung**, sondern eine Arbeitskette. Jeder Pfeil muss später mathematisch, numerisch und physikalisch gehärtet werden.

---

## 2. Mathematischer Kern: Beziehung statt Objektlabel

Die Grundidee ist, nicht zuerst absolute Orte zu verwenden, sondern Relationen.

Ein abstrakter Zustand oder eine lokale Struktur wird durch Beziehungen zwischen Einheiten beschrieben:

\[
K_{ij} = \langle \psi_i \mid \psi_j \rangle
\]

oder allgemeiner in der bisherigen numerischen Praxis:

\[
K_{ij} = f(x_i, x_j)
\]

wobei \(x_i\) und \(x_j\) Feature-, Rollen-, Graph- oder Strukturzustände sein können.

Eine einfache distanzartige Lesart ist:

\[
D_{ij} = -\ell_0 \log |K_{ij}|
\]

oder in numerischen Graphmodellen oft eine Gewichtung der Form:

\[
w_{ij} = \frac{1}{1 + d(x_i,x_j)}
\]

Die wichtige Idee ist nicht die einzelne Formel, sondern:

> Nähe ist nicht zuerst „Ort im Raum“, sondern kann als starke, stabile Beziehung gelesen werden.

---

## 3. Carrier: der Fleck

Ein Carrier ist im aktuellen FU02-Zweig eine zusammenhängende lokale Trägerregion im C60-Face-Graphen.

Der aktuelle Referenzcarrier hat:

```text
carrier_face_count = 17
carrier_hexagon_count = 12
carrier_pentagon_count = 5
carrier_component_count = 1
largest_carrier_component_count = 17
```

Als Menge:

```text
carrier_set =
H_07;H_09;H_11;H_12;H_13;H_14;H_15;H_16;H_17;H_18;H_19;H_20;P_07;P_08;P_09;P_10;P_11
```

Mathematisch kann man sagen:

\[
C \subset V(G), \qquad |C| = 17
\]

mit \(G\) als C60-Face-Graph und \(C\) als zusammenhängender Patch.

Der unkolorierte Test fragt:

\[
\text{Wie oft gibt es ein zusammenhängendes } C' \subset V(G), |C'|=17,
\]

das dieselbe oder nahe gleiche grobe Signatur besitzt?

Also zum Beispiel:

\[
\sigma_{\text{carrier}}(C') \approx \sigma_{\text{carrier}}(C)
\]

---

## 4. Rollenfarbe: die Botschaft im Fleck

Die Rollenfarbe ist die zusätzliche interne Struktur im Carrier.

Aktuell:

```text
mixed_core_set =
H_09;H_11;H_13;H_16;H_17;H_18;H_19;H_20

pentagon_boundary_set =
H_07;H_12;H_14;H_15;P_07;P_08;P_09;P_10;P_11
```

Rollenabbildung:

```text
mixed_core = mixed_seam_boundary_face
pentagon_boundary = hp_boundary_face
```

Mathematisch:

\[
r: C \rightarrow R
\]

mit \(R\) als Rollenmenge, zum Beispiel:

\[
R = \{\text{mixed\_core}, \text{pentagon\_boundary}\}
\]

Der role-colored Patch ist dann nicht nur \(C\), sondern:

\[
(C,r)
\]

Der entsprechende Test fragt:

\[
\sigma_{\text{role}}(C', r') \approx \sigma_{\text{role}}(C,r)
\]

Das ist härter als der unkolorierte Carrier-Test, weil jetzt nicht nur die grobe Form passt, sondern auch die innere Rollenstruktur.

Interne Merkhilfe:

```text
Carrier = Fleck.
Role-colored Carrier = Fleck mit innerer Grammatik.
```

---

## 5. Symmetrie und Orbit: nicht der Ort ist heilig

Da C60 symmetrisch ist, darf der konkrete absolute Ort nicht überinterpretiert werden.

Die Automorphismengruppe des C60-Face-Graphen hat hier:

\[
|\operatorname{Aut}(G)| = 120
\]

Ein Patch \(C\) erzeugt unter Automorphismen einen Orbit:

\[
\mathcal{O}(C) = \{g(C) \mid g \in \operatorname{Aut}(G)\}
\]

Für den role-colored Patch entsprechend:

\[
\mathcal{O}(C,r) = \{g(C,r) \mid g \in \operatorname{Aut}(G)\}
\]

Beobachtet wurde:

```text
automorphism_count_observed = 120
carrier_orbit_size_observed = 120
carrier_stabilizer_size_observed = 1
role_colored_orbit_size_observed = 120
role_colored_stabilizer_size_observed = 1
```

Das heißt:

\[
|\mathcal{O}(C)| = 120
\]

und

\[
|\operatorname{Stab}(C)| = 1
\]

Interne Übersetzung:

```text
Der konkrete Ort ist nicht heilig.
Die Strukturklasse ist der Klunker.
```

Aber: Das sagt nur etwas innerhalb dieses C60-Graphen. Es beweist keine physikalische Allgemeinheit.

---

## 6. Bisherige FU02g-Ergebnisse

### 6.1 FU02g3 Nulltests

```text
carrier_count_random_patch:
  near = 17/1000
  strict = 0/1000

type_count_preserving_patch:
  near = 35/1000
  strict = 0/1000

connected_patch_seeded:
  near = 90/1000
  strict = 0/1000

role_count_preserving_connected_patch:
  near = 95/1000
  strict = 1/1000
```

Lesart:

```text
Einfache Nullmodelle reproduzieren den Carrier selten.
Verbundenheits- und rollenbewusstere Nullmodelle kommen näher.
Strikte Treffer bleiben absent oder fast absent.
```

Claim Boundary:

```text
weak-to-moderate construction-qualified specificity against simple nulls,
not strong specificity against connected/role-aware decoys.
```

---

### 6.2 FU02g4 / FU02g4b

Bounded enumeration:

```text
enumerated_connected_patch_count = 3,682,435
enumeration_status = partial_timeout_reached
reference_is_connected = true
target_patch_size = 17
warnings_count = 0
```

Readout:

```text
carrier_signature_exact_match_count = 20
carrier_signature_near_match_count = 127

role_colored_signature_exact_match_count = 0
role_colored_signature_near_match_count = 3
```

Lesart:

```text
Der unkolorierte Fleck ist selten, aber nicht einzigartig.
Die exakte Rollenfarbe wurde in diesem bounded Run nicht reproduziert.
Near-role-colored Fälle existieren, sind aber extrem selten.
```

---

### 6.3 FU02g4c frühe orbit-reduzierte Chunks

#### Chunk 0

```text
raw_connected_patch_count_processed = 1,000,000
unique_orbit_patch_count_processed = 231,683

raw_carrier_exact = 12
raw_carrier_near = 78

raw_role_colored_exact = 0
raw_role_colored_near = 0

orbit_carrier_exact_classes = 1
orbit_carrier_near_classes = 9

orbit_role_colored_exact_classes = 0
orbit_role_colored_near_classes = 0
```

#### Chunk 1

```text
raw_connected_patch_count_processed = 1,000,000
unique_orbit_patch_count_processed = 589,796

raw_carrier_exact = 2
raw_carrier_near = 17

raw_role_colored_exact = 0
raw_role_colored_near = 0

orbit_carrier_exact_classes = 1
orbit_carrier_near_classes = 8

orbit_role_colored_exact_classes = 0
orbit_role_colored_near_classes = 0
```

#### Chunk 2

```text
raw_connected_patch_count_processed = 1,000,000
unique_orbit_patch_count_processed = 526,162

raw_carrier_exact = 6
raw_carrier_near = 26

raw_role_colored_exact = 0
raw_role_colored_near = 3

orbit_carrier_exact_classes = 1
orbit_carrier_near_classes = 8

orbit_role_colored_exact_classes = 0
orbit_role_colored_near_classes = 0
```

Kumulativ raw, Chunk 0–2:

```text
raw connected patches processed = 3,000,000

raw carrier exact = 20
raw carrier near  = 121

raw role-colored exact = 0
raw role-colored near  = 3
```

Wichtiger Aggregationshinweis:

```text
Orbit-Klassen dürfen über Chunks nicht naiv addiert werden.
Dafür braucht es kanonische Hash-Deduplizierung / Aggregationspass.
```

---

## 7. Was der Befund aktuell sagt

### Befund

```text
Der unkolorierte Carrier-Fleck tritt selten, aber wiederholt auf.
Die exakte role-colored Signatur wurde in den gesicherten frühen Chunks nicht reproduziert.
Near-role-colored Rohfälle sind extrem selten, aber nicht unmöglich.
Orbit-kanonische role-colored exact/near Treffer sind in den frühen Chunks null.
```

### Interpretation

```text
Die kombinierte role-colored Signatur erscheint unter der aktuellen Rollenzuordnung stärker eingeschränkt als die unkolorierte Carrier-Signatur.
```

### Hypothese

```text
Diagnostisch relevante relationale Information könnte nicht nur in lokaler Zugehörigkeit zu einem Carrier liegen,
sondern in der internen Rollenstruktur dieses Carriers.
```

### Offene Lücke

```text
Es ist noch ungeklärt, ob die Rollenfarbe robuste Strukturinformation ist oder ein Artefakt der gewählten Rollenzuordnung.
```

---

## 8. Red-Team-Befund

Das Red-Team-Verdikt lautet sinngemäß:

```text
Continue — aber mit klaren Korrekturen.
```

Die drei wichtigsten Kritikpunkte:

### 8.1 C60-Spezifität

Alles könnte ein Artefakt des einen C60-Face-Graphen sein.

Nächster Test:

```text
BMS-FU03a:
  alle C60-Fullerene-Isomere via buckygen / Generatorfamilie
```

### 8.2 Role-Assignment-Artefakt

Die Rollenfarbe könnte hand-crafted sein.

Nächste Tests:

```text
BMS-FU02g5:
  randomisierte Rollenzuordnungen
  alternative feste Rollenregeln
  rollenbewusste Nullmodelle
  Sensitivität gegen Role-Definition
```

### 8.3 Physik-Brücke noch metaphorisch

Die Kette:

```text
de-Broglie → Beziehung → Rolle → Geometrie
```

ist aktuell ein konzeptioneller Rahmen, keine physikalische Ableitung.

Daher muss externe Sprache streng bleiben:

```text
graph-based toy model
relational structure signal
bounded construction-qualified evidence
not spacetime derivation
not gravity proof
```

---

## 9. Deep-Research-Datenlage

Die externe Daten-/Kontrollkarte ist gut:

### 9.1 buckygen

Vorrangig für:

```text
alle C60-Fullerene-Isomere
C70/C80-Erweiterung
Dualgraphen
Automorphismen/Orbit-Kontrollen
```

Warum wichtig:

```text
Direktester Test, ob die FU02f1-Signatur spezifisch für einen C60-Graphen ist.
```

### 9.2 plantri/fullgen

Für:

```text
planare Graphen
cubische planare Graphen
Fullerene
Dual-/Face-Graph-Kontrollen
```

Warum wichtig:

```text
Testet, ob das Signal nur aus Planarität, Cubizität oder sphärischer Topologie kommt.
```

### 9.3 Program FULLERENE / Zenodo C20–C80 / CSIRO

Für:

```text
Topologie → Geometrie
XYZ-Strukturen
geometrisch optimierte Fullerene
eventuelle Moden-/Symmetrieanschlüsse
```

### 9.4 CaGe / NanoCap

Für:

```text
boundary-matched caps
nanotube caps
nanocones
Patch-/Randkontrollen
```

### 9.5 QM9S / Hessian QM9 / PCQM4Mv2 / PubChemQC

Für:

```text
chemische Negativkontrollen
ringreiche, nicht-sphärische Moleküle
Test gegen generische Chemoinformatik-Motive
```

---

## 10. Aktuelle Claim Boundary

### Nicht sagen

```text
Wir haben Raumzeit abgeleitet.
Die Rollenfarbe beweist geometrische Information.
Es gibt keine role-colored Patches.
Die FU02g4c-Enumeration ist vollständig.
Die Brücke ist physikalisch gezeigt.
```

### Sagen dürfen

```text
In einem C60-Face-Graph-Toy-Modell zeigt die aktuelle FU02g-Sequenz,
dass eine spezifische role-colored 17-Flächen-Signatur unter den bisher geprüften connected-patch-
und Orbit-Kontrollen seltener erscheint als die unkolorierte Carrier-Signatur.
Die Aussage ist bounded, konstruktionsabhängig und sensibel gegenüber der Rollendefinition.
Externe Fullerene-, planare und Rollen-Sensitivitätskontrollen sind erforderlich.
```

### Sehr gute defensive Version

```text
The current FU02/FU02g results provide bounded, construction-qualified evidence that the selected FU02f1 carrier region is not exhausted by a generic connected-patch description alone. In the tested C60 face-graph controls, the uncolored carrier signature occurs rarely but reproducibly, while the exact role-colored signature has not been reproduced in the validated early enumeration chunks. However, the dependence on the current role-assignment rule remains an open sensitivity issue, and external fullerene/planar controls are required before any broader interpretation.
```

---

## 11. Nächste Maschinenraum-Blöcke

### Block 1 — BMS-FU02g4d: Coverage and Canonical Hash Audit

Ziel:

```text
Prüfen, welche Chunks/Segments primäre lückenlose Coverage bilden.
V2-timeout samples als sekundär klassifizieren.
V3-gap-safe Segmente als primäre Fortsetzung behandeln.
```

Benötigte Outputs:

```text
runs/BMS-FU02g4c/aggregation/bms_fu02g4c_coverage_segments.csv
runs/BMS-FU02g4c/aggregation/bms_fu02g4c_summary.json
docs/BMS_FU02G4C_COVERAGE_AND_HASH_AUDIT_NOTE.md
```

Kernfelder:

```text
segment_id
skip_first_raw_patches
raw_patch_count_seen_including_skipped
next_skip
raw_connected_patch_count_processed
enumeration_status
validity_status
coverage_class
gap_before
overlap_before
canonical_hash_count
```

### Block 2 — BMS-FU02g5: Role-Assignment Sensitivity

Ziel:

```text
Prüfen, ob die Rollenfarbe robust ist oder aus der aktuellen type_preferred_role_assignment-Regel entsteht.
```

Tests:

```text
random roles within face types
random roles preserving role counts
distance-to-pentagon role rule
centrality-based role rule
spectral/community role rule
role-label permutation inside observed patch
```

### Block 3 — BMS-FU03a: External C60-Isomer Controls

Ziel:

```text
Alle C60-Fullerene-Isomere als externe adversarial controls.
```

Minimal:

```text
buckygen / prepared list
dual graphs
automorphism counts
basic metadata
uncolored carrier scan
then role-colored scan
```

### Block 4 — BMS-FU03b: Planar Non-Fullerene Controls

Ziel:

```text
Test gegen Planarität/Cubizität/Sphärentopologie als triviale Erklärungen.
```

---

## 12. Die Brücke — sauberer Status

Die Brücke ist aktuell am besten so zu formulieren:

```text
Wir untersuchen, ob stabile, rollenmarkierte relationale Strukturklassen in graphbasierten Toy-Modellen
nichttriviale Signale zeigen, die später als Kandidaten für geometrisch lesbare Ordnung dienen könnten.
```

Nicht:

```text
Wir haben gezeigt, wie Raumzeit aus de-Broglie-Wellen entsteht.
```

Besser:

```text
Die de-Broglie-Seite motiviert den Gedanken, Materie nicht als Punktobjekt,
sondern als wellenbasierte relationale Struktur zu betrachten.
Die C60/FU-Tests prüfen derzeit nur einen kleinen graphbasierten Baustein:
ob lokale Trägerregionen mit interner Rollenstruktur unter Symmetrie- und Nullmodellkontrollen unterscheidbar bleiben.
```

Interne Bildfassung:

```text
Unten wackelt die Quantenwelt als Welle.
Daraus entsteht ein Beziehungsgewusel.
In dem Gewusel bilden sich stabile Flecken.
Manche Flecken tragen innere Rollen.
Wenn diese Rollenstruktur unter Umbenennung und Kontrolle erhalten bleibt,
könnte daraus irgendwann geometrisch lesbare Ordnung werden.
```

---

## 13. Aktuelles Gesamturteil

```text
Continue — aber nicht aufblasen.
```

Was steht:

```text
ein interessantes graphbasiertes Rollenstruktur-Signal
saubere frühe Enumerationsergebnisse
gute Red-Team-Disziplin
gute externe Kontrollkarte
```

Was noch nicht steht:

```text
Robustheit gegen alternative Rollenzuordnungen
Generalisierung über andere Fullerene-Isomere
Kontrolle gegen planare Nicht-Fullerene
vollständige Coverage-/Hash-Aggregation
physikalische Ableitung von Dynamik, Metrik oder Krümmung
```

Finale interne Zusammenfassung:

```text
Der Klunker glänzt.
Jetzt prüfen wir:
Ist es Gold,
oder haben wir mit dem Rollenstift auf Kohle gemalt?
```

Finale wissenschaftliche Zusammenfassung:

```text
The project currently supports a bounded, graph-theoretic working hypothesis:
within the tested C60 face-graph setting, role-colored internal patch structure appears more restrictive than uncolored carrier membership alone. The result remains construction-dependent and requires coverage auditing, role-assignment sensitivity analysis, and external fullerene/planar controls before any broader physical interpretation is warranted.
```
