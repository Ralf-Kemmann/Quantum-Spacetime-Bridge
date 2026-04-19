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
- D1_permutation_null: -0.005667
- D2_topology_preserving_random_null: -0.005667

## Projektinterne Lesart
Support-like vs boundary-like readout with mixed pairs excluded from the hard neighbor set.

## Was der Block bewusst gut macht
- explizite Readability-Schwelle
- echter Nullmodelltest mit D1/D2
- monotone A/B/C-Architektur
- Replikationslogik
- mixed pairs are not forced into boundary-like

## Was der Block bewusst vermeidet
- reference claim
- full hierarchy claim
- post-hoc Schwellenkosmetik
- narrative Überdehnung

## Anschlussrichtung
Replikation / Achsenvergleich / Blockabbruch / Übergang in nächsten H3-Teilblock
