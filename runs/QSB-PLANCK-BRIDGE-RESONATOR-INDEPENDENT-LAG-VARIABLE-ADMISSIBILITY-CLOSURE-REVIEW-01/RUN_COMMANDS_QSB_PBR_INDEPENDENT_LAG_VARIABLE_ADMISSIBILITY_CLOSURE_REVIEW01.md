# Run Commands

Run package:

`runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-CLOSURE-REVIEW-01/`

Commands recorded for this closure-review creation:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
git status --short --untracked-files=all
git log --oneline -12
find runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01 runs/QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-EXECUTION-RESULT-REVIEW-01 runs/QSB-PLANCK-BRIDGE-RESONATOR-METADATA-REPAIR-TRIAGE-01 -maxdepth 3 -type f | sort
sed -n '1,220p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-EXECUTION-RESULT-REVIEW-01/README.md
sed -n '1,220p' runs/QSB-PLANCK-BRIDGE-RESONATOR-METADATA-REPAIR-TRIAGE-01/README.md
sed -n '1,220p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-EXECUTION-RESULT-REVIEW-01/validation/validation_results.csv
sed -n '1,220p' runs/QSB-PLANCK-BRIDGE-RESONATOR-METADATA-REPAIR-TRIAGE-01/validation/validation_results.csv
mkdir -p runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-CLOSURE-REVIEW-01/data runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-CLOSURE-REVIEW-01/docs runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-CLOSURE-REVIEW-01/validation
git diff --check
git status --short --untracked-files=all
```

No candidate search, candidate repair, admissibility rerun, mechanism test, or nullmodel command is part of this closure-review run.
