# BMC-15h — Structured Specificity Extension Specification

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Status: Specification only; no new numerical run is defined as completed by this note.

---

## 1. Purpose

BMC-15h is intended as the next diagnostic step after the BMC-15e/f/g series.

The purpose is to test whether the compact local core behavior observed in the BMC-15 geometry-proxy workflow is specific to the canonical N81-derived relational structure, or whether comparable behavior is reproduced by structured control families.

The target question is:

```text
Do structured null families reproduce the same combination of
core containment, envelope sensitivity, and topological core robustness
that was observed in the BMC-15e/f/g line?
```

This is a specificity diagnostic, not a proof of physical geometry.

---

## 2. Relation to BMC-15e/f/g

BMC-15e/f/g established the current working picture:

```text
BMC-15e:
  geometry-control nulls / control context

BMC-15f/f1/f2:
  envelope construction sensitivity
  node alignment
  connectedness transition behavior

BMC-15g:
  core perturbation robustness
```

Consolidated status before BMC-15h:

```text
Large envelope-level geometry proxies are construction- and parameter-sensitive.

In the canonical node-aligned 22-node regime, the compact reference core remains
strongly contained across multiple envelope families and connectedness-transition
sweeps.

Under small topological perturbations, the compact reference-core proxy remains
robust.

The current top-strength reconstruction rule is sensitive to weight-rank
perturbations.
```

BMC-15h extends this by asking whether the same pattern appears in structured
controls.

---

## 3. Scientific framing

BMC-15h must remain methodologically conservative.

Allowed framing:

```text
structured specificity diagnostic
construction-qualified comparison
geometry-proxy compatible behavior
local core proxy robustness
null-family exceedance diagnostic
```

Not allowed without substantially stronger evidence:

```text
physical spacetime emergence proven
unique recovered geometry
Lorentzian structure recovered
causal structure recovered
metric recovered
continuum limit established
specificity proven
```

The intended conclusion form is comparative:

```text
Relative to defined structured null families, the canonical N81 object does / does not
show stronger retention of the compact local core proxy under the selected envelope
and perturbation diagnostics.
```

---

## 4. Input objects

The BMC-15h runner should operate on existing project artifacts and should not
silently reconstruct undocumented inputs.

Expected input classes:

```text
canonical graph / edge inventory
node metadata
reference core definition
reference envelope definitions
BMC-15f/f1/f2 envelope-construction settings
BMC-15g perturbation settings
structured null family settings
```

The exact file paths should be declared in a YAML config.

No file path should be hard-coded inside the runner except for safe defaults that
are also documented in the config template.

---

## 5. Null-family design

BMC-15h should compare the canonical N81-derived object against several structured
null families. These controls should be strong enough to avoid trivial strawman
comparisons, but still interpretable.

### 5.1 Null family A — Degree-/weight-preserving rewires

Purpose:

```text
Preserve coarse graph statistics while disrupting the concrete local arrangement.
```

Preserve where possible:

```text
node count
edge count
degree sequence or approximate degree profile
weight multiset or approximate weight distribution
possibly connectedness, if the construction requires it
```

Disrupt:

```text
specific local adjacency pattern
specific reference-core edge arrangement
local neighborhood identity
```

Primary question:

```text
Does the reference-core behavior follow merely from graph density,
degree structure, or weight-rank distribution?
```

### 5.2 Null family B — Feature-structured shuffles

Purpose:

```text
Preserve broad feature-family structure while disrupting local node-to-node
assignment or local relational ordering.
```

Preserve where possible:

```text
node feature families
global feature distributions
family-level counts
possibly within-family distance scales
```

Disrupt:

```text
specific local pairing
specific N81 relational ordering
specific core-neighborhood identity
```

Primary question:

```text
Does the compact core proxy follow from broad feature-family structure,
or from more specific local relational organization?
```

### 5.3 Null family C — Core-seeded decoys

Purpose:

```text
Test how easily a compact BMC-15-like core can be artificially generated inside
otherwise controlled structures.
```

Preserve or impose:

```text
a small local dense/high-weight seed
controlled edge-count and weight-rank properties
comparable global graph size
```

Disrupt or vary:

```text
seed environment
connection pattern between seed and surrounding envelope
global compatibility with the canonical N81 object
```

Primary question:

```text
Can the BMC-15 reference-core behavior be reproduced cheaply by injecting a
local seed, or does the canonical object show additional envelope/context
compatibility?
```

### 5.4 Optional null family D — Family-block structured controls

Purpose:

```text
Preserve block-level family organization while randomizing within or across blocks.
```

This family is optional and should only be added if it can be implemented without
overcomplicating the first BMC-15h runner.

---

## 6. Metrics

The runner should compute metrics at three levels:

```text
core-level metrics
envelope-level metrics
real-vs-null comparison metrics
```

### 6.1 Core-level metrics

Recommended fields:

```text
core_edge_retention
core_node_retention
core_connected
core_connected_fraction
core_component_count
core_largest_component_fraction
core_mean_weight
core_weight_rank_stability
```

Interpretation:

