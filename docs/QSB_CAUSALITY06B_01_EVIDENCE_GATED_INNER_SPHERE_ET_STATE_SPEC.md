# QSB-CAUSALITY06B-01 — Evidence-Gated Inner-Sphere Electron-Transfer State Specification

## 1. Status and Scope

```text
block_id = QSB-CAUSALITY06B-01
block_type = specification_only
process_class = inner_sphere_electron_transfer
reference_case = classical_cobalt_chromium_chloride_transfer
runner_present = no
numerical_analysis_present = no
independent_causal_reconstruction_claimed = no
physical_causality_claimed = no
```

This block defines candidate states, feature axes, and evidence rules for a later controlled representation of a classical inner-sphere electron-transfer case. It does not run a machine reconstruction, fit kinetics, evaluate thermodynamics, compute transition states, or make a new mechanistic proof. The historical inner-sphere mechanism is used only as a documented reference case.

## 2. Research Question

Under which documented structural, electronic, coordination, and ligand-transfer conditions can a directed state transition in the classical Co(III)/Cr(II) chloride-transfer system be represented as formally admissible without treating mechanistic labels or known chronological order as independent directional evidence?

Subquestions:

- Which features distinguish mere donor-acceptor proximity from a bridge-capable configuration?
- Which features mark an electronically and structurally admissible inner-sphere step?
- Which evidence is directly observed, experimentally_traced, product-supported, kinetically supported, mechanistically_inferred, or only a formal candidate?
- Which reverse_direction candidates must be explicitly tested?
- Which candidate states are admissible for specification even though they were not separately isolated?

## 3. Reference Chemical System

```text
oxidant = [CoIII(NH3)5Cl]2+
reductant = [CrII(H2O)6]2+
electron_donor_center = CrII
electron_acceptor_center = CoIII
initial_transferable_ligand_owner = CoIII_complex
final_traced_ligand_owner = CrIII_complex
bridge_identity = chloride
electron_transfer_direction = Cr_to_Co
ligand_transfer_direction = Co_to_Cr
```

Conservative reference representation:

\[
[\mathrm{Co}^{III}(\mathrm{NH}_3)_5\mathrm{Cl}]^{2+}
+
[\mathrm{Cr}^{II}(\mathrm{H}_2\mathrm{O})_6]^{2+}
\rightarrow
\mathrm{Co}^{II}\text{-containing products}
+
[\mathrm{Cr}^{III}(\mathrm{H}_2\mathrm{O})_5\mathrm{Cl}]^{2+}
\]

The primary event is the redox-and-ligand-transfer event: electron transfer from Cr(II) to Co(III), accompanied by chloride transfer from the cobalt complex to chromium. Subsequent product relaxation or ligand exchange, especially around the labile Co(II)-containing products, must be represented separately and must not be folded into the primary event.

```text
primary_redox_and_ligand_transfer_event = CoIII/CrII redox change plus chloride transfer Co_to_Cr
subsequent_product_relaxation_or_ligand_exchange = later CoII-product and solvent/ligand-exchange chemistry, not modeled here
```

## 4. Mechanistic Boundary

```text
inner_sphere_pathway = historically_supported_reference_mechanism
chloride_bridge = mechanistically_inferred
chloride_transfer = experimentally_traced_or_product_supported
bridged_intermediate_directly_isolated = no
transition_state_directly_observed = no
```

The chloride-bridged candidate is treated as strongly supported by the inner-sphere interpretation, product identity, and tracer logic, but not as a separately resolved species. No proposed intermediate configuration in this specification is upgraded to direct observation merely because it is useful in the mechanism.

## 5. State-Candidate Vocabulary

State IDs are neutral bookkeeping labels. Descriptive roles must not be used as inputs to a later direction rule.

