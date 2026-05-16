# QSB-ST Resonance Matter Signature
## PADS-01 Phase-Amplitude Decoupling Study Specification

PADS-01 gives QSB-ST a controlled way to ask whether bridge-relevant readouts depend on phase organization, amplitude/magnitude organization, their interaction, label/topology leakage, or generic graph-pipeline behavior.

Guiding principle: "Die Idee ins Licht. Die Grenzen ans Geländer. Die Details in den Maschinenraum."

## 1. Purpose

This document specifies PADS-01: Phase-Amplitude Decoupling Study for QSB-ST Resonance Matter Signature.

It is a specification only. It is not an implementation, not a result note, and not a numerical block. It translates the current status/claim taxonomy, Geometry Anchor Conditions, RMS Carrier/Stability Criteria, Causality/Entropy Anchor Note, and Red-Team Matrix into a controlled numerical test design.

## 2. Why PADS-01 is needed

The current RMS carrier hypothesis is cautiously framed as phase-coherent off-diagonal relational organization. PADS-01 is needed because a readout that appears bridge-relevant may instead be explained by amplitude-only structure, labels, topology, covariance, mimicry, or generic pipeline behavior.

PADS-01 does not test physical spacetime emergence. It does not establish RMS. It does not establish a physical carrier. It is a diagnostic decoupling study.

## 3. Current theory context

PADS-01 follows:

- Status-/Claim-Taxonomy;
- Geometry Anchor Conditions;
- RMS Carrier / Stability Criteria;
- Causality & Entropy Anchor Note;
- Red-Team Matrix.

Using the status taxonomy:

- PADS-01 is a SPECIFICATION.
- Its future outputs would be DIAGNOSTIC READOUTS / EXPLORATORY RESULTS unless separately anchored.
- Any observed stability would be "supported under tested controls", not physical validation.
- Phase-coherent off-diagonal relational structure remains a CANDIDATE CARRIER, not established.

## 4. Central test question

Does the candidate bridge-relevant structure persist because of phase-coherent off-diagonal relational organization, or can it be reproduced by amplitude-only, label/topology, covariance, or generic graph-pipeline structure?

## 5. Study design overview

PADS-01 compares the original input object with controlled variants that preserve, destroy, shuffle, or constrain phase and amplitude layers separately.

The study should report all variants, including failed and inconclusive variants. It should not select only favorable contrasts after the fact. Each diagnostic must be assigned a warning mode and an interpretation status.

## 6. Input object and decomposition

Expected input is a complex or complex-compatible correlation object `K`, or a reconstructed object with separable:

- amplitude/magnitude layer: `|K|` or `G`;
- phase layer: `arg(K)` or equivalent phase relation;
- label/family metadata where available;
- optional matter-signature descriptors;
- optional geometry/reference observables if available.

If only real-valued historical matrices are available, PADS-01 must explicitly classify which phase-like layer is reconstructed, inferred, absent, or synthetic. A synthetic phase-like layer must not be treated as the same status as an observed or model-native phase layer.

## 7. Required variants

### V0_original_full

Original full structure with amplitude and phase as available.

### V1_amplitude_only_phase_uniform

Preserve `|K| / G`, set phases to zero or a uniform reference. Tests amplitude-only structure.

### V2_phase_random_uniform

Preserve `|K| / G`, randomize phases uniformly. Tests whether amplitude plus random phase reproduces readouts.

### V3_phase_random_spectrum_matched

Preserve amplitude and match relevant spectral / covariance constraints while disrupting phase organization. This is a hard control for structured non-specific phase.

### V4_phase_preserved_amplitude_shuffled

Preserve phase relations but shuffle or resample the amplitude/magnitude layer. Tests phase-only or phase-dominant contribution.

### V5_energy_momentum_shuffled_phase

Preserve phase distribution but disrupt physical de-Broglie-consistent energy/momentum assignment. Tests de-Broglie specificity.

### V6_label_family_shuffle_phase_preserved

Preserve phase/amplitude values but shuffle labels/families where meaningful. Tests label/topology leakage.

### V7_full_random

Randomize both amplitude and phase within matched marginal constraints. Negative control.

### V8_covariance_preserving_null

Preserve covariance / spectrum / marginal constraints while disrupting specific relational organization. This can use a Gaussian-copula, spectral, or maximum-entropy style null. It may be optional in the first implementation but is part of this spec.

### V9_mimicry_reference_control

Include known high-risk mimic cases, especially `within_system_label_shuffle__adamantane` where applicable, or equivalent highest-risk mimic controls from the active dataset.

