# QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN

Minimal synthetic D1K RELALG matrix/topology audit.

## Purpose

This package reads the existing synthetic D1K RELALG C-layer as a directed sparse matrix:

```text
rows = A_id
columns = B_id
value = C_AB
```

It describes the relation topology the data actually contains. It does not infer missing pixels, missing edges, reverse edges, or loops.

The matrix-as-image analogy is plain: existing relation rows can form visible contours such as blocks or stripes, but absent matrix cells stay absent. The no-data-baukasten rule is that missing relations are not assembled into synthetic topology.

## Inputs

Required:

```text
runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_c_layer.csv
```

Optional annotations:

```text
runs/QSB-ST-COMP01D1F/collision_aware_profile_robustness_sweep_open/case_profile_summary.csv
runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/phase_exposed_case_profile_summary.csv
runs/QSB-RELALG-SYNTH-D1K-LOOP-MIN/
```

## Outputs

The run writes artifacts under:

```text
runs/QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN/
```

Required outputs include adjacency, node-degree, component, family/block, sparse-edge, matrix-profile, validation, next-step gate, manifest, claim-boundary, readout, and summary files. It also writes optional heatmap-ready sparse edges and an aggregate Mermaid sketch.

## Sparse Matrix Convention

The sparse edge export has one row per existing C-layer row only. Deterministic indices are assigned by sorted `A_id` and sorted `B_id`.

Missing matrix cells are not emitted. Reverse edges count only if the reverse relation exists as a source-native row.

## Why This Follows BRIDGE and LOOP-MIN

`SYNTH-D1K-BRIDGE` creates the synthetic diagnostic C-layer. `SYNTH-D1K-LOOP-MIN` shows that source-native closed triples are absent. This task turns those inputs into a compact matrix/topology view that is easier to query and review.

## Why This Is Not REAL01

This is a synthetic diagnostic matrix/topology audit only. It is not REAL01 evidence, not a physical phase source, not a physical C-layer source, and not physical Bridge validation. It makes no spacetime, metric, gravity, or causal claim.

## Run

```bash
python scripts/qsb_relalg_synth_d1k_matrix_topology_min/relalg_synth_d1k_matrix_topology_min.py
```

The default run refuses to overwrite an existing output directory. To intentionally replay the same block:

```bash
python scripts/qsb_relalg_synth_d1k_matrix_topology_min/relalg_synth_d1k_matrix_topology_min.py --force
```

## Validate

```bash
python -m py_compile scripts/qsb_relalg_synth_d1k_matrix_topology_min/relalg_synth_d1k_matrix_topology_min.py
python scripts/qsb_relalg_synth_d1k_matrix_topology_min/relalg_synth_d1k_matrix_topology_min.py
python -m json.tool runs/QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN/qsb_relalg_synth_d1k_matrix_topology_validation_report.json
python -m json.tool runs/QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN/qsb_relalg_synth_d1k_matrix_topology_next_step_gate.json
python -m json.tool runs/QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN/qsb_relalg_synth_d1k_matrix_topology_summary.json
python scripts/qsb_relalg_synth_d1k_matrix_topology_min/relalg_synth_d1k_matrix_topology_min.py
git diff --check
git status --short
```

The second normal script invocation should fail with replay protection unless `--force` is supplied.
