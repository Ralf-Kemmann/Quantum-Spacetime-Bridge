# QSB-BRIDGE-DATA-02D Diagnostic Separation Plan

## 1. Purpose

QSB-BRIDGE-DATA-02D is planned as a synthetic/reference-style diagnostic separation block for the carbon bonding-organization scaffold line.

The block will run transparent scaffold-level diagnostics on:

```text
DATA-02B original carbon bonding-organization ladder:
  ethyne
  benzene
  C60
  adamantane

DATA-02C control klunkers:
  32 controls
  8 control families
```

The purpose is to test whether simple diagnostics can separate the original bonding-organization scaffold systems from control klunkers, or whether controls mimic the original too easily.

DATA-02D tests diagnostic separability, not physical truth.

It must explicitly make no claim of:

```text
real-data validation
molecular validation
physical validation
spacetime emergence
proof that electronic configurations or bonding organization are recognized
```

Poor separation, low original/control contrast, or control mimicry must be treated as a valid negative or boundary finding.

## 2. Inputs

The later runner should use only existing local scaffold/control artifacts:

```text
data/QSB-BRIDGE-DATA-02B/carbon_ladder_nodes.csv
data/QSB-BRIDGE-DATA-02B/carbon_ladder_edges.csv
data/QSB-BRIDGE-DATA-02B/carbon_bonding_organization_manifest.json
data/QSB-BRIDGE-DATA-02C/control_nodes.csv
data/QSB-BRIDGE-DATA-02C/control_edges.csv
data/QSB-BRIDGE-DATA-02C/control_ensemble_manifest.json
runs/QSB-BRIDGE-DATA-02C/control_ensembles_open/organization_coherence_summary.csv
```

These are synthetic/reference-style inputs only. They are not measured molecular data.

DATA-02C warnings to carry forward:

```text
highest-risk mimic control:
  within_system_label_shuffle__ethyne

lowest original/control coherence contrast:
  within_system_label_shuffle__adamantane

zero original/control contrast cases exist.
```

## 3. Proposed output files

Planned static files:

```text
docs/QSB_BRIDGE_DATA_02D_DIAGNOSTIC_SEPARATION_PLAN.md
docs/QSB_BRIDGE_DATA_02D_RESULT_NOTE.md
data/QSB-BRIDGE-DATA-02D/README.md
data/QSB-BRIDGE-DATA-02D/diagnostic_separation_config.json
scripts/qsb_bridge_data02d_diagnostic_separation.py
```

Planned generated data files:

```text
data/QSB-BRIDGE-DATA-02D/diagnostic_manifest.json
data/QSB-BRIDGE-DATA-02D/original_diagnostic_summary.csv
data/QSB-BRIDGE-DATA-02D/control_diagnostic_summary.csv
data/QSB-BRIDGE-DATA-02D/original_vs_control_separation.csv
data/QSB-BRIDGE-DATA-02D/highest_risk_mimic_diagnostic.csv
data/QSB-BRIDGE-DATA-02D/diagnostic_component_weights.csv
```

Planned run artifacts:

```text
runs/QSB-BRIDGE-DATA-02D/diagnostic_separation_open/summary.json
runs/QSB-BRIDGE-DATA-02D/diagnostic_separation_open/readout.md
runs/QSB-BRIDGE-DATA-02D/diagnostic_separation_open/original_diagnostic_summary.csv
runs/QSB-BRIDGE-DATA-02D/diagnostic_separation_open/control_diagnostic_summary.csv
runs/QSB-BRIDGE-DATA-02D/diagnostic_separation_open/original_vs_control_separation.csv
runs/QSB-BRIDGE-DATA-02D/diagnostic_separation_open/highest_risk_mimic_diagnostic.csv
runs/QSB-BRIDGE-DATA-02D/diagnostic_separation_open/diagnostic_component_weights.csv
runs/QSB-BRIDGE-DATA-02D/diagnostic_separation_open/proxy_risk_summary.csv
runs/QSB-BRIDGE-DATA-02D/diagnostic_separation_open/resolved_config.json
```

This planning task creates only this plan file. The other listed files are for a later implementation step.

## 4. Diagnostic design

The later runner should compute transparent scaffold diagnostics:

```text
topology_signature_diagnostic
degree_distribution_diagnostic
bond_order_distribution_diagnostic
hybridization_distribution_diagnostic
sigma_pi_organization_diagnostic
local_environment_consistency_diagnostic
combined_bonding_organization_score
original_vs_control_separation_score
```

Each diagnostic must identify what kind of signal it uses:

```text
label-derived signal
topology-derived signal
degree-derived signal
bond-order-derived signal
sigma/pi-derived signal
combined organization signal
```

The combined score must be a transparent scaffold score. It must not be described as evidence of real molecular recognition.

## 5. Separation logic

For each original system and each corresponding control, DATA-02D should compute:

```text
original_combined_score
control_combined_score
original_control_delta
separation_pass_flag
mimic_risk_flag
likely_signal_source
interpretation_boundary
```

Suggested interpretation:

```text
large delta:
  diagnostic separates original from control under this scaffold scoring rule

small delta:
  control is a mimic or low-contrast boundary

zero delta:
  diagnostic has no separation under this scoring rule
```

A failed separation is not a nuisance result. It is a valid negative or boundary finding.

The later runner should explicitly report:

```text
highest-risk mimic control
lowest original/control delta
separation_pass_count
separation_fail_count
possible_negative_finding_present
```

## 6. Required CSV/JSON fields

### diagnostic_manifest.json

