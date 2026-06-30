# Next Control Recommendation

Recommended next run:

`QSB-MATRIX-TOPOLOGY-ISOLATED-GENERATOR-WRAPPER-CONTROL`

Rationale:

The post-hoc label-permutation audit shows that the existing candidate edge artifact aligns with original pair-id absolute-delta classes and does not fully align with a deterministic non-trivial label permutation. A true source-native label-permuted recompute was not executed because the original generator has fixed output paths and the source-label permutation semantics need to be frozen before replay.

Required guard:

Do not overwrite `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/`. Build a run-local wrapper or controlled generator copy with explicit output paths and explicit source-label permutation semantics.

Claim boundary:

methodological control only; no physics, spacetime, gravity, causality, or source-signal claim
