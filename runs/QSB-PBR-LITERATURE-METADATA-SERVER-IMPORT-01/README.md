# QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01

Prepare-only package for claim-safe QSB/PBR literature metadata import.

Status:

```text
blocked_requires_human_db_target
```

No database was written. No physics analysis was run. No web access was used.

The source file `deep-research-report(3).md` was not found in the repository. The source copy in `source/` contains only the user-prompt seed rows and explicit missing-source limitations.

Claim boundary:

```text
literature_context_only_no_internal_evidence_no_mechanism_claim
```

Prepared counts:

- sources: 23
- mechanism tags: 50
- claim-boundary rows: 23

Next human action:

```bash
python runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py --db PATH_TO_APPROVED_DB --seed runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_source_seed.csv --mode dry-run
```
