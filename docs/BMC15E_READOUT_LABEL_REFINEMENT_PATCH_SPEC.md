# BMC-15e Readout Label Refinement Patch — Specification

## Purpose

This patch refines the BMC-15e observed-vs-geometry-control readout labels.

The first BMC-15e MVP completed successfully, but the position summary labeled all embedding-stress metrics as:

```text
not_directional
```

This is a readout-label issue.

Within the BMC-15 geometry-proxy logic, normalized embedding stress is directional:

```text
lower embedding stress = stronger embedding compatibility
```

Therefore the BMC-15e readout should treat:

```text
embedding_stress_2d
embedding_stress_3d
embedding_stress_4d
```

as:

```text
lower_is_more_geometry_like
```

This patch does not regenerate geometry controls.

This patch does not recompute graph metrics.

This patch only relabels the observed-position summary using existing BMC-15e outputs.

---

## Input files

Required input directory:

```text
runs/BMC-15e/geometry_control_nulls_open/
```

Required files:

```text
observed_position_summary.csv
geometry_control_metrics.csv
summary.json
```

The patch reads:

```text
observed_position_summary.csv
```

and writes refined versions.

---

## Output files

Recommended outputs:

```text
runs/BMC-15e/geometry_control_nulls_open/observed_position_summary_refined.csv
runs/BMC-15e/geometry_control_nulls_open/readout_refined.md
runs/BMC-15e/geometry_control_nulls_open/bmc15e_refinement_patch_metrics.json
```

Original files remain unchanged.

---

## Refinement rule

For rows where:

```text
metric in [
  embedding_stress_2d,
  embedding_stress_3d,
  embedding_stress_4d
]
```

apply directional comparison:

```text
lower_is_more_geometry_like
```

Given:

```text
observed_value
control_min
control_max
```

Labels:

```text
observed_within_geometry_control_range
  if control_min <= observed_value <= control_max

observed_more_geometry_like_than_geometry_controls
  if observed_value < control_min

observed_less_geometry_like_than_geometry_controls
  if observed_value > control_max
```

Tie handling:

```text
If observed_value, control_min, and control_max are all zero within tolerance,
label as observed_geometry_control_equivalent.
```

NaN handling:

```text
If observed_value, control_min, or control_max is not finite,
label as not_directional.
```

All other existing labels are preserved unless explicitly requested otherwise.

---

## Methodological boundary

This is a readout-label refinement patch.

It changes interpretation labels for embedding-stress rows.

It does not change:

```text
geometry_control_metrics.csv
generated controls
observed graph objects
distance matrices
MDS/stress calculations
negative-eigenvalue diagnostics
triangle-defect diagnostics
geodesic diagnostics
```

Therefore it is not a new numerical result block.

---

## Expected impact

Before refinement, embedding-stress rows are counted as:

```text
not_directional
```

After refinement, those rows should move into directional categories such as:

```text
observed_within_geometry_control_range
observed_more_geometry_like_than_geometry_controls
observed_less_geometry_like_than_geometry_controls
observed_geometry_control_equivalent
```

This will make the BMC-15e position summary more consistent with the BMC-15 geometry-proxy logic.

---

## Field list

| Field name | Field type | Description |
|---|---|---|
| `observed_object` | string | Observed graph object. |
| `control_family` | string | Geometry-control family. |
| `dimension` | integer | Geometry-control latent dimension. |
| `weight_mode` | string | Weight mode used for control generation. |
| `metric` | string | Metric being compared. |
| `observed_value` | float | Observed metric value. |
| `control_min` | float | Minimum control metric value. |
| `control_median` | float | Median control metric value. |
| `control_max` | float | Maximum control metric value. |
| `control_n` | integer | Number of finite control values. |
| `position_label` | string | Original position label. |
| `position_label_refined` | string | Refined position label after patch. |
| `refinement_action` | string | Description of whether and how the row was changed. |

---

## Conservative interpretation template

```text
The BMC-15e readout-label refinement patch treats embedding-stress metrics as directional
lower-is-more-embedding-compatible diagnostics, consistent with the BMC-15 geometry-proxy logic.
The patch changes only observed-position labels and does not recompute controls or metrics.
```

---

## Final internal sentence

```text
Das ist kein neuer Lauf.
Das ist der Stress-Label-Kobold im Readout.
Die Zahlen bleiben.
Die Schilder werden richtig herum gedreht.
```