## 8. Required controls

Required controls:

- random phase;
- trivial / uniform phase;
- spectrum-matched phase control;
- energy/momentum-shuffled phase control;
- amplitude-shuffled phase-preserving control;
- label/family shuffle;
- full random control;
- covariance-preserving null;
- known mimicry control;
- optional noise/decoherence perturbation.

## 9. Candidate diagnostics

| Diagnostic | Applies to | Interpretation | Warning mode |
|---|---|---|---|
| Phase Contribution Score | phase-disrupted variants | How much readout stability/readability is lost when phase organization is disrupted while amplitude is preserved | amplitude or topology still reproduces the readout |
| Amplitude Contribution Score | amplitude-only and phase-random variants | How much readout stability/readability remains when phase is uniform or randomized | amplitude-only structure explains most of the signal |
| Phase-Amplitude Interaction Score | original versus phase-only and amplitude-only variants | Whether the full structure performs better than phase-only or amplitude-only variants | interaction score is post hoc or unstable |
| Core Persistence | cores across variants | Overlap/Jaccard/shared-edge fraction of reference core across variants | pipeline-generated core appears in all variants |
| Reference Containment | backbone and readout variants | Whether reference structure is contained across alternative backbone methods or readout modes | containment follows labels or topology |
| Geometry Readability Change | metric and Green/Poisson diagnostics | Change in metric-readable or Green/Poisson-readable diagnostics relative to original | readability survives all nulls indiscriminately |
| D_rel Stability | relational marker readouts | Whether `D_rel` remains stable across variants | `D_rel` mistaken for carrier |
| Spectrum-Matched Control Gap | spectrum-matched phase controls | Whether structured phase controls fail to reproduce original readouts | gap vanishes under structured controls |
| Covariance-Preserving Null Gap | covariance-preserving nulls | Whether covariance-preserving nulls fail to reproduce original readouts | covariance alone explains the result |
| Label Leakage / Mimicry Gap | label shuffles and mimic controls | Whether labels, families, or mimic cases reproduce readouts | mimic matches or exceeds original |
| Decoherence Sensitivity | noise/decoherence variants | Whether off-diagonal loss affects the candidate carrier readout | entropy/noise response reflects normalization only |
| Coarse-Graining Stability | scale-reduced variants | Whether structure remains meaningful or transforms predictably under scale changes | result exists only at one resolution |
| Entropy / Mutual Information Change | entropy and information readouts | Exploratory readout inspired by the Causality & Entropy Anchor Note | not thermodynamic validation |
| Relational Delay Ordering Change, if available | delay-like readouts | Optional readout for delay-order sensitivity | delay ordering is a fit artifact |

Diagnostic concepts:

- Phase Contribution: how much readout stability/readability is lost when phase organization is disrupted while amplitude is preserved.
- Amplitude Contribution: how much readout stability/readability remains when phase is uniform or randomized.
- Phase-Amplitude Interaction: whether the full structure performs better than phase-only or amplitude-only variants.
- Core Persistence: overlap/Jaccard/shared-edge fraction of reference core across variants.
- Reference Containment: whether reference structure is contained across alternative backbone methods or readout modes.
- Geometry Readability Change: change in metric-readable or Green/Poisson-readable diagnostics relative to original.
- Entropy / Mutual Information Change: exploratory readout inspired by the Causality & Entropy Anchor Note; not thermodynamic validation.
- Relational Delay Ordering Change: optional if delay-like readouts exist.

## 10. Geometry-readability readouts

PADS-01 connects to Geometry Anchor Conditions.

It should not claim physical geometry. It may test whether metric-readable or Green/Poisson-readable diagnostics survive or collapse across variants.

Relevant readouts may include:

- metric-readability score;
- Green/Poisson-readable score;
- radial dominance;
- shell stability;
- scaling exponent alpha;
- `l0` handling;
- external-anchor status, if any.

If geometry readability survives all nulls indiscriminately, the result should be treated as a pipeline artifact warning.

## 11. Carrier/stability readouts

PADS-01 connects to RMS Carrier / Stability Criteria.

It should test:

- perturbation stability;
- phase stability;
- amplitude-decoupling stability;
- null-model stability;
- anti-mimicry stability;
- coarse-graining stability if available;
- decoherence tolerance if available.

Only phase-dependent or phase-amplitude interaction outcomes, combined with strong null-model gaps and mimicry resistance, can support the phase-coherent candidate carrier under tested controls.