```text
These metrics test whether the compact reference-core proxy survives the
construction or perturbation procedure.
```

### 6.2 Envelope-level metrics

Recommended fields:

```text
envelope_node_count
envelope_edge_count
envelope_density
envelope_connected
envelope_component_count
envelope_core_edge_containment
envelope_core_node_containment
envelope_edge_overlap_to_real
envelope_jaccard_to_real
```

Interpretation:

```text
These metrics test whether the larger construction envelope behaves similarly
or differently between canonical and structured-null objects.
```

### 6.3 Real-vs-null comparison metrics

Recommended fields:

```text
real_value
null_mean
null_median
null_std
null_min
null_max
real_minus_null_mean
real_minus_null_median
empirical_exceedance_fraction
real_rank_position
n_null_repeats
```

Terminology note:

```text
Use "empirical_exceedance_fraction" rather than overloading the result as a
formal p-value.
```

---

## 7. Output files

Recommended output directory pattern:

```text
runs/BMC-15h/structured_specificity_extension_open/
```

Recommended files:

```text
bmc15h_core_metrics.csv
bmc15h_envelope_metrics.csv
bmc15h_real_vs_null_summary.csv
bmc15h_run_manifest.json
bmc15h_warnings.json
```

Optional files:

```text
bmc15h_null_family_inventory.csv
bmc15h_config_resolved.yaml
```

---

## 8. Output schema draft

### 8.1 `bmc15h_core_metrics.csv`

| Field name | Type | Description |
|---|---:|---|
| run_id | string | Unique identifier for the BMC-15h run. |
| object_role | string | `real` or `null`. |
| null_family | string | Null family label; use `canonical` for the real object. |
| null_repeat | integer/null | Repeat index for null objects; null or -1 for real. |
| seed | integer/null | Random seed used for this object or perturbation. |
| construction_family | string | Envelope or graph construction family. |
| construction_variant | string | Concrete construction variant. |
| perturbation_family | string/null | Perturbation family if used. |
| perturbation_strength | float/null | Perturbation strength if used. |
| core_edge_retention | float | Fraction of reference-core edges retained. |
| core_node_retention | float | Fraction of reference-core nodes retained. |
| core_connected | boolean | Whether retained/reconstructed core is connected. |
| core_component_count | integer | Number of connected components in retained/reconstructed core. |
| core_largest_component_fraction | float | Fraction of retained/reconstructed core nodes in largest component. |
| core_mean_weight | float/null | Mean weight of retained/reconstructed core edges. |
| core_weight_rank_stability | float/null | Stability of weight-rank ordering under reconstruction or perturbation. |
| warning_count | integer | Number of warnings associated with this row. |

### 8.2 `bmc15h_envelope_metrics.csv`

| Field name | Type | Description |
|---|---:|---|
| run_id | string | Unique identifier for the BMC-15h run. |
| object_role | string | `real` or `null`. |
| null_family | string | Null family label; use `canonical` for the real object. |
| null_repeat | integer/null | Repeat index for null objects; null or -1 for real. |
| seed | integer/null | Random seed used for this object or construction. |
| construction_family | string | Envelope construction family. |
| construction_variant | string | Concrete construction variant. |
| envelope_node_count | integer | Number of nodes in the envelope. |
| envelope_edge_count | integer | Number of edges in the envelope. |
| envelope_density | float | Graph density of the envelope. |
| envelope_connected | boolean | Whether the envelope is connected. |
| envelope_component_count | integer | Number of connected components in the envelope. |
| envelope_core_edge_containment | float | Fraction of reference-core edges contained in the envelope. |
| envelope_core_node_containment | float | Fraction of reference-core nodes contained in the envelope. |
| envelope_edge_overlap_to_real | float/null | Edge-overlap count or fraction relative to canonical real envelope. |
| envelope_jaccard_to_real | float/null | Jaccard edge similarity relative to canonical real envelope. |
| warning_count | integer | Number of warnings associated with this row. |

### 8.3 `bmc15h_real_vs_null_summary.csv`

| Field name | Type | Description |
|---|---:|---|
| run_id | string | Unique identifier for the BMC-15h run. |
| metric_name | string | Metric being compared. |
| construction_family | string | Construction family for comparison. |
| construction_variant | string | Concrete construction variant. |
| null_family | string | Null family used for comparison. |
| real_value | float | Metric value for the canonical object. |
| null_mean | float | Mean of null metric values. |
| null_median | float | Median of null metric values. |
| null_std | float | Standard deviation of null metric values. |
| null_min | float | Minimum null metric value. |
| null_max | float | Maximum null metric value. |
| real_minus_null_mean | float | Difference between real value and null mean. |
| real_minus_null_median | float | Difference between real value and null median. |
| empirical_exceedance_fraction | float | Fraction of null values equal to or more extreme than the real value, direction declared per metric. |
| real_rank_position | float/integer | Rank or percentile position of the real value among null values. |
| n_null_repeats | integer | Number of null repeats in the comparison. |
| comparison_direction | string | `higher_is_more_core_like`, `lower_is_more_core_like`, or `two_sided`. |
| interpretation_label | string | Conservative qualitative label assigned by rule. |

