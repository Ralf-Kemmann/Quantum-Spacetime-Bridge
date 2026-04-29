# QSB Chat-Umzugsdatei — Stand nach BMC-15b

## Zweck

Diese Datei dient als kompakte Übergabe für einen neuen Chat.

Sie soll den aktuellen belastbaren Projektstand, die wichtigsten Begriffe, die methodische Haltung und den nächsten sinnvollen Arbeitsblock festhalten.

Projektkontext:

```text
Quantum-Spacetime-Bridge / Gravitation und RaumZeit
Arbeitslinie: robuste relationale Kern-/Hüllen-Strukturen und vorsichtige Geometry-Proxy-Diagnostik
```

---

## 1. Aktueller Kernstand

Der aktuelle belastbare Stand endet bei:

```text
BMC-15b Geometry-Proxy Null Comparison
inklusive Readout / Label Refinement Patch
```

Der wichtigste aktuelle Befund lautet:

```text
Der beobachtete N=81-Kern ist methodisch robust gegen die bisher getesteten Nullfamilien.
Die beobachteten Geometry-Proxy-Werte sind gegenüber Graph-Rewire-Nulls deutlich günstiger.
Gegen Feature-/Family-/Copula-Nulls sind die Geometry-Proxy-Werte jedoch oft null-typisch.
```

Interne Kurzform:

```text
Der Klunker glitzert geordneter als Grad-/Kantensortier-Klumpen.
Aber feature-/family-/copula-artige Nullklumpen können ebenfalls ordentlich glitzern.
```

---

## 2. Projektbild / interne Metapher

Das zentrale Arbeitsbild ist inzwischen:

```text
Eine relationale Suppe bildet einen stabilen Keim.
Dieser Keim liegt in methodenabhängigen Hüllen.
Die Frage ist nicht sofort: Ist das Raumzeit?
Die Frage ist zuerst: Ist der Keim robust?
Dann: Hat die Hülle geometry-like Ordnung?
Dann: Ist diese Ordnung spezifisch oder null-typisch?
```

Kristallisationsbild:

```text
homogene Lösung
→ Kristallisationskeim
→ erste stabile lokale Ordnung
→ Hüllenwachstum
→ Prüfung, ob echte innere Ordnung oder nur Klumpenbildung
```

Wichtige interne Begriffe:

```text
Klunker        = beobachteter robuster Kern / Kern-Hüllen-Struktur
Keim           = kompakter stabiler relationaler Kern
Hülle          = methodenabhängige Backbone-/Envelope-Struktur
Kristallordnung = geometry-like Proxy-Konsistenz
Küchenmaschine = Pipeline / Extraktionsmethode
```

---

## 3. Aktuelle methodische Kette

### BMC-12f

```text
Decision-Threshold / Dominance-Gap Sensitivity Sweep
```

Befund:

```text
N=81 baseline_all_features ist stabiler als kleinere Varianten.
Threshold-/Gap-Wackler erzeugen keinen einfachen Hard-Threshold-Artefaktbefund.
```

Konservative Lesart:

```text
N=81 ist innerhalb des getesteten sparse/local-Regimes threshold/gap-robust.
```

---

### BMC-13 / BMC-13a

```text
Alternative Backbone / Consensus-Backbone
Containment Metrics Refinement
```

Befund:

```text
Der kleine top_strength_reference-Kern ist vollständig in größeren alternativen Hüllen enthalten.
```

Wichtige Korrektur durch BMC-13a:

```text
Jaccard allein unterschätzt die Beziehung, weil kleiner Kern vs große Hülle asymmetrisch ist.
Containment ist hier die passendere Metrik.
```

Konservative Lesart:

```text
Der kompakte N=81-Referenzkern ist in allen getesteten alternativen Backbone-Konstruktionen eingebettet.
Die größere Hüllenform bleibt methodenabhängig.
```

---

### BMC-14

```text
Null-Model Feature-Control
```

Befund:

```text
Einfache Feature-randomisierte Nullmodelle rekonstruieren den beobachteten 6-Kanten-Kern nicht vollständig.
```

Wichtig:

```text
family-preserving Nulls rekonstruieren mehr als harte Randomisierung,
aber nie vollständig.
```

Lesart:

```text
Familien-/Blockstruktur trägt Signalanteile, erklärt aber den vollständigen Kern nicht.
```

---

### BMC-14d

```text
Covariance-Preserving / Structured Null Controls
```

Befund:

```text
global_covariance_gaussian: max 2/6
family_covariance_gaussian: max 3/6
weight_rank_edge_rewire: max 2/6
```

Lesart:

