# QSB-CAUSALITY06B-06 — Second Independent Inner-Sphere ET Case Runner Spec

## 1. Status and Scope

```text
block_id = QSB-CAUSALITY06B-06
block_type = second_independent_inner_sphere_case_run
runner_present = yes
physical_causality_claimed = false
```

This block evaluates a second source-bound inner-sphere electron-transfer case using generalized chemical fields. It does not create raw experimental data, a time-resolved trajectory, or a new mechanism proof.

## 2. Second Reference Case

The reference case is the documented reduction of `[CoIII(ox)3]3-` by a Co(II) tetraamine diaqua complex such as `[CoII(2,2,2-tet)(H2O)2]2+`. The role labels are `electron_acceptor_center` and `electron_donor_center`, so the two cobalt centers are not collapsed into an ambiguous single Co label.

```text
oxidant_center = CoIII_in_tris_oxalato_cobaltate
reductant_center = CoII_in_tetraamine_diaqua_complex
electron_transfer_direction = reductant_CoII_to_oxidant_CoIII
bridging_ligand = oxalate
bridge_mode = doubly_chelated_oxalate_bridge
primary_product_support = oxalate_bound_CoIII_tetraamine_products
```

## 3. State Data

The run uses five curated source-bound candidate-state records, `OX01_S0` through `OX01_S4`. `OX01_S3` is optional and is not required as a discrete species.

```text
data_status = curated_source_bound_candidate_state_data
raw_experimental_measurement_data = false
directly_time_resolved_trajectory = false
mechanistic_reference_decomposition = true
```

## 4. Rule Transfer

R1 and R4 are transferred unchanged on the role/general-feature level. R2 and R3 preserve the shared core but require limited oxalate/chelation-specific extensions.

```text
chloride_bridge_consistency -> bridging_ligand_consistency
R2_transfer_class = case_specific_extension
R3_transfer_class = case_specific_extension
case_specific_patch_count = 2
```

The bridge-consistency core transfers, but the oxalate case requires chelation-specific bond-state and product-chelate conditions beyond the chloride implementation. The coordination/association core transfers, but the oxalate case adds chelation-specific coordination-accessibility and bridge-geometry requirements.

```text
cross_case_comparison_mode = structured_manual_rule_classification
automatic_rule_equivalence_analysis_performed = false
formal_rule_equivalence_proven = false
```

The cross-case comparison is a structured classification of implemented rule forms and declared case-specific conditions. It is not an automatic rule-equivalence analysis.

## 5. Runner Logic

The runner loads the five oxalate records, validates the declared run-critical subset, evaluates five transition candidates forward and reverse, writes cross-case rule-transfer output, and records leakage flags. It does not use state IDs, reference order, evidence metadata, source metadata, localized aliases, case identity, or mechanism names as direction inputs.

## 6. Outputs

The runner writes exactly eight outputs under:

```text
runs/QSB-CAUSALITY06B-06/second_inner_sphere_case/
```

The outputs are `resolved_config.json`, `validated_oxalate_state_records.json`, `oxalate_transition_results.csv`, `oxalate_transition_results.json`, `cross_case_rule_transfer.csv`, `german_alias_view.csv`, `run_summary.json`, and `readout.md`.

## 7. Acceptance Criteria

The run is accepted when five records and five transition candidates are processed, all transitions are evaluated forward and reverse, the minimal path `OX01_S2 -> OX01_S4` is included, R2 is explicitly represented as `bridging_ligand_consistency`, R2 and R3 are classified as limited case-specific extensions, the cross-case transfer table is complete, no case label is used as a direction input, exactly eight outputs are written, and `physical_causality_claimed = false`.

## 8. Limitations

The shared rule architecture remains usable, but two rule groups require chelation-specific extensions. The cross-case comparison is a structured manual classification, not an automatic rule-equivalence proof. Rule transfer across two cases does not establish universal generalizability. Case-specific extensions are explicit and do not invalidate the preserved shared core. The second case is a curated source-bound mechanistic decomposition, not a directly observed frame-by-frame trajectory. Formal admissibility does not establish thermodynamic favorability, kinetic accessibility, irreversibility, or physical causality. Localized aliases are presentation metadata only.
