# Run Commands

Run from repository root:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

Fresh dry-run reviewed:

```bash
python runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py \
  --data-db runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/qsb_research_dwh_target_workcopy_dwh03.db \
  --metadata-db runs/QSB-META02/metadata_catalog_update/qsb_metadata_catalog_meta02.sqlite \
  --seed runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_source_seed.csv \
  --mode dry-run
```

Review script:

```bash
python runs/QSB-PBR-LITERATURE-METADATA-TWO-DB-DRYRUN-REVIEW-01/scripts/review_two_db_dryrun.py
```

Expected review outcome before repair:

```text
two_db_dryrun_review_blocked_validation_failed
```

Required checks:

```bash
git status --short --untracked-files=all
git diff --check
python -m py_compile runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py
python -m py_compile runs/QSB-PBR-LITERATURE-METADATA-TWO-DB-DRYRUN-REVIEW-01/scripts/review_two_db_dryrun.py
```

Do not run `--mode execute`.
