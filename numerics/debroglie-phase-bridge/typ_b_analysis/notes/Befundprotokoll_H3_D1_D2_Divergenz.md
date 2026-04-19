# Befundprotokoll  
## H3_D1_D2_DIVERGENCE_01

## 1. Ziel des Tests
Der Block `H3_D1_D2_DIVERGENCE_01` prüft, ob die beiden Nullmodelle

- `D1 = permutation_null`
- `D2 = topology_preserving_random_null`

im aktuellen H3-Setup tatsächlich **verschiedene Nullmodellmechaniken** repräsentieren oder in der vorliegenden Datenlage praktisch kollabieren.

Der Test ist damit kein neuer H3-Hauptbefund, sondern ein **Meta-Test auf die Glaubwürdigkeit der Nullmodellprüfung**.

## 2. Ausgangspunkt
Nach dem pair-based H3-Block und nach bestandenem mixed-like-Sensitivitätstest blieb als wichtigster methodischer Angriffspunkt:

- D1 und D2 lagen numerisch relativ nah beieinander
- daraus ergab sich der Verdacht, D2 könne im aktuellen Setup nur ein anders benannter D1 sein

Der Divergenztest wurde daher auf Basis des eingefrorenen Fixed-Logic-Stands durchgeführt:

- pair-based units
- G-basierte Primärscores
- `support_like / boundary_like / mixed_like`
- `is_support = support_like`
- `is_neighbor = boundary_like`

## 3. Testarchitektur
Der Block betrachtet nur die beiden Nullmodelle:

- `D1`
- `D2`

und rechnet sie über:

### Seeds
- `101`
- `202`
- `303`
- `404`
- `505`

### Profile
- `base`
- `mild_plus`
- `mild_minus`

Pro Seed/Profil werden zwei Ebenen verglichen:

### Ebene A — algorithmische Divergenz
Vergleich der effektiven Support-Mengen unter D1 und D2.

### Ebene B — outcome-seitige Divergenz
Vergleich der resultierenden Größen wie:
- `gain_value`
- `support_sep_combined`

## 4. Hauptbefund
Der Test ergibt:

- `algorithmic_divergence_detected = true`
- `outcome_divergence_detected = true`
- `practical_collapse_detected = false`
- `final_assessment = distinct_nullmodels`

Das ist der zentrale Befund dieses Blocks.

## 5. Algorithmische Divergenz
Die effektiven Support-Mengen unter D1 und D2 unterscheiden sich deutlich.

### Zentralwerte
- `median_jaccard_support = 0.230769`

Das bedeutet:
Die Überlappung der effektiven Support-Mengen liegt im Median nur bei etwa **23 % relativ zur Vereinigungsmenge**.

Zusätzlich zeigen die Assignment-Vergleiche:

- `changed_assignment_fraction_D1_vs_D2` liegt typischerweise bei
  - `0.444444`
  - oder `0.555556`

Das heißt:
Zwischen etwa **44 % und 56 %** der Zuordnungen unterscheiden sich zwischen D1 und D2.

### Methodische Lesart
D1 und D2 sind damit **algorithmisch klar getrennt**.  
Sie erzeugen nicht dieselbe effektive Support-Struktur.

## 6. Outcome-seitige Divergenz
Auch auf Ebene der resultierenden Größen sind Unterschiede sichtbar.

### Zentralwerte
- `median_delta_gain_D2_minus_D1 = -0.000544`
- `median_delta_support_sep_combined_D2_minus_D1 = 0.0`

Im Median bleiben die Unterschiede klein.  
Auf Einzelfallebene zeigen sich jedoch klare Abweichungen.

### Beispiele
- Seed `202`: `delta_gain_D2_minus_D1 = +0.014697`
- Seed `303`: `delta_gain_D2_minus_D1 = +0.008410`
- Seed `404`: `delta_gain_D2_minus_D1 = -0.011320`
- Seed `505`: `delta_gain_D2_minus_D1 = -0.012331`

### Methodische Lesart
D1 und D2 sind nicht nur algorithmisch verschieden, sondern führen auch zu **nichttrivial unterschiedlichen Outcome-Werten**, auch wenn diese Unterschiede im Median nicht groß sind.

## 7. Kein praktischer Kollaps
Ein praktischer Kollaps wäre dann gegeben, wenn:

- die effektiven Support-Mengen nahezu identisch wären
- und die Outcome-Werte praktisch zusammenfielen

Das ist hier ausdrücklich **nicht** der Fall.

Die Kombination aus
- niedriger Jaccard-Ähnlichkeit,
- hoher Änderungsquote der Zuordnungen
- und seedabhängigen Outcome-Differenzen

spricht klar gegen einen Kollaps.

## 8. Defensive Gesamtlesart
Die defensiv angemessene Lesart lautet:

> D1 und D2 sind im aktuellen H3-Setup algorithmisch klar verschieden und outcome-seitig nicht identisch. Ein praktischer Kollaps der beiden Nullmodelle wurde nicht gefunden. Gleichzeitig bleiben die resultierenden Null-Effekte in ähnlicher Größenordnung, sodass die Differenz eher als mechanistische als als großskalige Outcome-Trennung zu lesen ist.

## 9. Projektinterne Schlussfolgerung
Der wichtigste methodische Vorwurf gegen die Nullmodellprüfung wird durch diesen Block deutlich abgeschwächt.

Kurzform:
- D2 ist **nicht bloß D1 mit anderem Etikett**
- D1 und D2 erzeugen deutlich verschiedene effektive Support-Mengen
- ihre Wirkung bleibt in dieser Datenlage oft in derselben Größenordnung, aber nicht identisch

Damit ist die Nullmodellprüfung methodisch glaubwürdiger als zuvor.

## 10. Was der Test ausdrücklich **nicht** zeigt
Der Test zeigt **nicht**:
- dass D2 bereits maximal adversarial definiert ist
- dass D2 der bestmögliche harte Nulltest ist
- dass große Outcome-Differenzen zwischen D1 und D2 zwingend vorliegen müssten

Er zeigt nur:
- D1 und D2 sind verschieden gebaut
- sie kollabieren praktisch nicht
- ihre Wirkungen liegen im aktuellen Setup teilweise nah beieinander

## 11. Offene Folgefrage
Nach diesem Test bleibt als sinnvolle Folgefrage:

> Reicht die aktuelle D2-Definition als harter Nulltest bereits aus, oder sollte D2 künftig noch adversarialer konstruiert werden, um support-side Korrelation gezielter zu zerstören?

Das ist jedoch eine **Weiterentwicklung des Nullmodells**, nicht mehr die Klärung, ob D1 und D2 aktuell dasselbe tun.

## 12. Aktuelle Arbeitsformel
Der Block kann intern derzeit so verbucht werden:

> **D1 und D2 sind im aktuellen H3-Setup als unterschiedliche Nullmodelle zu bewerten. Sie unterscheiden sich deutlich in den effektiven Support-Zuordnungen und kollabieren praktisch nicht, auch wenn ihre Outcome-Effekte häufig in derselben Größenordnung bleiben.**

## 13. Einordnung
Das ist kein spektakulärer H3-Effekt an sich, aber ein **wichtiger methodischer Absicherungsbefund**.

Denn damit ist einer der stärksten Red-Team-Einwände nicht einfach wegdiskutiert, sondern explizit getestet worden — mit einem Ergebnis zugunsten einer echten D1/D2-Trennung.
