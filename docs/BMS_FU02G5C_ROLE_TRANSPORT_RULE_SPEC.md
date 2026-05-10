# BMS-FU02g5c — Role-Transport Rule Specification

**Date:** 2026-05-07  
**Project:** Quantum–Spacetime Bridge / Gravitation und RaumZeit  
**Status:** Internal specification / method-freeze candidate  
**Scope:** C60 face-graph carrier-signature controls after FU02g5 / FU02g5b

---

## 1. Purpose

BMS-FU02g5c specifies how role labels such as `mixed_core` and `pentagon_boundary` may or may not be assigned to arbitrary connected 17-face patches in the C60 face-graph control space.

This block is needed because FU02g5b showed that small deterministic connected-patch enumeration windows can be processed technically, but only some role modes are directly interpretable for arbitrary patches.

Key question:

```text
How may reference-side role labels be transported to arbitrary candidate patches
without smuggling the reference structure into the candidate?
```

Internal image:

```text
Dürfen wir dem fremden Klunker unsere Etiketten ankleben,
oder müssen die Etiketten aus seiner eigenen Nachbarschaft folgen?
```

---

## 2. Background

### 2.1 FU02g4c / FU02g4d anchor

The current FU02g4c/g4d anchor is:

```text
exact match found
exact match localized
exact match photographed
exact match automorphic to reference
```

The localized exact patch was:

