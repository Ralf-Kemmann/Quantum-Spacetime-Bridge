# QSB-BRIDGE-DATA-02D Diagnostic Separation Readout

## Purpose
Run a synthetic/reference-style scaffold diagnostic separation between DATA-02B originals and DATA-02C controls.

## Inputs
- data/QSB-BRIDGE-DATA-02B/carbon_ladder_nodes.csv
- data/QSB-BRIDGE-DATA-02B/carbon_ladder_edges.csv
- data/QSB-BRIDGE-DATA-02B/carbon_bonding_organization_manifest.json
- data/QSB-BRIDGE-DATA-02C/control_nodes.csv
- data/QSB-BRIDGE-DATA-02C/control_edges.csv
- data/QSB-BRIDGE-DATA-02C/control_ensemble_manifest.json
- runs/QSB-BRIDGE-DATA-02C/control_ensembles_open/organization_coherence_summary.csv

## Befund
Original systems: 4. Controls: 32 across 8 families.
Separation threshold: 0.2. Pass count: 24. Fail count: 8.
Lowest original/control delta: 0.0 for within_system_label_shuffle__adamantane.
Highest-risk mimic row: within_system_label_shuffle__adamantane.
Possible negative finding present: True.

## Interpretation
The diagnostic separates only under transparent scaffold scoring rules. Low or zero delta is treated as control mimicry or a boundary finding, not as a nuisance result.

## Hypothese
Under synthetic scaffold/control conditions, label, topology, degree, sigma/pi, and local-environment diagnostics can be used to test separability, while exposing cases where controls mimic originals.

## Offene Luecke
Missing: real molecular data, measured normal modes, spectral data, QC matrix outputs, inorganic comparison systems, and real K_ij proxies.

## Claim Boundary
No real-data validation, no molecular validation, no physical validation, no spacetime emergence, no physical metric recovery, no causal structure, no de-Broglie confirmation, no real quantum dynamics, and no proof that electronic configurations or bonding organization are recognized.

Warnings carried forward:
- local-neighborhood sensitivity under small additive magnitude noise at 0.02
- some controls show zero/low original-control contrast, especially within-system label shuffles for small/uniform systems

## Machine-readable outputs list
- summary.json
- original_diagnostic_summary.csv
- control_diagnostic_summary.csv
- original_vs_control_separation.csv
- highest_risk_mimic_diagnostic.csv
- diagnostic_component_weights.csv
- proxy_risk_summary.csv
- resolved_config.json
- data mirror: diagnostic_manifest.json
