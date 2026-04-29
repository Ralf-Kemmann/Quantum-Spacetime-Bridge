# BMC-09d – Threshold / Hybrid Local Graph Run Bundle

## Status
Offene Implementierung für den Zwischenregime-Test nach BMC-09a und BMC-09c.

## Zweck
BMC-09d prüft zwei lokale Graphfamilien:
- `threshold`
- `hybrid_local`

## Fälle
### Threshold
- `tau = 0.25`
- `tau = 0.30`
- `tau = 0.35`

### Hybrid
- `k = 3, tau = 0.25`
- `k = 3, tau = 0.30`

## Outputs
- `data/bmc09d_threshold_hybrid_inputs/graph_build_diagnostics.csv`
- `runs/BMC-09/BMC09d_threshold_hybrid_open/threshold_hybrid_sweep_summary.csv`
- Einzelruns für jeden Fall

## Befund
Noch keiner. Dieses Paket behauptet keinen Lauf.

## Interpretation
BMC-09d testet das offene Zwischenregime zwischen dem permissiveren symmetrischen k-NN
und dem streng fragmentierenden mutual-kNN.

## Hypothese
Wenn ein belastbares Strukturregime existiert, sollte es eher hier auftauchen als in den beiden Extremen.

## Offene Lücke
Nach dem Lauf sollten zuerst gelesen werden:
- `data/bmc09d_threshold_hybrid_inputs/graph_build_diagnostics.csv`
- `runs/BMC-09/BMC09d_threshold_hybrid_open/threshold_hybrid_sweep_summary.csv`
- die Einzel-Readouts
