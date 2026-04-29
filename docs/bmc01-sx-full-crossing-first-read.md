# BMC-01-SX Full-Crossing First Read

## Purpose of this document

This document records the first internal reading of the initial **three-mode medium-strength comparison** in the **Quantum–Spacetime Bridge** project:

- `within_shell_weight_permutation`
- `shell_crossing_weight_permutation` with `adjacent_shell_crossing`
- `shell_crossing_weight_permutation` with `full_shell_crossing`

Its purpose is to capture the first structured interpretation of the emerging **graded shell-order ladder**.

This is an internal reading note, not a public claim.

## Why this note matters

The earlier BMC-01-SX comparison already showed that:

- shell-crossing is more destructive than shell-preserving perturbation
- shell membership appears to preserve part of the bridge-relevant order

The new full-crossing run sharpens that result.

The current comparison no longer asks only:

> Is shell-crossing worse than shell-preserving?

It now asks the stronger graded question:

> Does broader shell-breaking produce progressively stronger structural disruption?

This is the key advance of the present note.

## Compared runs

### 1. Shell-preserving reference

- Run ID: `BMC01SX_fulltest_within_shell_medium`
- Variant: `within_shell_weight_permutation`
- Strength: `medium`
- Seed: `123`

### 2. Adjacent shell-crossing

- Run ID: `BMC01SX_fulltest_shell_crossing_adjacent_medium`
- Variant: `shell_crossing_weight_permutation`
- Policy: `adjacent_shell_crossing`
- Strength: `medium`
- Seed: `123`

### 3. Full shell-crossing

- Run ID: `BMC01SX_fulltest_shell_crossing_full_medium`
- Variant: `shell_crossing_weight_permutation`
- Policy: `full_shell_crossing`
- Strength: `medium`
- Seed: `123`

## Core numerical ladder

The most important result is the arrangement-sensitive ladder.

### Arrangement signal score

- `within_shell` → `0.148588`
- `adjacent_shell_crossing` → `0.319266`
- `full_shell_crossing` → `0.450544`

This is the clearest graded result.

It directly supports the pattern:

> `within_shell < adjacent_shell_crossing < full_shell_crossing`

This is the first strong internal graded shell-order ladder in the current bridge program.

## Supporting numerical pattern

The graded behavior is not confined to a single score.

### Endpoint load shift score

- `within_shell` → `0.100000`
- `adjacent_shell_crossing` → `0.230000`
- `full_shell_crossing` → `0.395000`

### Shell arrangement shift score

- `within_shell` → `0.500000`
- `adjacent_shell_crossing` → `0.666667`
- `full_shell_crossing` → `1.000000`

### Pair-to-neighborhood consistency shift score

- `within_shell` → `0.084167`
- `adjacent_shell_crossing` → `0.137500`
- `full_shell_crossing` → `0.246667`

### Shell distance mean

- `within_shell` → `0.000000`
- `adjacent_shell_crossing` → `0.500000`
- `full_shell_crossing` → `0.666667`

This is important because the result is not riding on one arbitrary summary metric. Multiple readouts move coherently in the same direction.

## First raw observation

The difference is not merely qualitative. It is graded and structured.

The current three-mode comparison shows:

- preserving shell membership is least destructive
- breaking shell membership locally is more destructive
- breaking shell membership more broadly is more destructive again

This is exactly the kind of result expected if shell structure is carrying nontrivial intermediate order.

## Strongest current internal result

The strongest current internal result is:

> Broader shell-breaking produces progressively stronger bridge-facing disruption under otherwise matched conditions.

This is stronger than the earlier shell-suspicion stage and stronger than the earlier adjacent-crossing-only comparison.

The bridge architecture now looks increasingly inconsistent with the idea that shell labels are merely decorative.

## What this implies about shell structure

The current result supports the following internal interpretation:

> shell membership preserves nontrivial bridge-relevant order, and the degree of shell-breaking matters quantitatively

This is important for two reasons.

### 1. Shell appears order-bearing

Shell structure is no longer well described as a passive grouping convenience. It behaves more like a real structural layer that constrains how disruption propagates.

### 2. Shell order appears graded rather than binary

The present ladder suggests that shell order is not just “present or absent.” It behaves more like a scaffold whose disruption can vary in severity.

That is a richer and more physically suggestive picture.

## What this does not yet prove

The current result still does **not** prove:

- shell is the final bridge carrier
- shell structure is already a fully physical law layer
- the bridge has been reduced to shell structure alone
- the weighted relational layer is fully decomposed

These would all be premature.

The current result is strong as an internal structural indication, but still bounded by the present implementation stage.

## Why the result is nevertheless substantial

Despite the remaining limits, this is a substantial methodological step.

Before this result, shell order was a serious and increasingly plausible intermediate-order hypothesis.

