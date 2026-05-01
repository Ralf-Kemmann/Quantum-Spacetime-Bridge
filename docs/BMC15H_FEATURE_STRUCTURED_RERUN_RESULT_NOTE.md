# BMC-15h — Feature-Structured Rerun Result Note

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMC15H_FEATURE_STRUCTURED_RERUN_RESULT_NOTE.md`  
Status: Result note for BMC-15h-v1 feature-structured rerun

---

## 1. Purpose

This note documents the BMC-15h-v1 rerun after correcting the metadata mapping for the feature-structured null family.

The BMC-15h-v0 run completed technically, but the `feature_structured_shuffle` family degraded to an unrestricted node-shuffle fallback because the runner looked for a metadata column named `family`, while the actual node metadata used `node_family`.

The v1 rerun fixes this mapping:

```yaml
columns:
  node_id: "node_id"
  family: "node_family"

null_families:
  feature_structured_shuffle:
    family_column: "node_family"
```

Thus, BMC-15h-v1 evaluates a genuine node-family-preserving feature-structured shuffle rather than an unrestricted fallback.

---

## 2. Run context

Runner:

```text
scripts/run_bmc15h_structured_specificity_extension.py
```

Config:

```text
data/bmc15h_structured_specificity_extension_config.yaml
```

Output directory:

```text
runs/BMC-15h/structured_specificity_extension_open/
```

Canonical graph object:

```text
runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects/N81_full_baseline_edges.csv
```

Reference core:

```text
runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects/top_strength_reference_core_edges.csv
```

Metadata table:

```text
data/node_metadata_real.csv
```

Metadata columns used in v1:

| field name | type | description |
|---|---:|---|
| `node_id` | string | Node identifier used to align metadata with graph nodes. |
| `node_family` | string | Feature-family label used for family-preserving node shuffles. |
| `shell_index` | integer-like string | Shell or layer index associated with the node. |
| `node_label` | string | Human-readable node description. |
| `origin_tag` | string | Source or construction origin tag. |
| `comment` | string | Methodological note attached to the node. |
| `feature_shape_factor` | numeric-like string | Shape-factor feature used in the real-data feature table. |
| `feature_spectral_index` | numeric-like string | Spectral-index feature used in the real-data feature table. |

---

## 3. Warning status

After the v1 rerun, the metadata/fallback warnings disappeared.

Remaining warnings:

```text
warnings: 3

info - Optional reference envelope file not found:
runs/BMC-15f/envelope_construction_sensitivity_open/bmc15f_variant_edges.csv

info - Optional reference envelope file not found:
runs/BMC-15f1/node_aligned_envelope_sensitivity_open/bmc15f1_variant_edges.csv

info - Optional reference envelope file not found:
runs/BMC-15f2/connectedness_transition_sweep_open/bmc15f2_variant_edges.csv
```

These warnings are non-critical for the v1 interpretation because the runner constructs the tested envelope families internally. The missing files are optional reference-envelope inputs only.

---

## 4. Summary readout

The real-vs-null summary contains 108 comparison rows.

Interpretation labels:

```text
real_exceeds_tested_null_family: 86
mixed_family_dependent_result: 22
```

Breakdown by null family:

```text
degree_weight_preserving_rewire:
  real_exceeds_tested_null_family: 54

feature_structured_shuffle:
  real_exceeds_tested_null_family: 32
  mixed_family_dependent_result: 22
```

This is the first BMC-15h run in which the feature-structured null is evaluated as a genuine family-preserving structured control rather than as an unrestricted fallback.

---

## 5. Befund

BMC-15h-v1 shows that the canonical real object exceeds the tested degree-/weight-preserving rewire null family in all comparison rows assigned to that null family.

For the feature-structured shuffle, the result is mixed: the real object still exceeds the feature-structured null in a majority of rows, but the null family reproduces substantial core containment in broader or denser envelope constructions.

Most selective local constructions remain strongly real-favored. For example:

```text
degree_weight_preserving_rewire
  envelope_core_edge_containment
  mutual_knn k_2
  real = 1.0
  null_mean ≈ 0.1267
  real_minus_null_mean ≈ 0.8733
  empirical_exceedance_fraction = 0.0
  label = real_exceeds_tested_null_family

feature_structured_shuffle
  envelope_core_edge_containment
  mutual_knn k_2
  real = 1.0
  null_mean ≈ 0.1400
  real_minus_null_mean ≈ 0.8600
  empirical_exceedance_fraction = 0.0
  label = real_exceeds_tested_null_family
