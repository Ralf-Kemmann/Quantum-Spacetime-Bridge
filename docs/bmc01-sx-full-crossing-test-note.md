# BMC-01-SX Full-Crossing Test Note

## Purpose of this document

This note defines the next immediate shell-focused follow-up test in the **Quantum–Spacetime Bridge** project:

- **within-shell preserving**
- **adjacent shell crossing**
- **full shell crossing**

Its purpose is to turn the current shell-order reading into a sharper graded stress test.

The motivating question is now:

> If adjacent shell crossing is already more destructive than shell-preserving reassignment, does full shell crossing become more destructive again?

This is an internal experimental note, not a public-facing claim.

## Why this test is now necessary

The current **BMC-01-SX** ladder already shows a nontrivial and encouraging pattern:

- `within_shell` is the least destructive
- `adjacent_shell_crossing` is consistently more destructive
- the difference persists across `low / medium / high`

That pattern already supports the reading that shell membership preserves part of the bridge-relevant order.

The next natural question is whether the shell effect is **graded**.

If shell structure is truly carrying intermediate order, then stronger forms of shell-breaking should produce stronger bridge-facing disruption.

That is exactly what `full_shell_crossing` is meant to test.

## Core test question

The central question is:

> Does `full_shell_crossing` produce stronger bridge-facing disruption than `adjacent_shell_crossing`, which is itself already more destructive than `within_shell`?

This gives the cleanest next stress hierarchy for the shell-order hypothesis.

## Current expected hierarchy

The current working expectation is:

> `within_shell` < `adjacent_shell_crossing` < `full_shell_crossing`

in terms of bridge-facing disruption.

This is the key ladder hypothesis.

## Interpretation of the hierarchy

### 1. `within_shell`

This preserves shell membership and only perturbs finer within-shell arrangement.

Interpretation:
- shell order scaffold remains intact
- only local fine arrangement is scrambled

### 2. `adjacent_shell_crossing`

This breaks shell membership, but only across neighboring shells.

Interpretation:
- local shell boundary crossing occurs
- shell scaffold is disturbed, but still in a comparatively controlled manner

### 3. `full_shell_crossing`

This allows unrestricted reassignment across all shells.

Interpretation:
- shell membership is globally broken
- the shell scaffold is stressed much more aggressively
- the shell order field is disrupted without adjacency restraint

If the shell-order reading is correct, this third mode should be the strongest stressor.

## Why full shell crossing is more than “just more random”

It is important not to reduce `full_shell_crossing` to generic additional noise.

The scientific point is not merely that more scrambling produces more damage.

The stronger claim being tested is:

> specifically broader shell-breaking should damage the bridge-facing response more strongly because shell structure itself is preserving part of the relevant order.

That is why shell-specific readouts matter.

If `full_shell_crossing` mainly raises shell-facing disruption measures while preserving topology and the global weight multiset, then the result becomes structurally meaningful, not merely more chaotic.

## Expected readout behavior

The following readouts are the most important.

### Primary expected movers

- `arrangement_signal_score`
- `shell_arrangement_shift_score`
- `shell_boundary_disruption_score`
- `shell_crossing_fraction`
- `shell_distance_mean`

### Secondary expected movers

- `endpoint_load_shift_score`
- `pair_neighborhood_consistency_shift_score`
- `endpoint_load_dispersion_shift_score`

### Expected pattern if shell order matters

Relative to:
- `within_shell`
and
- `adjacent_shell_crossing`

the `full_shell_crossing` run should show:

- higher shell-boundary disruption
- higher average shell distance
- higher or at least not lower arrangement signal
- broader endpoint load redistribution
- stronger pair-to-neighborhood inconsistency

This would be a strong graded shell-order pattern.

## Strong-support scenario

A strong-support result would look like this:

- `within_shell` = lowest disruption
- `adjacent_shell_crossing` = intermediate disruption
- `full_shell_crossing` = highest disruption

with the increase visible in:
- shell-specific metrics
- arrangement-sensitive metrics
- and ideally also in bridge-facing readability degradation

This would strengthen the internal reading that shell order is not binary but graded: the more strongly shell membership is broken, the more strongly bridge-relevant order is lost.

## Weak-support scenario

A weaker result would be:

- `adjacent_shell_crossing` and `full_shell_crossing` are nearly the same
- shell-specific metrics saturate early
- or the added shell-breaking does not produce a clearer bridge-facing effect

This would still be informative.

