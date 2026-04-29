# BMC-04 — Distribution-Preserving Organization Scramble  
## Testlogik, I/O-Spezifikation, Felder, Outputs, Entscheidungsregeln

## Zweck

BMC-04 ist der nächste harte Test nach der Deep-Research-Außenkartierung.

Die Kernfrage lautet:

> Bleibt der bisherige Befund bestehen, wenn wir Verteilungen weitgehend erhalten, aber die **Organisation** gezielt zerstören?

Oder in der kompakten Maschinenraumform:

\[
\text{Organisation} > \text{bloße Verteilung} \; ?
\]

BMC-04 soll genau das prüfen.

Das ist ein methodischer Nachfolgetest zu BMC-01/BMC-01-SX, aber mit schärferer Kontrolle darüber,
**was** erhalten bleibt und **was** gezielt gebrochen wird.

---

## 1. Grundidee des Tests

Ausgangspunkt ist wieder eine relationale Basistabelle:

- Knoten / Supports
- Paare / Kanten
- Gewichte
- optionale Ordnungs- und Organisationsfelder

BMC-04 erzeugt daraus mehrere kontrollierte Interventionsvarianten, die jeweils bestimmte grobe Verteilungen erhalten, aber die innere Organisation unterschiedlich stark umbauen.

Nicht mehr nur:

- shell-preserving
- shell-crossing

sondern eine **Stufenleiter von Erhaltungsklassen**.

---

## 2. Zentrale Hypothese

Die zentrale Testhypothese lautet:

### H_BMC04
Wenn bridge-relevante Struktur tatsächlich an der **Organisation** der gewichteten Relationen hängt, dann führen Interventionsvarianten mit gleicher oder fast gleicher Verteilung, aber zerstörter Organisation zu signifikanten Verschiebungen der arrangement-sensitiven Readouts.

Formal in Arbeitsform:

\[
\Delta_{\text{organization-broken}} > 0
\quad\text{bei}\quad
\Delta_{\text{distribution-preserved}} \approx 0.
\]

Die stärkere Form lautet:

\[
A_{\text{organization scramble}}
>
A_{\text{distribution-preserving control}}
\]

wobei \(A\) der bisherige arrangement signal score oder dessen Nachfolger ist.

---

## 3. Testfamilie und Varianten

BMC-04 ist keine einzelne Intervention, sondern eine Familie kontrollierter Varianten.

## 3.1 Variante V0 — Baseline
Keine Intervention.

Zweck:
- Referenzzustand
- Ursprung aller Vergleichsgrößen

---

## 3.2 Variante V1 — Weight multiset preserved only
Erhalten bleibt nur das Multiset der Gewichte:

\[
\{w(p)\}_{p\in E}^{\mathrm{multiset}}
\]

aber die Zuordnung der Gewichte zu Paaren wird frei permutiert.

### Gebrochen wird
- lokale Nachbarschaftspassung
- Shell-Zuordnung
- Block-/Mesostruktur
- paarbezogene Ordnung

### Zweck
Härtester erster Test dafür, ob bloße Gewichtsverteilung schon reicht.

---

## 3.3 Variante V2 — Degree + weight preserved
Erhalten bleiben:
- Kantenzahl pro Knoten (so weit die Interventionslogik das erlaubt)
- Gewichtsmultiset

Je nach technischer Umsetzung:
- entweder fixe Graphstruktur plus Gewichtspermutation
- oder degree-preserving rewiring plus neue Gewichtszuteilung

### Zweck
Testet, ob Gradstruktur plus Verteilung genügen.

---

## 3.4 Variante V3 — Degree + strength + weight preserved
Erhalten bleiben:
- Degree-Sequenz
- Strength-Sequenz
- Gewichtsmultiset

mit

\[
s(v)=\sum_{p\in E: v\in p} w(p).
\]

### Zweck
Sehr wichtige Zwischenstufe:
Wenn selbst unter Erhalt von Degree und Strength die Struktur kippt, spricht das stark gegen die These, dass nur grobe Knotensummen relevant sind.

---

## 3.5 Variante V4 — Degree + strength + shell counts preserved
Erhalten bleiben:
- Degree-Sequenz
- Strength-Sequenz
- Gewichtsmultiset
- grobe Shell-Besetzungen oder Shell-Kantenhäufigkeiten

