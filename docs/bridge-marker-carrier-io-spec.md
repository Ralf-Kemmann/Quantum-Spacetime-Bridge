# Bridge Marker–Carrier I/O Specification

## Purpose of this document

This document defines the initial input/output specification for the first implementation phase of the **marker–carrier test program** in the **Quantum–Spacetime Bridge** project.

Its purpose is to translate the conceptual test strategy into a concrete execution structure that is reproducible, inspectable, and extensible. The focus is the first practical bridge experiment family:

> **Weighted relational intervention under controlled structural constraints**

This specification is internal and implementation-facing. It is intended to support disciplined test execution, result interpretation, and later auditability.

## Scope

This specification applies to the first bridge experiment block aimed at distinguishing:

- **marker behavior**
from
- **carrier behavior**

for the current bridge candidate localized in:

- **weighted relational structure**

The initial concrete pilot should be understood as:

> **BMC-01 — Weighted Relational Scramble Probe**

This document can later be extended for additional intervention families such as homogenization, local lesioning, and reconstruction tests.

## Core experiment identity

### Block identifier
`BMC-01`

### Block title
`Weighted Relational Scramble Probe`

### Core question
How does the bridge-relevant readable effect respond when the weighted relational arrangement is selectively disturbed while the coarser structural shell is preserved as far as reasonably possible?

### Immediate hypothesis contrast
- **H(M)** marker hypothesis
- **H(C)** carrier hypothesis

## Input structure

The experiment should begin from a clearly defined baseline state.

### 1. Baseline structural input

The implementation must take as input a baseline representation of the relevant weighted relational system. At minimum, the input should allow access to:

- node identities
- pair or edge identities
- weighted relational assignments
- any coarser structural shell needed for control comparison
- the currently used bridge-relevant readout basis

### 2. Baseline metadata input

Each run should also include baseline metadata sufficient to identify:

- source dataset or source state
- framework line
- parameter setting
- baseline readout context
- intervention family
- intervention strength level
- random seed, if stochastic intervention is used

### 3. Optional control-shell inputs

Where available, the experiment should also include explicit or derived control representations such as:

- adjacency / topology shell
- distance-like surrogate shell
- coarse graph summary shell

These are not always the primary object of intervention, but they are necessary for interpretation.

## Minimal input files

The minimal initial pilot should produce or require the following logical inputs.

1. `baseline_state.json`  
   baseline structural state summary

2. `baseline_relational_table.csv`  
   edge/pair-wise table of weighted relational assignments

3. `baseline_readout.json`  
   bridge-relevant baseline readout summary

4. `run_config.yaml`  
   intervention and execution settings

5. `run_metadata.json`  
   execution metadata snapshot

These may be generated upstream if they do not already exist in precisely this form.

## Required input fields

The exact file schema may evolve, but the initial implementation should support at least the following logical fields.

### Baseline relational table — minimal fields

- `pair_id`
- `endpoint_a`
- `endpoint_b`
- `weight`
- `local_group` or equivalent grouping field if neighborhood-preserving scrambling is used
- `shell_label` or equivalent if shell-constrained scrambling is used

### Baseline state summary — minimal fields

- `run_id`
- `source_label`
- `framework_label`
- `baseline_topology_summary`
- `baseline_geometry_summary`
- `baseline_weight_summary`

### Baseline readout summary — minimal fields

- `bridge_signal_score`
- `readability_label`
- `d1_d2_separation_score`
- `support_side_score` if applicable
- `weighted_relational_contrast_score`

## Intervention configuration

The first pilot should expose intervention settings explicitly.

### Core intervention fields

- `intervention_family`
- `intervention_variant`
- `intervention_strength`
- `preserve_topology`
- `preserve_shell_membership`
- `preserve_global_weight_distribution`
- `random_seed`
- `replicate_count`

### Recommended initial variants

For BMC-01, the following variants are recommended:

1. `global_weight_permutation`
2. `within_shell_weight_permutation`
3. `within_local_group_weight_permutation`

### Recommended initial strength levels

- `low`
- `medium`
- `high`

These may later be mapped to numeric control parameters.

## Execution outputs

The experiment should produce a transparent set of outputs that allow both direct interpretation and later audit.

## Minimal output files

1. `intervention_table.csv`  
   edge/pair-level view of the modified weighted relational structure

2. `readout_comparison.csv`  
   comparison of baseline and perturbed readouts

3. `control_shell_comparison.csv`  
   comparison of topology-like and geometry-like control shells before and after perturbation

4. `decision_summary.json`  
   compact machine-readable decision summary for marker/carrier interpretation status

5. `block_readout.md`  
   human-readable summary of the run

6. `run_metadata.json`  
   execution metadata snapshot

7. `summary.json`  
   compact block-level result bundle

## Output interpretation layers

The outputs should support three distinct interpretation layers.

### 1. Structural intervention layer

What exactly was changed in the weighted relational layer?

This layer is represented by:
- `intervention_table.csv`
- selected summary fields in `summary.json`

### 2. Bridge-readout layer

What happened to the bridge-relevant readable effect?

This layer is represented by:
- `readout_comparison.csv`
- `decision_summary.json`
- `block_readout.md`

### 3. Control-shell layer

What remained stable in topology-like or geometry-like surrogate shells?

This layer is represented by:
- `control_shell_comparison.csv`

This separation is essential for meaningful marker–carrier interpretation.

## Decision logic outputs

The decision summary should not force a false binary. It should use graded internal labels.

### Required decision fields

