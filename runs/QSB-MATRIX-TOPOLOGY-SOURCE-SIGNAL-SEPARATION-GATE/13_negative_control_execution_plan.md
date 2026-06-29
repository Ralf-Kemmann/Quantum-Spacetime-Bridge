# Negative Control Execution Plan

## 1. Upstream generator trace resolution

Purpose: identify the exact script/config path that produced strength and candidate flags.
Needed inputs: generator scripts, configs, manifests, lineage hashes.
Expected if rule-induced: generator exposes rule/label/threshold construction.
Expected if source-signal present: generator exposes independent source features not reducible to labels.
Review boundary: trace resolution is methodological only.

## 2. Label-permuted recomputation

Purpose: test whether structure follows Pair-ID labels during generation.
Needed inputs: upstream generator, source features, config.
Expected if rule-induced: structure follows permuted labels or changes predictably.
Expected if source-signal present: structure remains aligned with source features, not labels.
Review boundary: post-hoc permutation is insufficient.

## 3. Abs-delta masking / rule ablation

Purpose: remove or mask abs_delta information in the generator.
Needed inputs: editable generator or configurable rule.
Expected if rule-induced: block topology collapses or changes.
Expected if source-signal present: residual structure remains.
Review boundary: ablation must not introduce unrelated algorithm changes.

## 4. Threshold sweep from continuous strength

Purpose: test candidate sensitivity to theta.
Needed inputs: continuous strength values and threshold rule.
Expected if rule-induced: block topology appears only in predictable threshold ranges.
Expected if source-signal present: source-aligned structure remains across meaningful ranges.
Review boundary: artifact-level sweep does not replace upstream recompute.

## 5. Independent source-feature matrix test

Purpose: compare detected structure against independent source-native features.
Needed inputs: source feature matrix not derived from Pair-ID label distance.
Expected if rule-induced: no independent support after controls.
Expected if source-signal present: source features align with residual structure.
Review boundary: source-feature independence must be documented.

## 6. Negative source control

Purpose: run detector on source data where no structure is expected.
Needed inputs: negative control matrix or synthetic source.
Expected if rule-induced: detector may reproduce rule patterns if labels remain.
Expected if source-signal present: no target-specific alignment should appear in control.
Review boundary: failed negative control blocks source claims.

## 7. Positive synthetic calibration control

Purpose: verify detector can recover known injected source structure.
Needed inputs: synthetic matrix with known injected pattern.
Expected if rule-induced: rule-only detector should not overclaim source origin.
Expected if source-signal present: injected source structure is recovered and classified correctly.
Review boundary: calibration proves detector behavior, not EXTRACT03 physics.
