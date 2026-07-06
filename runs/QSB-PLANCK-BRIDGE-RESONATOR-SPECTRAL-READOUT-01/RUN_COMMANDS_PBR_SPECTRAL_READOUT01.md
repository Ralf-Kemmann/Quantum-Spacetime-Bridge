# Run Commands

Run from repository root:

```bash
python3 runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/scripts/run_pbr_spectral_readout.py --repo-root . --run-dir runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01
python3 runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/scripts/validate_pbr_spectral_readout.py runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01
git diff --check
git status --short
git status --short --untracked-files=all
git check-ignore -v runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01 || true
```

Optional DWH import, from repository root after running the Python generator:

```bash
psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/sql/001_create_qsb_pbr_spectral_readout.sql
psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/sql/002_insert_qsb_pbr_spectral_readout.sql
psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/sql/003_validation_queries.sql
```

The import SQL uses repo-root-relative literal `\copy` paths to avoid psql variable quoting issues.

