# BMC-09c – Mutual-kNN + Vergleich

## Status
Offene Implementierung für den Mutual-kNN-Vergleich nach BMC-09a.

## Zweck
BMC-09c prüft, ob der in BMC-09a beobachtete Backbone-Hinweis
unter einer strengeren lokalen Nachbarschaftsregel bestehen bleibt.

## Graphregel
- gleiche BMC-08c-Featuretable
- gleiche Distanzbasis
- aber Kante nur dann, wenn:
  - `j` unter den k nächsten Nachbarn von `i` liegt
  - **und**
  - `i` unter den k nächsten Nachbarn von `j` liegt

## Sweep
- `k = 2`
- `k = 3`
- `k = 4`

## Outputs
- `data/bmc09c_mutual_knn_inputs/graph_build_diagnostics.csv`
- `runs/BMC-09/BMC09c_mutual_knn_open/mutual_knn_sweep_summary.csv`
- Einzelruns:
  - `runs/BMC-09/BMC09c_mutual_k_2_realdata_open/`
  - `runs/BMC-09/BMC09c_mutual_k_3_realdata_open/`
  - `runs/BMC-09/BMC09c_mutual_k_4_realdata_open/`

## Befund
Noch keiner. Dieses Paket behauptet keinen Lauf.

## Interpretation
BMC-09c ist der direkte Vergleichstest:
symmetrischer k-NN aus BMC-09a gegen mutual-kNN.

## Hypothese
Wenn der Backbone-Hinweis aus BMC-09a robust ist, sollte er unter mutual-kNN nicht vollständig verschwinden.
Wenn er verschwindet, war der BMC-09a-Effekt möglicherweise von einseitigen Nachbarschaften getragen.

## Offene Lücke
Nach dem Lauf sollten zuerst gelesen werden:
- `data/bmc09c_mutual_knn_inputs/graph_build_diagnostics.csv`
- `runs/BMC-09/BMC09c_mutual_knn_open/mutual_knn_sweep_summary.csv`
- die Einzel-Readouts