### 8.4 `bmc15h_run_manifest.json`

| Field name | Type | Description |
|---|---:|---|
| run_id | string | Unique identifier for the run. |
| created_at | string | ISO timestamp of run creation. |
| script_name | string | Runner script name. |
| config_path | string | Path to YAML config used for the run. |
| output_dir | string | Output directory. |
| input_files | object | Mapping of input roles to paths. |
| null_families | array | Null families included in the run. |
| construction_families | array | Construction families included in the run. |
| perturbation_families | array | Perturbation families included in the run. |
| seeds | array | Random seeds used. |
| repeats_per_family | integer/object | Number of repeats per null family. |
| warnings_file | string | Path to warnings JSON. |
| notes | string | Free-text notes for run context and limitations. |

### 8.5 `bmc15h_warnings.json`

| Field name | Type | Description |
|---|---:|---|
| warning_id | string | Unique warning identifier. |
| severity | string | `info`, `warning`, or `error`. |
| object_role | string/null | Associated object role if applicable. |
| null_family | string/null | Associated null family if applicable. |
| null_repeat | integer/null | Associated repeat if applicable. |
| construction_family | string/null | Associated construction family if applicable. |
| message | string | Human-readable warning message. |
| affected_output | string/null | Output file or metric affected by the warning. |

---

## 9. Interpretation rules

### 9.1 If structured nulls frequently reproduce the real pattern

Conservative interpretation:

```text
The observed BMC-15 core behavior is not specific to the canonical object under
the tested control family. The result remains geometry-proxy compatible but does
not support a stronger specificity statement.
```

### 9.2 If the canonical object is clearly above structured nulls

Conservative interpretation:

```text
Relative to the tested structured null family, the canonical object shows stronger
retention of the compact local core proxy. This supports a construction-qualified
specificity indication, but not a proof of physical geometry.
```

### 9.3 If only some null families reproduce the pattern

Conservative interpretation:

```text
The diagnostic identifies which structural ingredients are sufficient to reproduce
the BMC-15 behavior. The result should be treated as a decomposition of the signal,
not as a binary proof or disproof.
```

### 9.4 If results depend strongly on construction family

Conservative interpretation:

```text
The result is construction-sensitive. Any claim must be restricted to the tested
construction family and parameter regime.
```

---

## 10. Minimal acceptance criteria for first runner

A first BMC-15h runner should be considered useful if it can produce:

```text
one canonical real baseline
at least two structured null families
at least 50 repeats per null family
core-level metrics
envelope-level metrics
real-vs-null summary table
run manifest
warnings file
```

A stronger runner can later add:

```text
core-seeded decoys
multiple construction families
multiple perturbation strengths
node-aligned and non-node-aligned variants
connectedness-transition sweeps
```

---

## 11. Recommended initial scope

The recommended first implementation should avoid becoming too large.

Initial scope:

```text
Null family A:
  degree-/weight-preserving rewires

Null family B:
  feature-structured shuffles

Construction families:
  reuse BMC-15f/f1/f2 envelope families where possible

Core reference:
  reuse the BMC-15 reference core

Comparison:
  compute empirical exceedance fractions for core containment and envelope similarity
```

Do not include core-seeded decoys in the very first implementation unless the
configuration and output schema remain simple.

---

## 12. Recommended files for implementation phase

After this specification is reviewed, the implementation phase should create:

```text
data/bmc15h_structured_specificity_extension_config.yaml
scripts/run_bmc15h_structured_specificity_extension.py
docs/BMC15H_RUNNER_FIELD_LIST.md
```

Optional after the first successful run:

```text
docs/BMC15H_STRUCTURED_SPECIFICITY_EXTENSION_RESULT_NOTE.md
```

---

## 13. Conservative expected readout

BMC-15h should report one of the following conservative labels:

```text
null_reproduces_core_behavior
real_exceeds_tested_null_family
mixed_family_dependent_result
construction_sensitive_result
inconclusive_due_to_warnings_or_scope
```

These labels must not be interpreted as proof-level conclusions.

---

## 14. Internal working image

Internal, non-public shorthand:

```text
BMC-15f/g showed:
  Die Nebelschale ändert ihre Form.
  Der Klunker bleibt im relevanten 22-node-Regime sichtbar.

BMC-15h asks:
  Kann man denselben Klunker mit kontrollierten Attrappen billig nachbauen,
  oder braucht es die konkrete N81-Beziehungssuppe?
```

This image is useful for orientation, but should not replace the formal external
formulation.

---

## 15. Next step

Recommended next step:

```text
Review and commit this specification first.

Only after the specification is committed:
  build the YAML config,
  build the runner,
  build the runner field list,
  then run the first minimal structured-specificity diagnostic.
```

Suggested commit message:

```bash
git add docs/BMC15H_STRUCTURED_SPECIFICITY_EXTENSION_SPEC.md
git commit -m "Add BMC-15h structured specificity specification"
```
