# Validation Results

## Checks Run

```bash
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-ALIGNMENT-01/data/alignment_summary.csv
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-ALIGNMENT-01/data/contract_component_status.csv
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-ALIGNMENT-01/data/contract_gap_analysis.csv
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-ALIGNMENT-01/data/source_artifact_hashes.csv
find runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-ALIGNMENT-01 -type f
git diff --check
git status --short --untracked-files=all
git status --short --ignored=matching runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-ALIGNMENT-01/
```

## Actual Result

CSV parsing passed for the four checked CSV files. `git diff --check` returned no whitespace errors. `git status --short --untracked-files=all` returned no tracked or untracked non-ignored changes. `git status --short --ignored=matching runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-ALIGNMENT-01/` reported the new run package as ignored:

```text
!! runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-ALIGNMENT-01/
```

Validation status: pass for artifact parse/whitespace/status checks. Scientific unblock status remains blocked because the alignment classification is `partial_contract_found_requires_design_review`.