```text
Kovarianz-Rezept und Kantengewichtsrang bauen den beobachteten Klunker nicht vollständig nach.
```

---

### BMC-14e

```text
Degree-Preserving / Copula Structured Nulls
```

Befund:

```text
degree_preserving_edge_rewire: max 2/6
degree_weightclass_edge_rewire: max 2/6
gaussian_copula_feature_null: max 2/6
```

Rewire-Diagnostik:

```text
degree sequence preserved: 500/500
edge count preserved: 500/500
warnings: 0
```

Lesart:

```text
Hub-/Gradstruktur, Gewichtsklassen und Gaussian-Copula-Rangkorrelation rekonstruieren den vollständigen beobachteten Kern nicht.
```

---

## 4. Konsolidierter BMC-14-Stand

Nach BMC-14, BMC-14d und BMC-14e:

```text
0 / 3300 getestete Null-Replikate rekonstruieren den beobachteten 6-Kanten-N=81-Kern vollständig.
```

Maximale Teilrekonstruktion:

```text
max recovery = 3/6
```

Interpretation:

```text
Die konkrete Core-Identität ist robust gegen die getesteten Nullfamilien.
Core-in-envelope-Verhalten bleibt teilweise pipeline-generisch.
Family-/Feature-Struktur trägt Signalanteile.
```

Nicht sagen:

```text
Der Kern ist physikalisch bewiesen.
Alle Nullmodelle sind ausgeschlossen.
Das ist Raumzeit.
```

---

## 5. BMC-15a Geometry-Proxy Diagnostics

BMC-15a war bewusst:

```text
observed geometry-proxy baseline
kein Nullvergleich
keine physikalische Raumzeitbehauptung
```

Analysierte Graphobjekte:

```text
N81_full_baseline
top_strength_reference_core
maximum_spanning_tree_envelope
mutual_kNN_k3_envelope
threshold_path_consensus_envelope
```

Wichtigste Befunde:

```text
direkte Triangle defects: 0
Embedding stress: niedrig bis moderat niedrig
größere Hüllen: stabile sparse-scaffold shell-growth proxies
kompakter Core allein: zu klein/fragmentiert für standalone Geometry-Lesart
```

Lesart:

```text
Die beobachteten Hüllen zeigen geometry-like Proxy-Konsistenz.
Der Core allein ist zu klein und fragmentiert.
BMC-15b Nullvergleich bleibt zwingend.
```

---

## 6. BMC-15b Geometry-Proxy Null Comparison

BMC-15b fragte:

```text
Sind die geometry-like Proxy-Werte spezifisch,
oder zeigen Nullgraphen dieselben Werte?
```

Nullmodelle:

```text
global_covariance_gaussian
family_covariance_gaussian
weight_rank_edge_rewire
degree_preserving_edge_rewire
degree_weightclass_edge_rewire
gaussian_copula_feature_null
```

Replikate:

```text
200 pro Nullmodell
```

Vergleichsobjekte:

```text
null_N81_full
null_top_strength_core
null_maximum_spanning_tree
null_mutual_kNN_k3
```

---

## 7. BMC-15b Patch

Der erste BMC-15b-Readout hatte einen Label-Kobold:

```text
observed = 0
null = 0
wurde teils als observed_less_geometry_like_than_null gelabelt
```

Patch:

```text
BMC-15b Readout / Label Refinement Patch
```

Korrektur:

```text
all-zero observed/null tie cases = observed_null_equivalent
```

Patch änderte keine Numerik, nur Labels und Readout-Struktur.

---

## 8. Refined BMC-15b-Befund

Label counts nach Patch:

```text
feature_structured_nulls:
  more_geometry_like: 4
  null_typical: 135
  null_equivalent: 58
  less_geometry_like: 1
  not_directional: 18

graph_rewire_nulls:
  more_geometry_like: 78
  null_typical: 63
  null_equivalent: 60
  less_geometry_like: 0
  not_directional: 15
```

Starker Befund:

```text
Gegen Graph-Rewire-Nulls ist der beobachtete N81_full_baseline deutlich embedding-kompatibler.
```

Beispiele:

```text
degree_preserving_edge_rewire, N81_full_baseline stress_normalized:

observed:
  2D = 0.107
  3D = 0.063
  4D = 0.061

null median:
  2D = 0.361
  3D = 0.234
  4D = 0.167
```

Dämpfer / Nuance:

```text
Gegen Feature-/Family-/Copula-Nulls sind die beobachteten Geometry-Proxy-Werte oft null-typisch.
```

Interpretation:

