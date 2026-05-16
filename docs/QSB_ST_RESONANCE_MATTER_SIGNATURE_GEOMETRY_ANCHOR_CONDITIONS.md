# QSB-ST Resonance Matter Signature
## Geometry Anchor Conditions

This note gives QSB-ST a positive next test: define what would have to be true before a reconstructed relational distance can be treated as more than an internal graph/cost readout.

Guiding principle: "Die Idee ins Licht. Die Grenzen ans Geländer. Die Details in den Maschinenraum."

## 1. Purpose

This is a theory/architecture note for QSB-ST Resonance Matter Signature. It defines Geometry Anchor Conditions for reconstructed relational distances such as `D(A,B)` and `d_ij`.

It is not a result note and not a proof of physical geometry. It defines the requirements for moving from internal readability toward an externally anchored candidate distance.

## 2. Why a Geometry Anchor is needed

QSB-ST currently uses correlation-first relational structure and reconstructed distances such as:

- `d_ij = -l0 log |K_ij|`
- graph/cost distances `D(A,B)`
- `D_rel`
- Gram/Graph-derived distance readouts

These are currently candidate relational distance readouts, not physical spacetime metrics.

Geometric readability is not physical geometry. A readable graph or metric-like distance is not enough. A Geometry Anchor is required when a reconstructed distance is tied to independent, non-pipeline observables or scaling laws.

## 3. Current status of relational distance in QSB-ST

Using the status taxonomy:

- `K_ij`: DEFINITION / correlation object
- `d_ij`: DEFINITION / DIAGNOSTIC READOUT / candidate relational distance
- `D(A,B)`: DIAGNOSTIC READOUT / candidate reconstructed distance
- `D_rel`: DIAGNOSTIC READOUT / marker layer unless physically anchored
- metric-readable regime: HEURISTIC / SUPPORTED RESULT under tested conditions
- physical spacetime metric: NOT ESTABLISHED

This status discipline prevents a definition or diagnostic from being upgraded into physical geometry without additional anchoring.

## 4. Internal readability versus physical anchoring

Internal readability means that a distance-like object behaves coherently inside the pipeline. It may be stable, monotone, graph-readable, shell-readable, or useful for diagnostics.

Physical anchoring requires more. The distance-like object must be compared against independent observables, predeclared scaling laws, and null models that were not used to construct the readout.

The central distinction is:

- internal readout: useful diagnostic structure inside the model or pipeline;
- externally anchored candidate: a distance-like readout that survives independent comparison and robustness checks.

## 5. Candidate distance objects

Candidate distance objects include:

- `d_ij = -l0 log |K_ij|`, the overlap-derived distance-like definition;
- `D(i,j)` from overlap-derived costs / shortest paths;
- `D_rel` from graph-relational readouts;
- distance-like quantities from Gram/Graph cascades;
- phasengeometric delay-like quantities, if related to distance only as candidate anchors.

Each object should be classified separately. A success for one readout does not automatically validate the others.

## 6. Geometry Anchor hierarchy

### Level 0: Internal Readout

A distance-like quantity exists as part of the pipeline. No physical interpretation is made beyond diagnostic readout.

### Level 1: Metric-Readable Regime

The reconstructed distance satisfies internal consistency checks: monotonicity, stability, approximate triangle behavior where relevant, dominant-path behavior, volume-growth diagnostics, or spectral-dimension diagnostics.

### Level 2: Green/Poisson-Readable Regime

The reconstructed structure supports graph-Laplacian Green/Poisson behavior: radial dominance, shell stability, dimension-compatible scaling, and conservative potential-like readouts.

### Level 3: External Observable Anchor

The reconstructed distance correlates with independent observables not used to construct it: known geometric distances, spectroscopic or bonding distances, interaction strengths, delay readouts, potential response, field response, or other externally defined physical quantities.

### Level 4: Physical Geometry Candidate

Only if the reconstructed distance:

- is externally anchored;
- has stable scaling laws;
- survives pipeline variation;
- has controlled `l0` interpretation;
- remains compatible with relevant RT/QM constraints;
- and is not explained by null models or mimicry.

Even at this level, it should still be called a candidate, not established physical spacetime.

## 7. External observable requirements

