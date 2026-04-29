# run_bmc01_matrix.sh

## Purpose

This script runs a small **BMC-01 variants matrix** across:

- `global_weight_permutation`
- `within_shell_weight_permutation`
- `within_local_group_weight_permutation`

and strengths:

- `low`
- `medium`
- `high`

The goal is to get a first compact probe map of which intervention family and strength level produces the strongest arrangement-sensitive response.

## What it writes

The script creates a timestamped output tree under:

`runs/BMC-01/matrix/<STAMP>/`

Inside it creates one run directory per matrix cell plus two compact summaries:

1. `bmc01_matrix_summary.csv`
2. `bmc01_matrix_readout.md`

## Input assumption

The script expects:

`data/bmc01/bmc01_baseline_relational_table_template.csv`

and:

`scripts/bmc01_weighted_relational_scramble.py`

## Usage

```bash
bash scripts/run_bmc01_matrix.sh
```

or explicitly:

```bash
bash scripts/run_bmc01_matrix.sh /home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

## Field list

1. `PROJECT_ROOT` — Shell string — repository root path  
2. `INPUT_CSV` — Shell string — baseline CSV used for all matrix runs  
3. `SCRIPT_PATH` — Shell string — BMC-01 implementation script path  
4. `STAMP` — Shell string — timestamp for the matrix run  
5. `OUT_ROOT` — Shell string — output root for the matrix batch  
6. `SUMMARY_CSV` — Shell string — compact machine-readable matrix summary  
7. `SUMMARY_MD` — Shell string — compact human-readable matrix summary  
8. `VARIANTS` — Shell array — intervention variants used in the matrix  
9. `STRENGTHS` — Shell array — strength levels used in the matrix  
10. `RUN_ID` — Shell string — per-cell run identifier  
11. `RUN_DIR` — Shell string — per-cell output directory

## Why this is useful

This matrix is the smallest sensible next step after a single dry run because it helps answer:

- which intervention family is most arrangement-sensitive?
- how strongly does the response scale with perturbation strength?
- is shell-based scrambling more informative than global or local-group scrambling?
- where should the next bridge-stress effort focus?

## Bottom line

This is a probe map, not a final bridge result. Its value is comparative: it helps identify where the BMC-01 logic is structurally most sensitive.
