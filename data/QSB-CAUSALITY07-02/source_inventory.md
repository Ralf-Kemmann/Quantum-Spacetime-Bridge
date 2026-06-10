# QSB-CAUSALITY07-02 Source Inventory

| Source ID | Source Type | Citation | Supports | Does Not Establish |
|---|---|---|---|---|
| SRC_FKN_1972 | mechanism reference | Field, Koros, and Noyes, 1972, `Oscillations in Chemical Systems. II. Thorough Analysis of Temporal Oscillation in the Bromate-Cerium-Malonic Acid System`, JACS, DOI `10.1021/ja00780a001` | Detailed BZ mechanism frame and oscillatory reference context. | It does not make the generated run a laboratory trajectory and does not establish full chemical-state identity in this block. |
| SRC_OREGONATOR_1974 | reduced model reference | Field and Noyes, 1974, `Oscillations in Chemical Systems. IV. Limit Cycle Behavior in a Model of a Real Chemical Reaction` | Reduced Oregonator model basis and limit-cycle style temporal model behavior. | It does not simulate the complete FKN mechanism and does not model real batch resource depletion here. |
| SRC_BZ_OVERVIEW | secondary background | Secondary Oregonator/BZ framework overview used as background only. | General orientation for BZ/Oregonator terminology. | It does not provide input measurements, causal reconstruction, or QSB validation. |

The generated data are simulation outputs of the reduced Oregonator model. No laboratory time series is used.

The five phase labels in this block are heuristic functional working aliases for reduced-model state-space sectors. The source inventory does not validate independent chemical phase identity or independent cycle-order reconstruction.