| Observable anchor | Example | What must be compared | What it would support | Warning mode |
|---|---|---|---|---|
| known Euclidean or molecular distances | reference coordinates or known intersite distances | `D(A,B)` or `d_ij` against independent distances | externally anchored candidate distance | coordinates or distances were reused in construction |
| spectroscopic / bonding length references | bond lengths, spectral features tied to geometry | reconstructed distance against reference length scale | molecular or spectroscopic distance relevance | synthetic scaffold overread as physical validation |
| Coulomb-like potential or inverse-square scaling | potential or force-like benchmark | potential response versus reconstructed radius | candidate interaction-form anchor | apparent `1/r` fitted after the fact |
| graph-Laplacian Green/Poisson response | source-response readout on the graph | Green/Poisson behavior versus `D(A,B)` shells | Green/Poisson-Readable Regime | graph construction itself imposes the response |
| delay / phase-gradient readout | delay-like phase response | delay or phase-gradient behavior versus reconstructed distance | temporal or phasengeometric anchor candidate | delay readout is only a pipeline artifact |
| VDW interaction parameters | VDW radius, epsilon-like parameters, combined scores | VDW parameters versus distance or matter axis | candidate matter-sensitive interaction layer | VDW score mixing mistaken for physical interaction axis |
| isotope / mass-sensitive controls | isotope or mass-varied controls | distance and response stability under mass/nuclear variation | separation of geometry from mass-only effects | mass scaling explains the full readout |
| external field response | response to independently defined field or source | reconstructed distance versus field/potential response | candidate external observable anchor | field definition leaks pipeline information |
| coarse-graining / scale behavior | aggregation, scale reduction, binning | distance stability under coarse-graining | scale robustness of the anchor | signal exists only at one resolution |

## 8. Scaling-law requirements

`D(A,B)` should not only correlate qualitatively with a target. Where possible, it should satisfy a predeclared scaling law.

Examples:

- `D(A,B)` proportional to `r_AB`;
- Green/Poisson readout compatible with emergent dimension;
- inverse-square-like behavior only after dimension and radial criteria are fixed;
- delay-like readout only if the phase-gradient / energy-dependence connection is specified.

The scaling exponent alpha must not be selected after the fact without reporting that it was fitted. If a fitted exponent is used, the result should be labeled as a fit or exploratory calibration, not validation.

## 9. Role and risk of l0

`l0` is currently a scale parameter, not yet a physically established constant.

It must be either:

- fixed by convention and treated as gauge/scale choice;
- calibrated against a predeclared external observable;
- derived from deeper theory;
- or explicitly treated as a free parameter with reported sensitivity.

If `l0` is tuned post hoc to fit a desired physical distance or interaction law, the anchor becomes a fit, not validation.

## 10. Green/Poisson and Coulomb-like criteria

A Coulomb-like or Newton-like anchor must not be reduced to "we see 1/r".

It should require:

- graph-Laplacian construction defined before evaluation;
- source term specified;
- normalization specified;
- radial dominance with respect to reconstructed `D`;
- shell/flux stability where applicable;
- dimension-compatible scaling;
- comparison against null models and alternative distance readouts.

These criteria keep Green/Poisson and Coulomb-like behavior in the category of anchor conditions until external observables and robustness checks justify stronger language.

## 11. Robustness against pipeline choices

Geometry Anchor Conditions should be tested against pipeline choices, including:

- backbone method variation;
- threshold variation;
- edge-count neighborhoods;
- cost function variation;
- label/family shuffles;
- spectrum-matched / covariance-preserving nulls;
- amplitude/phase decoupling controls;
- coarse-graining;
- noise/decoherence perturbation.

If the geometric readout disappears under minor pipeline variation, it remains a pipeline-specific diagnostic rather than an externally anchored candidate.

## 12. Failure and warning modes

Failure and warning modes include:

- graph geometry artifact;
- pipeline-generated cores;
- label/topology leakage;
- `l0` overfitting;
- post hoc scaling exponent selection;
- null model too weak;
- external observable reused in construction;
- metric readability without physical anchor;
- Carbon calibration overread as molecular validation;
- VDW score mixing mistaken for physical interaction axis.

These failures are useful when reported explicitly because they prevent internal readability from being overinterpreted.

## 13. How this connects to the red-team roadmap

This document implements roadmap step 2:

1. Status-/Claim-Taxonomy
2. Geometry Anchor Conditions
3. RMS Carrier / Stability Criteria
4. Causality & Entropy Anchor Note
5. PADS-01 Spec
6. Matter Signature Canonicalization

It responds directly to the Physical Anchor Problem: a reconstructed distance must be classified, stress-tested, and externally anchored before it can support stronger geometry language.

## 14. Compact Claim Boundary

This note does not:

- establish physical geometry;
- derive spacetime;
- derive relativity;
- validate gravity;
- validate Coulomb/Newton laws from QSB-ST;
- establish `D(A,B)`, `d_ij`, or `D_rel` as physical distance;
- solve the `l0` problem;
- replace external observable anchoring, future derivation, or numerical validation.

It defines anchor conditions and claim discipline for future work.

## 15. Recommended next steps

1. Build a Geometry Anchor Status Table for current distance objects.
2. Select one external observable anchor for the next minimal test.
3. Predeclare scaling laws and `l0` handling.
4. Add spectrum-matched / covariance-preserving nulls where relevant.
5. Connect to RMS Carrier / Stability Criteria.
6. Use the result to design PADS-01 readouts.
