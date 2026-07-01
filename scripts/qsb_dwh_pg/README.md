# QSB PostgreSQL DWH Orchestrator

Run-local PostgreSQL migration scaffold for `QSB-DWH-POSTGRES-CORE-MIGRATION-01`.

This package prepares SQL for the target database `qsb_research_dwh` with schemas:

- `admin`
- `raw`
- `staging`
- `canonical`
- `metadata`
- `validation`
- `mart`

The runner is defensive. It does not install PostgreSQL, does not drop databases or
tables, and does not assert migration row counts unless a PostgreSQL connection is
available and an ingest step can be executed under explicit authorization.

Commands:

```bash
python scripts/qsb_dwh_pg/qsb_dwh_pg.py check
python scripts/qsb_dwh_pg/qsb_dwh_pg.py bootstrap
python scripts/qsb_dwh_pg/qsb_dwh_pg.py ingest --dataset sparc_rar
python scripts/qsb_dwh_pg/qsb_dwh_pg.py artifact-stage --patch legacy
python scripts/qsb_dwh_pg/qsb_dwh_pg.py validate
python scripts/qsb_dwh_pg/qsb_dwh_pg.py status
```

SQLite remains an audit snapshot only. The intended working DWH backend is
PostgreSQL.

`artifact-stage --patch legacy` writes
`runs/QSB-DWH-POSTGRES-LEGACY-MIGRATION-ARTIFACT-STAGING-PATCH-01/` and
performs additive artifact registration, generic CSV/JSON/Markdown/TXT staging,
SQLite catalog inventory, global-search token enrichment, view checks, and a
read-only metadata-server readiness check. It does not execute residual,
RBCI_v1, QSB-observable, optimization, or model-fit analysis.
