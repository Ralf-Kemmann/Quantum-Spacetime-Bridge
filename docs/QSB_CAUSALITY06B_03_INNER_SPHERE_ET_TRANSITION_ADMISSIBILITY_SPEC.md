# QSB-CAUSALITY06B-03 — Inner-Sphere ET Transition-Admissibility Specification

## 1. Status and Scope

```text
block_id = QSB-CAUSALITY06B-03
block_type = transition_admissibility_specification
runner_present = no
numerical_analysis_present = no
graph_analysis_present = no
independent_direction_reconstruction_present = no
physical_causality_claimed = no
```

This block defines a formal admissibility rule for a directed candidate transition `X -> Y` in the classical Co(III)/Cr(II) chloride-transfer record model. It depends on:

- `docs/QSB_CAUSALITY06B_01_EVIDENCE_GATED_INNER_SPHERE_ET_STATE_SPEC.md`
- `docs/QSB_CAUSALITY06B_02_INNER_SPHERE_ET_CANDIDATE_STATE_RECORD_SCHEMA_SPEC.md`
- `data/QSB-CAUSALITY06B-02/candidate_state_record_schema.json`
- `data/QSB-CAUSALITY06B-02/example_candidate_state_records.json`

The specification is limited to internal transition admissibility within the declared candidate-state schema. It does not execute a runner, compute a transition matrix, analyze a graph, reconstruct a physical arrow, score evidence, evaluate thermodynamics, fit kinetics, or prove a historical pathway.

```text
reference_order_used_as_direction_input = no
evidence_metadata_used_as_direction_input = no
descriptive_labels_used_as_direction_input = no
```

## 2. Transition Input

The transition input consists of two complete candidate-state records:

```text
source_state = X
target_state = Y
```

Both records must conform to the CAUSALITY06B-02 candidate-state record schema. The admissibility decision may inspect only fields under:

```text
source_state.chemical_features
target_state.chemical_features
```

The following fields and field groups are not allowed as direction inputs:

- `state_id`
- `state_role`
- `reference_order_index`
- `included_in_full_reference_path`
- `included_in_minimal_reference_path`
- `species_status`
- `pathway_evidence`
- `source_metadata`
- `known_mechanism_name`

The rule may compare chemical feature values between `source_state` and `target_state`. It may not infer direction from reference order, documentary order, state labels, evidence class, source names, or known mechanism labels.

**Canonical fields and localized aliases**

```text
canonical_field_names_remain_language_neutral = yes
human_readable_labels_are_localized_aliases = yes
localized_aliases_used_as_logic_inputs = no
```

Canonical technical field names remain unchanged and are used by schema, runner, JSON, CSV, tests, and validation logic. Examples include:

```text
redox_consistent
chloride_bridge_consistent
coordination_consistent
state_change_coherent
forward_admissible
reverse_admissible
forward_transition_status
direction_comparison_class
```

Human-readable German names are presentation aliases only. They may be documented in a later view layer but are not field identifiers in this specification block.

| Canonical Field Name | German Display Alias |
|---|---|
| `redox_consistent` | `Redoxbilanz konsistent` |
| `chloride_bridge_consistent` | `Chlorid- und Brückenstatus konsistent` |
| `coordination_consistent` | `Koordinations- und Assoziationsstatus konsistent` |
| `state_change_coherent` | `Zustandsänderung kohärent` |
| `forward_admissible` | `Vorwärtsübergang zulässig` |
| `reverse_admissible` | `Rückwärtsübergang zulässig` |
| `forward_transition_status` | `Status des Vorwärtsübergangs` |
| `direction_comparison_class` | `Klasse des Richtungsvergleichs` |

Later localized views must reference one stable canonical field name with language-specific display metadata:

```text
canonical_field_name
language_code
display_alias
display_description
```

Example:

```text
forward_admissible | de | Vorwärtsübergang zulässig
forward_admissible | en | Forward transition admissible
```

```text
one_canonical_field_multiple_language_aliases = yes
schema_change_required_for_new_language = no
localized_alias_as_field_identifier_allowed = no
localized_alias_as_direction_feature_allowed = no
localized_alias_as_result_logic_input_allowed = no
```

Localized aliases must never be used for field identity, transition logic, validation rules, result classification, joins, keys, or machine comparison.

## 3. Admissibility Rules

Exactly four rule groups define chemical admissibility. Each group returns one Boolean field and one reason field. The overall transition result is true only when all four Boolean fields are true.

```text
chemically_admissible = redox_consistent and chloride_bridge_consistent and coordination_consistent and state_change_coherent
```

**R1 Redox Consistency**

Output fields:

```text
redox_consistent
redox_reason
```

The redox rule tests whether the chemical-feature change is consistent with the declared Co(III)/Cr(II) inner-sphere electron-transfer record model.

