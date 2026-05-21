# QSB-ST-COMP01-D1h Cyclic-Coordinate Acceptance-Region and Impostor-Exclusion Result Note

## 1. Purpose

This file documents the existing synthetic D1h Cyclic-Coordinate Acceptance-Region and Impostor-Exclusion Run.

It is result documentation only:

- no new run
- no new implementation
- no new identity score
- no re-run of D1f
- no change to D1g outputs
- no physical proof
- no positive specificity finding
- no physical manifold

The cyclic-coordinate / cylindrical language is diagnostic-methodological. It describes a synthetic acceptance-region analysis layer, not physical spacetime, not Hilbert-space reconstruction, not Lorentzian geometry, and not physical phase space.

## 2. Current status anchor

- COMP01-D Concept documented
- COMP01-D1 Minimal Design Plan documented
- COMP01-D1a Scanner Specification documented
- COMP01-D1b Minimal Scanner implemented and result documented
- COMP01-D1c Control-Stress Runner implemented and result documented
- COMP01-D1d Manifold Degeneracy Audit implemented and result documented
- COMP01-D1e Collision-Aware Profile Runner implemented and result documented
- COMP01-D1f Robustness Sweep Runner implemented and result documented
- COMP01-D1g Warning Driver Decomposition Runner implemented and result documented
- COMP01-D1h Cyclic-Coordinate Acceptance-Region Runner implemented

Current commit anchor:

`b73e450 Add QSB-ST COMP01D1h cyclic-coordinate acceptance-region runner`

## 3. Run inputs and generated outputs

Run directory:

`runs/QSB-ST-COMP01D1H/cyclic_coordinate_acceptance_region_open/`

Generated output files:

- `summary.json`
- `readout.md`
- `cyclic_region_case_summary.csv`
- `cyclic_vs_current_region_summary.csv`
- `impostor_exclusion_summary.csv`
- `decision_table_cyclic_summary.csv`
- `kernel_size_cyclic_sensitivity_summary.csv`
- `resolved_config.json`

## 4. Befund

D1h completed the cyclic-coordinate acceptance-region layer on 9450 existing cases.

D1h did not rerun D1f. D1h did not modify D1g outputs. D1h did not introduce a physical manifold or new identity score. Input consistency passed.

Core run values:

```yaml
case_count: 9450
specificity_established: false
does_not_rerun_d1f: true
does_not_modify_d1g_outputs: true
does_not_introduce_physical_manifold: true
does_not_introduce_new_identity_score: true
input_consistency_passed: true
cyclic_phase_source: cyclic_phase_proxy
cyclic_acceptance_region_member_count: 1858
current_false_accept_warning_count: 4901
cyclic_false_accept_warning_count: 992
impostor_overlap_warning_count: 1431
spectrum_matched_null_intrusion_count: 141
adversarial_near_duplicate_intrusion_count: 106
local_response_dominant_warning_count: 146
cosmetic_penalty_lock_warning_count: 104
kernel_size_8_artifact_warning_count: 344
exclusion_success_count: 4750
exclusion_failure_count: 151
exclusion_success_rate: 0.9691899612324015
exclusion_failure_rate: 0.030810038767598448
stable_candidate_current_count: 2067
stable_candidate_cyclic_count: 7907
fragile_candidate_current_count: 7383
fragile_candidate_cyclic_count: 1543
mean_cyclic_acceptance_distance: 0.3438512101215752
mean_warning_count_current: 2.866243386243386
mean_warning_count_cyclic: 0.3453968253968254
mean_warning_delta_current_to_cyclic: -2.520846560846561
```

Decision status counts:

```yaml
adversarial_near_duplicate_intrusion_warning: 93
cosmetic_penalty_lock_warning: 84
cyclic_false_accept_warning: 320
cyclic_region_overstrict_warning: 302
cyclic_region_reduces_false_accept_candidate: 4667
kernel_size_8_artifact_warning: 256
local_response_open_door_warning: 73
phase_wrap_distance_warning: 274
spectrum_matched_null_intrusion_warning: 141
stable_under_cyclic_region_candidate: 3240
```

False-accept warnings decreased substantially, from 4901 current false-accept warnings to 992 cyclic false-accept warnings. Fragile cases decreased substantially, from 7383 current fragile cases to 1543 cyclic fragile cases. Stable candidates increased from 2067 to 7907.