| state_id | descriptive role | species_status | pathway_evidence_class | direct observability boundary |
|---|---|---|---|---|
| IS01_S0 | separated_reactant_configuration | reference_species_documented | not_applicable | documented reactant species; not a directly resolved reaction intermediate |
| IS01_S1 | encounter_and_substitution_ready_configuration | candidate_configuration | P1_chemically_plausible | encounter/readiness is not an isolated species here |
| IS01_S2 | chloride_bridged_pre_electron_transfer_candidate | candidate_configuration | P2_mechanistically_inferred | not separately resolved; IS01_S2_directly_isolated = no |
| IS01_S3 | chloride_bridged_post_electron_transfer_candidate | candidate_configuration | P2_mechanistically_inferred | optional formal decomposition; IS01_S3_required_as_discrete_species = no |
| IS01_S4 | separated_primary_product_configuration | product_species_documented | P4_tracer_supported | product species/component documented; later Co(II) relaxation remains separate |

## 6. Proposed State Order

Reference order:

```text
IS01_S0 -> IS01_S1 -> IS01_S2 -> IS01_S3 -> IS01_S4
documented_reference_order = yes
order_used_as_ground_truth_for_later_comparison = potentially
order_allowed_as_direction_feature = no
reference_order_type = documented_mechanistic_reference_decomposition
all_states_directly_resolved = no
IS01_S3_optional_in_minimal_path_representation = yes
```

Minimal reduced representation:

```text
IS01_S0 -> IS01_S1 -> IS01_S2 -> IS01_S4
```

This reduced representation does not deny bridge participation; it only avoids asserting a separately resolved post-electron-transfer bridged species. It is a cautious representation option, not a new mechanistic claim.

| state_id | Co oxidation state | Cr oxidation state | co_chloride_bond_status | cr_chloride_bond_status | shared_chloride_bridge_status | Cr coordination change | electron transfer status | ligand transfer status | association status | species_status | pathway_evidence_class | directly_observed_in_reaction_context |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IS01_S0 | Co(III) | Cr(II) | terminal_Co_Cl_present | no_Cr_Cl_product_bond | absent | aqueous Cr(II) coordination available as reactant context | not transferred | chloride still owned by Co complex | separated reactants | reference_species_documented | not_applicable | no, not an intermediate |
| IS01_S1 | Co(III) | Cr(II) | terminal_Co_Cl_present | no_stable_transferred_Cr_Cl_product_bond | absent_or_incipient_contact_only | substitution-ready or association-capable Cr(II) environment | not transferred | not transferred | encounter/association candidate | candidate_configuration | P1_chemically_plausible | no |
| IS01_S2 | Co(III) | Cr(II) | retained_in_bridged_configuration | bridge_coordination_present | present | Cr site compatible with bridge formation | not yet transferred | bridge-mediated transfer candidate | associated bridged candidate | candidate_configuration | P2_mechanistically_inferred | no |
| IS01_S3 | Co(II) | Cr(III) | weakened_or_cleaving_after_ET | Cr_Cl_ownership_emerging_or_formed | optional_successor_bridge | Cr(III) product coordination being established | transferred Cr_to_Co | chloride transferred Co_to_Cr | optional associated post-transfer candidate | candidate_configuration | P2_mechanistically_inferred | no |
| IS01_S4 | Co(II) | Cr(III) | Co product no longer modeled as retaining transferred chloride | Cr_Cl_present_in_product | absent | Cr(III) chloride product coordination established | completed | chloride product ownership at Cr | separated primary products | product_species_documented | P4_tracer_supported | product documented, not a direct movie of the path |

The Co-Cl bond is retained while chloride additionally coordinates the Cr(II) center, producing the shared chloride-bridged configuration.

```text
IS01_S2_directly_isolated = no
IS01_S2_mechanistically_inferred = yes
post_et_bridge_persistence_required = no
IS01_S3_required_as_discrete_species = no
IS01_S3_role = optional_formal_post_et_resolution
```

The inner-sphere mechanism requires bridge participation. It does not require a separately resolved or long-lived post-electron-transfer bridged species. IS01_S3 is retained only as an optional formal decomposition of the transfer and bridge-cleavage sequence. Later schemas may make IS01_S3 optional or nullable; omitting a discrete S3 state must not automatically be treated as a contradiction of the inner-sphere mechanism.

## 7. Feature Axes

