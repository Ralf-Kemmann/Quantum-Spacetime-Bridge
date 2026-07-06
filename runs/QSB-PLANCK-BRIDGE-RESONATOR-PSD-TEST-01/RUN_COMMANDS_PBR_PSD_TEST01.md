# Run Commands

Run from repository root:

```bash
python3 runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01/scripts/run_pbr_psd_test.py --repo-root . --run-dir runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01
python3 runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01/scripts/validate_pbr_psd_test.py runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01
git diff --check
git status --short
```

Optional SQL load, after running the Python generator:

```bash
psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01/sql/001_create_qsb_pbr_psd_test.sql
psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01/sql/002_insert_qsb_pbr_psd_test.sql
psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01/sql/003_validation_queries.sql
```

The SQL import commands are intended to be run from the repository root. The import SQL uses repo-root-relative literal `\copy` paths to avoid psql variable path quoting issues.