```

The strongest null-reproduction cases occur in broader or less selective constructions, especially feature-structured shuffle under high-k mutual-kNN and broad threshold envelopes:

```text
feature_structured_shuffle
  mutual_knn k_10 / k_15
  envelope_core_edge_containment:
    real = 1.0
    null_mean ≈ 0.8833
    real_minus_null_mean ≈ 0.1167
    empirical_exceedance_fraction ≈ 0.44
    label = mixed_family_dependent_result

  envelope_core_node_containment:
    real = 1.0
    null_mean ≈ 0.9156
    real_minus_null_mean ≈ 0.0844
    empirical_exceedance_fraction ≈ 0.44
    label = mixed_family_dependent_result
```

Broad threshold envelopes show a similar mixed-family-dependent pattern.

---

## 6. Interpretation

BMC-15h-v1 supports a construction-dependent local-core specificity indication.

The result is not a uniform specificity claim. Instead, the diagnostic separates two regimes:

1. Selective local constructions  
   Low-k mutual-kNN, smaller top-strength envelopes, and related selective constructions remain strongly real-favored. In this regime, the real object retains the compact reference-core proxy much more strongly than either tested null family.

2. Broad / dense envelope constructions  
   High-k mutual-kNN and broad threshold envelopes become less specific. In these regimes, node-family-preserving feature-structured nulls can reproduce a large fraction of core containment.

This indicates that the compact local core is not simply explained by degree-/weight-preserving rewiring. However, part of the core visibility is compatible with coarse feature-family structure when the envelope construction becomes broad enough.

Internal working image:

```text
Wenn man lokal und streng hinschaut, bleibt der echte Klunker deutlich schärfer.
Wenn man die Nebelschale breit genug macht, sammeln auch die Attrappen viel vom
Klunker mit ein.
```

---

## 7. Hypothesis

The BMC-15h-v1 result suggests that the compact BMC-15 reference-core proxy may depend on a combination of:

- local relational arrangement,
- weight-rank structure,
- feature-family organization,
- and envelope construction selectivity.

A purely degree-/weight-preserving explanation appears insufficient for the tested readouts. A coarse feature-family explanation is also insufficient in selective local constructions, but it becomes partially sufficient in broad envelope constructions.

Working hypothesis:

```text
The compact core is most diagnostic when tested through selective local
construction rules. Broad envelope constructions are less specific because
family-preserving structured nulls can recover substantial core containment.
```

---

## 8. Open gap

BMC-15h-v1 does not prove physical geometry, unique geometry recovery, or full core specificity.

Open points:

1. Core-seeded decoys remain untested.  
   These are needed to test whether a BMC-15-like compact core can be deliberately and cheaply inserted into otherwise controlled null graphs.

2. The mixed feature-structured cases require stability checks.  
   The current run uses the configured repeat count. Higher repeat counts may refine the empirical exceedance fractions.

3. Missing optional reference-envelope files should either be regenerated, deliberately removed from the config, or documented as non-required.  
   Their absence is not critical for the current internal constructions, but the warning should be resolved or intentionally accepted for a clean final run.

4. The claim remains construction-qualified.  
   The current evidence supports a methodological specificity indication under selected construction rules, not a physical-geometric proof.

---

## 9. Claim boundary

Allowed statement:

```text
BMC-15h-v1 supports a construction-dependent local-core specificity indication:
the canonical real graph exceeds degree-/weight-preserving nulls throughout and
exceeds feature-structured nulls mainly under more selective local construction
rules. Broader envelope constructions are less specific and are partially
reproduced by node-family-preserving structured nulls.
```

Not allowed:

```text
Core specificity is proven.
Feature-structured nulls are fully defeated.
A physical geometry has been recovered.
A unique spacetime geometry has been derived.
The BMC-15 core is independent of construction choices.
```

---

## 10. Recommended next step

The next diagnostic step should be a core-seeded decoy run:

```yaml
null_families:
  core_seeded_decoy:
    enabled: true
```

Purpose:

```text
Can the compact reference-core behavior be deliberately and cheaply reproduced
by inserting a small high-weight local seed into otherwise controlled null graphs?
```

Interpretation logic:

```text
If core-seeded decoys reproduce the real object easily:
  the current core metric is cheap and less specific.

If the real object still exceeds core-seeded decoys under selective local rules:
  the local-core specificity indication becomes stronger, but still remains
  methodological and construction-qualified.

If only broad envelope constructions are reproduced:
  the distinction between selective local specificity and broad-envelope
  non-specificity is reinforced.
```

Recommended follow-up note:

```text
docs/BMC15H_CORE_SEEDED_DECOY_EXTENSION_NOTE.md
```