```text
block_id: string
run_id: string
claim_boundary: string
external_data_downloaded: boolean
input_dependencies: object
diagnostic_families: array
component_weights: object
separation_threshold: float
data02c_low_contrast_warning: string
qsb_bridge_num_05c_warning: string
future_result_discussion_requirement: string
```

### original_diagnostic_summary.csv

```text
original_system_id: string
node_count: integer
edge_count: integer
degree_distribution: string/json
component_score_topology: float
component_score_degree: float
component_score_bond_order: float
component_score_hybridization: float
component_score_sigma_pi: float
combined_bonding_organization_score: float
likely_signal_source: string
interpretation_boundary: string
```

### control_diagnostic_summary.csv

```text
control_id: string
original_system_id: string
control_family_id: string
node_count: integer
edge_count: integer
degree_distribution: string/json
component_score_topology: float
component_score_degree: float
component_score_bond_order: float
component_score_hybridization: float
component_score_sigma_pi: float
combined_bonding_organization_score: float
likely_signal_source: string
mimic_risk_flag: boolean
interpretation_boundary: string
```

### original_vs_control_separation.csv

```text
original_system_id: string
control_id: string
control_family_id: string
original_combined_score: float
control_combined_score: float
original_control_delta: float
separation_pass_flag: boolean
mimic_risk_flag: boolean
likely_signal_source: string
control_warning_carried_from_DATA02C: string
interpretation_boundary: string
```

### highest_risk_mimic_diagnostic.csv

```text
control_id: string
original_system_id: string
control_family_id: string
component_score_topology: float
component_score_degree: float
component_score_bond_order: float
component_score_hybridization: float
component_score_sigma_pi: float
combined_bonding_organization_score: float
original_control_delta: float
mimic_risk_flag: boolean
possible_negative_finding: boolean
interpretation_boundary: string
```

### diagnostic_component_weights.csv

```text
component_id: string
component_weight: float
signal_type: string
risk_boundary: string
included_in_combined_score: boolean
```

### proxy_risk_summary.csv

```text
diagnostic_or_proxy_id: string
risk_type: string
risk_level: string
interpretation_boundary: string
qsb_bridge_num_05c_warning: string
data02c_low_contrast_warning: string
```

## 7. High-risk mimic handling

DATA-02D must explicitly carry forward the DATA-02C warning:

```text
some controls show zero or low original/control contrast
```

The later runner should always include rows for:

```text
within_system_label_shuffle__ethyne
within_system_label_shuffle__adamantane
```

If either remains high-scoring or low-delta under DATA-02D diagnostics, this must be reported as a possible negative or boundary finding.

High-risk mimic controls must not be explained away. They are the point of the diagnostic separation block.

## 8. Noise and robustness warning carried forward from 05C

DATA-02D must carry forward the 05C warning:

```text
local-neighborhood sensitivity under small additive magnitude noise at 0.02
```

This means any later local-neighborhood or local-environment diagnostic must be interpreted cautiously.

If a diagnostic depends strongly on local neighborhoods, bond-local environments, or degree-local structure, the readout should state that the 05C sensitivity may affect the apparent separation boundary.

## 9. Stop/Go criteria

Suggested stop/go outcomes:

```text
go_diagnostic_separation_with_documented_boundaries:
  diagnostics separate originals from most controls and high-risk mimics are bounded

revise_diagnostics_due_to_control_mimicry:
  high-risk mimics or many controls remain too close to originals

hold_before_realdata_due_to_label_or_topology_circularity:
  apparent separation is dominated by labels, topology, or degree structure
```

Any stop/go decision remains method-level and scaffold-only.

No stop/go outcome should be read as real-data validation, molecular validation, physical validation, or spacetime emergence.

## 10. Befund / Interpretation / Hypothese / Offene Luecke / Claim Boundary template

Future result discussion should include:

```text
## Befund
Report original/control counts, component scores, separation pass/fail counts,
highest-risk mimic behavior, lowest delta, and negative finding flags.

## Interpretation
Explain whether transparent diagnostics separate originals from controls, and
which signal sources dominate. Treat poor separation as boundary evidence.

## Hypothese
State only a method-level hypothesis about diagnostic separability under
synthetic scaffold/control conditions.

## Offene Luecke
List missing real molecular data, measured normal modes, spectral data, QC
matrix outputs, inorganic comparison systems, and real K_ij proxies.

## Claim Boundary
State no real-data validation, no molecular validation, no physical validation,
no spacetime emergence, no physical metric recovery, no causal structure, no
de-Broglie confirmation, no real quantum dynamics, and no proof that electronic
configurations or bonding organization are recognized.
```

The future discussion should include a human-readable Bauchbild: originals and control klunkers are placed on the same bench, and the scanner is asked whether it is seeing organization or only labels/topology/degree.

## 11. Implementation constraints for the later runner

The later implementation must follow these constraints:

```text
New files only.
Use only docs/, data/, scripts/, and runs/.
Do not download external data.
Do not edit 04A, 05A, 05B, 05C, DATA-01, DATA-02A, DATA-02B, DATA-02C, discussion, or roadmap files.
Do not create top-level folders.
Do not run git add, git commit, git push, git reset, git clean, or rm.
Keep all claims defensive and method-level.
DATA-02D is synthetic/reference-style diagnostic testing only.
No real-data validation claim.
No molecular validation claim.
No physical validation claim.
Treat poor separation or control mimicry as a valid negative finding.
Carry forward the 05C warning.
Carry forward the DATA-02C low-contrast mimic warning.
```

The runner should also check:

```text
all input files exist and parse
all JSON outputs parse
all CSV outputs have expected headers and nonzero rows
all four original systems are present
all DATA-02C controls are present
component weights sum to 1.0 if all are included
highest-risk mimic controls are explicitly reported
git diff --check passes
```
