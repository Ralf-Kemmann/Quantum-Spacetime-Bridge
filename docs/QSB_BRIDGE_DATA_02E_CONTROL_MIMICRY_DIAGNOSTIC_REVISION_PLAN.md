# QSB-BRIDGE-DATA-02E Diagnostic Sharpening Against Control Mimicry

Project anchor: `fa9dbaf (HEAD -> main, origin/main) Add QSB bridge DATA-02D program flow plan`

Block definition:

- block_id: QSB-BRIDGE-DATA-02E
- proposed run_id: control_mimicry_revision_open
- role: diagnostic revision and sharpening plan
- starting point: DATA-02D partial separation with control mimicry

This plan is strictly synthetic/reference-style. It makes no real-data validation claim, no molecular validation claim, no physical validation claim, no spacetime emergence claim, and no proof that electronic configurations or bonding organization are recognized.

## 1. Purpose

DATA-02E is not a larger validation step. It is a diagnostic revision and sharpening plan after DATA-02D found partial separation between original systems and controls, but also found control mimicry.

The purpose is to define how the next diagnostic block should inspect why some controls remain close to the original systems. DATA-02E should make the failure modes explicit before any later implementation changes are attempted.

The target is narrower than validation: identify mimic controls, classify likely mimic mechanisms, define conservative risk summaries, and preserve negative findings as first-class outputs.

## 2. Starting findings from DATA-02D

DATA-02E starts from the following DATA-02D findings:

- block_id: QSB-BRIDGE-DATA-02D
- run_id: diagnostic_separation_open
- stop_go_outcome: revise_diagnostics_due_to_control_mimicry
- original_system_count: 4
- control_count: 32
- control_family_count: 8
- separation_threshold: 0.2
- separation_pass_count: 24
- separation_fail_count: 8
- possible_negative_finding_present: True
- lowest original/control delta: 0.0
- highest-risk mimic control: within_system_label_shuffle__adamantane
- highest-risk mimic family: within_system_label_shuffle
- highest-risk mimic original system: adamantane

Warnings carried forward:

- QSB-BRIDGE-NUM-05C warning: local-neighborhood sensitivity under small additive magnitude noise at 0.02
- DATA-02C mimic warning: some controls show zero/low original-control contrast, especially within-system label shuffles for small/uniform systems

## 3. Main Problem

DATA-02D separates many controls, but fails on 8 controls at the selected separation threshold. The most important failure is a zero-delta adamantane within-system label-shuffle mimic:

- control: within_system_label_shuffle__adamantane
- family: within_system_label_shuffle
- original system: adamantane
- original/control delta: 0.0

This means the current diagnostic readout can identify many perturbed or mismatched controls, but some controls still preserve enough of the measured scaffold to pass as original-like. The problem is therefore not whether the DATA-02D scanner can separate anything. It can. The problem is that some counterfeit controls appear to carry the same measured signature.

Persistent mimicry must be treated as a boundary finding, not as something to hide behind aggregate separation counts.

## 4. Diagnostic Questions

DATA-02E should sharpen the next implementation around these questions:

- Which 8 controls failed separation?
- Are failures concentrated in specific control families?
- Are failures caused by uniform labels?
- Are failures caused by preserved topology or degree distribution?
- Are failures caused by local-environment reuse?
- Does combined_bonding_organization_score overweight label/topology sameness?
- Do some controls fail to destroy the relevant scaffold feature?
- Should weak or degenerate controls be explicitly flagged?
- Are small and uniform systems intrinsically more vulnerable to low-delta label shuffles?
- Are failed controls true diagnostic challenges, or controls that are too weak to serve their intended role?
- Which mimic modes remain after separating label effects from topology effects?

## 5. Proposed New Diagnostic Concepts

The following concepts are proposed for later implementation only. DATA-02E does not implement them in this plan file.

### control_destruction_effectiveness_score

- purpose: Estimate whether a control actually destroys the feature it is supposed to disrupt.
- likely inputs: original system identifier, control identifier, control family, original/control score delta, label distribution changes, topology changes, degree distribution changes, local-environment overlap measures.
- interpretation: High values would indicate that the control strongly disrupted the diagnostic scaffold. Low values would indicate a weak or degenerate control that may preserve too much of the original structure.
- claim boundary: This is a synthetic diagnostic adequacy score only. It does not show physical destruction, molecular realism, or recognition of real bonding organization.

### diagnostic_specificity_score

- purpose: Estimate whether a diagnostic score responds specifically to the intended scaffold feature rather than to broad sameness between original and control.
- likely inputs: per-score original/control deltas, control family labels, scaffold feature tags, combined_bonding_organization_score components, family-level pass/fail summaries.
- interpretation: High values would suggest that a score responds to targeted scaffold changes. Low values would suggest the score may be too generic or may overweight preserved labels/topology.
- claim boundary: This is a reference-style specificity estimate. It is not evidence of molecular validation, physical metric recovery, or real quantum dynamics.

### label_uniformity_risk_score

- purpose: Flag systems where label shuffling may be ineffective because labels are uniform, near-uniform, or repeated in a way that preserves the measured signature.
- likely inputs: label counts, label entropy, number of unique labels, within-system label-shuffle deltas, system size.
- interpretation: High values would indicate that label-based controls may be weak because shuffling labels changes little or nothing.
- claim boundary: This only describes synthetic label degeneracy. It is not proof that electronic configurations are recognized.

### topology_preservation_risk_score

- purpose: Flag controls that preserve graph topology strongly enough to keep the diagnostic scaffold intact.
- likely inputs: edge overlap, graph isomorphism indicators where available, adjacency similarity, path-length summaries, topology-sensitive score deltas.
- interpretation: High values would indicate that a control may be too topology-preserving to challenge topology-dependent diagnostics.
- claim boundary: This is not a claim about physical spacetime topology, molecular structure validation, or causal structure.

