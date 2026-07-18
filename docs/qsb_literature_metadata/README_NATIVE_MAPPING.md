# QSB/PBR Literature Native Metadata Mapping

This patch adds deterministic native metadata operation planning for the
literature metadata registration plan.

Boundaries:

```text
literature_context_only_no_internal_evidence_no_mechanism_claim
physical_claim_release=blocked_no_physics_claim
mechanism_claim_release=blocked_no_mechanism_claim
execution_import_authorized=false
data_mart_creation_authorized=false
planck_space_mapping_status=future_contract_only_not_populated
cube_mapping_status=future_design_dependency_not_implemented
```

Dry-run behavior:

- real data and metadata DBs are fingerprinted
- fresh temp copies are created
- data-side literature rows are applied to the temp data DB
- exactly 170 native operation candidates are planned from 17 registration rows
- operation candidates are applied only to the temp metadata DB
- idempotent rerun and rollback checks run on the temp metadata DB
- real targets are verified unchanged

Execute behavior:

- default remains blocked
- deprecated single-DB execute remains blocked
- two-DB execute requires explicit authorization and remains blocked by this
  implementation patch because no real native registration is authorized

Metadata registration remains a cataloging operation only. It is not physical
validation, mechanism evidence, Data Mart creation, cube population, or
Planck-space coordinate computation.