- `decision_label`
- `marker_support_level`
- `carrier_support_level`
- `test_informativeness`
- `primary_reason`
- `secondary_reason`
- `topology_preservation_status`
- `geometry_surrogate_preservation_status`
- `weighted_relational_disruption_status`

### Allowed initial decision labels

- `marker_supported`
- `carrier_leaning`
- `carrier_supported`
- `undecided`
- `test_not_informative`

## Suggested output directory convention

The initial recommended directory convention is:

```text
runs/BMC-01/<RUN_ID>/
```

with contents such as:

```text
runs/BMC-01/<RUN_ID>/
  run_config.yaml
  run_metadata.json
  baseline_state.json
  baseline_readout.json
  intervention_table.csv
  readout_comparison.csv
  control_shell_comparison.csv
  decision_summary.json
  summary.json
  block_readout.md
```

If replicate runs are used, a nested structure may be added:

```text
runs/BMC-01/<RUN_ID>/replicates/<REPLICATE_ID>/
```

## Naming convention

### Block prefix
`BMC01`

### Example run identifier
`BMC01_2026-04-20_001`

### Replicate example
`BMC01_2026-04-20_001_rep03`

The exact format may be adapted, but block identity and date should remain visible.

## Minimal readout fields

The `readout_comparison.csv` and `summary.json` should include at least the following bridge-relevant readout fields.

- `baseline_bridge_signal_score`
- `perturbed_bridge_signal_score`
- `delta_bridge_signal_score`
- `baseline_d1_d2_separation_score`
- `perturbed_d1_d2_separation_score`
- `delta_d1_d2_separation_score`
- `baseline_weighted_relational_contrast_score`
- `perturbed_weighted_relational_contrast_score`
- `delta_weighted_relational_contrast_score`
- `baseline_readability_label`
- `perturbed_readability_label`

## Minimal control-shell comparison fields

The `control_shell_comparison.csv` should include at least:

- `topology_similarity_score`
- `geometry_surrogate_similarity_score`
- `global_weight_distribution_similarity_score`
- `local_group_preservation_score`
- `shell_preservation_score`

These values do not themselves decide marker vs carrier. They establish whether the intervention was interpretable.

## Informativeness rule

A run should be marked `test_not_informative` if any of the following holds:

- topology changed too strongly to isolate weighted-layer role
- geometry-like surrogates changed too strongly to isolate weighted-layer role
- intervention implementation violated its own preservation constraints
- readout collapse is total but structurally uninterpretable
- readout stability is total but intervention strength was too weak to matter

This rule is crucial to avoid over-reading bad interventions.

## Minimal block readout structure

The `block_readout.md` should contain:

1. run identity  
2. baseline description  
3. intervention description  
4. bridge-readout change summary  
5. topology/geometry-control summary  
6. marker-vs-carrier interpretation  
7. informativeness assessment  
8. next-step note

This keeps the human-readable output aligned with the machine summary.

## Recommended first implementation boundaries

The first implementation should remain deliberately small.

### Recommended boundaries
- only one intervention family: weighted scramble
- only a few variants
- only a small number of readouts
- only a graded decision rubric
- no broad mechanistic language in output labels

### Not yet required
- full bridge mechanism scoring
- full hierarchy mapping
- large multi-block orchestration
- outward-facing interpretation documents as primary outputs

The goal of BMC-01 is discrimination, not grand synthesis.

## Follow-up extensions

Once BMC-01 is working, likely next extensions include:

- `BMC-02` weight homogenization probe
- `BMC-03` local bridge-path lesion probe
- `BMC-04` reconstruction test block

These should build on the same I/O philosophy where possible.

## Field list

1. `block_identifier` — String — block code for the experiment family  
2. `block_title` — String — human-readable name of the experiment block  
3. `core_question` — String — central scientific question addressed by the block  
4. `hypothesis_label` — String — hypothesis class such as `H(M)` or `H(C)`  
5. `baseline_input` — String — input representing the unperturbed structural state  
6. `baseline_metadata` — String — metadata describing source and execution context  
7. `control_shell_input` — String — optional coarse structural shell used for interpretation  
8. `input_file` — String — required or expected input file name  
9. `input_field` — String — logical field required inside an input file  
10. `intervention_family` — String — high-level perturbation class  
11. `intervention_variant` — String — specific perturbation variant  
12. `intervention_strength` — String — intensity level of the perturbation  
13. `output_file` — String — produced output file name  
14. `output_interpretation_layer` — String — structural, bridge-readout, or control-shell layer  
15. `decision_field` — String — field used in the decision summary  
16. `decision_label` — String — graded run outcome label  
17. `directory_convention` — String — recommended path structure for outputs  
18. `run_identifier` — String — unique identifier for one run  
19. `readout_field` — String — bridge-relevant score or label  
20. `control_field` — String — control-shell comparison field  
21. `informativeness_rule` — String — rule determining whether the run is interpretable  
22. `block_readout_section` — String — section required in the Markdown run summary  
23. `implementation_boundary` — String — deliberate limit of the first implementation phase  
24. `follow_up_extension` — String — likely next experiment block after BMC-01

## Bottom line

The first bridge marker–carrier implementation should be small, explicit, and audit-friendly.

Its job is not to prove the full bridge, but to create a disciplined experiment in which the **weighted relational layer** is perturbed, the **bridge-relevant readout** is tracked, and the **coarser structural shell** is monitored closely enough that marker and carrier behavior begin to separate in an interpretable way.
