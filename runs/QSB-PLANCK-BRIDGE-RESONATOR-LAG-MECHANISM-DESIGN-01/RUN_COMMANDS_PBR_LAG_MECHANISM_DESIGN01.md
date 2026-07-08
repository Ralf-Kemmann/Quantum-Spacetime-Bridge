# Run Commands

```bash
RUN_DIR="runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01"
.venv/bin/python "$RUN_DIR/scripts/run_pbr_lag_mechanism_design.py" --repo-root . --run-dir "$RUN_DIR"
.venv/bin/python "$RUN_DIR/scripts/validate_pbr_lag_mechanism_design.py" "$RUN_DIR"
git diff --check
git status --short --untracked-files=all
```

Dieser Designlauf führt keine Lag-Mechanismus-Tests und keine Nullmodelle aus.