It could mean:
- local shell crossing already destroys most of the relevant shell-preserved order
- the baseline is too small to show a clean gradient
- the current readouts saturate too quickly
- or shell order is real, but the difference between adjacent and full crossing is not well resolved yet

## Non-supportive scenario

A more difficult outcome would be:

- `full_shell_crossing` is not stronger than `adjacent_shell_crossing`
- shell-specific metrics do not separate clearly
- and generic disruption dominates everything

That would weaken the graded shell-order interpretation, though not necessarily the broader shell relevance question.

## Why the current baseline still limits interpretation

As before, the current result must remain bounded because:

### 1. Template baseline
The current baseline is still synthetic and small.

### 2. Early readout architecture
The shell-facing readouts are already useful, but still scaffold-level.

### 3. No replicated batch yet
The current shell ladder is still an early probe, not yet a robust replicated batch.

Because of this, the full-crossing test should be read as a next stress step, not as final adjudication.

## Recommended direct comparison structure

The cleanest next comparison should be:

### At fixed strength
- `within_shell`
- `adjacent_shell_crossing`
- `full_shell_crossing`

with:
- same baseline
- same seed
- same run metadata structure
- same readout architecture

### Recommended first pass
Run at:
- `medium`

because the medium runs are already interpretable without being maximally saturated.

Then extend to:
- `low`
- `high`

if the first result is promising.

## Recommended decision logic

For the full-crossing test, the current graded internal labels could include:

- `shell_order_leaning`
- `shell_order_supported`
- `undecided`
- `test_not_informative`

A result should lean toward stronger shell-order support if:

- `full_shell_crossing` is clearly more disruptive than `adjacent_shell_crossing`
- shell-specific metrics scale upward in the expected direction
- topology remains preserved
- the global weight multiset remains preserved

## Internal wording recommendation

A careful internal sentence for the next stage is:

> The next decisive shell stress test is whether unrestricted shell-breaking produces a stronger bridge-facing response than boundary-limited shell crossing under otherwise matched conditions.

A compact shorthand is:

> `within_shell < adjacent < full` is now the key shell-order ladder to test.

## Strategic consequence

This test matters because it asks whether shell structure behaves like a **graded order scaffold**.

If the ladder holds, then shell order is not only relevant, but quantitatively structured:
- preserving shell membership retains more order
- breaking shell boundaries locally loses more order
- breaking shell boundaries globally loses even more order

That would significantly strengthen the interpretation of the bridge as an internally layered architecture.

## Suggested next implementation consequence

The practical next step is straightforward:

- run `bmc01_shell_crossing_probe.py`
with:
- `variant = shell_crossing_weight_permutation`
- `shell_crossing_policy = full_shell_crossing`

and compare directly against:
- `within_shell`
- `adjacent_shell_crossing`

preferably first at `medium`.

If the result looks promising, the next move is a full matched three-mode ladder.

## Field list

1. `core_test_question` — String — central question of the full-crossing follow-up  
2. `expected_hierarchy` — String — preserving vs adjacent vs full shell-breaking order expectation  
3. `within_shell_interpretation` — String — role of shell-preserving perturbation in the ladder  
4. `adjacent_crossing_interpretation` — String — role of adjacent shell crossing in the ladder  
5. `full_crossing_interpretation` — String — role of unrestricted shell crossing in the ladder  
6. `primary_expected_readout` — String — readout expected to react most strongly  
7. `secondary_expected_readout` — String — supporting readout expected to move  
8. `strong_support_scenario` — String — pattern supporting graded shell-order interpretation  
9. `weak_support_scenario` — String — weaker but still informative outcome  
10. `non_supportive_scenario` — String — pattern that would weaken the graded shell-order reading  
11. `baseline_limit` — String — reason current inference remains bounded  
12. `comparison_structure` — String — recommended direct comparison setup  
13. `decision_label` — String — graded internal interpretation label  
14. `internal_wording` — String — recommended internal phrasing for the test  
15. `strategic_consequence` — String — broader implication if the hierarchy holds  
16. `implementation_consequence` — String — next practical coding or run step

## Bottom line

The next shell-focused question is no longer whether shell matters at all.

It is now:

> does broader shell-breaking destroy more bridge-facing order than boundary-limited shell-breaking?

If the answer is yes, then shell structure begins to look not just relevant, but **gradedly order-bearing** — a real intermediate scaffold inside the bridge architecture rather than a mere static label system.
