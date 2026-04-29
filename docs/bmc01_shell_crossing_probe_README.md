# BMC-01-SX Shell-Crossing Probe

## Purpose

This file documents the first executable shell-focused extension of the BMC experiment line:

`scripts/bmc01_shell_crossing_probe.py`

Its purpose is to test whether **breaking shell membership** damages the bridge-facing response more strongly than shell-preserving reassignment.

## Current supported variants

1. `within_shell_weight_permutation`
2. `shell_crossing_weight_permutation`

## Current supported shell-crossing policies

1. `adjacent_shell_crossing`
2. `full_shell_crossing`

The recommended first use is:

- variant: `shell_crossing_weight_permutation`
- policy: `adjacent_shell_crossing`

## Required input columns

1. `pair_id`
2. `endpoint_a`
3. `endpoint_b`
4. `weight`
5. `shell_label`

Optional:
6. `local_group`

## Current output files

1. `intervention_table.csv`
2. `shell_crossing_summary.csv`
3. `readout_comparison.csv`
4. `control_shell_comparison.csv`
5. `decision_summary.json`
6. `summary.json`
7. `block_readout.md`
8. `run_config.json`
9. `run_metadata.json`
10. `baseline_state.json`
11. `baseline_readout.json`

## Current shell-focused readouts

- `shell_arrangement_shift_score`
- `shell_boundary_disruption_score`
- `shell_crossing_fraction`
- `shell_distance_mean`

Plus retained arrangement-sensitive readouts:
- `endpoint_load_shift_score`
- `endpoint_load_dispersion_shift_score`
- `pair_neighborhood_consistency_shift_score`
- `arrangement_signal_score`

## Usage example

```bash
python scripts/bmc01_shell_crossing_probe.py   --input data/bmc01/bmc01_baseline_relational_table_template.csv   --output-dir runs/BMC-01-SX/BMC01SX_adjacent_low_001   --variant shell_crossing_weight_permutation   --shell-crossing-policy adjacent_shell_crossing   --strength low   --seed 123
```

## Field list

1. `ALLOWED_VARIANTS` — Python set[str] — supported preserving/crossing variants  
2. `ALLOWED_CROSSING_POLICIES` — Python set[str] — supported shell-crossing policy modes  
3. `ALLOWED_STRENGTHS` — Python set[str] — strength labels  
4. `STRENGTH_FRACTIONS` — Python dict[str, float] — mapping from strength label to affected fraction  
5. `RunConfig` — dataclass — run configuration bundle  
6. `BaselineState` — dataclass — baseline structural summary  
7. `BridgeReadout` — dataclass — bridge-facing and shell-facing readout bundle  
8. `DecisionSummary` — dataclass — graded shell-order interpretation bundle  
9. `parse_shell_index()` — function — parses shell order from shell labels  
10. `choose_crossing_target_shell()` — function — chooses shell target under a crossing policy  
11. `apply_within_shell_permutation()` — function — preserving intervention  
12. `apply_shell_crossing_permutation()` — function — shell-breaking intervention  
13. `compute_control_shell_comparison()` — function — control-shell comparison summary  
14. `write_markdown_readout()` — function — human-readable block summary

## Bottom line

This script is the first executable implementation of the shell-preserving vs shell-crossing comparison. It is meant to be used in matched preserving-vs-crossing runs, not interpreted in isolation.
