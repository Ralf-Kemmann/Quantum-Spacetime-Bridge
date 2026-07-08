# Run Commands

```bash
RUN_DIR="runs/QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01"
.venv/bin/python "$RUN_DIR/scripts/run_pbr_input_artifact_enrichment_dwh_repo_scout.py" --repo-root . --run-dir "$RUN_DIR" --database qsb_research_dwh
.venv/bin/python "$RUN_DIR/scripts/validate_pbr_input_artifact_enrichment_dwh_repo_scout.py" "$RUN_DIR"
git diff --check
git status --short --untracked-files=all
```
