# BMC-09a – k-NN Run Bundle

## Status
Offene Implementierung für den ersten k-NN-Graph-Test auf BMC-08c-Basis.

## Zweck
Dieses Paket liefert:
- das k-NN-Build-Script
- die k-NN-Config
- die BMC-09a-Realdaten-Run-Config
- das offene Run-Script

## Graphregel
- z-standardisierte BMC-08c-Features
- euklidische Distanz
- symmetrischer k-NN-Graph
- `k = 2, 3, 4` werden gebaut
- der erste eigentliche Lauf ist in der Run-Config auf `k = 3` gesetzt

## Zusätzliche Outputs
Unter `data/bmc09a_knn_inputs/`:
- `k_2/`
- `k_3/`
- `k_4/`
- `graph_build_diagnostics.csv`

## Befund
Noch keiner. Dieses Paket behauptet keinen Lauf.

## Interpretation
BMC-09a verschiebt den Fokus von Featurevariation zu lokaler Nachbarschaftsstruktur.

## Hypothese
Wenn der Vollgraph bisher zu stark geglättet hat, sollte ein lokaler k-NN-Graph ein schärferes Muster zeigen.

## Offene Lücke
Nach dem Lauf sollten zuerst gelesen werden:
- `data/bmc09a_knn_inputs/graph_build_diagnostics.csv`
- `runs/BMC-09/BMC09a_realdata_open/readout.md`
- `runs/BMC-09/BMC09a_realdata_open/backbone_variant_summary.csv`
- `runs/BMC-09/BMC09a_realdata_open/summary.json`
