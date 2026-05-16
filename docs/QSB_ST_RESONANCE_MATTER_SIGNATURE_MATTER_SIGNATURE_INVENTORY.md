# QSB-ST Resonance Matter Signature
## Matter Signature / Carrier Specificity Inventory

## 1. Purpose

This note inventories the rediscovered `typ_b_analysis` result cluster from the duplicate-quarantine archive as a Matter Signature / Carrier Specificity subpuzzle for QSB-ST Resonance Matter Signature.

It is an archival recovery and integration note. It is not a new theory proof, not a result rerun, and not a replacement for provenance cleanup or current-repository integration.

## 2. Why this inventory matters

The current working-tree `typ_b_analysis/results` directories appear mostly empty, while the duplicate-quarantine copy contains the actual result files. This creates a risk that prior Matter Signature carrier-axis tests are forgotten or recreated without reference to earlier readouts.

This inventory preserves the rediscovered structure in a compact form so later Bridge Architecture Synthesis work can decide what to rerun, retire, or connect to newer RMS and Carbon scaffold lines.

## 3. Archival source and status

Archival source location:

`/home/ralf-kemmann/Downloads/_duplicate_quarantine/run_20260429_091132/files/deBroglie_Kaster_Theorie/debroglie-phase-bridge/debroglie-phase-bridge/typ_b_analysis/results`

Status:

- Source context: duplicate-quarantine archival recovery.
- Active canonical status: not established by this note.
- Current-repo status: the corresponding working-tree result directories appear mostly empty.
- Interpretation status: inventory only; no claims are upgraded by this document.

## 4. Result clusters found

- `bridge_carrier_block_c_v1`
- `bridge_carrier_block_d_v1`
- `bridge_carrier_block_e_v1`
- `bridge_carrier_leave_one_out_v1`
- `bridge_carrier_minimal_set_block_b_v1`
- `bridge_minimal_model_v1`
- `debroglie_matter_signature` runs A-D
- `debroglie_matter_signature_isotope` runs A-C
- `debroglie_matter_signature_isotope_carbon` runs A-C
- `debroglie_matter_signature_isotope_strontium` runs A-C
- `debroglie_matter_signature_qc` run A
- `debroglie_matter_signature_qc_shell` run A
- `debroglie_matter_signature_qc_valence` run A
- `debroglie_matter_signature_vdw` runs A-C
- `n1_a1_b1_decoupling_v1`
- `n1_alt_neighborhood_v1 / v2 / v22`
- `n1_exportclass_nullmodel_v1`
- `n1_negative_vs_abs_markers_v1`
- `n1_negative_vs_abs_v1`

## 5. Matter Signature baseline runs

Matter Signature A-D readout summary:

- `overall_status: partly_supported`
- `matter_sensitive_status: supported` for A-C
- `mass_only_status: partly_supported` for A-C
- `max_matter_sensitive_delta: 5.0`
- `tau_candidate_count: 0` for A-C
- Run D: `overall_status: partly_supported`, `max_matter_sensitive_delta: 5.0`, `near_window_count: 0`

Bottom line: reproducible de-Broglie-related matter-signature surrogates exist, but robustness beyond trivial mass scaling remains an open question.

## 6. Isotope sensitivity runs

Isotope-line readout summary:

- `debroglie_matter_signature_isotope` A-C: supported
- `debroglie_matter_signature_isotope_carbon` A-C: supported
- `debroglie_matter_signature_isotope_strontium` A-C: supported

Interpretation: these isotope tests are candidate mass/nuclear-parameter sensitivity controls, not physical validation. They mark possible RMS sensitivity axes that require reruns, cleaned provenance, and external observable anchoring before they can be used as anything stronger than surrogate-level structure.

## 7. QC / shell / valence runs

QC, shell, and valence readout summary:

- `debroglie_matter_signature_qc` run A: supported
- `debroglie_matter_signature_qc_shell` run A: supported
- `debroglie_matter_signature_qc_valence` run A: supported

Interpretation: these suggest candidate quantum-chemical / shell / valence descriptor axes for RMS, but remain surrogate-level. They should be treated as candidate descriptor channels to preserve and test, not as evidence that QC, shell, or valence descriptors are true physical carriers.

## 8. VDW matter-interaction layer

VDW readout summary:

- `debroglie_matter_signature_vdw` run A: partly_supported
- `debroglie_matter_signature_vdw` runs B and C: supported
- VDW B/C notes:
  - `max_wave_delta: 5.0`
  - `max_combined_delta: 2.0`
- VDW B/C bottom line:
  - strongest wave candidate is hydrogen
  - strongest combined candidate is sodium

Central open question: whether the VDW matter layer brings real additional structure or whether the ordering remains mainly on the previous wave axis.

The inspected VDW run C reported `tau_response_score` and `tau_alignment_score` as `0.0 / off_window`. Therefore, the VDW line should not be over-read as tau-window support.

