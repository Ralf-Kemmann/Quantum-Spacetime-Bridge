# BMC-01 Readout Upgrade Note

## Purpose of this document

This note records the first major methodological lesson from the initial dry run of:

- `BMC-01`
- `Weighted Relational Scramble Probe`

Its purpose is to explain why the current implementation is already useful as a software and intervention scaffold, but not yet sufficient as a bridge-discrimination experiment in the stronger scientific sense.

The issue is not that the intervention failed. The issue is that the current readout layer is still too insensitive to the specific kind of structural change that BMC-01 introduces.

## Immediate result of the first dry run

The first dry run showed the following pattern:

- the script executed successfully
- all intended output files were produced
- the intervention table confirmed that weights were actually reassigned across pairs
- many pair-level weights changed substantially
- yet the current bridge-facing summary scores remained unchanged

This is the key methodological observation.

## What actually happened

The current intervention:

- permuted weights across pair assignments
- preserved the overall multiset of weight values
- preserved topology
- preserved much of the coarse structural shell

So the **arrangement** of weights changed, but the **distribution** of weight values remained essentially the same.

## Why the current readouts failed to react

The present readout layer is dominated by **distribution-sensitive** but not sufficiently **arrangement-sensitive** measures.

Examples of current first-pass readouts include:

- coefficient-of-variation style bridge signal proxy
- D1/D2 separation proxy based on value spread
- weighted relational contrast proxy based on deviation from the mean

These measures are legitimate as transparent first-pass summaries, but they mostly depend on:

- which values exist
- how spread out the values are
- how the value distribution looks in aggregate

They do **not** sufficiently capture:

- where the values are located
- which endpoints carry which weights
- how weights are organized across local relational structure
- whether the same weight multiset has been rearranged into a different bridge-relevant pattern

This is why the dry run changed the structure but not the readout.

## Core methodological conclusion

The first BMC-01 dry run shows:

> the intervention is already structurally more bridge-relevant than the current readout layer

That is an important and useful result.

It means the experiment is not yet scientifically informative enough for marker–carrier discrimination, but it also means the project has already identified the next technical bottleneck very clearly.

## What the first dry run does support

The dry run already supports several positive conclusions:

### 1. The implementation scaffold works

The BMC-01 script is operational and produces the intended output bundle.

### 2. The intervention logic works

The intervention table confirms that pair-level weights are genuinely being changed.

### 3. The I/O structure is viable

The run bundle format, summary outputs, metadata files, and block readout are already usable.

### 4. The current limitation is localized

The main limitation is not the run orchestration or intervention mechanism. It is the readout layer.

This is a strong engineering advantage because it localizes the next upgrade target.

## What the first dry run does not support

The dry run does **not** support the claim that marker behavior has already been demonstrated.

That would be an over-reading.

Why not?

Because if the readout is invariant under relational rearrangement, then a “marker-supported” decision may simply mean that the readout failed to see the intervention, not that the bridge candidate survived it in a scientifically meaningful way.

This distinction is crucial.

## Required upgrade direction

The next version of BMC-01 needs **arrangement-sensitive readouts**.

These are readouts that respond not only to the weight distribution, but to the **placement**, **assignment**, and **local organization** of weights in the relational structure.

## Recommended readout upgrade classes

The following classes are recommended for the next implementation pass.

### 1. Endpoint load readouts

These capture how the total or average weighted load changes at each endpoint.

Possible metrics:
- node total incident weight
- node mean incident weight
- node weighted imbalance
- node load dispersion

Why useful:
A permutation that changes where weights sit should often show up at the endpoint level even when global value distribution is unchanged.

### 2. Local-group arrangement readouts

These capture how weighted structure is organized inside `local_group` partitions.

Possible metrics:
- within-group weight variance
- within-group max/min spread
- group-local concentration score
- group-local endpoint asymmetry

Why useful:
If the intervention is constrained within local groups, then group-level organization becomes a natural readout surface.

### 3. Shell-placement readouts

These capture how weighted support is positioned within and across shell partitions.

