# BMC-01 Shell-Crossing I/O Specification

## Purpose of this document

This document defines the initial input/output specification for the **shell-crossing extension** of the BMC-01 bridge experiment family in the **Quantum–Spacetime Bridge** project.

Its purpose is to turn the shell-focused follow-up question into a concrete implementation structure.

The specific scientific motivation is:

> determine whether breaking shell membership damages the bridge-facing response more strongly than shell-preserving reassignment under otherwise comparable conditions

This specification is internal and implementation-facing. It is not a public interpretation document.

## Scope

This specification applies to the next focused BMC-01-style intervention block that compares:

- **shell-preserving weighted permutation**
with
- **shell-crossing weighted permutation**

The immediate use case is a controlled follow-up to the first BMC-01 matrix.

## Core experiment identity

### Block identifier
`BMC-01-SX`

### Block title
`Shell-Preserving vs Shell-Crossing Weighted Permutation Probe`

### Core question
Does shell-crossing reassignment produce stronger bridge-facing disruption than shell-preserving reassignment when the global weight multiset and topology are kept broadly stable?

### Immediate interpretation target
- shell as weak label
vs
- shell as intermediate order-preserving layer

## Required baseline inputs

The shell-crossing block should begin from the same baseline logic already used in BMC-01, but now shell membership becomes a primary controlled variable.

### Required baseline files

1. `baseline_relational_table.csv`
2. `baseline_state.json`
3. `baseline_readout.json`
4. `run_config.yaml` or `run_config.json`
5. `run_metadata.json`

### Required baseline columns in relational table

The baseline relational table must include at least:

1. `pair_id`
2. `endpoint_a`
3. `endpoint_b`
4. `weight`
5. `shell_label`

### Optional but recommended columns

6. `local_group`
7. additional shell-adjacency or shell-order metadata if available

## Core intervention classes

The shell-focused block should expose at least two explicit intervention classes.

### 1. `within_shell_weight_permutation`

This is the shell-preserving comparator.

**Definition:**  
Weights may be reassigned only to pairs inside the same shell label.

### 2. `shell_crossing_weight_permutation`

This is the new shell-breaking intervention.

**Definition:**  
Weights may be reassigned across shell boundaries according to a defined shell-crossing policy.

This new class is the central addition.

## Shell-crossing policy variants

The shell-crossing variant should not remain underspecified. It should expose explicit policy modes.

### Recommended initial policy modes

#### A. `adjacent_shell_crossing`
Weights may be reassigned only between neighboring shell labels.

Example:
- `s_1 ↔ s_2`
- `s_2 ↔ s_3`

This is the preferred initial mode because it is controlled and interpretable.

#### B. `full_shell_crossing`
Weights may be reassigned freely across all shell labels.

This is the stronger stress mode.

#### C. `boundary_focused_crossing`
Only pairs near designated shell boundaries are targeted.

This is more advanced and not required for the first implementation pass.

## Intervention strength

The shell-crossing block should use the same basic strength ladder as BMC-01 for comparability.

### Allowed initial strength labels

- `low`
- `medium`
- `high`

### Meaning

Strength continues to refer to the fraction of weights or eligible pairs affected by reassignment.

This should remain explicit in metadata.

## Preservation constraints

To keep the shell comparison interpretable, the following preservation rules should hold as far as possible.

### Required preservation targets

1. `preserve_topology = true`
2. `preserve_global_weight_distribution = true`
3. `preserve_pair_count = true`
4. `preserve_node_count = true`

### Optional preservation targets

5. `preserve_local_group_membership` where relevant
6. `preserve_shell_count_distribution` where relevant

The shell-crossing block is allowed to break shell assignment consistency, but should not casually break everything else.

## Required configuration fields

The run configuration should include at least:

- `block_identifier`
- `block_title`
- `intervention_family`
- `intervention_variant`
- `shell_crossing_policy`
- `intervention_strength`
- `preserve_topology`
- `preserve_global_weight_distribution`
- `random_seed`
- `replicate_count`

## Required output files

The block should produce a run bundle closely aligned with BMC-01 for comparability.

### Minimal output set

1. `intervention_table.csv`
2. `readout_comparison.csv`
3. `control_shell_comparison.csv`
4. `decision_summary.json`
5. `summary.json`
6. `block_readout.md`
7. `run_metadata.json`

### Recommended additional shell-focused output

8. `shell_crossing_summary.csv`

This file should summarize how much shell membership was actually violated by the intervention.

## Required shell-crossing output fields

The shell-crossing summary should include at least:

- `pair_id`
- `baseline_shell_label`
- `perturbed_shell_label` or target-shell assignment indicator
- `shell_crossing_flag`
- `shell_distance` if shell adjacency order is defined
- `weight`
- `baseline_weight`
- `weight_delta`

This makes the shell-breaking action explicit and auditable.

## Required readout fields

The shell-crossing block should keep existing arrangement-sensitive readouts and emphasize shell-facing ones.

### Existing readouts to retain

- `endpoint_load_shift_score`
- `endpoint_load_dispersion_shift_score`
- `pair_neighborhood_consistency_shift_score`
- `arrangement_signal_score`

### Shell-focused readouts to require

- `shell_arrangement_shift_score`
- `shell_boundary_disruption_score`
- `shell_to_shell_support_redistribution_score`
- `shell_coherence_retention_score`

If not all are implemented immediately, the first version should at minimum expose:

