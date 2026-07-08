# Run Commands

```bash
RUN_DIR="runs/QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-EXECUTION-RESULT-REVIEW-01"
git status --short --untracked-files=all
sed -n '1,10p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-EXECUTION-01/data/execution_summary.csv
sed -n '1,10p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-EXECUTION-01/data/lineage_repair_execution_results.csv
sed -n '1,10p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-EXECUTION-01/data/source_artifact_hashes.csv
sed -n '1,10p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-EXECUTION-01/data/excluded_candidates.csv
git diff --check
git status --short --untracked-files=all
```
