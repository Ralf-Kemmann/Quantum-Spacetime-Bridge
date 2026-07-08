# Run Commands

```bash
RUN_DIR="runs/QSB-PLANCK-BRIDGE-RESONATOR-METADATA-REPAIR-TRIAGE-01"
git status --short --untracked-files=all
git log --oneline -10
sed -n '1,10p' runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-01/data/repair_required_candidate_summary.csv
sed -n '1,80p' data/QSB-OUTREACH01A/001_qsb_outreach01a_sqlite_dwh_ddl.sql
git log --oneline -- data/QSB-OUTREACH01A/001_qsb_outreach01a_sqlite_dwh_ddl.sql
sha256sum data/QSB-OUTREACH01A/001_qsb_outreach01a_sqlite_dwh_ddl.sql
git diff --check
git status --short --untracked-files=all
```
