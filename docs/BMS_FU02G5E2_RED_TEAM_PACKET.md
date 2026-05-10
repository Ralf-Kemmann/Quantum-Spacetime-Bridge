# BMS-FU02g5e2 — Red-Team Packet

**Date:** 2026-05-08  
**Project:** Quantum–Spacetime Bridge / Gravitation und RaumZeit  
**Status:** Internal red-team packet  
**Scope:** FU02g5c → FU02g5d → FU02g5e1 → FU02g5e2 methodological chain

---

## 1. Purpose

This packet is intended for external AI-assisted red-team review by Claude, Louis, Grok, or equivalent reviewers.

The goal is not to validate QSB as a physical theory.

The goal is to stress-test a narrow methodological claim:

```text
Given the current FU02g5c–g5e2 control chain, is it justified to treat only
the known exact FU02g4c mirror candidate as reference-role-transportable,
while the other scaffold-localized near candidates remain non-transportable decoys?
```

Reviewers should focus on method, logic, assumptions, claim boundaries, and possible hidden circularity.

---

## 2. Minimal Project Context

QSB currently studies matter-motivated relational carrier regions in graph-like control spaces.

The current FU02 block uses the C60 face graph:

```text
nodes = C60 faces
edges = face adjacency
H_xx = hexagon face
P_xx = pentagon face
```

The working object is a connected 17-face carrier patch in the C60 face graph.

This block does not claim physical emergence, spacetime dynamics, Lorentz compatibility, or global uniqueness.

---

## 3. Current FU02 Anchor

### 3.1 FU02g4c / FU02g4d

A primary-audited enumeration previously found:

```text
raw_role_colored_signature_exact_match_count = 1
raw_role_colored_signature_near_match_count  = 11
```

Known exact localized candidate:

```text
raw_index / skip_first_raw_patches = 26,187,175
```

Known exact patch:

```text
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

It was identified as automorphic/isomorphic to the FU02f1 reference carrier.

Internal shorthand:

```text
Der Klunker war kein fremder Kristall.
Es war unser eigener Klunker im Spiegelkabinett.
```

Allowed interpretation:

```text
The known exact candidate is a symmetry twin of the FU02f1 reference carrier.
```

Not allowed:

```text
A second independent carrier structure was found.
```

---

## 4. FU02g5c — Role-Transport Rule Specification

FU02g5c froze a conservative methodological rule.

Primary rule:

```text
For arbitrary connected 17-face candidate patches, use only:
- uncolored_carrier_only
- face_type_only
```

Role transport rule:

```text
mixed_core and pentagon_boundary roles may be transported only under explicit
automorphy/isomorphism mapping from the FU02f1 reference carrier to the candidate.
```

Deferred / not accepted for primary claims:

```text
local structural role rules
post-hoc role assignment
free analogy-based role transport
```

Internal shorthand:

```text
Keine Etiketten auf fremde Klunker kleben.
Nur Spiegelklunker dürfen Referenzetiketten tragen.
```

Red-team target:

```text
Is this rule sufficiently conservative?
Is it too strict?
Is it still vulnerable to circularity?
```

---

## 5. FU02g5d — Automorphy-Only Role Transport Check

FU02g5d tested the known exact candidate under the g5c rule.

Result:

```text
mapping_count = 1
transport_allowed = true
mixed_core_invariant_across_mappings = True
pentagon_boundary_invariant_across_mappings = True
```

Transported candidate roles:

```text
candidate mixed_core:
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09

candidate pentagon_boundary:
H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Allowed interpretation:

```text
The known exact candidate receives its reference roles uniquely through the
single face-type-preserving mapping.
```

Not allowed:

```text
Role transport is solved for arbitrary patches.
```

---

## 6. FU02g5e1 — Near-Match Candidate Localization

FU02g5e1 localized/fotographed the near-match candidates.

Important label:

```text
Run label: scaffold localization
fu02g4c_order_guarantee = False
```

This means:

```text
The run provides a candidate photo set.
It does not certify exact FU02g4c raw-order replay.
```

Result:

```text
near_match_candidate_count = 11
exact_match_count = 1
max_raw_index_visited = 26784197
```

Distribution:

