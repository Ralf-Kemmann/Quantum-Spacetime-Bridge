# QSB-BRIDGE-DATA-02E Control Mimicry Revision Readout

## Purpose

DATA-02E analyzes why DATA-02D controls passed or failed. It is a synthetic/reference-style diagnostic revision block, not a larger validation step.

## Inputs

Primary inputs are local DATA-02D outputs from `runs/QSB-BRIDGE-DATA-02D/diagnostic_separation_open/`. No external data were downloaded. No coordinates or geometry-derived `K_ij` were used.

## Befund

- controls analyzed: 32
- failed controls from DATA-02D: 8
- degenerate controls classified: 8
- high-risk control families: 4
- lowest original/control delta: {'control_id': 'within_system_label_shuffle__adamantane', 'original_system_id': 'adamantane', 'original_control_delta': 0.0}
- primary revision target: within_system_label_shuffle__adamantane
- stop/go outcome: go_revision_targets_identified_with_documented_boundaries

The DATA-02D warning is carried forward: some controls show zero/low original-control contrast, especially within-system label shuffles for small/uniform systems.
The QSB-BRIDGE-NUM-05C warning is carried forward: local-neighborhood sensitivity under small additive magnitude noise at 0.02.

## Interpretation

DATA-02E analyzes why DATA-02D controls passed or failed. DATA-02E does not prove physical recognition. Degenerate controls are not discarded; they are classified as a boundary/failure mode. Persistent mimicry is a valid negative/boundary finding. Any improved diagnostic must avoid merely tuning to the known controls.

## Hypothese

The current failed controls appear to preserve one or more diagnostic scaffold features: labels, topology, degree distribution, local environment, or the combined weighted component set. Adamantane within-system label shuffle remains the key zero-delta fake passport case.

## Offene Luecke

The block classifies mimic modes using DATA-02D component scores. It does not independently establish which synthetic scaffold feature should be physically preferred, and it does not prove that any real bonding or electronic structure has been recognized.

## Consequences for next blocks

Next blocks should inspect failed controls explicitly, avoid hiding mimicry behind aggregate scores, flag weak or degenerate controls, and keep persistent mimicry as a reportable boundary finding.

## Claim Boundary

DATA-02E provides no:

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

## Machine-readable outputs list

- `summary.json`
- `resolved_config.json`
- `control_mimic_failure_inventory.csv`
- `control_destruction_effectiveness_summary.csv`
- `diagnostic_specificity_summary.csv`
- `mimic_family_risk_summary.csv`
- `revision_recommendation_summary.csv`
- `proxy_risk_summary.csv`
- `readout.md`
