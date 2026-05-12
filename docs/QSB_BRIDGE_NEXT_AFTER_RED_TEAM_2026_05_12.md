# QSB Bridge Next After Red Team 2026-05-12

## 1. Purpose

This document records the accepted Red-Team criticisms after QSB-BRIDGE-NUM-04A and defines the revised next roadmap.

It is a planning and specification note only. It creates no new numerical result, no new evidence claim, and no physical validation claim.

## 2. Accepted Red-Team Criticisms After 04A

### Befund

QSB-BRIDGE-NUM-04A shows that magnitude-only distance and graph diagnostics remain invariant when `|K_ij|` is fixed and only `phi_ij` is changed.

The Red-Team criticism is accepted: this invariance is expected by definition. If `D_ij` and the threshold graph are constructed only from `|K_ij|`, pure phase changes cannot alter those outputs.

04A is therefore a definitional consistency and sanity check. It is not evidence for physical robustness.

### Interpretation

04A is useful as a reproducibility anchor and code-level separation check:

```text
Magnitude |K_ij| -> distance-like toy readout
Phase phi_ij    -> phase-sensitive toy readout
```

It does not test whether a magnitude-based geometry readout survives realistic disturbances, real quantum structure, coupled magnitude/phase dynamics, finite-size effects, or hostile null families.

### Hypothese

The next testable hypothesis is not that 04A supports a physical bridge. The revised working hypothesis is narrower:

```text
If magnitude-derived graph diagnostics are to be useful as method-level proxies,
they should survive hostile geometric controls, parameter sweeps, perturbations,
and real-data preflight checks better than intentionally misleading controls.
```

This remains a method-level hypothesis.

### Offene Lücke

The following gaps remain open after 04A:

- The magnitude invariance result is tautological for fixed `|K_ij|`.
- The tested toy graph is too friendly and too small to support robustness language.
- No hostile controls test circularity, fake geometry, near-degenerate magnitudes, node relabeling, or non-geometric correlation structure.
- No phase/gauge/flux block distinguishes gauge-like phase changes from loop-flux-sensitive phase structure.
- No real-data preflight yet tests whether the method can be attached to actual molecular or materials data.
- No quantitative failure threshold has been defined for degradation under perturbation.

### Claim Boundary

The accepted boundary is:

```text
04A is a definitional consistency/sanity check.
04A is not evidence for physical robustness.
04A does not validate QSB physically.
04A does not show spacetime emergence.
04A does not recover a physical metric.
04A does not derive causal structure.
04A does not confirm de-Broglie physics.
```

All next blocks must keep the distinction between toy construction, method-level diagnostic behavior, and physical interpretation explicit.

## 3. Revised Next Roadmap

### QSB-BRIDGE-NUM-05A: Geometric Validation & Hostile Controls

Purpose: test whether magnitude-derived distance and graph diagnostics distinguish intended geometric structure from hostile controls and misleading nulls.

This is the immediate next numerical block.

### QSB-BRIDGE-NUM-05B: Phase/Gauge/Flux Stress Test

Purpose: test phase-sensitive structure more directly, including gauge-like transformations, loop flux, magnetic/Hermitian Laplacian options, and phase perturbation ensembles.

This block should not be merged into 05A unless explicitly approved. 05A tests geometry and hostile controls first; 05B tests phase/gauge/flux behavior separately.

### QSB-BRIDGE-DATA-01: Real-data Preflight, with C60/Benzol Candidates

Purpose: identify real-data candidates and preflight whether a defensible `K_ij` or proxy matrix can be constructed without smuggling in the target geometry.

Candidate families:

```text
C60 fullerene
Benzol / benzene
possibly additional small molecules only after C60/Benzol preflight
```

This block is a preflight only. It should check data availability, provenance, definitions, and limits before any physical interpretation is attempted.

## 4. QSB-BRIDGE-NUM-05A Specification

### 4.1 Candidate Inputs

05A should use controlled synthetic inputs where the intended geometry or non-geometry is known.

Candidate geometric inputs:

```text
1D ring or chain
2D grid / torus-like grid
3D lattice subset
random geometric graph with known coordinates
```

Candidate hostile controls:

```text
permuted node labels with invariant diagnostics expected
degree-preserving or distribution-preserving randomization
near-degenerate magnitude matrix with ambiguous rank order
non-geometric block matrix with geometry-like local weights
random magnitude matrix matched on summary distribution
small Gaussian perturbations of |K_ij|
tau and l0 sweeps
n_nodes scaling sweep
```

Candidate baseline from 04A:

```text
reuse the 04A circular-distance magnitude construction only as a baseline sanity case
do not treat it as evidence
```

### 4.2 Diagnostics

Magnitude-derived diagnostics:

```text
distance_matrix_max_abs_diff_vs_baseline
rank_order_stability
threshold_graph_edge_count
threshold_graph_jaccard
shortest_path_distance_error_vs_known_geometry
nearest_neighbor_recall_vs_known_geometry
triangle_inequality_violation_rate
connected_component_count
```

