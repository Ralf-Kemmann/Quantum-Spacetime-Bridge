# Run Commands

Run from repository root:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

Repair and validate seed alignment:

```bash
python runs/QSB-PBR-LITERATURE-METADATA-SOURCE-SEED-CSV-ALIGNMENT-FIX-01/scripts/repair_literature_source_seed_alignment.py
```

Two-DB dry-run after repair:

```bash
python runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py \
  --data-db runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/qsb_research_dwh_target_workcopy_dwh03.db \
  --metadata-db runs/QSB-META02/metadata_catalog_update/qsb_metadata_catalog_meta02.sqlite \
  --seed runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_source_seed.csv \
  --mode dry-run
```

Git checks:

```bash
git status --short --untracked-files=all
git diff --check
git diff -- runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_source_seed.csv
```

Do not run `--mode execute`.