| feature_axis | feature group | later direction-input eligibility |
|---|---|---|
| co_oxidation_state | chemical_feature | eligible |
| cr_oxidation_state | chemical_feature | eligible |
| co_chloride_bond_status | chemical_feature | eligible |
| cr_chloride_bond_status | chemical_feature | eligible |
| shared_chloride_bridge_status | chemical_feature | eligible |
| cr_coordination_vacancy_or_substitution_readiness | chemical_feature | eligible |
| metal_pair_association_status | chemical_feature | eligible |
| electron_transfer_balance | chemical_feature | eligible |
| ligand_transfer_balance | chemical_feature | eligible |
| co_coordination_environment | chemical_feature | eligible |
| cr_coordination_environment | chemical_feature | eligible |
| product_separation_status | chemical_feature | eligible with caution |
| substitution_lability_class | chemical_feature | eligible only if independently documented |
| spectroscopic_or_tracer_support | evidence_metadata | not a direction feature |
| species_status | evidence_metadata | not a direction feature |
| pathway_evidence_class | evidence_metadata | not a direction feature |
| descriptive_state_role | descriptive_state_role | not a direction feature |
| reference_order_index | reference_order_metadata | not a direction feature |

Only `chemical_feature` fields may be considered for a later formal admissibility rule. `evidence_metadata`, `descriptive_state_role`, and `reference_order_metadata` are documentation fields and must not be used as directional predictors.

## 8. Evidence Classes

```text
species_status
reference_species_documented
product_species_documented
candidate_configuration
not_separately_resolved
not_applicable
```

```text
pathway_evidence_class
P0_formal_candidate_only
P1_chemically_plausible
P2_mechanistically_inferred
P3_kinetically_or_product_supported
P4_tracer_supported
P5_directly_resolved_in_reaction_context
not_applicable
```

```text
evidence_classes_are_probabilities = no
species_status_is_pathway_evidence = no
documented_species_identity_implies_direct_pathway_observation = no
directly_documented_species_identity != directly_resolved_reaction_intermediate
mechanistically_supported_state != isolated_species
```

The former mixed label `E5_directly_observed_or_isolated_species` is replaced by the separated `species_status` and `pathway_evidence_class` axes. It is not an active evidence class in this specification. A documented starting or product species is not automatically a directly resolved reaction intermediate.

| state_id | species_status | pathway_evidence_class | mechanistically_inferred | experimentally_traced | product_supported | rationale |
|---|---|---|---|---|---|---|
| IS01_S0 | reference_species_documented | not_applicable | no | no | not_applicable | reactant complexes are specified reference inputs, not path-resolved intermediates |
| IS01_S1 | candidate_configuration | P1_chemically_plausible | limited | no | no | encounter/readiness is chemically plausible but not isolated here |
| IS01_S2 | candidate_configuration | P2_mechanistically_inferred | yes | indirect | indirect | bridge is required by the reference inner-sphere interpretation but is not directly isolated here |
| IS01_S3 | candidate_configuration | P2_mechanistically_inferred | yes | indirect | indirect | optional formal post-ET bridge-resolution candidate; product support constrains but does not directly resolve it |
| IS01_S4 | product_species_documented | P4_tracer_supported | no for intermediate status | yes | yes | Cr(III)-chloride product ownership supports chloride transfer |

## 9. Observation-Inference Separation

