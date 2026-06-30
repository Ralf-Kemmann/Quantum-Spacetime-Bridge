# Trace Resolution Limitations

- The direct generator is found and the rule is reconstructable from repo artifacts.
- The original generator has fixed output paths and an overwrite guard, so replay must not be run against the existing A-R1 directory.
- Label-permuted recomputation requires a controlled design for how Pair-ID labels are permuted before the generator sees them.
- Abs-delta masking or rule ablation requires an audited code variant or parameterized wrapper.
- This run does not establish source-driven signal support.
