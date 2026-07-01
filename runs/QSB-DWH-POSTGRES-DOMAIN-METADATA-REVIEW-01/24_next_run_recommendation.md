# Next Run Recommendation

1. `QSB-DWH-POSTGRES-DOMAIN-ROUTING-PATCH-02`
   Recommended first because the `unknown` bucket is large.

2. `QSB-DWH-POSTGRES-SPARC-RAR-METADATA-PRECONTRACT-01`
   SPARC/RAR has the strongest domain-specific metadata/view visibility, with claim boundaries still active.

3. `QSB-DWH-POSTGRES-INTERFACE01-METADATA-PRECONTRACT-01`
   INTERFACE01 gate artifacts are visible but require semantic loader review.

4. `QSB-DWH-POSTGRES-MATRIX-EXTRACT03-METADATA-PRECONTRACT-01`
   Matrix/EXTRACT03 is structurally visible and should be reviewed as structure/method metadata only.

5. `QSB-DWH-POSTGRES-RELALG-CAUSALITY-METADATA-PRECONTRACT-01`
   RELALG and CAUSALITY remain partial/artifact-level enough to pair with stricter claim-boundary review.
