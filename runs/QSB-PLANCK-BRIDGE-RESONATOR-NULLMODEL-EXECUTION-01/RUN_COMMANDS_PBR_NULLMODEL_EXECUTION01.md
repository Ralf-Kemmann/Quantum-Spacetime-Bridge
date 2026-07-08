# Run Commands

```bash
RUN_DIR="runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01"
.venv/bin/python "$RUN_DIR/scripts/run_pbr_nullmodel_execution.py" --repo-root . --run-dir "$RUN_DIR"
.venv/bin/python "$RUN_DIR/scripts/validate_pbr_nullmodel_execution.py" "$RUN_DIR"
git diff --check
git status --short --untracked-files=all
```

No git add, commit, push, reset, or destructive git command is part of this run.
