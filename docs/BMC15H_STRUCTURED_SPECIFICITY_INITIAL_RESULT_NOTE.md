# BMC-15h — Structured Specificity Extension Initial Result Note

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Status: Initial diagnostic run / smoke-test plus partial structured-null readout

---

## 1. Purpose

This note records the first BMC-15h structured-specificity diagnostic run.

BMC-15h asks whether structured null families reproduce the compact-core and
envelope behavior observed in the BMC-15e/f/g geometry-proxy line.

The diagnostic question is:

```text
Do structured control families reproduce the same combination of
core containment, envelope sensitivity, and topological core robustness
seen in the canonical BMC-15/N81-derived graph object?
```

This note does not claim physical spacetime emergence, metric recovery,
Lorentzian structure, causal structure, continuum limit, or proof of specificity.

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
runs/BMC-15h/structured_specificity_extension_open
```

Primary canonical graph input:

```text
runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects/N81_full_baseline_edges.csv
```

Reference-core input:

```text
runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects/top_strength_reference_core_edges.csv
```

Both canonical graph and reference-core tables expose the required columns:

```text
source, target, weight
```

---

## 3. Inputs and construction design

The first BMC-15h run used:

```text
1 canonical real object
50 degree-/weight-preserving rewire nulls
50 feature_structured_shuffle configured nulls
```

The construction families were internally reconstructed by the runner:

```text
top_strength:
  4 variants

threshold:
  7 variants

mutual_knn:
  6 variants

maximum_spanning_tree:
  1 variant
```

Total construction variants:

```text
4 + 7 + 6 + 1 = 18
```

Total graph objects:

```text
1 real + 50 + 50 = 101
```

Expected primary metric rows:

```text
18 construction variants × 101 objects = 1818
```

---

## 4. Output row counts

Observed row counts:

```text
bmc15h_core_metrics.csv:              1818
bmc15h_envelope_metrics.csv:          1818
bmc15h_real_vs_null_summary.csv:       108
bmc15h_null_family_inventory.csv:      100
warnings:                               5
```

Design check:

```text
18 construction variants × 101 objects = 1818
```

The row counts match the intended first-run design.

---

## 5. Warnings and methodological status

The run produced five warnings.

### 5.1 Metadata warning

The configured node metadata file was present or referenced, but did not expose
the expected columns:

```text
node_id, family
```

Warning:

```text
Could not load node metadata for feature shuffles:
data/node_metadata_real.csv missing columns needed for feature shuffle:
node_id, family
```

Consequence:

```text
feature_structured_shuffle degraded to an unrestricted node-shuffle fallback.
```

Therefore, the second null family in this initial run must not yet be interpreted
as a fully feature-structured shuffle.

### 5.2 Optional envelope-file warnings

The optional BMC-15f/f1/f2 reference envelope files configured in the YAML were
not found under the configured paths.

This did not stop the run because the runner reconstructed envelope variants
internally.

Interpretation:

```text
These warnings limit direct reuse of prior envelope-edge exports,
but do not invalidate the internally reconstructed first-run diagnostics.
```

---

## 6. Primary result summary

The summary table contains:

```text
108 comparison rows
```

All 108 rows received the conservative diagnostic label:

```text
real_exceeds_tested_null_family
```

Breakdown by null family:

```text
degree_weight_preserving_rewire:
  real_exceeds_tested_null_family: 54

feature_structured_shuffle:
  real_exceeds_tested_null_family: 54
```

Important qualification:

```text
The feature_structured_shuffle family was not a true feature-structured null in
this first run. It degraded to an unrestricted node-shuffle fallback because
the configured metadata columns were unavailable.
```

---

## 7. Core-related readout

The strongest real-minus-null differences occurred for core containment metrics.

Representative strongest cases:

```text
feature_structured_shuffle / fallback
  envelope_core_edge_containment
  mutual_knn k_2
  real = 1.0
  null_mean = 0.09
  delta = 0.91
  empirical_exceedance_fraction = 0.0

feature_structured_shuffle / fallback
  envelope_core_edge_containment
  top_strength top_edges_21
  real = 1.0
  null_mean ≈ 0.1067
  delta ≈ 0.8933
  empirical_exceedance_fraction = 0.0

degree_weight_preserving_rewire
  envelope_core_edge_containment
  mutual_knn k_2
  real = 1.0
  null_mean ≈ 0.1267
  delta ≈ 0.8733
  empirical_exceedance_fraction = 0.0

degree_weight_preserving_rewire
  envelope_core_edge_containment
  top_strength top_edges_21
  real = 1.0
  null_mean = 0.13
  delta = 0.87
  empirical_exceedance_fraction = 0.0