- `shell_arrangement_shift_score`
- `shell_boundary_disruption_score`

## Control-shell comparison fields

The `control_shell_comparison.csv` should include:

- `topology_similarity_score`
- `geometry_surrogate_similarity_score`
- `global_weight_distribution_similarity_score`
- `shell_preservation_score`
- `shell_crossing_fraction`
- `shell_distance_mean` if defined

The purpose is to distinguish true shell effects from uncontrolled general disruption.

## Minimal decision logic

The decision logic should remain cautious and graded.

### Suggested decision labels

- `shell_order_supported`
- `shell_order_leaning`
- `undecided`
- `test_not_informative`

### Minimal interpretation rule

A run should lean toward shell-order support when:

- shell-crossing perturbation produces stronger disruption than matched shell-preserving perturbation
- shell-specific readouts show clear additional damage
- topology remains preserved
- the global weight distribution remains preserved
- the effect is not explained by generic uncontrolled collapse

## Comparison requirement

The shell-crossing block should not be interpreted in isolation.

Each shell-crossing run should be compared against a matched shell-preserving run with the same:

- baseline
- strength
- seed policy
- readout architecture

This matched comparison is essential.

## Suggested directory convention

A practical directory structure is:

```text
runs/BMC-01-SX/<RUN_ID>/
```

with contents such as:

```text
runs/BMC-01-SX/<RUN_ID>/
  run_config.json
  run_metadata.json
  intervention_table.csv
  shell_crossing_summary.csv
  readout_comparison.csv
  control_shell_comparison.csv
  decision_summary.json
  summary.json
  block_readout.md
```

For paired comparison, a batch structure may be used:

```text
runs/BMC-01-SX/<BATCH_ID>/
  preserving_<...>/
  crossing_<...>/
  comparison_summary.csv
  comparison_readout.md
```

## Naming convention

### Block prefix
`BMC01SX`

### Example preserving run
`BMC01SX_preserving_adjacent_low_001`

### Example crossing run
`BMC01SX_crossing_adjacent_low_001`

### Example batch
`BMC01SX_batch_2026-04-20_001`

The naming should keep preserving vs crossing visible at a glance.

## Informativeness rule

A run should be classified as `test_not_informative` if:

- topology preservation fails
- shell-crossing fraction is too small for the intended strength
- shell-preserving and shell-crossing interventions are not meaningfully comparable
- shell-specific readouts are absent or inconsistent
- global disruption overwhelms shell-specific interpretation

This avoids over-reading noisy collapse.

## Minimal block readout structure

The `block_readout.md` should contain:

1. run identity  
2. baseline description  
3. intervention policy description  
4. shell-crossing summary  
5. bridge-facing readout changes  
6. shell-specific readout changes  
7. preserving-vs-crossing interpretation  
8. informativeness assessment  
9. next-step note

## Recommended first implementation boundary

The first implementation should remain narrow.

### Recommended boundary

- implement only one new intervention family:
  - `shell_crossing_weight_permutation`
- start with one policy mode:
  - `adjacent_shell_crossing`
- use the existing BMC-01 readout architecture plus a small shell-focused extension
- compare directly against `within_shell_weight_permutation`

### Not yet required

- multi-hop shell-distance logic beyond adjacency
- fully physical shell interpretation
- large orchestration layer
- outward-facing inference language

The first goal is disciplined discrimination, not grand synthesis.

## Suggested immediate implementation consequence

The cleanest next implementation step is:

- extend `bmc01_weighted_relational_scramble.py`
or
- create `scripts/bmc01_shell_crossing_probe.py`

with a first explicit:
- `shell_crossing_weight_permutation`
- `adjacent_shell_crossing`

mode and a paired comparison output.

## Field list

1. `block_identifier` — String — code of the shell-focused experiment block  
2. `block_title` — String — human-readable title of the block  
3. `core_question` — String — scientific question addressed by shell-preserving vs shell-crossing comparison  
4. `baseline_input_file` — String — required baseline input file  
5. `required_input_field` — String — field that must exist in the baseline relational table  
6. `intervention_class` — String — preserving or crossing intervention type  
7. `shell_crossing_policy` — String — shell-crossing policy mode such as `adjacent_shell_crossing`  
8. `intervention_strength` — String — strength level of reassignment  
9. `preservation_constraint` — String — structural property intended to remain stable  
10. `output_file` — String — produced run output file  
11. `shell_crossing_output_field` — String — field documenting shell-breaking action explicitly  
12. `readout_field` — String — bridge-facing or shell-facing score  
13. `control_field` — String — control comparison field  
14. `decision_label` — String — graded interpretation label  
15. `comparison_requirement` — String — requirement for matched preserving vs crossing comparison  
16. `directory_convention` — String — recommended path layout for outputs  
17. `informativeness_rule` — String — condition under which the run should not be over-read  
18. `implementation_boundary` — String — deliberate limit of the first shell-crossing implementation phase  
19. `implementation_consequence` — String — next practical code-level consequence of this spec

## Bottom line

The shell-crossing follow-up should be implemented as a tightly matched comparison to shell-preserving reassignment.

Its job is not to prove shell as a final carrier in one step, but to test a much sharper question:

> does breaking shell membership damage bridge-facing organization more strongly than preserving shell membership while scrambling finer weight assignment?

If yes, shell structure becomes much harder to treat as a mere technical label and much more plausible as a genuine intermediate order-bearing layer.
