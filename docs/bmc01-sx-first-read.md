# BMC-01-SX First Read

## Purpose of this document

This document records the first internal reading of the initial **BMC-01-SX** paired comparison in the **Quantum–Spacetime Bridge** project.

Its purpose is to capture the first structured interpretation of the matched comparison between:

- `within_shell_weight_permutation`
and
- `shell_crossing_weight_permutation` with `adjacent_shell_crossing`

under otherwise comparable conditions.

This is an internal reading note, not an outward-facing claim.

## Why this note matters

The first BMC-01 matrix already suggested that shell-preserving perturbation might be comparatively buffered. But the matrix alone did not provide the cleanest direct contrast.

The **BMC-01-SX** paired comparison does something sharper:

- same baseline
- same strength
- same seed
- same readout architecture
- same preserved weight multiset
- same preserved topology

but:
- one run preserves shell membership
- the other breaks shell membership by adjacent shell crossing

That makes the current comparison methodologically much stronger.

## Compared runs

### Shell-preserving reference run

- Run ID: `BMC01SX_within_shell_medium`
- Variant: `within_shell_weight_permutation`
- Strength: `medium`
- Seed: `123`

### Shell-crossing comparison run

- Run ID: `BMC01SX_shell_crossing_adjacent_medium`
- Variant: `shell_crossing_weight_permutation`
- Policy: `adjacent_shell_crossing`
- Strength: `medium`
- Seed: `123`

## Direct numerical contrast

### Shell-preserving run

- arrangement signal score: `0.148588`
- shell boundary disruption score: `0.000000`
- shell crossing fraction: `0.000000`
- shell distance mean: `0.000000`
- endpoint load shift score: `0.100000`
- shell arrangement shift score: `0.500000`
- pair-to-neighborhood consistency shift score: `0.084167`
- decision label: `undecided`

### Shell-crossing run

- arrangement signal score: `0.319266`
- shell boundary disruption score: `0.500000`
- shell crossing fraction: `0.500000`
- shell distance mean: `0.500000`
- endpoint load shift score: `0.230000`
- shell arrangement shift score: `0.666667`
- pair-to-neighborhood consistency shift score: `0.137500`
- decision label: `shell_order_leaning`

## First raw observation

The difference is not subtle.

Compared to the shell-preserving reference:

- arrangement-sensitive response is clearly stronger under shell crossing
- shell-specific disruption metrics activate as expected
- the run remains interpretable because topology and global weight multiset are preserved
- the decision logic moves from `undecided` to `shell_order_leaning`

This is the first direct internal result that makes shell structure look more like an active structural layer and less like a passive label.

## What the comparison shows

The current paired comparison shows:

> breaking shell membership is more destructive to the bridge-facing response than preserving shell membership while perturbing finer assignment within the shell.

This is the central result.

The importance of that statement is not rhetorical. It is structural.

If shell-preserving reassignment is buffered while shell-crossing reassignment is substantially more disruptive under matched conditions, then shell membership is preserving something real.

## What shell seems to preserve

The current result suggests that shell structure preserves at least part of:

- bridge-facing arrangement stability
- endpoint load organization
- shell-level support ordering
- pair-to-neighborhood consistency

This means shell is not only a grouping convenience. It appears to constrain how disruption propagates through the weighted relational system.

## First disciplined interpretation

The strongest current internal interpretation is:

> Shell membership appears to preserve nontrivial bridge-relevant order, and breaking shell membership produces measurably stronger structural disruption than shell-preserving reassignment.

This is stronger than the earlier matrix-based suspicion and is now supported by a direct matched comparison.

## Why this still remains a first read

Despite the strength of the current pattern, caution is still required.

### 1. Template baseline

The current paired comparison still uses the synthetic BMC template baseline, not yet a project-derived real baseline state.

### 2. Single strength level

The current contrast has been demonstrated at `medium`, but not yet across a full strength ladder.

### 3. Single crossing policy

The current comparison uses `adjacent_shell_crossing`, not yet `full_shell_crossing`.

### 4. Early shell-specific readouts

The shell-specific readout layer is already useful, but still scaffold-level rather than final.

For these reasons, the result should be treated as a **strong first internal indication**, not yet a final proof.

## Why the result is nevertheless important

The current paired comparison changes the internal project picture in a meaningful way.

Before this comparison, shell structure was a serious suspicion.

After this comparison, shell structure is better understood as a **supported intermediate-order candidate**.

This is still not equivalent to saying that shell is the final bridge carrier. But it does mean that the bridge candidate is increasingly difficult to interpret as a flat weighted layer without internal structural hierarchy.