## 9. Bridge carrier / minimal model / negative-abs-positive blocks

N1 and negative/abs/positive readout summary:

- `n1_a1_b1_decoupling_v1`: supported
- Bottom line: Combined N1 pattern is primarily B1-driven while A1 remains weak across launchable classes.
- `n1_negative_vs_abs_v1`: inconclusive
- `n1_negative_vs_abs_markers_v1`: inconclusive
- Bottom line: current signal supports a shared upper block negative/abs over positive, but does not yet show a stable internal advantage of negative over abs.
- `n1_alt_neighborhood_v1 / v2 / v22`: inconclusive in the listed readouts.
- `n1_exportclass_nullmodel_v1`: supported.

Bridge Minimal Model readout pattern:

- `k0 / negative / macro`: A-source=G, stability=0.5602, phase_influence=0.0123, geometry_readability=1.0000
- `k0 / abs / macro`: A-source=G, stability=0.5502, phase_influence=0.0123, geometry_readability=1.0000
- `k0 / positive / macro`: A-source=G, stability=0.4899, phase_influence=0.0000, geometry_readability=0.7000
- `theta_0.03 / negative / macro`: A-source=G, stability=0.5602, phase_influence=0.0123, geometry_readability=1.0000
- `theta_0.03 / abs / macro`: A-source=G, stability=0.5502, phase_influence=0.0123, geometry_readability=1.0000
- `theta_0.03 / positive / macro`: A-source=G, stability=0.4899, phase_influence=0.0000, geometry_readability=0.7000
- `n1a_alpha / negative / macro`: A-source=G, stability=0.5296, phase_influence=0.0123, geometry_readability=1.0000
- `n1a_alpha / abs / macro`: A-source=G, stability=0.5561, phase_influence=0.0123, geometry_readability=1.0000
- `n1a_alpha / positive / macro`: A-source=G, stability=0.5550, phase_influence=0.0000, geometry_readability=0.7000

The bridge carrier blocks, minimal-set block, leave-one-out tests, and minimal model readouts belong together as candidate carrier-specificity scaffolding. They are useful as architecture inventory, but they do not identify a physical carrier on their own.

## 10. Architecture interpretation

This cluster contributes a new/rediscovered RMS subpuzzle:

Matter Signature / Carrier Specificity:

- wave-only axis
- mass-only axis
- isotope/nuclear-parameter sensitivity
- quantum-chemical descriptor axis
- shell/valence axis
- VDW interaction-like matter layer
- negative/abs/positive marker channel
- bridge carrier minimal-set / leave-one-out tests

The Matter Signature cluster shows that the project had already begun to separate wave-only, mass-only, isotope-sensitive, quantum-chemical, shell/valence, VDW interaction-like, and negative/abs/positive marker contributions. Its value for QSB-ST is not physical validation, but a structured inventory of candidate carrier axes for the Resonance Matter Signature.

## 11. What this contributes to RMS

This inventory contributes candidate RMS carrier axes and preserves their relation to one another. It should be integrated into the Bridge Architecture Synthesis as a recovered inventory of candidate RMS carrier axes.

It does not replace the newer Carbon scaffold line. Instead, it sits between the deBroglie phase-bridge mechanism chain and the later Carbon scanner-calibration line. Its practical value is to help prevent re-inventing old tests and to make future reruns more targeted.

## 12. What remains open

Open items include:

- whether the baseline matter-sensitive behavior survives cleaned reruns and stricter controls;
- whether the mass-only axis explains most or all of the apparent matter signature;
- whether isotope, carbon, strontium, QC, shell, valence, or VDW descriptors contribute independent structure;
- whether negative or abs markers have stable internal separation;
- whether bridge carrier minimal-set and leave-one-out tests remain stable in the current repository;
- how these archived readouts should be mapped into the newer Carbon scanner-calibration line;
- which outputs can be promoted from duplicate-quarantine inventory to canonical current-repo artifacts after provenance cleanup.

## 13. Compact Claim Boundary

This inventory does not provide:

- physical validation of the Bridge;
- spacetime emergence;
- molecular validation;
- experimental prediction;
- proof that RMS is physically established;
- proof that VDW, isotope, QC, shell, or valence descriptors are true carriers;
- proof that negative or abs is the physical carrier;
- replacement for future reruns, provenance cleanup, external observable anchoring, and current-repo integration.

## 14. Next preservation / integration steps

Suggested next steps:

- Preserve the duplicate-quarantine source path and record which result files correspond to each cluster.
- Add a current-repo provenance map before treating any archived result as canonical.
- Re-run only after defining exact run inputs, ordering, randomization behavior, and acceptance criteria.
- Compare recovered carrier-axis tests against the newer Carbon scaffold and scanner-calibration line.
- Integrate the surviving inventory into Bridge Architecture Synthesis as candidate RMS carrier axes, with explicit separation between archival readout, rerun result, and interpretation.
