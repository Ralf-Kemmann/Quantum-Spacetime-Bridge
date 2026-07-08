# Run Commands

```bash
RUN_DIR="runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01"
.venv/bin/python "$RUN_DIR/scripts/run_pbr_independent_lag_variable_admissibility_execution_result_review.py" --repo-root . --run-dir "$RUN_DIR" --database qsb_research_dwh
.venv/bin/python "$RUN_DIR/scripts/validate_pbr_independent_lag_variable_admissibility_execution_result_review.py" "$RUN_DIR"
git diff --check
git status --short --untracked-files=all
psql -d qsb_research_dwh -f "$RUN_DIR/sql/001_create_qsb_pbr_independent_lag_variable_admissibility_execution_result_review.sql"
psql -d qsb_research_dwh -f "$RUN_DIR/sql/002_insert_qsb_pbr_independent_lag_variable_admissibility_execution_result_review.sql"
psql -d qsb_research_dwh -f "$RUN_DIR/sql/003_validation_queries.sql"
```