### degree_preservation_risk_score

- purpose: Flag controls that preserve degree distribution or degree-local patterns that may dominate the diagnostic readout.
- likely inputs: degree histograms, node-level degree matches, degree-sequence similarity, local degree neighborhood overlap, score deltas under degree-preserving controls.
- interpretation: High values would suggest that degree preservation may explain low original/control contrast.
- claim boundary: This is a synthetic graph diagnostic only. It does not establish physical insight or bonding recognition.

### local_environment_reuse_risk_score

- purpose: Flag controls that reuse local neighborhoods closely enough to preserve local diagnostic responses.
- likely inputs: local neighborhood fingerprints, radius-limited neighborhood overlap, node-label neighborhood patterns, NUM-05C sensitivity notes, small additive noise responses.
- interpretation: High values would indicate that local-environment reuse may allow a control to mimic the original system.
- claim boundary: This is a local synthetic scaffold risk measure. It does not validate real molecular environments or physical local neighborhoods.

### degenerate_control_flag

- purpose: Mark controls that do not meaningfully alter the targeted scaffold feature and should not be counted as strong separation challenges without qualification.
- likely inputs: control family, original/control delta, label uniformity risk, topology preservation risk, degree preservation risk, local-environment reuse risk.
- interpretation: `True` would mean the control may be weak, degenerate, or not destructive enough for its intended diagnostic role.
- claim boundary: This flag classifies synthetic control design risk. It does not remove failures and does not convert failed separation into validation.

### mimic_family_risk_summary

- purpose: Summarize control mimicry by family so that repeated failure modes are visible instead of buried in per-control rows.
- likely inputs: control family, pass/fail counts, minimum delta, median delta, systems affected, highest-risk system, degenerate control flags, proposed risk scores.
- interpretation: Families with repeated low-delta failures would be treated as high-risk mimic families requiring revision or more careful interpretation.
- claim boundary: This is a reporting summary, not a validation result and not evidence of physical emergence.

## 6. Proposed Outputs for Later Implementation

Planned files for later implementation may include:

- docs/QSB_BRIDGE_DATA_02E_RESULT_NOTE.md
- docs/QSB_BRIDGE_DATA_02E_RESULT_DISCUSSION.md
- data/QSB-BRIDGE-DATA-02E/README.md
- data/QSB-BRIDGE-DATA-02E/control_mimicry_revision_config.json
- scripts/qsb_bridge_data02e_control_mimicry_revision.py
- runs/QSB-BRIDGE-DATA-02E/control_mimicry_revision_open/summary.json
- runs/QSB-BRIDGE-DATA-02E/control_mimicry_revision_open/readout.md
- runs/QSB-BRIDGE-DATA-02E/control_mimic_failure_inventory.csv
- runs/QSB-BRIDGE-DATA-02E/control_mimicry_revision_open/control_mimic_failure_inventory.csv
- runs/QSB-BRIDGE-DATA-02E/control_mimicry_revision_open/control_destruction_effectiveness_summary.csv
- runs/QSB-BRIDGE-DATA-02E/control_mimicry_revision_open/diagnostic_specificity_summary.csv
- runs/QSB-BRIDGE-DATA-02E/control_mimicry_revision_open/mimic_family_risk_summary.csv
- runs/QSB-BRIDGE-DATA-02E/control_mimicry_revision_open/proxy_risk_summary.csv

These are planned outputs only. This plan creates no scripts, data files, or runs.

## 7. Stop/Go Criteria

Conservative DATA-02E outcomes should include:

- go_revision_plan_ready: The failed controls can be inventoried, mimic families can be summarized, and the proposed risk concepts are sufficient for a later implementation plan.
- revise_due_to_unclassified_mimic_modes: Some low-delta or zero-delta controls cannot be explained by the proposed risk classes and require additional diagnostic concepts.
- stop_due_to_missing_DATA02D_inputs: Required DATA-02D summary fields or per-control outputs are unavailable, so the revision cannot be responsibly specified.

Persistent mimicry is a valid boundary finding. If a control continues to mimic the original after sharper diagnostics, that result should be reported directly as a remaining limitation.

## 8. Human-Readable Bauchbild / Intuition

DATA-02D built the scanner. It can reject many counterfeit tiles, but not all of them.

DATA-02E checks why some counterfeit tiles pass the scanner. It asks whether the scanner is reading the intended feature, or whether some fake tiles keep enough of the same surface pattern, topology, degree structure, or local environment to look original.

Adamantane is the key fake passport case. The within-system label-shuffle control for adamantane passed with zero delta, so DATA-02E treats it as the clearest example of control mimicry that must be explained before stronger claims are considered.

## 9. Misstrauen / Self-Deception Risks

- risk of tuning diagnostics to known controls
- risk of making controls too easy
- risk of confusing control destruction with physical insight
- risk of hiding failures behind aggregate scores
- risk of over-reading scaffold labels
- risk of treating degenerate controls as successful evidence after the fact
- risk of converting a diagnostic boundary into a validation-sounding result
- risk of ignoring small-system or uniform-label edge cases because most controls separated

## 10. Claim Boundary

DATA-02E will not establish:

- real-data validation
- molecular validation
- physical validation
- spacetime emergence
- physical metric recovery
- causal structure
- de-Broglie confirmation
- real quantum dynamics
- proof that electronic configurations are recognized
- proof that bonding organization is physically recognized

DATA-02E remains a synthetic/reference-style diagnostic revision plan. It can organize and sharpen the interpretation of control mimicry, but it cannot validate real molecules, physical spacetime, real quantum dynamics, or physical bonding organization.