```text
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

It was identified as automorphic to the FU02f1 reference carrier. Therefore, the observed role-colored exact match is not a new independent second structure, but a symmetry twin of the reference carrier.

Safe internal shorthand:

```text
Der Klunker war kein fremder Kristall.
Es war unser eigener Klunker im Spiegelkabinett.
```

### 2.2 FU02g5 direct role-assignment sensitivity test

FU02g5 tested the direct comparison:

```text
FU02f1 reference carrier
vs.
localized FU02g4c automorphic exact patch
```

under the configured variants:

```text
v0_type_preferred
uncolored_carrier_only
face_type_only
swap_core_boundary
core_erased
boundary_erased
```

Result:

```text
localized_candidate_exact_match = True
localized_candidate_near_distance = 0
localized_candidate_near_match = True
```

for all six variants.

### 2.3 FU02g5b first-500 scaffold enumeration

FU02g5b repaired the scaffold enumerator and processed:

```text
500 connected 17-face patches per variant
stop_reason = max_count_reached
partial_run = False
```

In the first window:

```text
enumerated_exact_match_count = 0
enumerated_near_match_count = 0
```

for all variants.

However, warnings were produced for variants requiring `mixed_core` / `pentagon_boundary` role transport for arbitrary patches:

```text
v0_type_preferred
swap_core_boundary
core_erased
boundary_erased
```

The directly clean enumeration modes were:

```text
uncolored_carrier_only
face_type_only
```

---

## 3. Problem Statement

For the FU02f1 reference carrier, the roles are known by construction:

```text
mixed_core
pentagon_boundary
```

For the localized FU02g4c exact patch, the roles are known because the patch was inspected as the localized automorphic exact candidate and shown to be automorphic to the reference.

For an arbitrary connected 17-face patch, however, the following is not automatically known:

```text
which nodes should be mixed_core?
which nodes should be pentagon_boundary?
whether those roles should be transported from the reference?
whether the candidate has its own internally defined analogues?
```

Assigning roles incorrectly can create a circular test:

```text
If the reference role structure is pasted onto arbitrary patches,
then the test may partly measure the imposed labeling rule rather than the patch structure.
```

Therefore, role transport must be explicitly specified before primary-scale role-colored enumeration can be interpreted.

---

## 4. Definitions

**Carrier patch**  
A `carrier_patch` is a connected set of 17 face-nodes in the C60 face graph.

**Reference carrier**  
The `reference_carrier` is the FU02f1 carrier region with known project-defined role subsets.

**Candidate patch**  
A `candidate_patch` is any connected 17-face patch evaluated against the reference signature.

**Role-colored signature**  
A `role_colored_signature` is a graph signature computed from the induced patch subgraph and a role map assigned to its nodes.

**Role transport**  
`role_transport` means assigning reference-like roles such as `mixed_core` and `pentagon_boundary` to nodes in a candidate patch.

**Automorphy-only role transport**  
`automorphy_only_role_transport` means transporting roles only through an explicit graph automorphism or isomorphism that maps the reference carrier to the candidate patch.

**Local structural role rule**  
A `local_structural_role_rule` means assigning roles from candidate-local features, such as H/P face type, internal degree, boundary degree, pentagon adjacency, shell position, or other graph-local diagnostics.

---

## 5. Candidate Role-Transport Options

### Option A — No role transport for arbitrary patches

For arbitrary candidate patches, do not assign `mixed_core` or `pentagon_boundary`.

Allowed enumeration modes:

```text
uncolored_carrier_only
face_type_only
```

Advantages:

```text
maximally defensive
no reference labels are pasted onto candidates
directly interpretable for arbitrary connected patches
simple null/control behavior
```

Disadvantages:

```text
does not test full v0 role-colored specificity across arbitrary candidates
cannot directly count mixed_core/pentagon_boundary decoys
```

Status:

```text
Recommended primary default for arbitrary-patch enumeration.
```

### Option B — Automorphy-only role transport

Transport `mixed_core` and `pentagon_boundary` only if the candidate patch is automorphic/isomorphic to the reference carrier under the tested full graph or induced-patch relation.

Advantages:

```text
scientifically clean
avoids arbitrary labeling
directly separates symmetry twins from independent decoys
consistent with FU02g4c/g4d automorphy result
```

Disadvantages:

```text
does not find non-automorphic but structurally similar decoys
requires explicit mapping choice if multiple automorphisms exist
needs deterministic tie-handling for multiple valid maps
```

Status:

```text
Allowed hard rule.
Recommended as secondary control after Option A.
```

### Option C — Local structural role rule

Define candidate roles using local graph features of the candidate itself.

Possible features:

```text
face type H/P
internal patch degree
external boundary degree
pentagon adjacency count
distance to pentagon nodes
shell position within induced patch
membership in local high-connectivity core
role-degree histogram class
```

Advantages:

```text
could allow real non-automorphic decoy search
may detect structural analogues not captured by strict automorphy
can become a useful future specificity test
```

Risks:

```text
high researcher degrees of freedom
danger of post-hoc role fitting
requires separate null models
requires preregistered deterministic rule
needs field list and audit trail
```

Status:

```text
Not accepted for primary claims in FU02g5c.
Allowed only as future-work candidate after separate specification and red-team review.
```

---

## 6. Recommended FU02g5c Rule Freeze

### 6.1 Primary rule

For arbitrary connected 17-face patch enumeration:

```text
Use only:
uncolored_carrier_only
face_type_only
```

Do not assign `mixed_core` or `pentagon_boundary` to arbitrary patches.

### 6.2 Secondary hard rule

Allow `mixed_core` and `pentagon_boundary` transport only under:

```text
automorphy_only_role_transport
```

A candidate must have an explicitly recorded automorphic/isomorphic mapping to the reference carrier.

### 6.3 Deferred rule

Do not use local structural role transport for primary claims until a separate specification exists.

Deferred block:

```text
BMS-FU02g5e — Local Structural Role Rule Candidate Tests
```

---

## 7. Practical Consequences for Existing FU02g5b Output

The cleanest interpreted FU02g5b enumeration results are:

```text
uncolored_carrier_only
face_type_only
```

For these modes:

```text
500 patches processed
0 exact
0 near
0 warnings
stop_reason = max_count_reached
partial_run = False
```

Variants involving `mixed_core` / `pentagon_boundary` for arbitrary enumeration should be treated as scaffold output only unless role transport is explicitly resolved.

Therefore, FU02g5b can be cited as:

```text
The patched FU02g5b scaffold processed a first deterministic 500-patch window.
No exact or near matches were observed in the directly interpretable
uncolored-carrier and face-type-only modes.
```

It should not be cited as:

```text
A full role-colored enumeration under v0_type_preferred.
```

---

## 8. Proposed Next Block

Recommended next implementation block:

```text
BMS-FU02g5d — Automorphy-Only Role Transport Check
```

Purpose:

```text
Search or inspect candidate patches for automorphy/isomorphism to the FU02f1 reference,
and transport roles only when an explicit mapping exists.
```

Outputs should include:

```text
candidate_patch_id
candidate_nodes
automorphic_to_reference
mapping_count
selected_mapping_rule
transported_mixed_core_nodes
transported_pentagon_boundary_nodes
role_colored_signature
exact_match
near_distance
stop_reason
warnings
```

This preserves the strongest defensive line:

```text
No role labels are assigned to arbitrary patches unless justified by automorphy.
```

---

## 9. Claim Boundary

Allowed:

```text
FU02g5c defines a conservative role-transport rule for future role-colored
connected-patch enumeration.
```

Allowed:

```text
For arbitrary patch enumeration, only uncolored-carrier and face-type-only modes
are currently directly interpretable without additional role transport assumptions.
```

Allowed:

```text
mixed_core and pentagon_boundary roles may be transported only under explicit
automorphy/isomorphism control.
```

Not allowed:

```text
QSB has solved role transport.
All arbitrary candidate patches can be assigned mixed_core/pentagon_boundary roles by analogy with the reference.
FU02g5b already proves full role-colored rarity under v0_type_preferred.
Any of this establishes physical emergence or spacetime dynamics.
```

---

## 10. Red-Team Notes

### 10.1 Main risk

The main methodological risk is circularity:

```text
A candidate is made reference-like by the role assignment rule,
then counted as reference-like by the signature test.
```

### 10.2 Reviewer-sensitive point

A reviewer may ask:

```text
How were candidate roles assigned?
Were these roles defined before seeing the candidate?
Are they invariant under automorphisms?
Would another reasonable rule change the counts?
```

FU02g5c answers:

```text
Until this is solved, primary enumeration claims use only no-transport modes.
Role transport is allowed only when automorphy provides a mapping.
```

### 10.3 Relation to aperiodic / non-lattice literature

The literature on aperiodic order suggests the value of local motif classes and finite local complexity. It does not license arbitrary role assignment.

Safe analogy:

```text
role-colored signatures may be treated like controlled local motif classes.
```

Unsafe analogy:

```text
role-colored signatures automatically define quasicrystalline order.
```

---

## 11. Minimal Implementation Requirements for FU02g5d

Before running FU02g5d, implement or verify:

```text
1. deterministic induced-patch isomorphism / automorphy checker
2. explicit mapping output
3. handling of multiple mappings
4. stable selected_mapping_rule
5. no role transport if automorphy check fails
6. warning if multiple mappings induce different role assignments
7. CSV/JSON field list
8. result note with Befund / Interpretation / Hypothese / Offene Lücke / Claim Boundary
```

Recommended selected-mapping rule:

```text
If multiple valid automorphisms exist, retain all transported role sets
or choose the lexicographically minimal mapping only for display,
while reporting mapping_count and role_set_variance.
```

Do not hide ambiguity.

---

## 12. Final Recommendation

FU02g5c freezes the conservative rule:

```text
Primary arbitrary-patch enumeration:
use uncolored_carrier_only and face_type_only.

Role transport:
allowed only under explicit automorphy/isomorphism mapping.

Local structural role rules:
future work only, not accepted for current primary claims.
```

Internal shorthand:

```text
Keine Etiketten auf fremde Klunker kleben.
Nur Spiegelklunker dürfen Referenzetiketten tragen.
```

---

## 13. Status Line

```text
BMS-FU02g5c provides the methodological bridge between FU02g5b enumeration
and any future role-colored decoy search.
It is a rule specification, not a new numerical result.
```
