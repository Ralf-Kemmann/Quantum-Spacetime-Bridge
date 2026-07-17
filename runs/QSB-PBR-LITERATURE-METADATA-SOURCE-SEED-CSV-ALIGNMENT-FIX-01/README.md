# QSB-PBR-LITERATURE-METADATA-SOURCE-SEED-CSV-ALIGNMENT-FIX-01

Seed CSV alignment repair and validation for the QSB/PBR literature metadata import path.

Final status:

```text
source_seed_alignment_fix_validated_for_dryrun_review_retry
```

Modified seed file:

```text
runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_source_seed.csv
```

Repair summary:

- Reconstructed the 23 source rows from the documented source copy.
- Rewrote the seed using Python `csv.DictWriter` with stable field order.
- Kept DOI, arXiv ID, venue, and source URL empty where not supplied.
- Preserved row order `L1-L7`, `W1-W7`, `F1-F9`.
- Did not change mechanism tags or claim-boundary rows.

Post-repair validation:

- source count: 23
- mechanism tag count: 50
- claim boundary count: 23
- no DictReader overflow
- no enum/alignment failures
- two-DB dry-run passed
- real DB targets unchanged

Claim boundary:

```text
literature_context_only_no_internal_evidence_no_mechanism_claim
physical_claim_release=blocked_no_physics_claim
mechanism_claim_release=blocked_no_mechanism_claim
execution_import_authorized=false
```
