# N1 Readout — Alternative Neighborhood v1

## A. Fragestellung
Prüfung der Sensitivität der aktuellen Exportklassen-Ordnung gegenüber einer alternativen Neighborhood-Definition.

## B. Konstante Baseline
- Exportklassen: negative, abs, positive
- A1: reformed rule
- B1 conflict_penalty: 1.0
- Decision logic unchanged

## C. Variierte Komponente
- Neighborhood changed from shared_endpoint to graph_distance_1

## D. Beobachteter Befund
- negative: baseline=boundary_non_launchable, alternative=boundary_non_launchable, baseline_launchable=False, alternative_launchable=False
- abs: baseline=boundary_non_launchable, alternative=boundary_non_launchable, baseline_launchable=False, alternative_launchable=False
- positive: baseline=boundary_non_launchable, alternative=boundary_non_launchable, baseline_launchable=False, alternative_launchable=False

## E. Struktursignal
- Vergleich bleibt operational; keine physikalische Privilegierung der alternativen Neighborhood wird behauptet.

## F. Offene Punkte
- Alternative neighborhood remains operational, not physically privileged.
- No direct geometry claim follows from this block.

## G. Blockurteil
- inconclusive
- No usable local shell structure was generated under either neighborhood; block is not interpretable as a regime failure.
