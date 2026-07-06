# Run Commands

Run from repository root:

```bash
python3 runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01/scripts/run_pbr_result_review.py --repo-root . --run-dir runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01
python3 runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01/scripts/validate_pbr_result_review.py runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01
git diff --check
git status --short
git status --short --untracked-files=all
git check-ignore -v runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01 || true
```

Optional DWH import:

```bash
psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01/sql/001_create_qsb_pbr_result_review.sql
psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01/sql/002_insert_qsb_pbr_result_review.sql
psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01/sql/003_validation_queries.sql
```

The SQL import uses literal repo-root-relative `\copy` paths to avoid psql variable quoting issues.