Possible metrics:
- shell-level weight concentration by pair
- shell-local ordering stability
- shell-specific endpoint load asymmetry
- shell-to-shell support redistribution score

Why useful:
The current intervention already uses shell membership. The readout should therefore also inspect shell-structured organization.

### 4. Pair-to-neighborhood consistency readouts

These measure whether a pair’s weight remains structurally consistent with the weighted environment of its endpoints.

Possible metrics:
- pair weight vs endpoint neighborhood mean
- pair weight vs local-group median
- pair-level surprise relative to endpoint support context
- pair-to-neighborhood coherence score

Why useful:
This class begins to capture relational placement rather than just scalar distribution.

### 5. Relational asymmetry readouts

These measure whether weighted support becomes more or less unevenly distributed across structurally related regions.

Possible metrics:
- local asymmetry scores
- endpoint contrast imbalance
- region-to-region weighted skew
- support-side asymmetry index

Why useful:
This is closer to the bridge question than raw value statistics.

## Decision logic upgrade

The current decision logic is too permissive for readout-invariant cases.

### Current issue

The current dry run produced:

- intervention confirmed
- readout unchanged
- decision label: `marker_supported`

This is too strong for the current methodological state.

### Recommended rule change

If:
- intervention clearly changes pair-level weight placement
- but arrangement-sensitive readouts are absent or unresponsive
- and only distribution-style readouts are being used

then the decision should default to one of:

- `undecided`
or
- `test_not_informative`

rather than:
- `marker_supported`

This prevents the experiment from accidentally rewarding readout blindness.

## Recommended immediate implementation changes

The next BMC-01 upgrade should include at least the following:

1. add endpoint-load comparison metrics  
2. add local-group arrangement metrics  
3. add shell-placement metrics  
4. add at least one pair-to-neighborhood consistency score  
5. downgrade decision logic for readout-invariant but intervention-positive runs

These upgrades should remain transparent and small. There is no need yet to overbuild the block.

## Suggested near-term implementation philosophy

The next version should still remain a scaffold.

That means:
- a few strong arrangement-sensitive readouts are better than many weak ones
- every metric should be interpretable
- every metric should be written out explicitly
- no hidden scoring logic should creep in
- the experiment should still remain audit-friendly

The goal is not immediate sophistication. The goal is structural adequacy.

## Suggested next file-level consequences

A practical next step after this note would be one of the following:

- update `scripts/bmc01_weighted_relational_scramble.py`
- create a companion note such as `docs/bmc01-arrangement-readouts.md`
- define explicit output fields for endpoint-load and shell-placement metrics

## Field list

1. `dry_run_result` — String — key result of the first BMC-01 dry run  
2. `intervention_status` — String — whether weighted reassignment actually occurred  
3. `readout_limitation` — String — reason the current readout failed to respond  
4. `distribution_sensitive_measure` — String — measure reacting mainly to value distribution  
5. `arrangement_sensitive_measure` — String — measure reacting to placement and local organization  
6. `core_methodological_conclusion` — String — central lesson from the dry run  
7. `supported_positive_conclusion` — String — what the dry run already justifies  
8. `non_supported_claim` — String — claim that must not yet be made  
9. `upgrade_class` — String — class of readouts recommended for the next version  
10. `decision_logic_issue` — String — current over-reading risk in decision labeling  
11. `recommended_rule_change` — String — improved decision behavior for non-informative readout cases  
12. `implementation_change` — String — concrete next modification to BMC-01  
13. `implementation_philosophy` — String — principle for the next scaffold upgrade

## Bottom line

The first BMC-01 dry run did not fail. It exposed the next real bottleneck.

The intervention already changes the relational arrangement of weights. The current readout layer is simply too insensitive to that arrangement change.

This means the next task is clear:

> upgrade BMC-01 from distribution-sensitive readouts toward arrangement-sensitive readouts, and prevent readout invariance from being misclassified as marker support.

That is the correct next step if BMC-01 is to become a meaningful bridge marker–carrier discriminator.
