# QSB-RELALG-SYNTH-D1K-LOOP-MIN

## Purpose

`QSB-RELALG-SYNTH-D1K-LOOP-MIN` runs a minimal loop diagnostic on the synthetic C-layer produced by `QSB-RELALG-SYNTH-D1K-BRIDGE`.

The block checks whether the D1K-derived synthetic diagnostic ordered-pair C-layer contains source-native closed directed triples that can support RELALG loop-phase calculation.

This is not REAL01, not a physical phase source, not a physical C-layer source, and not evidence for physical Bridge validation or any spacetime, metric, gravity, causal, or physics claim.

## Input Dependency

Required inputs:

- `runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_c_layer.csv`
- `runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_validation_report.json`
- `runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_next_step_gate.json`

The bridge validation report must pass, and the bridge next-step gate must authorize `QSB-RELALG-SYNTH-D1K-LOOP-MIN`.

## Source-Native Loop Policy

A valid ordered loop is an ordered triple `(A, B, C)` with distinct nodes and all three directed C-layer relations available as source-native rows:

```text
C_AB
C_BC
C_CA
```

The script does not infer missing edges, does not auto-close star graphs, does not derive B-C or C-A relations from row-level phase fields, and does not use K-layer, proxy-distance, score, profile-distance, or acceptance-distance fields as loop relations.

Default reverse-edge policy:

```text
derived_reverse_edges_allowed = false
```

Possible reverse-derived relations may be counted diagnostically, but they are marked `not_used_for_valid_loops`.

## Loop Formula

For valid source-native triples, the script computes:

```text
loop_product = C_AB * C_BC * C_CA
Phi_ABC = atan2(loop_product_imag, loop_product_real)
```

Only C-layer complex columns are used.

## Missing-Edge And Topology Blocks

If no valid loops exist, the run still succeeds as an audit run with:

```text
completed_no_closed_source_native_triples
```

`valid_loops.csv` is still written with headers and zero data rows. Candidate and blocked CSV files contain representative blocked examples and aggregate blocking counts are recorded in the summary, topology report, and validation report.

## Generated Outputs

Outputs are written under:

- `runs/QSB-RELALG-SYNTH-D1K-LOOP-MIN/`

Required artifacts:

- `qsb_relalg_synth_d1k_loop_min_source_topology.csv`
- `qsb_relalg_synth_d1k_loop_min_loop_candidates.csv`
- `qsb_relalg_synth_d1k_loop_min_valid_loops.csv`
- `qsb_relalg_synth_d1k_loop_min_blocked_loops.csv`
- `qsb_relalg_synth_d1k_loop_min_validation_report.json`
- `qsb_relalg_synth_d1k_loop_min_next_step_gate.json`
- `qsb_relalg_synth_d1k_loop_min_manifest.json`
- `qsb_relalg_synth_d1k_loop_min_claim_boundary.md`
- `qsb_relalg_synth_d1k_loop_min_readout.md`
- `qsb_relalg_synth_d1k_loop_min_summary.json`

## Claim Boundary

Every output is bounded by:

- synthetic diagnostic only
- not REAL01 evidence
- not a physical phase source
- not a physical C-layer source
- no physical Bridge validation
- no spacetime, metric, gravity, or causal claim

Valid loop rows, if any, carry:

- `evidence_class = synthetic_diagnostic_loop_from_d1k_bridge`
- `allowed_use = synthetic RELALG loop/nullmodel/control tests only`
- `blocked_use = REAL01 evidence; physical phase claim; physical C-layer source; Bridge validation; spacetime/metric/gravity interpretation`
- `claim_boundary = synthetic diagnostic D1K RELALG loop-min only`

## Run And Validate

Run from the repository root:

```bash
python scripts/qsb_relalg_synth_d1k_loop_min/relalg_synth_d1k_loop_min.py
```

The default run refuses to overwrite an existing output directory. To intentionally replace the run output directory:

```bash
python scripts/qsb_relalg_synth_d1k_loop_min/relalg_synth_d1k_loop_min.py --force
```

Local validation commands:

```bash
python -m py_compile scripts/qsb_relalg_synth_d1k_loop_min/relalg_synth_d1k_loop_min.py
python scripts/qsb_relalg_synth_d1k_loop_min/relalg_synth_d1k_loop_min.py
python -m json.tool runs/QSB-RELALG-SYNTH-D1K-LOOP-MIN/qsb_relalg_synth_d1k_loop_min_validation_report.json
python -m json.tool runs/QSB-RELALG-SYNTH-D1K-LOOP-MIN/qsb_relalg_synth_d1k_loop_min_next_step_gate.json
python scripts/qsb_relalg_synth_d1k_loop_min/relalg_synth_d1k_loop_min.py
git diff --check
git status --short
```

The second normal script run is expected to refuse overwrite unless `--force` is supplied.
