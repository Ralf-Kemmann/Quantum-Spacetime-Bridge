# BMS-FU02g5d — Automorphy-Only Role Transport Result Note

**Date:** 2026-05-07  
**Project:** Quantum–Spacetime Bridge / Gravitation und RaumZeit  
**Status:** Internal result note  
**Block:** BMS-FU02g5d — Automorphy-Only Role Transport Check

---

## 1. Purpose

BMS-FU02g5d implements the conservative role-transport rule specified in FU02g5c:

```text
No reference roles are assigned to arbitrary candidate patches unless an explicit
face-type-preserving isomorphism / automorphy mapping to the FU02f1 reference
carrier exists.
```

Internal shorthand:

```text
Keine Etiketten auf fremde Klunker kleben.
Nur Spiegelklunker dürfen Referenzetiketten tragen.
```

The purpose of this run was to test whether the localized FU02g4c exact candidate admits such a mapping and whether the transported `mixed_core` and `pentagon_boundary` roles are unique or mapping-dependent.

---

## 2. Inputs

### 2.1 Source graph

```text
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/bms_fu02d1_face_adjacency_edges.csv
```

The graph is the repaired C60 face-adjacency graph.

### 2.2 Reference carrier

```text
H_07;H_09;H_11;H_12;H_13;H_14;H_15;H_16;H_17;H_18;H_19;H_20;P_07;P_08;P_09;P_10;P_11
```

Reference `mixed_core`:

```text
H_09;H_11;H_13;H_16;H_17;H_18;H_19;H_20
```

Reference `pentagon_boundary`:

```text
H_07;H_12;H_14;H_15;P_07;P_08;P_09;P_10;P_11
```

### 2.3 Localized FU02g4c candidate patch

```text
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

---

## 3. Outputs

Generated run directory:

```text
runs/BMS-FU02g5d/automorphy_only_role_transport/
```

Generated files:

```text
runs/BMS-FU02g5d/automorphy_only_role_transport/summary.json
runs/BMS-FU02g5d/automorphy_only_role_transport/mappings.csv
runs/BMS-FU02g5d/automorphy_only_role_transport/transported_role_sets.csv
runs/BMS-FU02g5d/automorphy_only_role_transport/result_note.md
```

---

## 4. Befund

The runner compared the FU02f1 reference carrier and the localized FU02g4c candidate as induced subgraphs of the repaired C60 face graph.

Observed result:

```text
mapping_count = 1
transport_allowed = true
mixed_core_invariant_across_mappings = True
pentagon_boundary_invariant_across_mappings = True
```

The candidate admits exactly one face-type-preserving isomorphism from the FU02f1 reference carrier.

Because there is exactly one mapping, the transported role sets are unique within the tested mapping set.

---

## 5. Transported role sets

### 5.1 Transported candidate `mixed_core`

```text
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09
```

### 5.2 Transported candidate `pentagon_boundary`

```text
H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

These are the same candidate role sets previously used in the localized FU02g4c patch photo / inspection context, but FU02g5d now justifies them by explicit automorphy-only transport rather than by free assignment.

---

## 6. Mapping

The unique mapping from reference node to candidate node is:

```text
H_07 -> H_15  pentagon_boundary
H_09 -> H_05  mixed_core
H_11 -> H_03  mixed_core
H_12 -> H_10  pentagon_boundary
H_13 -> H_09  mixed_core
H_14 -> H_17  pentagon_boundary
H_15 -> H_16  pentagon_boundary
H_16 -> H_06  mixed_core
H_17 -> H_01  mixed_core
H_18 -> H_02  mixed_core
H_19 -> H_08  mixed_core
H_20 -> H_07  mixed_core
P_07 -> P_01  pentagon_boundary
P_08 -> P_00  pentagon_boundary
P_09 -> P_03  pentagon_boundary
P_10 -> P_07  pentagon_boundary
P_11 -> P_02  pentagon_boundary
```

The mapping preserves face type:

```text
H -> H
P -> P
```

