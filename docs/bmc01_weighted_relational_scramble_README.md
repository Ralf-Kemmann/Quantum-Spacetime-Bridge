# BMC-01 Weighted Relational Scramble Probe

## Purpose

This file documents the initial implementation scaffold:

`scripts/bmc01_weighted_relational_scramble.py`

The script is the first executable prototype for the bridge marker–carrier experiment family.

Its job is to create a transparent and reproducible first-pass intervention block in which the **weighted relational layer** is perturbed while the coarser structural shell is preserved as far as reasonably possible.

## What the script currently does

The current scaffold implements:

1. reading a baseline relational CSV table  
2. validating minimal required columns  
3. computing baseline bridge-facing readouts  
4. applying one of several weighted-relational permutation variants  
5. computing perturbed readouts  
6. comparing baseline and perturbed bridge-facing scores  
7. writing transparent outputs into one run directory  

## Current supported intervention variants

1. `global_weight_permutation`  
   permutes a fraction of weights globally

2. `within_shell_weight_permutation`  
   permutes a fraction of weights within each `shell_label` group

3. `within_local_group_weight_permutation`  
   permutes a fraction of weights within each `local_group`

## Current supported strength levels

- `low`
- `medium`
- `high`

These map internally to fraction levels:
- low = 0.25
- medium = 0.50
- high = 1.00

## Required input columns

Minimal required columns in the input CSV:

1. `pair_id`
2. `endpoint_a`
3. `endpoint_b`
4. `weight`

Optional columns used by constrained variants:

5. `local_group`
6. `shell_label`

## Current output files

The script writes:

1. `intervention_table.csv`
2. `readout_comparison.csv`
3. `control_shell_comparison.csv`
4. `run_config.json`
5. `run_metadata.json`
6. `baseline_state.json`
7. `baseline_readout.json`
8. `decision_summary.json`
9. `summary.json`
10. `block_readout.md`

## Current interpretation status

This is a **scaffold**, not a final physics engine.

The readouts are intentionally simple and transparent:
- coefficient-of-variation style bridge signal proxy
- D1/D2 separation proxy
- weighted relational contrast proxy
- coarse readability label

These can and should later be replaced or extended with more project-specific bridge-facing measures.

## Usage example

```bash
python scripts/bmc01_weighted_relational_scramble.py   --input baseline_relational_table.csv   --output-dir runs/BMC-01/BMC01_2026-04-20_001   --variant within_shell_weight_permutation   --strength medium   --seed 123
```

## Field list

1. `ALLOWED_VARIANTS` — Python set[str] — supported intervention variants  
2. `ALLOWED_STRENGTHS` — Python set[str] — supported strength labels  
3. `STRENGTH_FRACTIONS` — Python dict[str, float] — mapping from strength label to intervention fraction  
4. `RunConfig` — dataclass — run configuration bundle  
5. `BaselineState` — dataclass — baseline structural summary  
6. `BridgeReadout` — dataclass — bridge-facing readout bundle  
7. `DecisionSummary` — dataclass — graded marker–carrier decision summary  
8. `parse_args()` — function — command-line argument parser  
9. `ensure_required_columns()` — function — validates minimal input columns  
10. `safe_std()` — function — stable standard deviation helper  
11. `compute_bridge_readout()` — function — computes baseline or perturbed bridge-facing readouts  
12. `compute_baseline_state()` — function — computes baseline structural summary  
13. `similarity_preserved_fraction()` — function — compares preservation of grouping columns  
14. `permute_subset()` — function — partially permutes a subset of weights  
15. `apply_intervention()` — function — applies the selected weighted-relational intervention  
16. `compute_control_shell_comparison()` — function — computes shell-preservation diagnostics  
17. `build_readout_comparison()` — function — constructs baseline vs perturbed readout table  
18. `make_decision_summary()` — function — generates the graded decision bundle  
19. `write_json()` — function — writes JSON output  
20. `write_markdown_readout()` — function — writes human-readable block summary  
21. `main()` — function — orchestrates one BMC-01 run

## Immediate next improvement points

Likely next implementation upgrades:

1. replace proxy readouts with project-specific bridge-facing measures  
2. add real geometry-surrogate comparison  
3. support replicate series directly  
4. add homogenization and lesion interventions  
5. externalize run config to YAML  
6. add schema validation for outputs

## Bottom line

This scaffold is the first executable bridge marker–carrier probe. It is deliberately transparent, limited, and inspectable.

Its purpose is not to settle the bridge question in one shot, but to establish a reproducible intervention pattern in which weighted-relational disruption, bridge-facing readouts, and control-shell preservation can be compared in a disciplined way.
