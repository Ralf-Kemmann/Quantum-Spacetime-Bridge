# QSB-CAUSALITY07-01 — Oscillatory Reaction State-Cycle Case Definition

## 1. Status and Scope

```text
block_id = QSB-CAUSALITY07-01
block_type = oscillatory_case_definition
reference_system = homogeneous_Belousov_Zhabotinsky_reaction
mechanistic_basis = FKN_and_Oregonator
runner_present = no
numerical_simulation_present = no
reaction_diffusion_analysis_present = no
physical_causality_claimed = no
closed_causal_loop_claimed = no
```

This block defines a state-cycle framework for later analysis of recurrent chemical state sequences. It does not rerun or re-prove the microscopic mechanism of the Belousov-Zhabotinsky reaction. It treats only temporal oscillation in an idealized homogeneous, well-stirred reaction medium.

Spatial waves, spiral patterns, diffusion, convection, and reaction-diffusion analysis are outside this block. The BZ reaction is treated as a driven dissipative non-equilibrium system, not as an equilibrium fluctuation.

Reference basis:

- Field, Koros, and Noyes, 1972, `Oscillations in Chemical Systems. II. Thorough Analysis of Temporal Oscillation in the Bromate-Cerium-Malonic Acid System`, JACS, DOI `10.1021/ja00780a001`.
- Related 1972 FKN mechanism work by Noyes, Field, and collaborators.
- Field and Noyes, 1974, `Oscillations in Chemical Systems. IV. Limit Cycle Behavior in a Model of a Real Chemical Reaction`.
- A secondary overview of the Oregonator/BZ framework, used only as background.

## 2. Reference Oscillatory System

The reference system is a homogeneous Belousov-Zhabotinsky reaction represented at the method level by the Field-Koros-Noyes mechanism and by the Oregonator reduction. This case definition does not fix one laboratory recipe.

```text
oxidant_pool = bromate_containing_reaction_pool
organic_substrate_pool = malonic_acid_or_related_organic_substrate
redox_catalyst_pool = cerium_or_ferroin_family
inhibitory_species_role = bromide_related_inhibition
autocatalytic_species_role = bromous_acid_related_activation
observable_marker = catalyst_oxidation_state_or_color_signal
```

The observable marker may be a catalyst oxidation-state signal or a color signal, depending on the catalyst family and measurement design. A repeated visible color or redox marker is not treated as the full chemical state.

```text
observable_color_state_is_full_chemical_state = no
oscillation_is_equilibrium_fluctuation = no
oscillation_requires_nonequilibrium_chemical_driving = yes
continuous_external_feed_required_for_finite_batch_oscillation = no
sustained_stationary_oscillation_may_require_open_flow_conditions = yes
```

A finite batch BZ system may exhibit transient oscillations by consuming initially available reactants and free-energy gradients. Continuous external feeding is not required for such finite-duration oscillations. Long-term stationary oscillation may, however, require open-flow conditions that replenish reactants and remove products. This is not a perpetual-motion or self-supply statement; non-equilibrium chemical driving remains required.

## 3. Cycle-State Vocabulary

The minimal cycle vocabulary uses neutral state-region labels:

```text
BZ01_P0 = bromide_inhibited_region
BZ01_P1 = inhibitor_depletion_and_activation_region
BZ01_P2 = autocatalytic_oxidation_region
BZ01_P3 = oxidized_catalyst_and_recovery_region
BZ01_P4 = inhibitor_regeneration_region
```

Reference sequence:

```text
BZ01_P0
-> BZ01_P1
-> BZ01_P2
-> BZ01_P3
-> BZ01_P4
-> BZ01_P0_prime
```

`BZ01_P0_prime` is a later recurrent state region that is observably similar to `BZ01_P0`. It is not asserted to be the same full chemical state.

```text
BZ01_P0_prime != BZ01_P0
observable_recurrence_documented_for_reference_system = yes
observable_recurrence_established_for_future_run_input = not_yet_assessed
full_state_identity_recurrence = no_or_not_assessed
```

`BZ01_P0_prime` may share a phase role or marker range with `BZ01_P0` while having different resource pools, product loads, inhibitor history, temperature history, or cycle index.

Observable recurrence is documented for the BZ reference system in the literature. Whether a specific future input dataset exhibits recurrence under the declared detection rules remains to be assessed by the later data-and-runner block. Reference-system knowledge must not be preloaded as a result of a future run, and recurrence of the observable signal remains separate from complete chemical-state identity.

## 4. State Identity and Recurrence

The later runner must keep these concepts separate:

```text
observable_state_similarity
full_chemical_state_identity
cycle_phase_identity
cycle_index
resource_pool_state
```

Definitions:

