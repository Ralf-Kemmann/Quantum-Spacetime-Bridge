# QSB-RELALG-SYNTH-D1K-SOURCE-TOPOLOGY-LIMIT-NOTE

This package creates a compact source-topology limit note for the synthetic D1K RELALG branch.

## Purpose

The task condenses already completed results. It is not a new exploratory computation and does not construct new relations.

## Upstream Dependency Chain

- `QSB-RELALG-SYNTH-D1K-BRIDGE`
- `QSB-RELALG-SYNTH-D1K-LOOP-MIN`
- `QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN`

The matrix-topology summary, validation report, matrix profile, component summary, and claim boundary are required. Bridge and Loop-Min summaries/validation reports are consumed when present.

## What Is Being Summarized

D1K provides a synthetic diagnostic C-layer over observed `A->B` relations. The matrix-topology audit reports a fully occupied local `1 x 9450` source-target matrix and a one-center outgoing star.

## Why D1K Remains Useful

D1K remains useful for synthetic C-layer export, matrix/topology diagnostics, family/block readouts, and conservative documentation of source-topology limits.

## Why D1K Does Not Authorize Loop-Phase Analysis

Source-native loop-phase analysis requires closed triples with actual `A->B`, `B->C`, and `C->A` rows. D1K lacks source-native `B->C` and `C->A` closure, so loop-phase analysis is not authorized from this source topology.

## Local Meaning of Density 1.0

The density value `1.0` is local to the observed `A_id x B_id` matrix shape of `1 x 9450`. It is not the density of the full node-to-node graph over `9451` nodes and does not imply missing `B->C`, `C->A`, or reverse relations.

## No Data-Baukasten Rule

Missing relations are not assembled from available rows. The script records `inferred_edge_count = 0` and preserves the no inferred edges / no fabricated loops boundary.

## Claim Boundary

- synthetic diagnostic source-topology limit note only
- not REAL01 evidence
- not a physical phase source
- not a physical C-layer source
- no physical Bridge validation
- no spacetime, metric, gravity, or causal claim
- no inferred edges
- no fabricated loops
- no source-native loop phase authorization from D1K

## Run

```bash
python scripts/qsb_relalg_synth_d1k_source_topology_limit_note/relalg_synth_d1k_source_topology_limit_note.py
```

The default run refuses to overwrite existing outputs. To intentionally regenerate:

```bash
python scripts/qsb_relalg_synth_d1k_source_topology_limit_note/relalg_synth_d1k_source_topology_limit_note.py --force
```

## Validate

```bash
python -m py_compile scripts/qsb_relalg_synth_d1k_source_topology_limit_note/relalg_synth_d1k_source_topology_limit_note.py
python scripts/qsb_relalg_synth_d1k_source_topology_limit_note/relalg_synth_d1k_source_topology_limit_note.py
python -m json.tool runs/QSB-RELALG-SYNTH-D1K-SOURCE-TOPOLOGY-LIMIT-NOTE/qsb_relalg_synth_d1k_source_topology_limit_validation_report.json
python -m json.tool runs/QSB-RELALG-SYNTH-D1K-SOURCE-TOPOLOGY-LIMIT-NOTE/qsb_relalg_synth_d1k_source_topology_limit_next_step_gate.json
python -m json.tool runs/QSB-RELALG-SYNTH-D1K-SOURCE-TOPOLOGY-LIMIT-NOTE/qsb_relalg_synth_d1k_source_topology_limit_summary.json
python -m json.tool runs/QSB-RELALG-SYNTH-D1K-SOURCE-TOPOLOGY-LIMIT-NOTE/qsb_relalg_synth_d1k_source_topology_limit_manifest.json
python scripts/qsb_relalg_synth_d1k_source_topology_limit_note/relalg_synth_d1k_source_topology_limit_note.py
git diff --check
git status --short
```

The second normal invocation should refuse overwrite unless `--force` is supplied.