## Emerging layered picture

The current internal bridge picture now looks more strongly layered:

1. **topology**  
   too coarse to capture the current effect by itself

2. **shell structure**  
   partially order-preserving, robust intermediate layer

3. **local weighted arrangement**  
   sensitive fine-structure layer

4. **full weighted relational configuration**  
   strongest current overall bridge-candidate layer

The BMC-01-SX comparison strengthens the second layer in this architecture.

## Marker–carrier consequence

The current result does not yet prove shell as a full carrier.

But it does make the following internal position more plausible:

> shell is not merely a marker of order, but may already participate in the bridge-supporting structural scaffold.

This is a significant shift.

The bridge candidate now looks less like:
- one diffuse weighted cloud

and more like:
- an internally organized architecture with robust and fragile sublayers

That is an important conceptual gain.

## Strongest current internal takeaway

The strongest current takeaway is:

> Shell-preserving scrambling perturbs fine arrangement, but shell-crossing perturbs the order scaffold itself.

The present paired result supports exactly this distinction.

That is why the comparison is scientifically valuable.

## What should be tested next

The next steps are now very clear.

### 1. Strength ladder for shell crossing

Run:
- `low`
- `medium`
- `high`

for:
- `within_shell_weight_permutation`
- `shell_crossing_weight_permutation`

under matched conditions

This will show whether the shell-order effect scales consistently.

### 2. Full shell-crossing comparison

Compare:
- `adjacent_shell_crossing`
vs
- `full_shell_crossing`

If full shell crossing is significantly more destructive again, the shell architecture becomes even more interesting.

### 3. Real baseline replication

Repeat the same preserving-vs-crossing comparison on a project-derived real baseline.

This is essential before stronger generalization.

### 4. Sharper shell-specific readouts

Develop:
- shell coherence retention
- shell boundary disruption score refinement
- shell-to-shell support redistribution
- shell-local concentration shift

These will make later interpretations stronger.

## Current internal wording recommendation

A careful internal sentence now justified is:

> The first BMC-01-SX paired comparison supports the interpretation that shell membership preserves part of the bridge-relevant order and that breaking shell membership produces measurably stronger disruption than shell-preserving reassignment.

A slightly shorter internal shorthand is:

> shell-crossing hits harder than shell-preserving under matched conditions

This is compact, concrete, and currently well supported.

## Outward-facing caution

Outward-facing texts should still avoid saying:

- shell structure is proven to be the bridge carrier
- shell structure is a physical law layer
- shell structure alone explains the bridge

Those statements are premature.

At most, later outward-facing language could cautiously say that:
- the weighted relational layer appears internally structured
- and shell-like organization may be part of that structure

## Strategic consequence

The strategic consequence is substantial:

The bridge program should now explicitly treat shell structure as a live internal hypothesis and not merely as an operational convenience.

That means future bridge testing should ask not only:
- whether weighted arrangement matters

but also:
- which internal layer of weighted arrangement carries which kind of order?

This is a richer and stronger research direction.

## Field list

1. `paired_comparison_scope` — String — preserving vs crossing comparison addressed by this note  
2. `reference_run` — String — shell-preserving reference run  
3. `comparison_run` — String — shell-crossing comparison run  
4. `numerical_contrast` — String — direct quantitative difference between preserving and crossing  
5. `raw_observation` — String — immediate first observation from the paired result  
6. `central_result` — String — strongest direct statement supported by the comparison  
7. `preserved_order_candidate` — String — type of order that shell membership appears to preserve  
8. `disciplined_interpretation` — String — strongest cautious internal interpretation  
9. `caution_reason` — String — reason the result is still a first read and not final proof  
10. `layered_bridge_picture` — String — emerging hierarchical internal bridge picture  
11. `marker_carrier_consequence` — String — implication for marker-vs-carrier reasoning  
12. `strongest_takeaway` — String — most important current internal conclusion  
13. `next_test_candidate` — String — immediate follow-up test implied by the result  
14. `internal_wording` — String — recommended current internal formulation  
15. `outward_facing_limit` — String — statement not yet warranted publicly  
16. `strategic_consequence` — String — broader implication for the research program

## Bottom line

The first BMC-01-SX paired comparison is a real step forward.

It shows that **shell-crossing** is measurably more destructive than **shell-preserving** reassignment under matched conditions.

That does not yet prove shell as a final bridge carrier. But it does support something important:

> shell membership appears to preserve nontrivial bridge-relevant order

This makes shell structure a much stronger candidate for a genuine intermediate order-bearing layer within the broader bridge architecture.