```

Interpretation:

```text
In sparse/local envelope variants, the canonical object fully contains the
reference-core proxy while the tested null objects retain only a small fraction
on average.
```

---

## 8. Strongest null-reproduction side

The highest empirical exceedance fractions among the displayed core-related
rows were still low:

```text
empirical_exceedance_fraction = 0.02
```

Representative cases:

```text
degree_weight_preserving_rewire
  envelope_core_edge_containment
  top_strength top_edges_75
  real = 1.0
  null_mean = 0.57
  delta = 0.43
  empirical_exceedance_fraction = 0.02

degree_weight_preserving_rewire
  envelope_core_edge_containment
  mutual_knn k_10 / k_15
  real = 1.0
  null_mean = 0.60
  delta = 0.40
  empirical_exceedance_fraction = 0.02

degree_weight_preserving_rewire
  envelope_core_node_containment
  threshold family variants
  real = 1.0
  null_mean ≈ 0.6733
  delta ≈ 0.3267
  empirical_exceedance_fraction = 0.02
```

Interpretation:

```text
Broader / denser envelope variants allow some null objects to recover more of
the reference-core proxy, but the canonical object remains above the tested
null distributions in this first run.
```

---

## 9. Befund

BMC-15h-v0 completed successfully as a first structured-specificity diagnostic
run.

Observed:

```text
All 108 real-vs-null comparison rows were labeled:
real_exceeds_tested_null_family.
```

For the tested construction variants and the configured degree-/weight-preserving
rewire null family, the canonical N81-derived graph object retains the compact
reference-core proxy more strongly than the null objects.

The configured feature-structured shuffle branch also produced real-exceeds-null
labels, but because metadata loading failed, this branch is only an unrestricted
node-shuffle fallback in the present run.

---

## 10. Interpretation

The first BMC-15h readout is compatible with a stronger local-core specificity
signal than BMC-15f/g alone.

Conservative interpretation:

```text
Relative to the tested degree-/weight-preserving rewire family, the canonical
BMC-15/N81 object shows stronger retention of the compact local reference-core
proxy across the internally reconstructed envelope construction variants.
```

For the fallback shuffle branch:

```text
Relative to an unrestricted node-shuffle fallback, the canonical object also
shows stronger reference-core retention.
```

This should not yet be phrased as a completed feature-structured specificity
test.

---

## 11. Methodological caution

The present run is an initial diagnostic, not the final BMC-15h result.

Limitations:

```text
Feature-structured shuffle did not use the intended metadata columns.
Optional prior BMC-15f/f1/f2 envelope exports were not loaded.
Core-seeded decoys were disabled.
Only 50 repeats per active null family were used.
The current comparison uses empirical exceedance fractions, not formal p-values.
```

The most important limitation is the metadata mismatch:

```text
The feature-structured null family has not yet been tested as designed.
```

---

## 12. Conservative conclusion

BMC-15h-v0 supports the following construction-qualified statement:

```text
In the first BMC-15h diagnostic run, the canonical BMC-15/N81 graph object
retained the compact reference-core proxy more strongly than the tested
degree-/weight-preserving rewire null family across the internally reconstructed
construction variants. A second configured null branch also showed real-exceeds-null
behavior, but it degraded to an unrestricted node-shuffle fallback because the
configured feature metadata columns were unavailable.
```

This strengthens the methodological picture, but does not establish physical
geometry or proof-level specificity.

---

## 13. Recommended next step

Before treating BMC-15h as a full structured-specificity test, fix the metadata
mapping for the feature-structured shuffle branch.

Recommended immediate check:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

python - <<'PY'
from pathlib import Path
import csv

p = Path("data/node_metadata_real.csv")
with p.open(newline="", encoding="utf-8") as f:
    header = next(csv.reader(f))
print(header)
PY
```

Then update the YAML block:

```yaml
columns:
  node_id: "<actual node id column>"
  family: "<actual family / class column>"
```

After the metadata mapping is corrected, rerun BMC-15h and compare the new
feature-structured null readout against the present v0 run.

---

## 14. Suggested commit sequence

If the current code/config/docs are not yet committed:

```bash
git status --short

git add \
  data/bmc15h_structured_specificity_extension_config.yaml \
  scripts/run_bmc15h_structured_specificity_extension.py \
  docs/BMC15H_STRUCTURED_SPECIFICITY_EXTENSION_SPEC.md \
  docs/BMC15H_RUNNER_FIELD_LIST.md

git status --short

git commit -m "Add BMC-15h structured specificity diagnostic"
git push
```

For this result note:

```bash
git add docs/BMC15H_STRUCTURED_SPECIFICITY_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMC-15h initial structured specificity result note"
git push
```

Only commit result outputs from `runs/` if the project intentionally tracks
selected lightweight run artifacts.
