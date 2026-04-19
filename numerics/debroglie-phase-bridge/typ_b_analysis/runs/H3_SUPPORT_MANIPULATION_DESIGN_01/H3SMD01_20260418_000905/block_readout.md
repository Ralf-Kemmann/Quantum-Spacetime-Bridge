# H3_SUPPORT_MANIPULATION_DESIGN_01

## Status
completed

## Zweck
Prüfung des bislang einzigen kleinen support-side-H3-Befunds unter kontrollierter A/B/C/D-Manipulation.

## Ausgangspunkt
Source block: `N1_A1_B1_DECOUPLING`
Current numerical status: limited support-side entry only.

## Kernbefund
- baseline_first_preserved: yes
- aux_shift_detectable: yes
- aux_shift_readable: yes
- monotone_support_scaling: yes
- null_model_suppression: yes
- boundedness_preserved: yes
- overall_outcome: limited_supported

## Nullmodell-Varianten
- D1_permutation_null: -0.010398
- D2_topology_preserving_random_null: -0.009487

## Projektinterne Lesart
Defensive Einordnung des Blocks auf Basis der aktuellen Entscheidungslogik.

## Was der Block bewusst gut macht
- explizite Readability-Schwelle
- echter Nullmodelltest mit D1/D2
- monotone A/B/C-Architektur
- Replikationslogik
- kein stillschweigendes Aufblasen lokaler Befunde

## Was der Block bewusst vermeidet
- reference claim
- full hierarchy claim
- post-hoc Schwellenkosmetik
- narrative Überdehnung

## Anschlussrichtung
Replikation / Achsenvergleich / Blockabbruch / Übergang in nächsten H3-Teilblock
