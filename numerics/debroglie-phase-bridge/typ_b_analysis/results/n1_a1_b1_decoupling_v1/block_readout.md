# N1 Readout — A1/B1 Decoupling v1

## A. Fragestellung
Trägt die beobachtete N1-Klassifikation primär A1, primär B1 oder beide Kanäle gemeinsam?

## B. Konstante Basis
- Exportklassen: negative, abs, positive
- Pair-unit adapter: adjacency_plus_threshold
- Threshold tau: 0.025
- Baseline neighborhood: shared_endpoint
- Alternative neighborhood: graph_distance_1

## C. Beobachteter Befund
- negative: baseline dominant=b1, alternative dominant=mixed, baseline combined=structured_intermediate, alternative combined=structured_intermediate
- abs: baseline dominant=b1, alternative dominant=mixed, baseline combined=structured_intermediate, alternative combined=structured_intermediate
- positive: baseline dominant=none, alternative dominant=none, baseline combined=boundary_non_launchable, alternative combined=boundary_non_launchable

## D. Entkopplungslesart
- A1-only und B1-only werden getrennt gegen den Combined-Status gelesen.
- Dominanz wird nur diagnostisch, nicht ontologisch interpretiert.

## E. Blockurteil
- supported
- Combined N1 pattern is primarily B1-driven while A1 remains weak across launchable classes.