`specificity_established` remains false. `cyclic_phase_source` is `cyclic_phase_proxy`, so the result is diagnostic and proxy-based.

## 5. Interpretation

D1h provides a positive synthetic diagnostic result: a cyclic-coordinate acceptance-region layer substantially reduces false-accept and fragile-case warnings compared with the current D1g/D1f interpretation, while specificity remains false and the cyclic phase source is diagnostic/proxy-based.

Die zylindrisch/zyklische Buehne reduziert im synthetischen Test deutlich die Zahl falscher Akzeptanzen und fragiler Faelle. Das spricht dafuer, dass ein Teil des D1f/D1g-Problems tatsaechlich in der Geometrie der Akzeptanzregion lag.

This is not a physical validation. It is a methodological geometry result.

The result supports testing cyclic-coordinate treatment more seriously, but it does not establish diagnostic specificity or physical wave identity.

## 6. Hypothese

A relevant part of the D1f/D1g false-accept problem may have been caused by reading phase-sensitive diagnostic structure in a mixed profile space that did not sufficiently respect cyclic geometry.

A cyclic-coordinate / cylindrical diagnostic acceptance region may be a better method for orchestrating phase-like and nonperiodic profile components.

However, the current run used `cyclic_phase_proxy`, so a later test should check whether the result persists when explicit phase-like fields are available or reconstructed transparently from the synthetic generator.

## 7. Offene Lücke

- no real data
- no physical validation
- no diagnostic specificity established
- cyclic_phase_source is proxy-based
- no physical phase reconstruction
- no physical manifold
- no Hilbert-space reconstruction
- no robust identity metric yet
- no physical null model
- no Lorentzian structure
- no physical time
- no physical wavefunction claim
- no Pauli or spin-statistics claim
- no Bridge validation
- possible overstrictness needs review
- proxy construction needs follow-up validation

## 8. Comparison to D1g/D1f

D1g/D1f current:

```yaml
current_false_accept_warning_count: 4901
stable_candidate_current_count: 2067
fragile_candidate_current_count: 7383
mean_warning_count_current: 2.866243386243386
```

D1h cyclic:

```yaml
cyclic_false_accept_warning_count: 992
stable_candidate_cyclic_count: 7907
fragile_candidate_cyclic_count: 1543
mean_warning_count_cyclic: 0.3453968253968254
mean_warning_delta_current_to_cyclic: -2.520846560846561
```

This comparison is promising as a synthetic diagnostic reduction of false-accept and fragile-case warnings, not as a specificity proof.

## 9. Cyclic-coordinate acceptance-region behavior

D1h treats phase-sensitive structure as cyclic-coordinate / cylindrical diagnostic structure.

Because no secure raw phase fields were present in the input tables, the run used:

```yaml
cyclic_phase_source: cyclic_phase_proxy
```

The use of `cyclic_phase_proxy` means the run tests the diagnostic geometry idea, not physical phase reconstruction.

Key cyclic-region values:

```yaml
cyclic_acceptance_region_member_count: 1858
cyclic_false_accept_warning_count: 992
impostor_overlap_warning_count: 1431
mean_cyclic_acceptance_distance: 0.3438512101215752
```

The cylindrical coordinate-space language is methodological and diagnostic only.

## 10. Targeted driver behavior

Targeted residual warnings:

```yaml
spectrum_matched_null_intrusion_count: 141
adversarial_near_duplicate_intrusion_count: 106
local_response_dominant_warning_count: 146
cosmetic_penalty_lock_warning_count: 104
kernel_size_8_artifact_warning_count: 344
exclusion_failure_count: 151
```

D1h strongly reduced many false-accept cases, but it did not eliminate targeted driver problems. The remaining warnings are useful because they indicate where the cyclic model still leaks.

## 11. Consequence for next design step

The next step should not be claim escalation.

Possible next block:

`QSB-ST-COMP01-D1i`

`Cyclic-Phase Source Validation and Overstrictness Audit Plan`

Possible target path:

`docs/QSB_ST_COMP01D1I_CYCLIC_PHASE_SOURCE_VALIDATION_OVERSTRICTNESS_AUDIT_PLAN.md`

D1i should plan:

