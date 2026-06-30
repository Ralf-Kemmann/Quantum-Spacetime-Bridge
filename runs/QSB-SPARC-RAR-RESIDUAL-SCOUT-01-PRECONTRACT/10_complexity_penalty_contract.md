# Complexity Penalty Contract

The later execution run must preserve these constraints:

- exactly one additional candidate term: `RBCI_v1`
- no uncontrolled parameter expansion
- report AIC/BIC or an equivalent complexity penalty if feasible
- report cross-validation or leave-one-galaxy-out validation if feasible
- no interpretation if improvement is only in-sample
- no tuning of RBCI formula after observing residual improvement
- any formula change after data profiling requires a new precontract or explicit amendment

Interpretation boundary:

Only out-of-sample or complexity-penalized residual improvement may be called a candidate residual structure. It must not be called QSB detection, dark-matter explanation, gravity claim, spacetime claim, or causality claim.