| item | species_status | pathway_evidence_class | directly_observed_in_reaction_context | experimentally_traced | product_supported | kinetically_supported | mechanistically_inferred | formal_candidate | allowed_interpretation | forbidden_overinterpretation |
|---|---|---|---|---|---|---|---|---|---|---|
| Co(III) starting complex | reference_species_documented | not_applicable | no, not an intermediate | not required | yes as consumed reactant | context only | no | no | oxidant and initial chloride owner | do not infer microscopic bridge geometry from reactant label alone |
| Cr(II) starting complex | reference_species_documented | not_applicable | no, not an intermediate | not required | yes as consumed reactant | context only | no | no | reductant and electron donor center | do not treat donor label as direction input |
| Cr(III)-bound chloride product | product_species_documented | P4_tracer_supported | product documented, path not directly resolved | yes, chloride-origin logic | yes | may be supported in literature | no for product identity | no | chloride ends at Cr in primary product event | do not claim a frame-by-frame path |
| origin of transferred chloride | not_applicable | P4_tracer_supported | no direct movie | experimentally_traced | product_supported | context-supported | yes | no | chloride comes from cobalt complex in the reference case | do not treat tracer/product support as direct observation of the activated configuration |
| chloride-bridged precursor | candidate_configuration | P2_mechanistically_inferred | no | indirectly constrained | indirectly supported | mechanistic context | yes | yes | bridge-capable precursor candidate | do not say it was separately resolved in this block |
| electron transfer through or with bridge participation | not_applicable | P2_mechanistically_inferred | no direct electron path measurement | no direct trajectory | supported by mechanism/product logic | historically supported | yes | yes | inner-sphere ET reference event | do not claim an electron trajectory was measured |
| bridge-connected post-transfer state | candidate_configuration | P2_mechanistically_inferred | no | indirectly constrained | product-supported boundary | mechanistic context | yes | yes | optional successor candidate after redox change | do not assign direct observation status |
| subsequent dissociation | not_separately_resolved | P2_mechanistically_inferred | no | no | product-supported boundary | possible context | yes | yes | separation step after primary event | do not call it absolute irreversibility |
| Co(II) product relaxation or ligand exchange | not_separately_resolved | P2_mechanistically_inferred | no | no | product mixture/relaxation context | possible context | yes | yes | later lability-driven chemistry | do not fold it into the primary ET step |

## 10. Direction-Leakage Prohibitions

The following fields are prohibited as direction inputs:

```text
state_id_sequence
reactant_label
precursor_label
pre_electron_transfer_label
post_electron_transfer_label
product_label
before_after_language
source_document_order
figure_arrow_direction
known_mechanism_name
evidence_class_rank
species_status
pathway_evidence_class
```

```text
descriptive_label_leakage_allowed = no
reference_order_leakage_allowed = no
evidence_rank_as_direction_feature_allowed = no
species_status_as_direction_feature_allowed = no
pathway_evidence_class_as_direction_feature_allowed = no
```

This direction_leakage rule allows the reference order to be used later for evaluation, but not as a predictor.

## 11. Formal Transition-Admissibility Requirements

No final algorithm is defined in this block. A later candidate transition `X -> Y` may be tested only if:

- electron balance and oxidation-state changes are chemically consistent;
- no impossible simultaneous ligand ownership is asserted;
- bridge formation has a coordination-access condition at the Cr(II) center;
- ligand ownership and bridge status are updated consistently;
- charge and material balance are not violated;
- the process class is not inferred from the label "inner-sphere" alone;
- a product observation is not retroactively treated as direct observation of an intermediate.

Required category separation:

```text
chemically_admissible_transition_candidate
evidence_supported_transition_candidate
direction_qualified_transition_candidate
experimentally_documented_transition_relation
```

These categories are not synonyms.

## 12. Reverse-Direction Test

Every proposed neighbor relation `X -> Y` requires this reverse_direction question:

```text
Is Y -> X chemically admissible under the same feature rules?
```

Allowed reverse-test outcomes:

```text
reverse_chemically_impossible
reverse_chemically_admissible_but_not_supported
reverse_requires_external_reagents_or_conditions
reverse_excluded_only_by_known_reference_order
reverse_not_assessed
```

A reverse candidate must not be rejected merely because it is absent from the historical mechanism diagram. Thermodynamic or kinetic irreversibility must not be claimed unless the required data are evaluated in a later block. Product separation or kinetic inertness of a Cr(III) product complex may be discussed as a condition restricting a continuation space, but not as automatic absolute irreversibility.

## 13. Continuation-Space Interpretation

```text
chemical_continuation_space = set of follow-on state candidates still allowed under documented chemical feature and balance rules
```

Allowed interpretation:

```text
continuation_space_restriction
```

Not allowed without further data:

```text
physical_fixation
absolute_irreversibility
causal_lock_in
unique_microscopic_pathway
```

Candidate restrictions for later work include common chloride-bridge formation, oxidation-state change, kinetic inertness of the Cr(III) product complex, product separation, and subsequent ligand exchange at the labile Co(II) center. These are candidate restrictions on `chemical_continuation_space`, not proven physical lock-in claims.

## 14. Allowed Claims

Allowed defensive claims:

- The classical Co(III)/Cr(II) system provides a historically supported inner-sphere reference case.
- Electron transfer and ligand transfer occur in opposite center-to-center directions.
- Product and tracer evidence strongly support direct chloride transfer from the cobalt complex to chromium.
- A chloride-bridged state is mechanistically supported but not treated as a directly isolated intermediate.
- A feature-based state specification can be constructed without using chronological labels as directional inputs.
- Reverse-direction admissibility must be tested separately.
- The specification prepares, but does not perform, a later controlled state-order comparison.

## 15. Forbidden Claims

Do not state or imply that this block:

- reconstructs causality;
- proves physical causality;
- observes one unique microscopic pathway;
- directly observes the activated transition configuration;
- separately isolates the bridge-connected candidate;
- measures an electron path;
- derives time from chemical state order;
- proves irreversible behavior;
- validates QSB through electron transfer;
- confirms bridge theory.

Semantically equivalent claims are also forbidden.

## 16. Acceptance Criteria

This block is accepted only if:

- exactly one new Markdown file is generated;
- no runner and no data artifact are generated;
- the reference chemical system is described conservatively;
- electron-transfer and ligand-transfer directions are separated;
- at least five candidate states are specified;
- species_status and pathway_evidence_class are separated;
- direct observation, tracer evidence, product support, and mechanistic inference are separated;
- the chloride-bridged candidate is not represented as isolated;
- IS01_S3 is optional in a minimal path representation;
- direction_leakage rules are explicit;
- reverse_direction testing is prepared;
- `chemical_continuation_space` is not equated with physical fixation;
- allowed and forbidden claims are explicit;
- physical_causality_claimed = no.

## 17. Limitations

- The proposed state order is a documented mechanistic reference order.
- Intermediate configurations are not all directly observed or isolated.
- Chloride transfer supports an inner-sphere mechanism but does not provide a frame-by-frame microscopic trajectory.
- Evidence classes are documentation categories, not posterior probabilities.
- Species identity is not pathway evidence, and documented species identity does not imply a directly resolved reaction intermediate.
- No kinetic fitting, thermodynamic reconstruction, or transition-state calculation is performed.
- No independent direction reconstruction is performed in this specification block.
- No physical causality claim follows from the state order.
- Subsequent Co(II) ligand exchange must be separated from the primary electron- and chloride-transfer event.
- IS01_S3 is an optional formal post-ET resolution; post-ET bridge persistence is not required.

## 18. Source Basis

Primary and official sources:

1. Henry Taube, Nobel Lecture, 8 December 1983, *Electron Transfer between Metal Complexes - Retrospective*. NobelPrize.org. This lecture is used as a historical primary source for Taube's retrospective account of electron-transfer mechanisms in metal complexes.  
   <https://www.nobelprize.org/prizes/chemistry/1983/taube/lecture/>

2. H. Taube, H. Myers, R. L. Rich, 1953, *Observations on the Mechanism of Electron Transfer in Solution*, Journal of the American Chemical Society 75, 4118-4119. This is the classic report associated with the cobalt/chromium chloride-transfer evidence and inner-sphere interpretation.  
   <https://pubs.acs.org/doi/10.1021/ja01112a546>

3. Nobel Prize in Chemistry 1983 press release and Nobel background material on Henry Taube's studies of electron-transfer mechanisms in metal complexes. These sources are used only for historical framing, not for new mechanistic inference.  
   <https://www.nobelprize.org/prizes/chemistry/1983/press-release/>

Secondary source:

4. Peter C. Ford, 2006, *Henry Taube: Inorganic Chemist Extraordinaire*, Inorganic Chemistry. This is used as a secondary historical and disciplinary overview of Taube's coordination-chemistry and electron-transfer work.  
   <https://pubs.acs.org/doi/10.1021/ic060669s>

No long verbatim quotations are used. The source basis is paraphrased for boundary setting.

## 19. Next-Step Boundary

The next allowed block after acceptance of this specification is:

> QSB-CAUSALITY06B-02 — Inner-Sphere ET Candidate-State Record Schema

Not included in this block:

- machine-readable schema;
- concrete data records;
- runner;
- scoring;
- directed graph analysis;
- continuation-space calculation;
- result claim.
