# QSB-BRIDGE-DATA-01 Run Readout

## Run

```text
block_id: QSB-BRIDGE-DATA-01
run_id: realdata_preflight_open
stop_go_outcome: hold_for_DATA02_until_local_sources_and_provenance_are_supplied
network_policy: no_downloads_no_network_required
```

## Claim Boundary

DATA-01 is preflight only, with no physical validation claim.

It does not establish spacetime emergence, physical metric recovery, causal structure, de-Broglie confirmation, real quantum dynamics, or molecular validation.

## 05C Warning Carried Forward

Local-neighborhood diagnostics showed sensitivity under small additive magnitude noise, with the first configured warning at noise level 0.02.

Any later DATA-02 work must report local-neighborhood sensitivity, not only global geometry scores.

## Candidate Decisions

|candidate_id|candidate_label|go_no_go_recommendation_for_DATA02|reason|
|---|---|---|---|
|c60|C60 fullerene|hold_for_DATA02_until_local_sources_and_provenance_are_supplied|Candidate needs machine-readable local sources, provenance, and a K proxy that does not simply re-encode known geometry.|
|benzene|Benzene / Benzol|hold_for_DATA02_until_local_sources_and_provenance_are_supplied|Candidate needs machine-readable local sources, provenance, and a K proxy that does not simply re-encode known geometry.|
|h2|H2 sanity candidate|go_pipeline_sanity_only|Small system can test parsing flow only; no meaningful geometry-recovery interpretation.|

## K Proxy Risk Summary

|candidate_id|proxy_id|geometry_smuggling_risk|preflight_assessment|
|---|---|---|---|
|c60|coordinate_distance_kernel|high|hold_as_reference_control_only|
|c60|bond_graph_adjacency_or_laplacian|high|hold_as_control_or_pipeline_sanity_only|
|c60|normal_mode_correlation_or_coupling|medium|candidate_for_DATA02_if_provenance_and_uncertainty_are_documented|
|c60|spectral_mode_participation_similarity|medium|candidate_for_DATA02_if_machine_readable_and_not_collapsed_to_geometry|
|c60|local_quantum_chemistry_matrix_output|medium_to_high|candidate_only_if_local_outputs_and_method_metadata_are_available_later|
|benzene|coordinate_distance_kernel|high|hold_as_reference_control_only|
|benzene|bond_graph_adjacency_or_laplacian|high|hold_as_control_or_pipeline_sanity_only|
|benzene|normal_mode_correlation_or_coupling|medium|candidate_for_DATA02_if_provenance_and_uncertainty_are_documented|
|benzene|spectral_mode_participation_similarity|medium|candidate_for_DATA02_if_machine_readable_and_not_collapsed_to_geometry|
|benzene|local_quantum_chemistry_matrix_output|medium_to_high|candidate_only_if_local_outputs_and_method_metadata_are_available_later|
|h2|coordinate_distance_kernel|high|pipeline_sanity_only_no_geometry_recovery_interpretation|
|h2|bond_graph_adjacency_or_laplacian|high|pipeline_sanity_only_no_geometry_recovery_interpretation|
|h2|normal_mode_correlation_or_coupling|medium|pipeline_sanity_only_no_geometry_recovery_interpretation|
|h2|spectral_mode_participation_similarity|medium|pipeline_sanity_only_no_geometry_recovery_interpretation|
|h2|local_quantum_chemistry_matrix_output|medium_to_high|pipeline_sanity_only_no_geometry_recovery_interpretation|

## Future Result Discussion Requirement

Create a separate DATA-01 result discussion only after reading these outputs. It must include a human-readable Bauchbild and remain defensive and method-level.

The Bauchbild should explain DATA-01 as a source-material and lab-notebook precheck: provenance, machine-readable fields, uncertainty, and proxy risks are inspected before any validation-like interpretation is attempted.

## Download Policy

No external data were downloaded by this script. The outputs are generated from local static preflight declarations only.