- Beobachtbare Zustandsaehnlichkeit (`observable_state_similarity`): Similar color, redox indicator, absorbance region, or selected measured marker.
- Vollstaendige chemische Zustandsidentitaet (`full_chemical_state_identity`): Agreement of all relevant species concentrations, resource pools, product loads, and boundary conditions.
- Zyklusphasenidentitaet (`cycle_phase_identity`): Assignment to the same functional region of the oscillation cycle.
- Zyklusnummer (`cycle_index`): The counted recurrence number of a phase-region visit.
- Zustand der Ressourcenbestaende (`resource_pool_state`): Oxidant, organic substrate, inhibitor, catalyst, product, and acid-medium status relevant to later cycle continuation.

```text
same_observable_marker_implies_same_full_state = no
same_cycle_phase_implies_same_resource_pool = no
cycle_recurrence_implies_state_reset = no
```

German display aliases for later human-readable views:

| Deutsche Bezeichnung | Canonical Field |
|---|---|
| Beobachtbare Zustandsaehnlichkeit | `observable_state_similarity` |
| Vollstaendige chemische Zustandsidentitaet | `full_chemical_state_identity` |
| Zyklusphasenidentitaet | `cycle_phase_identity` |
| Zyklusnummer | `cycle_index` |
| Zustand der Ressourcenbestaende | `resource_pool_state` |
| Rueckkehr in wiederkehrende Zustandsregion | `return_to_recurrent_state_region` |
| Lokale Uebergangsfolge vollstaendig | `local_transition_sequence_complete` |
| Grund des Zyklusabbruchs | `cycle_termination_reason` |

```text
canonical_field_names_remain_language_neutral = yes
human_readable_labels_are_localized_aliases = yes
localized_aliases_used_as_logic_inputs = no
```

## 5. Local Transition and Cycle Rules

A later local transition `X -> Y` may be assessed only from chemical and observable state features. The following inputs are not allowed as direction inputs:

```text
phase_label
cycle_position_label
cycle_index
known_reference_order
figure_arrow_direction
color_name_alone
source_document_order
```

```text
reference_cycle_order_used_as_direction_input = no
phase_labels_used_as_direction_input = no
cycle_index_used_as_direction_input = no
```

Cycle closure may be represented only as observable closure when all required conditions are met:

```text
local_transition_sequence_complete = yes
return_to_recurrent_state_region = yes
observable_state_similarity_threshold_met = yes
full_chemical_state_identity = no_or_not_assessed
```

Local direction and global recurrence are compatible:

```text
local_direction_can_coexist_with_global_recurrence = yes
global_recurrence_negates_local_direction = no
```

Possible termination or drift reasons for a later runner:

```text
cycle_termination_reason
substrate_depletion
oxidant_depletion
catalyst_deactivation
inhibitor_pool_shift
temperature_or_mixing_change
transition_to_steady_state
not_assessed
```

## 6. Allowed and Forbidden Claims

Allowed statements:

- The BZ reaction provides a documented oscillatory reference system.
- Local directed transitions may occur within a globally recurrent state sequence.
- Observable recurrence does not establish full chemical-state identity.
- Repeated color or redox signals may identify recurrent phase regions rather than exact state resets.
- Finite-duration batch oscillation may occur without continuous external feeding, while non-equilibrium chemical driving remains required.
- Sustained stationary oscillation may require open-flow conditions.
- A later runner may test local admissibility, recurrence, and cycle termination separately.

Forbidden claim classes:

- Claiming a proven closed causal cycle from recurrence alone.
- Claiming that time is generated by the oscillation.
- Claiming exact whole-state reset on every cycle.
- Claiming demonstrated recurrence of an identical complete state.
- Claiming reconstruction of physical causality.
- Claiming indefinite self-sustained chemistry without resource consumption.
- Treating the oscillation as an equilibrium process.
- Treating cycle direction as proof of causal direction.
- Treating the BZ case as validation of QSB.

## 7. Acceptance Criteria

This block is accepted only if:

- exactly one new Markdown file is created;
- no existing file is changed;
- FKN and Oregonator are named separately as mechanism and model basis;
- five neutral cycle phase regions are defined;
- `BZ01_P0_prime` is not equated with `BZ01_P0`;
- observable recurrence and full chemical-state identity are separated;
- local direction and global recurrence are both allowed;
- cycle-termination reasons are defined;
- no spatial reaction-diffusion analysis is included;
- no numerical simulation is included;
- German aliases for human-readable presentation are documented;
- no forbidden claim class is introduced;
- `git diff --check` passes.

## 8. Next Step

The next permissible block is:

```text
QSB-CAUSALITY07-02 — First Oscillatory State-Cycle Data and Runner
```

That block should combine curated source-bound BZ state data, observable time-series or model-phase data, a German alias view, local transition checks, recurrence handling, `P0` versus `P0_prime`, cycle termination or resource-shift handling, runner implementation, and outputs. No additional pure specification block is planned between CAUSALITY07-01 and CAUSALITY07-02.