## 12. Causality/entropy readouts

Causality and entropy readouts are optional exploratory diagnostics:

- mutual information;
- von Neumann entropy if a density matrix is available;
- relative entropy between variants;
- spectral / graph entropy;
- coherence loss / off-diagonal loss;
- relational delay order if available.

These are exploratory readouts, not causality or entropy derivations.

## 13. Null-model and mimicry controls

PADS-01 must include strong null and mimicry controls where possible:

- random phase controls;
- uniform phase controls;
- spectrum-matched phase controls;
- energy/momentum-shuffled phase controls;
- amplitude-shuffled phase-preserving controls;
- label/family shuffles;
- covariance-preserving nulls;
- full random controls;
- known mimicry controls such as `within_system_label_shuffle__adamantane` where applicable.

Weak nulls are not enough for carrier specificity. Random/trivial controls are necessary but not sufficient.

## 14. Acceptance logic

Use cautious result categories:

- PADS-01A_phase_dependent: original differs strongly from phase-random / phase-uniform while amplitude-only does not reproduce the structure.
- PADS-01B_amplitude_dominated: amplitude-only or phase-random variants reproduce most readouts.
- PADS-01C_phase_amplitude_interaction: original exceeds both phase-only and amplitude-only variants.
- PADS-01D_label_or_topology_leakage: label/family shuffles or known mimics reproduce readouts.
- PADS-01E_pipeline_artifact_warning: full random or covariance-preserving nulls reproduce core/readability structure.
- PADS-01F_inconclusive: no stable separation across variants.

Only PADS-01A_phase_dependent or PADS-01C_phase_amplitude_interaction, combined with strong null-model gaps and mimicry resistance, would support the phase-coherent candidate carrier under tested controls. Even then, it would not establish physical carrier status.

## 15. Failure modes

Failure modes include:

- amplitude dominance;
- label/topology leakage;
- spectrum-matched null reproduces original;
- covariance-preserving null reproduces original;
- random phase reproduces original;
- geometry readability survives all nulls indiscriminately;
- entropy readouts reflect matrix size or normalization only;
- `l0` fitted post hoc;
- multiple testing / post hoc diagnostic selection;
- archival input provenance unclear.

These failures should be reported as boundary findings.

## 16. Output files and schemas

Future implementation may write outputs under:

`runs/QSB-ST-PADS-01/phase_amplitude_decoupling_open/`

This specification does not create that directory or any run output.

Proposed output files:

- `summary.json`
- `readout.md`
- `pads01_variant_summary.csv`
- `pads01_diagnostic_summary.csv`
- `pads01_pairwise_variant_contrast.csv`
- `pads01_core_persistence.csv`
- `pads01_geometry_readability.csv`
- `pads01_entropy_coherence_readouts.csv`
- `pads01_mimicry_risk_summary.csv`
- `resolved_config.json`

### pads01_variant_summary.csv

- `variant_id`: string - variant identifier.
- `variant_family`: string - original/amplitude/phase/null/mimic.
- `amplitude_status`: string - preserved/shuffled/randomized/uniform/not_applicable.
- `phase_status`: string - preserved/randomized/uniform/spectrum_matched/shuffled/not_available.
- `label_status`: string - preserved/shuffled/not_applicable.
- `covariance_status`: string - preserved/approximately_preserved/disrupted/not_applicable.
- `run_status`: string - completed/failed/skipped.
- `note`: string - short interpretation note.

### pads01_diagnostic_summary.csv

- `diagnostic_name`: string - diagnostic identifier.
- `original_value`: float - value measured on V0_original_full.
- `variant_value_mean`: float - mean value across the relevant variant family.
- `variant_value_std`: float - standard deviation across the relevant variant family.
- `contrast_to_original`: float - contrast between variant and original.
- `control_gap`: float - gap between original and control family.
- `interpretation_status`: string - supported/weak/inconclusive/warning/not_applicable.
- `warning_flag`: string - main warning mode if present.
- `note`: string - short interpretation note.

### pads01_pairwise_variant_contrast.csv

- `variant_a`: string - first variant identifier.
- `variant_b`: string - second variant identifier.
- `diagnostic_name`: string - diagnostic used for contrast.
- `contrast_value`: float - numeric contrast value.
- `effect_direction`: string - higher_in_a/higher_in_b/no_clear_difference.
- `interpretation_status`: string - supported/weak/inconclusive/warning/not_applicable.
- `note`: string - short interpretation note.

### pads01_core_persistence.csv

