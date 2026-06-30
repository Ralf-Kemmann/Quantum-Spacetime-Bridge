# Next Recompute Control Recommendation

Recommended next run:

`QSB-MATRIX-TOPOLOGY-LABEL-PERMUTED-RECOMPUTE-CONTROL`

Rationale:

The direct generator and candidate-edge rule are now traceable. The next useful control is an isolated recomputation in which Pair-ID labels or label-derived mappings are permuted before generator execution, without mutating existing source artifacts or prior runs.

Required guard:

Do not overwrite `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/`. Use a new run directory and explicitly document any generator copy or wrapper changes.
