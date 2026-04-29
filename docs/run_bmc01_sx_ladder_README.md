# run_bmc01_sx_ladder.sh

## Purpose

This script runs the first clean **BMC-01-SX strength ladder** across:

- `within_shell_weight_permutation`
- `shell_crossing_weight_permutation` with `adjacent_shell_crossing`

for strengths:

- `low`
- `medium`
- `high`

The goal is to test whether shell-crossing remains more destructive than shell-preserving reassignment across a matched strength ladder.

## What it writes

The script creates a timestamped output tree under:

`runs/BMC-01-SX/ladder/<STAMP>/`

Inside it creates one run directory per ladder cell plus:

1. `bmc01_sx_ladder_summary.csv`
2. `bmc01_sx_ladder_readout.md`

## Input assumption

The script expects:

- `data/bmc01/bmc01_baseline_relational_table_template.csv`
- `scripts/bmc01_shell_crossing_probe.py`

## Usage

```bash
bash scripts/run_bmc01_sx_ladder.sh
```

or explicitly:

```bash
bash scripts/run_bmc01_sx_ladder.sh /home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

## Field list

1. `PROJECT_ROOT` — Shell string — repository root path  
2. `INPUT_CSV` — Shell string — baseline CSV used for all ladder runs  
3. `SCRIPT_PATH` — Shell string — BMC-01-SX implementation script path  
4. `STAMP` — Shell string — timestamp for the ladder batch  
5. `OUT_ROOT` — Shell string — output root for the ladder batch  
6. `SUMMARY_CSV` — Shell string — machine-readable ladder summary  
7. `SUMMARY_MD` — Shell string — human-readable ladder summary  
8. `STRENGTHS` — Shell array — low/medium/high strength levels  
9. `RUN_ID` — Shell string — per-cell run identifier  
10. `RUN_DIR` — Shell string — per-cell output directory  
11. `mode` — String — preserving vs shell-crossing-adjacent mode

## Why this is useful

This is the cleanest immediate next step after a single matched preserving-vs-crossing comparison because it shows whether the shell-order effect:

- is stable across strength levels
- grows with intervention strength
- remains stronger for shell-crossing than shell-preserving

## Bottom line

This ladder is a matched robustness test for the shell-order reading. Its value is comparative and structural.