```text
early_2m_3m                  3 near, 0 exact
mid_17987055_18925223        1 near, 0 exact
exact_zone_25979015_26784197 7 near, 1 exact
```

All 11 candidates share the coarse carrier profile:

```text
n = 17
H = 12
P = 5
candidate_connected = True
candidate_edge_count = 37
```

Candidate categories before decoy classification:

```text
1 exact known mirror candidate:
26187175, exact=True, near_distance=0

1 coarse-distance-0 non-exact candidate:
26157530, exact=False, near_distance=0

2 distance-1 near candidates:
26161006
26167866

7 distance-2 near candidates:
2338804
2338805
2839553
18575893
26157529
26187327
26328307
```

Red-team target:

```text
Does scaffold localization make this candidate set useful for analysis?
Is the lack of FU02g4c raw-order certification sufficiently emphasized?
```

---

## 7. FU02g5e2 — Near-Match Decoy Classification

FU02g5e2 classified the 11 scaffold-localized candidates.

Result:

```text
candidate_count = 11
face_type_preserving_isomorphic_candidates = 1
non_isomorphic_near_candidates = 10
role_transport_allowed_candidates = 1
```

Classification counts:

```text
1 known_exact_spiegelklunker
1 coarse_signature_twin_but_not_exact
2 local_near_decoy_distance_1
7 near_decoy_distance_2
```

Only candidate with role transport allowed:

```text
candidate_008
raw_index = 26187175
exact_match = True
near_distance = 0
uncolored_isomorphic_to_reference = True
face_type_preserving_isomorphic_to_reference = True
mapping_count = 1
role_transport_allowed = True
classification_primary = known_exact_spiegelklunker
```

All other 10 candidates:

```text
uncolored_isomorphic_to_reference = False
face_type_preserving_isomorphic_to_reference = False
mapping_count = 0
role_transport_allowed = False
```

Important boundary:

```text
classification_boundary = scaffold_only_candidate_pending_fu02g4c_replay_validation
scaffold_order_certification = False
```

---

## 8. Narrow Claim Under Review

The current narrow claim is:

```text
Within the g5e1 scaffold-localized candidate set, FU02g5e2 finds that only the
known exact FU02g4c mirror candidate is face-type-preserving isomorphic to the
FU02f1 reference carrier and therefore eligible for automorphy-only role
transport under the FU02g5c rule. The remaining 10 near candidates are
non-isomorphic near decoys and do not receive reference-role transport.
```

This claim is intentionally limited to:

```text
the g5e1 scaffold-localized candidate set
the repaired C60 face graph
the implemented isomorphism checks
the FU02g5c role-transport rule
```

This claim does not include:

```text
FU02g4c raw-order replay certification
global uniqueness
global rarity proof
physical emergence
spacetime dynamics
Lorentz compatibility
```

---

## 9. Specific Questions for Claude

Claude should focus on structural method review.

Please answer:

```text
1. Is the chain g5c → g5d → g5e1 → g5e2 logically coherent?
2. Does the role-transport rule avoid circularity?
3. Is the distinction between scaffold localization and FU02g4c replay certification clear enough?
4. Is candidate_005, the near_distance=0 non-exact case, handled adequately?
5. Are the claim boundaries strong enough?
6. What would a skeptical reviewer object to first?
7. What result-note wording should be tightened?
8. What additional table/field would make the result more auditable?
```

Expected output format:

```text
Major concerns
Minor concerns
What is defensible
What is not defensible
Recommended wording changes
Recommended next control
```

---

## 10. Specific Questions for Louis

Louis should act as a careful theoretical-physics colleague, not a hostile reviewer.

Please answer:

```text
1. Is the scientific story understandable?
2. Does the Klunker / mirror-candidate metaphor help or distract?
3. Is the relationship to aperiodic / non-lattice structure literature appropriately cautious?
4. Does the current result sound methodologically interesting without overclaiming?
5. Where would a cautious theoretical physicist become uneasy?
6. How should this be explained in external-facing language?
7. What should remain internal shorthand only?
```

Expected output format:

```text
Intuitive summary
Strength of the result
Main caution
External-facing phrasing
Internal-only phrasing
Suggested next step
```

---

## 11. Specific Questions for Hard Red Team / Grok

The hard red team should try to break the result.

Please answer aggressively:

```text
1. Is g5e2 merely classifying artifacts of the scaffold enumerator?
2. Does lack of FU02g4c raw-order certification undercut the result?
3. Is face-type-preserving isomorphism too strict, too weak, or arbitrary?
4. Does candidate_005 undermine the exact/near distinction?
5. Are near_distance and role_colored_signature being conflated?
6. Could the 10 decoys become role-transportable under another reasonable rule?
7. Is the result tautological because role transport is defined by isomorphism?
8. What minimal additional evidence would be required before citing this result?
```

Expected output format:

```text
Attack summary
Strongest objection
Second strongest objection
Potential fatal flaw
Non-fatal weaknesses
What survives the attack
Minimal repair/control
```

---

## 12. Data Summary for Reviewers

### 12.1 Known exact candidate

```text
candidate_id = candidate_008
raw_index = 26187175
nodes =
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
exact_match = True
near_distance = 0
uncolored_isomorphic_to_reference = True
face_type_preserving_isomorphic_to_reference = True
mapping_count = 1
role_transport_allowed = True
classification_primary = known_exact_spiegelklunker
```

### 12.2 Coarse signature twin but not exact

```text
candidate_id = candidate_005
raw_index = 26157530
exact_match = False
near_distance = 0
uncolored_isomorphic_to_reference = False
face_type_preserving_isomorphic_to_reference = False
mapping_count = 0
role_transport_allowed = False
classification_primary = coarse_signature_twin_but_not_exact
```

### 12.3 Distance-1 near decoys

```text
candidate_006
raw_index = 26161006
near_distance = 1
role_transport_allowed = False

candidate_007
raw_index = 26167866
near_distance = 1
role_transport_allowed = False
```

### 12.4 Distance-2 near decoys

```text
candidate_000 raw_index = 2338804
candidate_001 raw_index = 2338805
candidate_002 raw_index = 2839553
candidate_003 raw_index = 18575893
candidate_004 raw_index = 26157529
candidate_009 raw_index = 26187327
candidate_010 raw_index = 26328307
```

All have:

```text
near_distance = 2
role_transport_allowed = False
classification_primary = near_decoy_distance_2
```

---

## 13. Red-Team Boundaries

Reviewers should not evaluate whether QSB is true as a physical theory.

Reviewers should not assume that:

```text
near candidate = physical structure
role-colored signature = emergent geometry
rare patch = spacetime
```

Reviewers should evaluate only:

```text
methodological consistency
classification logic
role-transport defensibility
clarity of claim boundaries
adequacy of next controls
```

---

## 14. Current Allowed Statement

A currently allowed statement is:

```text
BMS-FU02g5e2 classifies the 11 scaffold-localized near-match candidates from
BMS-FU02g5e1. Only the known exact FU02g4c mirror candidate is face-type-
preserving isomorphic to the FU02f1 reference and therefore eligible for
automorphy-only role transport under the FU02g5c rule. The other 10 near
candidates are non-isomorphic decoys without reference-role transport. This is
a scaffold-localization classification and does not certify FU02g4c raw-order
replay.
```

---

## 15. Current Disallowed Statements

Do not say:

```text
QSB proves physical emergence.
QSB proves spacetime emergence.
QSB proves global uniqueness.
QSB proves global rarity.
FU02g5e2 certifies FU02g4c replay order.
The 10 decoys are physically irrelevant.
The 10 decoys are globally irrelevant.
The exact mirror candidate is an independent second carrier.
Non-isomorphic patches may receive reference roles by analogy.
```

---

## 16. Proposed Next Controls

Recommended next controls:

```text
1. FU02g5e3 — Result Note / Red-Team Synthesis
2. FU02g5f — FU02g4c Raw-Order Replay Certification for g5e1/g5e2 Candidates
3. FU03a — External Fullerene / Planar / Spherical Graph Controls
4. Optional: Local Structural Role Rule Study as explicitly separate future work
```

Do not proceed to stronger physical claims before these controls are addressed.

---

## 17. Internal Summary

```text
Zehn Steine glitzern ähnlich.
Einer ist der Spiegelklunker.
Nur dieser bekommt das Referenzetikett vom Spiegel zurück.
```

This metaphor is useful internally but should be replaced by technical wording in external-facing material.