```text
Das Geometry-Proxy-Signal ist informativ, aber nicht eindeutig spezifisch.
Es ist nicht bloß Graph-Rewire-/Degree-/Weight-Rank-Artefakt.
Aber Feature-/Family-/Correlation-Struktur kann ähnliche geometry-like Proxy-Werte erzeugen.
```

---

## 9. Aktueller stärkster Claim

Englisch, defensiv:

```text
BMC-15b suggests that the observed geometry-proxy behavior is not merely a generic consequence of graph rewiring or degree/weight-rank structure. The observed N81 full baseline and selected envelopes are generally more embedding-compatible than graph-rewire nulls, with lower normalized embedding stress and lower negative-eigenvalue burden. However, feature/family/correlation-structured nulls often generate geometry-proxy values in the observed range. Thus the geometry-proxy signal is informative but not uniquely specific.
```

Deutsch intern:

```text
Der Klunker glitzert geordneter als Grad-/Kantensortier-Klumpen.
Aber feature-/family-/copula-artige Nullklumpen können ebenfalls ordentlich glitzern.
```

---

## 10. Strikte Grenzen

Nicht behaupten:

```text
Wir haben Raumzeit bewiesen.
Wir haben physikalische Geometrie rekonstruiert.
Wir haben eine Metrik im physikalischen Sinn.
Wir haben Kausalstruktur.
Wir haben Kontinuum.
Alle Nullerklärungen sind ausgeschlossen.
```

Erlaubt:

```text
methodologische Robustheit
core identity robustness within tested null families
geometry-like proxy consistency
embedding compatibility
graph-rewire null comparison
feature/family/correlation contribution
```

---

## 11. Wichtige Dateien im Repo

Spezifikationen / Notes:

```text
docs/BMC14_SERIES_CONSOLIDATED_ROBUSTNESS_NOTE.md
docs/BMC14E_DEGREE_COPULA_STRUCTURED_NULLS_RESULT_NOTE.md
docs/BMC15_GEOMETRY_PROXY_DIAGNOSTICS_SPEC.md
docs/BMC15_GEOMETRY_PROXY_DIAGNOSTICS_RESULT_NOTE.md
docs/BMC15B_GEOMETRY_PROXY_NULL_COMPARISON_SPEC.md
docs/BMC15B_READOUT_LABEL_REFINEMENT_PATCH_SPEC.md
docs/BMC15B_GEOMETRY_PROXY_NULL_COMPARISON_RESULT_NOTE.md
```

Configs / Runner:

```text
data/bmc15_geometry_proxy_diagnostics_config.yaml
scripts/run_bmc15_geometry_proxy_diagnostics.py

data/bmc15b_geometry_proxy_null_comparison_config.yaml
scripts/run_bmc15b_geometry_proxy_null_comparison.py
scripts/run_bmc15b_readout_label_refinement_patch.py
```

Outputs:

```text
runs/BMC-15/geometry_proxy_diagnostics_open/
runs/BMC-15b/geometry_proxy_null_comparison_open/
```

---

## 12. Nächste sinnvolle Schritte

Empfohlene Reihenfolge:

```text
1. BMC-15d Red-Team Integration
2. Danach ggf. BMC-15c Visual/Layout Diagnostics
3. Danach BMC-15 Series Consolidated Geometry-Proxy Note
```

Warum Red-Team vor Visualisierung?

```text
BMC-15b ist gemischt.
Visualisierungen können rhetorisch stark wirken.
Vor PM-/Publikationsbildern sollte die Interpretation von außen abgeklopft werden.
```

Nächster guter Dateiname:

```text
docs/BMC15D_GEOMETRY_PROXY_RED_TEAM_INTEGRATION_NOTE.md
```

oder falls zuerst eine Gesamtzusammenfassung gewünscht ist:

```text
docs/BMC15_SERIES_GEOMETRY_PROXY_CONSOLIDATED_NOTE.md
```

---

## 13. Arbeitsmodus für neuen Chat

Bitte im neuen Chat fortfahren mit:

```text
Wir stehen nach BMC-15b refined readout und Result Note.
Nächster sinnvoller Block: BMC-15d Red-Team Integration oder BMC-15 Series Consolidated Geometry-Proxy Note.
Bitte defensiv bleiben: geometry-proxy, nicht spacetime proof.
```

Arbeitsstil:

```text
erst Spezifikation / Logik
dann Config / Runner
dann Lauf
dann Readout
dann Result Note
dann Red-Team / Konsolidierung
```

Längere Inhalte als Dateien liefern.

Repo-Struktur respektieren:

```text
docs/
data/
scripts/
runs/
```

Keine versteckten Rechnungen.
Keine versteckten Dateien.
Keine Overclaims.
