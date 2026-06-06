# ELL1 Geometric Phase Mapping Evidence

evidence_id: ELL1_GEOMETRIC_PHASE_MAPPING
model: ELL1
phase_origin: TASC
phase_origin_semantics: ascending_node_epoch
superior_conjunction_phase: 0.25
mapping_status: supported
mapping_type: documented_model_inference
applies_to_phase_axis: SHAPIROMART11

## Befund

Local archived PINT 1.1.5 source evidence supports the ELL1 phase convention used for the SHAPIROMART11 phase axis:

- `pint_1_1_5_binary_ell1.py` defines `TASC` for `BinaryELL1` as the epoch of the ascending node.
- `pint_1_1_5_stand_alone_ELL1_model.py` defines ELL1 `Phi` as the orbit phase using `TASC`, and computes the ELL1 Shapiro formula with `sin(Phi)`.
- `pint_1_1_5_timing_model.py` documents superior conjunction as the point where true anomaly plus omega equals 90 degrees.
- `pint_pulsar_1_1_5_METADATA.txt` identifies the local package as `pint-pulsar` version 1.1.5 and points to the official PINT project and documentation.

## Interpretation

For the normalized SHAPIROMART11 ELL1 phase coordinate, phase `0.00` is anchored at `TASC`, which is the ascending-node epoch.

The PINT ELL1 Shapiro expression uses `sin(Phi)`. The supported geometric inference is that the superior-conjunction reference point for this convention is reached at `Phi = pi / 2`. With a full orbit equal to `2 pi`, the normalized phase is `0.25`.

## Hypothese

No new hypothesis is introduced in this block. The mapping applies an archived model convention to an already reconstructed ELL1 phase coordinate.

## Offene Luecke

No J0740-specific publication figure or caption was used here to independently label superior conjunction at normalized orbital phase `0.25`. The J0740 applicability in this block comes from SHAPIROMART11 confirming that the reconstructed phase axis was generated for the J0740 ELL1 model.

## Claim Boundary

This mapping assigns geometric meaning to the reconstructed ELL1 orbital-phase coordinate. It does not calculate a Shapiro delay, measure a residual, or establish a new physical effect.

The generated cyclic phase offset and phase distance are dimensionless coordinates on the normalized orbit. They are not a timing residual, not a fitted parameter, not an exposure class, and not a measurement of conjunction.