After this result, shell order becomes a much more strongly supported internal layer in the emerging bridge architecture.

The important shift is this:

> shell relevance is no longer only inferred from relative robustness; it is now supported by a graded disruption ladder.

That makes the shell-order reading harder to dismiss.

## Emerging bridge architecture

The current internal picture now looks more clearly layered.

### 1. Topology

Too coarse to recover the present bridge-facing effect by itself.

### 2. Shell order

A robust intermediate order-bearing layer that preserves part of the relevant organization.

### 3. Local weighted arrangement

A finer and more fragile relational support layer.

### 4. Full weighted relational configuration

The strongest current overall bridge-candidate structure.

The full-crossing result strengthens the second layer substantially.

## Marker–carrier consequence

The current result does not yet establish shell as a full carrier.

However, it materially shifts the internal balance.

A more defensible current wording is now:

> shell structure appears to participate in the bridge-supporting scaffold rather than merely marking it from the outside.

This is stronger than a pure marker reading.

The current bridge picture increasingly resembles an internally organized scaffold with multiple sublayers of differing robustness and sensitivity.

## Why this still remains provisional

Several reasons still require caution.

### 1. Small synthetic baseline

The comparison still uses the current BMC template baseline rather than a project-derived real baseline.

### 2. Scaffold-level readout architecture

The shell-facing metrics are useful and already informative, but still early-stage.

### 3. No replicate batch yet

The current result is a matched comparison, but not yet a replicated run family.

### 4. No batch across multiple seeds yet

The graded ladder is promising, but still tested at one seed and one baseline.

For these reasons, the correct current status is:

- strong internal support
- not final proof

## Strongest current internal wording

A careful but strong current sentence is:

> The first BMC-01-SX full-crossing comparison supports a graded shell-order interpretation: preserving shell membership is least destructive, adjacent shell-crossing is more destructive, and full shell-crossing is more destructive again under matched conditions.

A compact shorthand is:

> shell-breaking scales with disruption

This is currently well supported internally.

## What should be tested next

The current result directly implies several next steps.

### 1. Repeat the three-mode ladder at low and high

The medium run is strong, but the full graded reading should be checked across:
- `low`
- `medium`
- `high`

### 2. Run the same ladder on a real extracted baseline

This is the most important next validation step.

### 3. Replicate across seeds

The graded ladder should be checked for stability under seed variation.

### 4. Refine shell-specific readouts

Particularly useful next refinements include:
- shell coherence retention
- shell-to-shell support redistribution
- refined shell boundary disruption
- shell-local concentration shift

### 5. Compare against non-shell grouping alternatives

If possible, shell-specific effects should later be contrasted with alternative grouping structures to test whether shell is uniquely informative.

## Strategic consequence

This result materially strengthens the shell line in the bridge program.

The project should now treat shell order as a **live, graded intermediate scaffold hypothesis** rather than as a speculative side note.

That means future bridge testing should explicitly distinguish:
- shell-preserved order
- shell-broken order
- local weighted fine structure
- broader weighted relational configuration

This is a much stronger and more structured research direction than the original flat weighted-layer picture.

## Field list

1. `comparison_scope` — String — three-mode comparison addressed in this note  
2. `reference_run` — String — shell-preserving reference run  
3. `adjacent_crossing_run` — String — adjacent shell-crossing run  
4. `full_crossing_run` — String — full shell-crossing run  
5. `core_ladder_result` — String — main graded arrangement-signal result  
6. `supporting_metric_pattern` — String — additional metric pattern supporting the ladder  
7. `raw_observation` — String — first direct observation from the three-mode comparison  
8. `strongest_internal_result` — String — most important current internal result  
9. `shell_implication` — String — what the result implies about shell structure  
10. `non_claim` — String — stronger claim not yet justified  
11. `bridge_architecture_picture` — String — emerging layered bridge architecture  
12. `marker_carrier_consequence` — String — implication for scaffold vs carrier reasoning  
13. `provisional_limit` — String — reason the result remains bounded  
14. `internal_wording` — String — recommended current internal formulation  
15. `next_test_candidate` — String — immediate follow-up implied by the result  
16. `strategic_consequence` — String — broader impact on project direction

## Bottom line

The first **BMC-01-SX full-crossing comparison** is a significant internal result.

It supports a clear graded ladder:

> `within_shell < adjacent_shell_crossing < full_shell_crossing`

in bridge-facing disruption under matched medium-strength conditions.

That does not yet prove shell as the final bridge carrier. But it strongly supports something important:

> shell membership appears to preserve nontrivial bridge-relevant order, and broader shell-breaking destroys progressively more of that order.

This makes shell structure a much stronger candidate for a genuine intermediate order-bearing scaffold within the broader bridge architecture.
