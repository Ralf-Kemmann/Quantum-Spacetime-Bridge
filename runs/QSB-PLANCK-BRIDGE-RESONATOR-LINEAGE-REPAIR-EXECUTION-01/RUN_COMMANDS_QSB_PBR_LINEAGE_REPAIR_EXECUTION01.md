# Run Commands

```bash
RUN_DIR="runs/QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-EXECUTION-01"
git status --short --untracked-files=all
sed -n '1,5p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-DESIGN-01/data/lineage_repair_design.csv
sed -n '1,5p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-DESIGN-01/data/lineage_repair_candidate_requirements.csv
sha256sum data/bmc01/bmc01_baseline_relational_table_template.csv data/bmc04/bmc04_baseline_relational_table_template.csv
sed -n '1,20p' data/bmc01/bmc01_baseline_relational_table_template.csv
sed -n '1,20p' data/bmc04/bmc04_baseline_relational_table_template.csv
git log --oneline -- data/bmc01/bmc01_baseline_relational_table_template.csv
git log --oneline -- data/bmc04/bmc04_baseline_relational_table_template.csv
wc -l data/bmc01/bmc01_baseline_relational_table_template.csv data/bmc04/bmc04_baseline_relational_table_template.csv
git show --stat --oneline c89be08 -- data/bmc01/bmc01_baseline_relational_table_template.csv data/bmc04/bmc04_baseline_relational_table_template.csv
git diff --check
git status --short --untracked-files=all
```