- `variant_id`: string - variant identifier.
- `backbone_method`: string - backbone or core extraction method.
- `edge_count`: integer - number of edges considered.
- `reference_core_edges`: integer - edge count in the reference core.
- `recovered_core_edges`: integer - edge count in the recovered core.
- `shared_edges`: integer - count of shared edges with the reference core.
- `jaccard`: float - Jaccard overlap score.
- `containment`: float - containment score.
- `interpretation_status`: string - supported/weak/inconclusive/warning/not_applicable.

### pads01_geometry_readability.csv

- `variant_id`: string - variant identifier.
- `metric_readability_score`: float - metric-readable diagnostic score.
- `green_poisson_score`: float - Green/Poisson-readable diagnostic score.
- `radial_dominance_score`: float - radial dominance score.
- `scaling_exponent_alpha`: float - fitted or predeclared scaling exponent.
- `l0_handling`: string - fixed/calibrated/derived/free/fitted/not_applicable.
- `external_anchor_used`: string - external anchor identifier or none.
- `interpretation_status`: string - supported/weak/inconclusive/warning/not_applicable.
- `warning_flag`: string - main warning mode if present.

### pads01_entropy_coherence_readouts.csv

- `variant_id`: string - variant identifier.
- `entropy_measure`: string - entropy or information measure used.
- `entropy_value`: float - measured entropy value.
- `mutual_information_value`: float - measured mutual information value where applicable.
- `coherence_measure`: float - coherence diagnostic value.
- `off_diagonal_retention`: float - retained off-diagonal structure fraction.
- `decoherence_level`: float - applied decoherence/noise level.
- `interpretation_status`: string - supported/weak/inconclusive/warning/not_applicable.
- `note`: string - short interpretation note.

### pads01_mimicry_risk_summary.csv

- `variant_id`: string - variant identifier.
- `mimic_family`: string - mimic class or control family.
- `mimic_reference`: string - specific mimic reference case.
- `mimic_similarity_score`: float - similarity to original readout.
- `exceeds_original`: boolean - whether mimic equals or exceeds the original on a key diagnostic.
- `risk_level`: string - low/medium/high/critical.
- `note`: string - short interpretation note.

### summary.json

- `block_id`: string - study block identifier.
- `status`: string - completed/failed/partial/skipped.
- `input_object`: string - input object identifier or path.
- `variant_count`: integer - number of planned variants.
- `completed_variant_count`: integer - number of completed variants.
- `primary_result_class`: string - PADS-01A/B/C/D/E/F class.
- `strongest_warning_mode`: string - strongest warning encountered.
- `phase_dependency_status`: string - supported/weak/inconclusive/warning/not_applicable.
- `amplitude_dominance_status`: string - supported/weak/inconclusive/warning/not_applicable.
- `mimicry_status`: string - low_risk/medium_risk/high_risk/inconclusive.
- `geometry_readability_status`: string - supported/weak/inconclusive/warning/not_applicable.
- `entropy_coherence_status`: string - exploratory_supported/exploratory_weak/inconclusive/not_applicable.
- `claim_boundary`: array of strings - explicit claim limits for the run.

### readout.md and resolved_config.json

- `readout.md`: human-readable summary with result class, diagnostics, warning modes, and claim boundary.
- `resolved_config.json`: exact resolved input, variant, control, diagnostic, and randomization configuration.

## 17. How PADS-01 connects to the roadmap

This document implements roadmap step 5:

1. Status-/Claim-Taxonomy
2. Geometry Anchor Conditions
3. RMS Carrier / Stability Criteria
4. Causality & Entropy Anchor Note
5. PADS-01 Spec
6. Matter Signature Canonicalization

PADS-01 operationalizes the carrier/stability criteria before canonical Matter Signature reruns are interpreted.

## 18. Compact Claim Boundary

PADS-01 does not:

- establish RMS;
- establish a physical carrier;
- prove de-Broglie uniqueness;
- validate spacetime emergence;
- derive geometry, causality, entropy, or interactions;
- replace Geometry Anchor validation;
- replace canonical Matter Signature reruns;
- provide experimental prediction.

It is a diagnostic decoupling study whose future results should be reported as exploratory or supported under tested controls, depending on the controls passed.

## 19. Recommended implementation steps

1. Identify a minimal input object with explicit amplitude/phase decomposition.
2. Predeclare variants and diagnostics.
3. Implement a smoke run on a small canonical dataset.
4. Include high-risk mimic controls.
5. Report all variants, including failures.
6. Do not interpret PADS-01 as physical validation.
