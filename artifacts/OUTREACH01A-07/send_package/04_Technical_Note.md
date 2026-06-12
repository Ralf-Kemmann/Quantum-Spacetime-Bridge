# A Minimal State-Identity Demonstrator for Phase-Shifted Equivalent Configurations

*A synthetic, traceable representation prepared for technical assessment*

## 1. Purpose

This note describes a deliberately small synthetic demonstrator. Its purpose is not to model a reported laser experiment, reproduce a measurement, or propose a new theory of discrete time-crystal behavior. Its purpose is narrower: to make three distinctions explicit enough to be assessed technically. The distinctions are record identity, dynamic equivalence, and temporal phase position. A fourth issue, the representation of a boundary between coexisting equivalent configurations, is included as an open modelling question rather than as a proposed physical ontology.

The demonstrator uses one canonical synthetic dataset with three records: `DTC_A`, `DTC_B`, and `BOUNDARY_AB`. The visible table and figure are derived from those same records and do not alter their identifiers, controlled values or comparison logic.

## 2. Why This Representation

The chosen form is intentionally minimal because the later technical question should not ask a reader to evaluate a broad project. It should ask whether a compact state-identity representation is methodologically useful, trivial, misleading, or incomplete. The representation therefore separates what is asserted synthetically from what is not established physically.

`DTC_A` and `DTC_B` are declared to belong to one dynamic equivalence class. They are also declared to differ by one drive period in temporal phase offset. This lets the record structure distinguish a shared equivalence class from the identity of a particular record. The distinction is important for the demonstrator because two records can be treated as dynamically equivalent for a method example without being the same record and without asserting full physical state identity.

The boundary record is included to make the second question concrete. It does not claim that a boundary object is physically correct. It only gives a visible place where an expert could say that a separate boundary record is useful, too strong, too weak, or should be replaced by another dynamical description.

## 3. The Three Records

`DTC_A` is a synthetic state configuration. It has state class `DTC_EQUIVALENT_PAIR`, dynamic equivalence class `DTC_EQ_CLASS_01`, temporal phase offset `0`, drive-period shift `0`, and domain `DOMAIN_A`. Its full-state identity status is `self_identical_only`, meaning that this record is identical only to itself inside the demonstrator.

`DTC_B` is a second synthetic state configuration. It has the same state class and dynamic equivalence class as `DTC_A`, but temporal phase offset `1`, drive-period shift `1`, and domain `DOMAIN_B`. Its full-state identity status is `distinct_record_not_identical_to_DTC_A`. Thus the dataset explicitly marks dynamic equivalence without collapsing record identity.

`BOUNDARY_AB` is a synthetic boundary configuration. Its state class is `DTC_BOUNDARY_CLASS`. It is not assigned to `DTC_EQ_CLASS_01`; its dynamic equivalence class, temporal phase offset, and drive-period shift are `not_applicable`. Its domain field references `DOMAIN_A__DOMAIN_B`, and its boundary role is `interface_between_equivalent_phase_shifted_domains`. Its uncertainty status is `representation_choice_open`.

## 4. Identity, Equivalence and Phase Offset

The demonstrator carries three guard statements. Observable similarity does not imply full-state identity. Dynamic equivalence does not imply record identity. Phase-shifted equivalence does not imply membership in the same domain. These statements are not empirical findings. They are rules that prevent the small example from smuggling a stronger conclusion than it can support.

The dynamic equivalence class is declared for method demonstration only. The dataset does not infer equivalence from experimental data. It does not estimate parameters, reconstruct a mechanism, or validate a physical interpretation. Its value is that it exposes the bookkeeping question: if two configurations are considered equivalent under a one-period shift, what information is still required to decide whether they are identical, merely equivalent, or physically distinguishable?

## 5. Boundary Representation as an Open Question

The separate boundary record is a representation option. It gives the boundary an explicit record identifier, type, role, and uncertainty status. That makes the boundary visible in the same table as the state configurations, but it also creates a risk: the table could look as though the boundary object has been validated as a physical entity. To avoid that, the record says `representation_choice_open` and `not_experimental`.

The intended use is to ask whether this representation is adequate. A different answer may be better: a state label, an interface condition, a dynamical transition region, a domain-wall variable, or a model-specific description. The demonstrator is designed to make that criticism easy to state.

## 6. Technical Questions

1. Is it methodologically useful to distinguish record identity, dynamic equivalence and temporal phase position for two configurations related by a one-drive-period shift?

2. From the group’s perspective, what would be the minimal adequate representation for long-lived boundaries between coexisting equivalent configurations: a state label, a distinct boundary object, or another dynamical description?

3. What is the minimum state or observable information required for such a relational comparison to become physically meaningful rather than merely formally consistent?

## 7. Scope and Limitations

This is a synthetic method demonstrator. It uses no experimental data, is not a model of the physical systems studied by the group, makes no physical prediction and does not explain a mechanism. Dynamic equivalence is declared rather than inferred, and the separate boundary record remains an open representation option rather than a validated physical ontology. The visible table and figure support inspection of the representation; they do not establish its physical adequacy.
