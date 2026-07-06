# Run Commands: QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01

    ## Generate artifacts

    ```bash
    python runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/scripts/run_pbr_nullmodel_design.py --repo-root . --run-dir runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01
    ```

    ## Validate package

    ```bash
    python runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/scripts/validate_pbr_nullmodel_design.py runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01
    ```

    ## Optional DWH import

    ```bash
    psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/sql/001_create_qsb_pbr_nullmodel_design.sql
    psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/sql/002_insert_qsb_pbr_nullmodel_design.sql
    psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/sql/003_validation_queries.sql
    ```

    ## Local checks

    ```bash
    git diff --check
    git status --short
    ```