- A completed electron-transfer transition requires the cobalt feature to move from Co(III) to Co(II) and the chromium feature to move from Cr(II) to Cr(III).
- The accepted completed electron-transfer balance is `transferred_Cr_to_Co`.
- A unilateral oxidation-state change is not accepted as a full electron-transfer transition.
- If no completed electron-transfer step is claimed by the compared chemical features, the rule may remain true only for preparatory structural transitions that do not mislabel electron transfer as completed.
- A transition that sets `electron_transfer_balance = transferred_Cr_to_Co` without the paired Co and Cr oxidation-state change is rejected.

**R2 Chloride and Bridge Consistency**

Output fields:

```text
chloride_bridge_consistent
chloride_bridge_reason
```

The chloride-and-bridge rule tests whether chloride ownership, bridge status, and metal chloride bond fields are mutually coherent.

- A terminal chloride cannot be simultaneously represented as fully terminal on both metal centers.
- Bridge formation is admissible only from a source state in which chloride is still available from the Co-Cl side and the chromium center has coordination access.
- If a shared bridge is present, the target state must satisfy:

```text
co_chloride_bond_status = retained_in_bridged_configuration
cr_chloride_bond_status = bridge_coordination_present
```

- Chloride transfer to chromium is not admissible when the target state keeps chromium chloride bonding absent.
- Product-side chloride-on-Cr representation is admissible only when the target chemical features represent chromium chloride ownership or bridge coordination coherently.
- A transition that removes Co-Cl ownership and does not create bridge coordination or Cr-Cl product ownership is rejected as chemically incomplete in this record model.

**R3 Coordination and Association Consistency**

Output fields:

```text
coordination_consistent
coordination_reason
```

The coordination-and-association rule tests whether the association state and coordination-access fields support the declared structural change.

- A bridge can be introduced only when the pair is associated, encounter-associated, or otherwise bridge-capable under the chemical-feature fields.
- Cr(II) lability or substitution accessibility must be represented for bridge formation by `cr_coordination_vacancy_or_substitution_readiness` or compatible coordination-environment fields.
- A separated product configuration cannot jump directly to a bridged configuration unless reassociation and coordination access are represented by the compared chemical features.
- A target state that is bridged while the metal-pair association remains separated is rejected.
- Dissociation or product separation after electron transfer is admissible only when the chloride and redox fields are already coherent with the product-side representation.

**R4 State-Change Coherence**

Output fields:

```text
state_change_coherent
state_change_reason
```

The state-change rule tests whether the transition represents a real chemical-feature change rather than a relabeling.

- At least one field under `chemical_features` must change between `source_state` and `target_state`.
- Metadata-only, evidence-only, or label-only changes are not chemical transitions.
- Contradictory simultaneous changes are excluded, including changes that both complete and undo the same redox, chloride, bridge, or association feature within one directed comparison.
- `IS01_S3` is not required for admissibility.
- A reduced minimal-path transition from the bridged pre-electron-transfer candidate to the separated primary product candidate is allowed in principle, provided R1, R2, R3, and R4 are all satisfied by chemical features alone.

```text
IS01_S3_required_for_admissibility = no
minimal_path_transition_S2_to_S4_allowed_in_principle = yes
```

A transition satisfying all four rule groups receives the forward transition status:

```text
chemically_admissible_transition_candidate
```

## 4. Reverse-Direction Test

For every assessed transition `X -> Y`, the reverse comparison `Y -> X` must be assessed with the same four rule groups and the same chemical-feature-only input restriction.

Required reverse-test output fields:

```text
forward_admissible
reverse_admissible
reverse_requires_external_conditions
reverse_assessment
forward_transition_status
direction_comparison_class
```

Allowed `reverse_assessment` values are:

```text
reverse_chemically_inadmissible_under_declared_rules
reverse_chemically_admissible_under_declared_rules
reverse_requires_external_reagents_or_conditions
reverse_not_assessed
```

The reverse direction must not be rejected solely because it disagrees with reference order. The reverse test is not a thermodynamic verdict, not a kinetic verdict, and not a physical-causality reconstruction. If the reverse comparison would require reagents, redox partners, ligand exchange conditions, or other external conditions not encoded in the two records' chemical features, it may be classified as `reverse_requires_external_reagents_or_conditions`.

A formally asymmetric result under these declared rules means only that the two directions are not equally admissible inside this record model. It is not identical to a physical causal arrow.

```text
formal_directional_asymmetry_is_physical_causality = no
formal_directional_asymmetry_is_thermodynamic_irreversibility = no
formal_directional_asymmetry_is_kinetic_inaccessibility = no
```

## 5. Result Classes

This specification separates the forward transition status from the final direction-comparison class. `chemically_admissible_transition_candidate` is a forward status only. It is not an exclusive final direction-comparison class.

The allowed values for `forward_transition_status` are:

```text
chemically_admissible_transition_candidate
chemically_inadmissible_transition_candidate
not_assessed
```

Forward status meanings:

| forward_transition_status | meaning |
|---|---|
| `chemically_admissible_transition_candidate` | All four rule groups are satisfied for `X -> Y`. |
| `chemically_inadmissible_transition_candidate` | At least one rule group is violated for `X -> Y`. |
| `not_assessed` | The available record state is insufficient for a complete assessment. |

The Boolean fields remain:

```text
forward_admissible
reverse_admissible
```

The allowed values for `direction_comparison_class` are:

```text
forward_inadmissible
admissible_but_direction_not_qualified
directionally_asymmetric_under_declared_rules
reverse_requires_external_conditions
not_assessed
```

The final comparison class is assigned by an exclusive mapping:

| Forward assessment | Reverse assessment | direction_comparison_class |
|---|---|
| `forward_admissible = false` | any assessed value | `forward_inadmissible` |
| `forward_admissible = true` | `reverse_admissible = true` | `admissible_but_direction_not_qualified` |
| `forward_admissible = true` | `reverse_admissible = false` | `directionally_asymmetric_under_declared_rules` |
| `forward_admissible = true` | external conditions required | `reverse_requires_external_conditions` |
| not fully assessable | not fully assessable | `not_assessed` |

```text
directionally_asymmetric_under_declared_rules
=
forward_admissible_true_and_reverse_admissible_false
```

The constellation below must not receive `directionally_asymmetric_under_declared_rules`:

```text
forward_admissible = false
reverse_admissible = true
direction_comparison_class = forward_inadmissible
```

Direction-comparison meanings:

| direction_comparison_class | meaning |
|---|---|
| `forward_inadmissible` | The assessed forward transition fails or cannot satisfy the four chemical rule groups. |
| `admissible_but_direction_not_qualified` | Forward and reverse transitions are both admissible under the declared rules, so this specification does not qualify one direction over the other. |
| `directionally_asymmetric_under_declared_rules` | Forward is admissible and reverse is inadmissible under the same declared rules. |
| `reverse_requires_external_conditions` | Reverse comparison would require reagents, redox partners, ligand exchange conditions, or other conditions not represented by the two record features. |
| `not_assessed` | The forward/reverse comparison was not fully evaluated by this specification. |

No additional forward status or direction-comparison class is introduced in this block.

## 6. Acceptance Criteria

This corrected specification is accepted only if all criteria below are met:

- No new file is created by this correction.
- No file outside this specification is changed by this correction.
- The file is a specification only and creates no runner, JSON artifact, CSV artifact, transition matrix, graph, or result directory.
- Transition input is limited to two CAUSALITY06B-02-conforming records.
- Only fields under `chemical_features` are used for the admissibility decision.
- Reference order, evidence metadata, descriptive labels, source metadata, state IDs, and known mechanism labels are not used as direction inputs.
- Exactly four rule groups are defined: R1 Redox Consistency, R2 Chloride and Bridge Consistency, R3 Coordination and Association Consistency, and R4 State-Change Coherence.
- Forward and reverse directions are assessed with the same rules.
- Forward status and final direction-comparison class are separate fields.
- Every fully assessable forward/reverse constellation receives exactly one final direction-comparison class.
- `directionally_asymmetric_under_declared_rules` applies only when `forward_admissible = true` and `reverse_admissible = false`.
- Canonical field names remain language-neutral and technically stable.
- German display names are aliases in a view or presentation layer only.
- Localized aliases are not used as logic, identity, result-classification, or direction inputs.
- New languages do not require changing canonical field names.
- `IS01_S3` is not mandatory for admissibility.
- The minimal-path transition from S2 to S4 is allowed in principle when all four rule groups are satisfied.
- Forward status values and direction-comparison classes are restricted to Section 5.
- The specification does not claim kinetic accessibility, thermodynamic favorability, physical causal reconstruction, or proof of a historical mechanism.
- `git diff --check` reports no whitespace errors.

## 7. Limitations

- The rules test internal chemical consistency within the declared record model.
- They do not prove historical mechanism.
- They do not establish thermodynamic favorability.
- They do not establish kinetic accessibility.
- They do not establish irreversibility.
- They do not reconstruct physical causality.
- Reference-order labels are not used as directional inputs.
- IS01_S3 remains optional.
- A formally asymmetric rule result is not identical to a physical causal arrow.
- The rules do not replace experimental evidence, transition-state calculation, kinetic modeling, or thermodynamic analysis.
- The rules do not guarantee that all chemically possible side processes are represented by the schema fields.
- Localized field labels improve human readability but do not alter canonical field identity.
- Alias mappings are presentation metadata and are not part of transition admissibility.
- No localized view artifact is created in this specification block.
- The formal result classes describe rule outcomes only.

## 8. Next Step

The next permissible block is:

```text
QSB-CAUSALITY06B-04 — Inner-Sphere ET Transition-Admissibility Runner
```

That later block may implement the declared rule groups against schema-conforming records. This block itself does not create such a runner and does not emit transition results.