Geometry validation diagnostics:

```text
coordinate_distance_correlation
distance_stress_or_mds_stress
local_neighborhood_precision
known_dimension_readout_if_applicable
spectral_dimension_proxy_if stable enough
low_eigenvalue_spectrum_summary
```

Hostile-control diagnostics:

```text
false_positive_geometry_score
control_gap_vs_geometric_baseline
noise_breakdown_threshold
parameter_sensitivity_tau
parameter_sensitivity_l0
scaling_sensitivity_n_nodes
```

All diagnostics must be reported as method-level readouts, not physical readouts.

### 4.3 Planned Output Files

Static files:

```text
docs/QSB_BRIDGE_NUM_05A_GEOMETRIC_VALIDATION_HOSTILE_CONTROLS_SPEC.md
data/qsb_bridge_num_05a_geometric_validation_config.yaml
scripts/run_qsb_bridge_num_05a_geometric_validation.py
docs/QSB_BRIDGE_NUM_05A_RESULT_NOTE.md
```

Run directory:

```text
runs/QSB-BRIDGE-NUM-05A/geometric_validation_hostile_controls_open/
```

Run artifacts:

```text
summary.json
readout.md
variant_summary.csv
control_summary.csv
pairwise_or_matrix_diagnostics.csv
parameter_sweep_summary.csv
resolved_config.json
```

Optional only if dependency-light and reproducible:

```text
diagnostic_plot.png
```

### 4.4 Stop/Go Criteria

Go criteria for carrying the method forward:

```text
geometric baselines outperform hostile controls on predefined geometry-validation diagnostics
permutation controls behave invariantly where invariance is expected
distribution-matched random controls do not receive the same geometry score as true geometric baselines
noise and parameter sweeps show a documented degradation curve rather than unreported fragility
claim boundary remains intact in result note and readout
```

Stop or revise criteria:

```text
hostile controls score as well as geometric baselines
geometry readouts depend strongly on arbitrary tau or l0 choices without a stable region
near-degenerate magnitude matrices produce unstable or misleading geometry readouts
scaling from small n to larger n changes conclusions qualitatively
diagnostics cannot distinguish known geometry from distribution-matched non-geometry
```

### 4.5 Failure Interpretation

Failure in 05A should not be treated as a project failure by default. It should be interpreted as information about the boundary of the method.

Allowed failure interpretations:

```text
The current magnitude-derived diagnostics are too weak for this control family.
The chosen parameter region is unstable.
The toy construction is too circular to support broader use.
The method requires stronger controls before real-data work.
The candidate diagnostic should be demoted or removed.
```

Disallowed failure interpretations:

```text
The physical idea is disproven.
The physical idea is proven by surviving one control.
The method is physically validated.
The hostile control is irrelevant because it is inconvenient.
```

## 5. QSB-BRIDGE-NUM-05B Outline

05B should address the Red-Team concern that phase structure is not merely decorative.

Planned components:

```text
gauge-like phase transformations
loop-closure / flux diagnostics
random phase ensembles with controlled sigma
correlated versus uncorrelated phase noise
magnetic or Hermitian Laplacian candidate diagnostics
magnitude-only versus phase-aware spectral comparison
```

Main question:

```text
Which phase changes are pure gauge-like changes, and which produce loop-flux-sensitive diagnostic changes?
```

Claim boundary:

```text
05B can test phase/gauge/flux sensitivity in toy graphs.
05B cannot establish real quantum dynamics or de-Broglie physics.
```

## 6. QSB-BRIDGE-DATA-01 Outline

DATA-01 should be a real-data preflight, not a result claim.

Candidate inputs:

```text
C60 fullerene: coordinates, adjacency, vibrational modes if available
Benzol / benzene: coordinates, adjacency, vibrational modes if available
```

Preflight questions:

```text
Which source provides the data?
What exact objects can be read as nodes?
What exact quantity could define K_ij or a proxy for K_ij?
Does the construction use true overlap/mode information, or does it merely re-encode known geometry?
Are phases available, reconstructable, or absent?
What controls can prevent circular rediscovery of input geometry?
```

Expected output of DATA-01:

```text
a candidate-source inventory
a data-definition table
a risk register for circularity and missing phase information
a go/no-go recommendation for a first real-data diagnostic
```

Claim boundary:

```text
DATA-01 is source and feasibility preflight.
It is not a real-data validation result.
```

## 7. Conservative Working Language

Preferred phrases:

```text
method-level diagnostic
definitional consistency check
hostile control
failure boundary
proxy readout
geometric baseline
distribution-matched control
real-data preflight
```

Avoid:

```text
physically validated
spacetime emergence
physical metric recovered
causal structure derived
de-Broglie confirmation
bridge to wave physics established
```

## 8. Immediate Next Step

The next implementation step, after explicit approval, should be QSB-BRIDGE-NUM-05A only.

Before coding 05A, create a file-level plan listing the exact new files, run artifacts, diagnostics, and acceptance checks. No existing result notes should be modified unless explicitly approved.