Aber innerhalb dieser Constraints wird die Organisation umgebaut.

### Zweck
Testet, ob Shell nur als Histogramm / Besetzungsstatistik reicht oder ob die **interne Shell-Organisation** zählt.

---

## 3.6 Variante V5 — Degree + strength + block counts preserved
Erhalten bleiben:
- Degree-Sequenz
- Strength-Sequenz
- Gewichtsmultiset
- Block-/Mesostruktur-Zählungen aus einer extern inferierten Partition

z. B. DCSBM / nested SBM.

### Zweck
Vergleich Shell-vs-Block als Organisationsträger.

---

## 4. Operationaler Testkern

Der eigentliche Test vergleicht zwei Größenfamilien:

## 4.1 Distribution-preservation side
Wie gut wurden Verteilungen oder grobe Statistiken erhalten?

## 4.2 Organization-disruption side
Wie stark wurde die innere Organisation verändert?

BMC-04 ist erst dann informativ, wenn:

- die Erhaltungsseite stabil bleibt
- die Organisationsseite aber sichtbar driftet
- und die bridge-facing Readouts darauf reagieren

---

## 5. Eingabedaten (Input)

## 5.1 Pflichtinput

Eine CSV-Datei mit mindestens folgenden Feldern:

- `pair_id`
- `endpoint_a`
- `endpoint_b`
- `weight`

## 5.2 Empfohlene Zusatzfelder

- `shell_label`
- `local_group`
- `baseline_block_label`
- `pair_role`
- `bridge_candidate_flag`
- `boundary_flag`

Nicht alle sind für die erste Version zwingend, aber sie erhöhen die Aussagekraft.

---

## 6. Eingabeparameter (CLI / Config)

## 6.1 Pflichtparameter

- `--input`
- `--output-dir`
- `--variant`
- `--seed`

## 6.2 Empfohlene Pflichtliste für BMC-04

- `--variant`
  - `weight_multiset_preserved`
  - `degree_weight_preserved`
  - `degree_strength_weight_preserved`
  - `degree_strength_shellcount_preserved`
  - `degree_strength_blockcount_preserved`

- `--seed`
- `--n-iterations`
- `--max-attempts`

## 6.3 Optionale Parameter

- `--block-source`
  - `none`
  - `input_column`
  - `dcsbm_external`
- `--shell-source`
  - `input_column`
  - `derived`
- `--preservation-tolerance`
- `--write-pair-level-debug`
- `--write-node-level-debug`

---

## 7. Interne Hilfsgrößen

## 7.1 Degree
Für einen Knoten \(v\):

\[
d(v)=|\{p\in E: v\in p\}|.
\]

## 7.2 Strength
Für einen Knoten \(v\):

\[
s(v)=\sum_{p\in E: v\in p} w(p).
\]

## 7.3 Shell occupancy
Wenn \(\sigma(v)\) das Shell-Label ist:

\[
N_{\sigma=k} = |\{v\in V:\sigma(v)=k\}|.
\]

Auf Paarniveau optional:

\[
M_{ab}=|\{(u,v)\in E : \sigma(u)=a,\sigma(v)=b\}|.
\]

## 7.4 Block occupancy
Für Blocklabels \(b(v)\):

\[
B_{ij}=|\{(u,v)\in E : b(u)=i,b(v)=j\}|.
\]

---

## 8. Erhaltungsmetriken

Diese Größen messen, ob die jeweilige Interventionsklasse ihre Versprechen einhält.

## 8.1 Weight multiset preservation score

