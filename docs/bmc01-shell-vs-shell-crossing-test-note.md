# BMC-01 Shell vs Shell-Crossing Test Note

## Purpose of this document

This note defines the next focused follow-up test implied by the first **BMC-01** matrix in the **Quantum–Spacetime Bridge** project.

Its purpose is to sharpen the emerging shell interpretation by comparing two specific classes of perturbation:

- **shell-preserving perturbation**
- **shell-crossing perturbation**

The underlying question is no longer only whether weighted arrangement matters in general. It is now more specific:

> Does preserving shell membership retain a meaningful part of the bridge-relevant order, and does breaking shell membership damage that order more strongly?

This is an internal experimental note, not an outward-facing claim.

## Why this test is now necessary

The first BMC-01 matrix suggested a nontrivial pattern:

- global reweighting disrupts strongly
- local-group reweighting reacts early
- within-shell reweighting appears comparatively buffered at low and medium strengths

That buffered within-shell behavior creates a new structural suspicion:

> shell structure may already preserve part of the bridge-relevant organization

The most direct next test is therefore not another broad intervention family, but a comparison that isolates exactly this shell question.

## Core test question

The central question is:

> For comparable intervention strength, does shell-crossing perturbation damage the bridge-facing response more strongly than shell-preserving perturbation?

If the answer is consistently yes, then shell structure becomes much more credible as a genuine intermediate order layer.

## Definitions

### Shell-preserving perturbation

A shell-preserving perturbation is one in which weight reassignment is restricted so that each reassigned weight remains inside its original shell class.

Example:
- a weight associated with a pair in `s_2` may only be reassigned to another pair in `s_2`

This preserves shell membership while altering finer pair-level assignment.

### Shell-crossing perturbation

A shell-crossing perturbation is one in which weights are reassigned across shell boundaries.

Examples:
- `s_1` to `s_2`
- `s_2` to `s_3`
- unrestricted reassignment across all shells

This breaks shell membership stability while still preserving the global weight multiset if implemented as permutation-based reassignment.

## Minimal experimental contrast

The test should begin with the cleanest possible contrast:

1. **within-shell permutation**
2. **cross-shell permutation**

with matched:
- intervention strength
- random seed policy
- baseline input
- output readout structure

This makes the comparison interpretable.

## Why this comparison is stronger than the current matrix alone

The first matrix already hinted that shell-preserving perturbation may be less destructive. But the matrix did not yet include an explicitly shell-breaking counterpart matched to the shell-preserving design.

Without that direct comparison, shell robustness remains suggestive but underdetermined.

The shell-vs-shell-crossing design closes exactly that gap.

## Expected patterns

### Pattern A — Shell is only a weak label

If shell structure is not a meaningful order-preserving layer, then:
- shell-preserving and shell-crossing perturbations should not differ dramatically once intervention strength is comparable
- observed differences may be small, unstable, or explainable by secondary artifacts

Under this pattern, shell may be operationally convenient but not structurally important.

### Pattern B — Shell is a robust intermediate order layer

If shell structure already preserves part of the bridge-relevant organization, then:
- shell-preserving perturbation should be comparatively buffered
- shell-crossing perturbation should produce stronger arrangement-sensitive disruption
- this difference should remain visible even when topology and global weight distribution are held broadly stable

Under this pattern, shell becomes a serious candidate for an order-bearing intermediate layer.

### Pattern C — Shell is closer to a partial carrier than expected

A stronger version of Pattern B would be:
- shell-crossing perturbation causes a disproportionately strong collapse in bridge-facing readouts
- shell-preserving perturbation leaves much of the readable effect intact
- shell-sensitive metrics show strong boundary-disruption signatures

Under this pattern, shell may begin to look like more than an intermediate scaffold.

This stronger reading would still require caution, but it would substantially raise the importance of shell structure.

## Recommended intervention variants

The following variants should be considered in increasing order of interpretive sharpness.

### 1. Adjacent-shell crossing

Weights may move only between neighboring shells.

Examples:
- `s_1 ↔ s_2`
- `s_2 ↔ s_3`

This is a controlled shell-crossing design with relatively mild structural disruption.

### 2. Full shell-crossing permutation

Weights may move freely across all shell boundaries.

This is the cleanest strong contrast to shell-preserving permutation.

### 3. Boundary-focused shell-crossing