- validate `cyclic_phase_proxy` against explicit phase-like synthetic fields
- add explicit phase columns if the synthetic generator can expose them
- audit whether cyclic reduction is genuine or overstrict
- inspect `cyclic_region_overstrict_warning` cases
- inspect `exclusion_failure_count` cases
- inspect remaining `spectrum_matched_null` intrusion
- inspect remaining `adversarial_near_duplicate` intrusion
- inspect `kernel_size_8` artifact warnings
- retain decision-table transparency
- avoid physical claim escalation

## 12. Machine-readable status

```yaml
block_id: QSB-ST-COMP01D1H
run_id: cyclic_coordinate_acceptance_region_open
commit_anchor: b73e450
case_count: 9450
specificity_established: false
does_not_rerun_d1f: true
does_not_modify_d1g_outputs: true
does_not_introduce_physical_manifold: true
does_not_introduce_new_identity_score: true
input_consistency_passed: true
cyclic_phase_source: cyclic_phase_proxy
cyclic_acceptance_region_member_count: 1858
current_false_accept_warning_count: 4901
cyclic_false_accept_warning_count: 992
impostor_overlap_warning_count: 1431
spectrum_matched_null_intrusion_count: 141
adversarial_near_duplicate_intrusion_count: 106
local_response_dominant_warning_count: 146
cosmetic_penalty_lock_warning_count: 104
kernel_size_8_artifact_warning_count: 344
exclusion_success_count: 4750
exclusion_failure_count: 151
exclusion_success_rate: 0.9691899612324015
exclusion_failure_rate: 0.030810038767598448
stable_candidate_current_count: 2067
stable_candidate_cyclic_count: 7907
fragile_candidate_current_count: 7383
fragile_candidate_cyclic_count: 1543
mean_cyclic_acceptance_distance: 0.3438512101215752
mean_warning_count_current: 2.866243386243386
mean_warning_count_cyclic: 0.3453968253968254
mean_warning_delta_current_to_cyclic: -2.520846560846561
current_status_label: COMP01D1H_cyclic_coordinate_acceptance_region_impostor_exclusion_result_documented
```

## 13. Claim Boundary

D1h is a cyclic-coordinate acceptance-region and impostor-exclusion result note.

D1h did not rerun D1f.

D1h did not modify D1g outputs.

D1h did not introduce a new identity score.

D1h did not introduce a physical manifold.

Cyclic-coordinate and cylindrical language denotes a diagnostic coordinate model.

It is not a physical spacetime manifold.

It is not a Hilbert-space reconstruction.

It is not a Lorentzian geometry.

It is not a physical phase space.

The cylindrical picture is a methodological representation of periodic phase-like structure plus nonperiodic diagnostic coordinates.

cyclic_phase_proxy is diagnostic only.

cyclic_phase_proxy is not a physical phase reconstruction.

psi is a diagnostic pattern object here, not automatically a physical wavefunction.

wave_identity_profile is a diagnostic profile concept, not a proof of physical identity.

false_accept_region is a diagnostic acceptance-region concept, not a physical region.

impostor_distribution_overlap is a diagnostic distribution-overlap concept, not a physical particle population.

Decision tables are transparent methodological classification rules, not physical laws.

The orchestration metaphor is an internal explanatory image, not a physical mechanism claim.

The D1h result does not establish diagnostic specificity.

The D1h result does not prove wave identity.

The D1h result does not validate physical phase reconstruction.

"wave-Pauli" is a heuristic internal analogy only.

It does not claim fermionic Pauli exclusion.

It does not invoke quantum spin-statistics.

It does not assert a physical exclusion principle.

type-like similarity is not the same as relational identity.

spectral shift is used here as a diagnostic analogy, not as cosmological redshift.

phase drift is used here as a structure-internal pattern marker, not as physical time delay.

tau is not physical time.

tau is not proper time.

tau is not a universal clock.

COMP01-D1h does not attach D(A,B).

COMP01-D1h does not construct S_rel2.

COMP01-D1h does not derive a Lorentzian metric.

COMP01-D1h does not validate a physical Bridge.

COMP01-D1h does not establish diagnostic specificity.

This is synthetic diagnostic cyclic-coordinate acceptance-region result documentation only.

## 14. Current status label

current_status_label: COMP01D1H_cyclic_coordinate_acceptance_region_impostor_exclusion_result_documented