Wenn \(w^{\uparrow}\) und \(w'^{\uparrow}\) die sortierten Gewichtslisten sind:

\[
P_w =
\begin{cases}
1, & w^{\uparrow}=w'^{\uparrow} \\
0, & \text{sonst}
\end{cases}
\]

oder robuster numerisch:

\[
P_w^{\ast}=1-\frac{\sum_i |w_i^{\uparrow}-w_i'^{\uparrow}|}{\sum_i |w_i^{\uparrow}|+\varepsilon}.
\]

---

## 8.2 Degree preservation score

\[
P_d = 1 - \frac{\sum_{v\in V}|d'(v)-d(v)|}{\sum_{v\in V}d(v)+\varepsilon}.
\]

---

## 8.3 Strength preservation score

\[
P_s = 1 - \frac{\sum_{v\in V}|s'(v)-s(v)|}{\sum_{v\in V}s(v)+\varepsilon}.
\]

---

## 8.4 Shell count preservation score

Wenn \(M\) die Shell-Paarzählmatrix ist:

\[
P_{\sigma} = 1 - \frac{\sum_{a,b}|M'_{ab}-M_{ab}|}{\sum_{a,b}M_{ab}+\varepsilon}.
\]

---

## 8.5 Block count preservation score

\[
P_b = 1 - \frac{\sum_{i,j}|B'_{ij}-B_{ij}|}{\sum_{i,j}B_{ij}+\varepsilon}.
\]

---

## 9. Organisations-Disruptionsmetriken

Diese Größen sollen gerade **nicht** erhalten bleiben, sondern Verschiebung sichtbar machen.

## 9.1 Arrangement signal score
Wie bisher bzw. kompatibel zu BMC-01/BMC-01-SX:

\[
A =
\frac{
\Delta_{\text{endpoint}}
+
\Delta_{\text{disp}}
+
\Delta_{\text{shell-rank}}
+
\Delta_{\text{pair-neigh}}
+
\Delta_{\text{shell-boundary}}
}{5}
\]

falls alle Komponenten vorliegen.

Für Varianten ohne Shell-Komponenten reduzierte Mittelung über die verfügbaren Teilterme.

---

## 9.2 Motif profile distance
Wenn \(m_k\) und \(m'_k\) Motivhäufigkeiten sind:

\[
\Delta_{\text{motif}} =
\frac{1}{K}\sum_{k=1}^{K}|m'_k-m_k|.
\]

---

## 9.3 Block organization drift

\[
\Delta_{\text{block}} =
\frac{1}{|V|}\sum_{v\in V}\mathbf{1}[b'(v)\neq b(v)]
\]

falls eine Re-Inferenz oder Blockzuordnung im Output geführt wird.

---

## 9.4 Diffusion distance
Wenn verfügbar als externer oder interner Folgeblock:

\[
\Delta_{\text{diff}}
\]

als graph diffusion distance zwischen Baseline und Perturbation.

---

## 9.5 Resistance perturbation distance
Optional:

\[
\Delta_{\text{res}}
\]

als globales graphmetrisches Störmaß.

---

## 10. Bridge-facing Reaktionsseite

BMC-04 ist dann stark, wenn die organization disruption nicht nur abstrakt wächst, sondern bridge-sensitive Readouts mitzieht.

Dafür mindestens verfolgen:

- `arrangement_signal_score`
- `bridge_signal_score`
- `pair_neighborhood_shift`
- `shell_boundary_disruption_score` (falls sinnvoll)
- optionale curvature-/diffusion-/resistance-basierte Reaktionen

---

## 11. Ausgabe-Dateien (Output)

## 11.1 Pflicht-Outputs

- `run_metadata.json`
- `run_config.json`
- `summary.json`
- `decision_summary.json`
- `intervention_table.csv`
- `preservation_summary.csv`
- `organization_disruption_summary.csv`
- `block_readout.md`

## 11.2 Empfohlene Zusatz-Outputs

- `node_level_comparison.csv`
- `pair_level_comparison.csv`
- `variant_comparison_row.csv`
- `constraint_status.json`

---

## 12. Feldlisten der Hauptoutputs

## 12.1 `preservation_summary.csv`

Pflichtfelder:
- `run_id`
- `variant`
- `seed`
- `weight_multiset_preservation_score`
- `degree_preservation_score`
- `strength_preservation_score`
- `shell_count_preservation_score`
- `block_count_preservation_score`
- `preservation_status`

## 12.2 `organization_disruption_summary.csv`

Pflichtfelder:
- `run_id`
- `variant`
- `arrangement_signal_score`
- `endpoint_load_shift_score`
- `endpoint_load_dispersion_shift_score`
- `pair_neighborhood_consistency_shift_score`
- `shell_arrangement_shift_score`
- `shell_boundary_disruption_score`
- `motif_profile_distance`
- `block_organization_drift`
- `diffusion_distance`
- `resistance_perturbation_distance`

## 12.3 `decision_summary.json`

Pflichtfelder:
- `decision_label`
- `primary_reason`
- `secondary_reason`
- `test_informativeness`
- `distribution_preservation_status`
- `organization_disruption_status`
- `bridge_response_status`

---

## 13. Entscheidungslogik

## 13.1 Test nicht informativ
Wenn die relevante Preservation-Klasse nicht gehalten wurde, z. B.

\[
P_w < \theta_w
\]

oder

\[
P_d < \theta_d
\]

oder

\[
P_s < \theta_s
\]

je nach Variante, dann:

- `decision_label = test_not_informative`

### Grund
Dann wurde nicht nur Organisation verändert, sondern die Kontrollbedingung ist gerissen.

---

## 13.2 Organization-sensitive support
Wenn die Preservation-Seite stabil bleibt, aber organization disruption klar ansteigt und bridge-facing Readouts mitziehen:

- `decision_label = organization_sensitive`

### Arbeitslogik
Zum Beispiel:

\[
P_{\text{required}} \approx 1
\quad\text{und}\quad
A > \theta_A
\quad\text{und}\quad
\Delta_{\text{bridge}} > \theta_B
\]

---

## 13.3 Distribution-dominant or weakly informative
Wenn trotz harter Organisationsumbauten die Readouts kaum reagieren:

- `decision_label = distribution_dominant_or_weak`

### Interpretation
Entweder:
- Organisation ist doch weniger tragend als gedacht
- oder die verwendeten Organisationsmetriken greifen noch nicht tief genug

---

## 13.4 Ambiguous
Wenn Preservation nur teilweise erfüllt ist und die Reaktion uneindeutig:

- `decision_label = ambiguous`

---

## 14. Empfohlene Schwellwerte für erste Version

Nicht als Endwahrheit, sondern als erste plausible Arbeitswerte:

- \(\theta_w = 0.999\)
- \(\theta_d = 0.999\) für degree-preserving Varianten
- \(\theta_s = 0.98\) oder strenger, je nach Konstruktion
- \(\theta_A = 0.15\) als erste Lesbarkeitsgrenze analog zur bisherigen Probeerfahrung

Die finalen Schwellen sollen aber empirisch an Trockenläufen kalibriert werden.

---

## 15. Minimaler Variantenplan für die erste Testserie

Wenn wir BMC-04 schlank starten wollen, reicht zuerst:

### Serie S1
- `weight_multiset_preserved`
- `degree_strength_weight_preserved`
- `degree_strength_shellcount_preserved`

mit jeweils:
- `low`
- `medium`
- `high`

### Vergleichslogik
Wenn bei steigender organisatorischer Zerstörung und stabiler Preservation gilt:

\[
A_{\text{S1-low}}
<
A_{\text{S1-medium}}
<
A_{\text{S1-high}}
\]

und gleichzeitig die Verteilungen kontrolliert bleiben, dann wäre das ein starker Befund zugunsten der Organisationshypothese.

---

## 16. Wichtigste Interpretation

BMC-04 ist kein Test auf „welche Theorie stimmt“, sondern auf:

> wie viel der bisherigen Beobachtung wirklich in der Organisation der gewichteten Relationen sitzt.

Der Test ist damit ein zentraler Brückenschritt zwischen:

- BMC-01/BMC-01-SX
- der Deep-Research-Kartierung
- und einer späteren Minimalgesetz-Frage

---

## 17. Kurzfassung für die direkte Umsetzung

### Kernsatz
BMC-04 soll Verteilungen erhalten, aber Organisation gezielt zerstören.

### Entscheidende Frage
Reagieren die bridge-facing Readouts trotzdem stark?

### Minimalformel
\[
\Delta_{\text{organization-broken}} > 0
\quad\text{bei}\quad
\Delta_{\text{distribution-preserved}} \approx 0
\]

### Schärfste Maschinenraumformel
\[
\text{Organisation} > \text{bloße Verteilung} \; ?
\]

---

## Bottom line

BMC-04 ist der richtige nächste Test, weil er eure derzeit stärkste Behauptung direkt angreift.

Er verbindet:
- Deep-Research-Methodeninput
- BMC-/BMC-SX-Erfahrung
- und die Kernfrage nach der Tragfähigkeit von Organisation

in einer einzigen kontrollierten Probe.

Die stärkste erste Serie wäre:

- `weight_multiset_preserved`
- `degree_strength_weight_preserved`
- `degree_strength_shellcount_preserved`

mit low/medium/high-Stärke und klarer Trennung zwischen
- Preservation-Erfolg
- Organisationsdisruption
- bridge-facing Reaktion.
