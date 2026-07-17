# QSB-PBR-LITERATURE-METADATA-TWO-DB-IMPORTER-PATCH-01

Importer patch and dry-run design for the approved two-DB QSB/PBR literature metadata architecture.

Final status:

```text
two_db_importer_patch_dry_run_passed
```

Modified importer:

```text
runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py
```

Dry-run strategy:

```text
copy real data DB and metadata DB to /tmp, write only to the copies, validate copies, compare real target SHA256 and mtime before/after
```

No real import was executed. No real target DB was modified. Execute mode remains blocked with:

```text
execution_import_authorized=false
```

Claim boundary:

```text
literature_context_only_no_internal_evidence_no_mechanism_claim
physical_claim_release=blocked_no_physics_claim
mechanism_claim_release=blocked_no_mechanism_claim
execution_import_authorized=false
```