---

## 7. Interpretation

FU02g5d supports the following methodological reading:

```text
The localized FU02g4c candidate is not merely role-colored by convention.
Its candidate roles can be transported from the FU02f1 reference carrier through
the unique tested face-type-preserving graph isomorphism.
```

This strengthens the previous FU02g4c/g4d interpretation:

```text
The observed role-colored exact match is a symmetry twin of the FU02f1 reference,
not an independent second carrier structure.
```

Internal shorthand:

```text
Der Spiegelklunker bekommt seine Etiketten zurück —
aber nicht von Hand aufgeklebt,
sondern vom Spiegel selbst geliefert.
```

---

## 8. Hypothese

A bounded working hypothesis is now allowed:

```text
For the localized FU02g4c candidate, the role-colored exact structure is fully
explained by automorphy to the FU02f1 reference carrier.
```

This hypothesis is restricted to the tested reference-candidate pair and the implemented face-type-preserving isomorphism check.

It does not imply that arbitrary non-isomorphic patches can receive reference-like roles.

---

## 9. Offene Lücke

The following remain open:

```text
1. Non-isomorphic candidate patches still lack an accepted local structural role-transport rule.
2. Near-exact role-colored decoys outside the automorphy class remain a separate inspection task.
3. Larger FU02g5b enumeration windows remain local scaffold tests unless role transport is resolved.
4. External fullerene / planar / spherical graph controls remain open.
5. No physical dynamics, Lorentz compatibility, or spacetime emergence claim follows from this check.
```

---

## 10. Claim Boundary

### Allowed

```text
BMS-FU02g5d confirms that the localized FU02g4c candidate admits exactly one
face-type-preserving isomorphism to the FU02f1 reference carrier.
```

Allowed:

```text
Under automorphy-only role transport, the candidate receives a unique
mixed_core and pentagon_boundary assignment.
```

Allowed:

```text
The previously used candidate role split is methodologically supported for this
candidate by explicit graph mapping, not by arbitrary label assignment.
```

### Not allowed

```text
QSB has solved role transport for arbitrary patches.
```

Not allowed:

```text
FU02g5d proves global uniqueness or global rarity.
```

Not allowed:

```text
FU02g5d establishes physical emergence, spacetime dynamics, or Lorentz compatibility.
```

Not allowed:

```text
Non-isomorphic patches may be assigned reference roles by analogy.
```

---

## 11. Consequence for the FU02 line

The current chain is now:

```text
FU02g4c/g4d:
exact match found, localized, photographed, automorphic to reference.

FU02g5:
direct role-assignment sensitivity test stable across configured variants.

FU02g5c:
role-transport rule frozen defensively:
no transport except under explicit automorphy/isomorphism.

FU02g5d:
localized candidate passes automorphy-only transport with mapping_count = 1.
Transported roles are unique.
```

This makes FU02g5d a methodological closure step for the localized FU02g4c candidate, not a new global enumeration result.

---

## 12. Recommended next block

Recommended next block:

```text
BMS-FU02g5e — Near-Exact Automorphy-Class / Decoy Inspection
```

Possible purpose:

```text
Inspect the previously observed role-colored near-match cases and determine
whether they are automorphic variants, near automorphic decoys, or structurally
independent candidates under no-transport / face-type-only / automorphy-only logic.
```

Alternative next block:

```text
BMS-FU03a — External Fullerene / Planar / Spherical Graph Controls
```

Purpose:

```text
Test whether the FU02 role-colored carrier signature behavior is C60-specific,
fullerene-generic, planar/spherical-generic, or more broadly motif-generic.
```

---

## 13. Status line

```text
BMS-FU02g5d provides a clean automorphy-only role-transport confirmation for
the localized FU02g4c candidate: exactly one face-type-preserving mapping exists,
and the transported role sets are unique.
```

Internal closure:

```text
Nur Spiegelklunker dürfen Referenzetiketten tragen.
Dieser Spiegelklunker trägt sie eindeutig.
```
