# Threshold Calibration Note — M.3.9x.3g.a

## Status
This note documents the current calibration logic for the working thresholds used in the
Type-B exclusion test.

## Purpose
The thresholds are **working values** for defensive analysis and should not be interpreted
as final physical constants. Their role is to:
- reduce false positives,
- make the decision logic transparent,
- and support reproducible comparison across runs.

## Current calibrated working thresholds

### Absolute original-quality threshold
- `reference_rules.original_separation_margin.min = 0.21`

### Relative-advantage threshold
- `decision_rules.thresholds.min_original_over_control_margin_delta = 0.086`

## Current calibration logic

### Original separation margin threshold
The current working threshold was calibrated from observed original-pair margins using:

`median(original_margins) + std(original_margins)`

Example calibration set used in the exploratory block:
- original margins: `[0.18, 0.20, 0.16, 0.22, 0.19]`

This yielded:
- median = `0.19`
- std = `0.02`
- suggested threshold = `0.21`

### Relative-advantage threshold
The current working threshold was calibrated from observed control-delta values using:

`q0.90(control_deltas)`

Example calibration set used in the exploratory block:
- control deltas: `[0.07, 0.06, 0.08, 0.09, 0.05]`

This yielded:
- q0.90 = `0.086`

## Why this calibration is acceptable for the current stage
The project is still in a hardening phase. At this stage, the purpose of threshold calibration is:
1. to avoid arbitrary fixed values,
2. to make the rule system data-informed,
3. to keep the logic conservative but not unrealistically strict.

## Known limitations
The current thresholds still have important limitations:

1. **Small-sample dependence**
   - The calibration examples are based on small exploratory sets.
   - More realistic original and control datasets may shift the values.

2. **Potential circularity**
   - Calibration and evaluation are not yet fully separated by a strict holdout protocol.

3. **Model-transfer uncertainty**
   - It remains open whether the same thresholds transfer equally well across FSW and AO
     without model-specific adjustment.

4. **Working-value status**
   - These thresholds are analysis values, not final theory statements.

## Current interpretation
At the present stage:
- controls are being excluded successfully under the hardened Type-B rule block,
- relative advantage over adversarial controls can be achieved,
- but absolute original quality still remains the main bottleneck.

## Next hardening steps
1. Fine boundary scan for `K2a` and `K3a`
2. Better original-pair selection and validation (`O1/O2/O3`)
3. Threshold robustness check under improved original/control datasets
4. Later: split-sample or holdout-style confirmation of calibration choices

## Recommended reporting language
Suggested internal phrasing:

> The current threshold values are data-informed working calibrations introduced to
> stabilize the exclusion logic. They are sufficient for the present hardening phase,
> but remain subject to later validation against stronger original references, adversarial
> controls, and more explicit anti-selection-bias procedures.