Only pairs near or across shell boundaries are targeted.

This is a more refined later-stage design and probably not necessary for the first pass.

## Required readout families

The existing arrangement-sensitive readouts remain relevant, but shell-specific readouts now become central.

### Keep

- endpoint load shift
- endpoint load dispersion shift
- pair-to-neighborhood consistency shift
- arrangement signal score

### Add or emphasize

- shell arrangement shift score
- shell coherence retention
- shell-to-shell support redistribution
- shell boundary disruption score
- shell-local concentration shift

These will allow the shell comparison to be read directly rather than indirectly.

## Minimal decision logic

The first interpretation logic should remain cautious and graded.

### Shell-order leaning

Use this when:
- shell-crossing consistently produces stronger disruption than shell-preserving perturbation
- the difference is visible in shell-sensitive readouts
- topology and global weight distribution remain broadly comparable

### Shell-order supported

Use this only if:
- the difference is robust across strengths and variants
- shell-preserving perturbation is repeatedly buffered
- shell-crossing perturbation is repeatedly stronger
- the result survives beyond one template baseline

### Undecided

Use this when:
- the difference is weak
- the readouts disagree
- the intervention is too destructive
- shell labels are not stably interpretable

## What would count as a strong result

A strong result would look roughly like this:

- `within_shell`: low to medium disruption
- `shell_crossing`: clearly higher disruption at matched strength
- shell-specific metrics respond strongly
- topology remains preserved
- global weight distribution remains preserved
- arrangement-sensitive readouts shift in the expected direction

This would not yet prove shell as a final bridge carrier, but it would make shell as intermediate order layer much harder to dismiss.

## What would count as a weak result

A weak or non-supportive result would look like this:

- shell-preserving and shell-crossing perturbations behave similarly
- shell-specific readouts do not separate the cases
- only generic disruption is observed
- topology or geometry-like surrogates collapse together
- the shell distinction does not add explanatory value

In that case, shell may be less structurally significant than currently suspected.

## Current internal wording recommendation

A good current internal formulation is:

> The next decisive shell test is whether shell-crossing perturbation damages the bridge-facing response more strongly than shell-preserving perturbation under otherwise comparable conditions.

This keeps the focus sharp and honest.

## Strategic consequence

This comparison is strategically important because it helps decide whether the emerging bridge architecture is merely:

- weighted relations plus arbitrary labels

or instead:

- layered weighted relations with a real shell-organized intermediate order field

That is a major structural difference.

## Suggested next implementation consequence

The practical next step after this note is likely one of the following:

- extend `bmc01_weighted_relational_scramble.py` with a `shell_crossing_weight_permutation` variant
- or create a dedicated block note such as `docs/bmc02-shell-crossing-io-spec.md`
- or both

The cleanest next move is probably to specify the shell-crossing intervention explicitly before coding it.

## Field list

1. `core_test_question` — String — central scientific question of the shell-vs-shell-crossing comparison  
2. `shell_preserving_definition` — String — definition of shell-preserving perturbation  
3. `shell_crossing_definition` — String — definition of shell-crossing perturbation  
4. `minimal_experimental_contrast` — String — minimal direct comparison needed for interpretation  
5. `pattern_a` — String — expected pattern if shell is not structurally important  
6. `pattern_b` — String — expected pattern if shell is a robust intermediate order layer  
7. `pattern_c` — String — stronger expected pattern if shell approaches partial carrier status  
8. `intervention_variant` — String — specific shell-crossing design option  
9. `required_readout_family` — String — readout class needed to interpret the result  
10. `decision_label` — String — cautious internal interpretation label  
11. `strong_result_condition` — String — condition under which shell-order reading becomes much stronger  
12. `weak_result_condition` — String — condition under which shell-order reading weakens  
13. `strategic_consequence` — String — broader project implication of the shell comparison  
14. `implementation_consequence` — String — likely next practical step after this note

## Bottom line

The shell question now deserves its own focused experiment.

The right next test is not a vague expansion of BMC-01, but a direct comparison between:

- **shell-preserving perturbation**
and
- **shell-crossing perturbation**

If shell-crossing proves consistently more destructive than shell-preserving reassignment under matched conditions, then shell structure becomes a much stronger candidate for a genuine intermediate order-bearing layer within the bridge architecture.
