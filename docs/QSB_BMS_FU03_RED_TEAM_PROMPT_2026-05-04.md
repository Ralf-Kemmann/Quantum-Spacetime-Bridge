# Red-Team Prompt — QSB / BMS-FU02g4c → FU03 External Controls

## Context

We are working on a cautious theoretical-physics research program called **Quantum–Spacetime Bridge (QSB)** / **Gravitation und RaumZeit**.

The central working idea is not that spacetime is already given as a fixed stage. Instead, the project explores whether **de-Broglie-like matter-wave relations** can give rise to **relational correlation structure**, from which stable, transformation-aware patterns may become **geometrically readable**.

A compact internal summary is:

```text
Welle → Beziehung → Rolle → Geometrie
```

Or in more explanatory language:

```text
de-Broglie-like matter waves
→ relational correlations
→ stable carrier patches
→ role-colored internal structure
→ symmetry/orbit-aware structural classes
→ geometrically readable order
```

This is **not** claimed as a completed theory of gravity, cosmology, or spacetime emergence. It is currently a methodological and structural hypothesis being tested with graph-based controls.

## Current Numerical Toy Framework

The current hard-test branch is called:

```text
BMS-FU02g4c — Orbit-Reduced / Resumable Connected Patch Enumeration
```

The test object is a **C60 fullerene face graph**. A previously identified FU02f1 carrier region is treated as a local relational patch. We test whether this patch is merely a generic connected patch or whether its **role-colored signature** is unusually constrained under connected-patch, null-model, and automorphism/orbit controls.

Reference carrier sets:

```text
carrier_set =
H_07;H_09;H_11;H_12;H_13;H_14;H_15;H_16;H_17;H_18;H_19;H_20;P_07;P_08;P_09;P_10;P_11

mixed_core_set =
H_09;H_11;H_13;H_16;H_17;H_18;H_19;H_20

pentagon_boundary_set =
H_07;H_12;H_14;H_15;P_07;P_08;P_09;P_10;P_11
```

Reference carrier summary:

```text
carrier_face_count = 17
carrier_hexagon_count = 12
carrier_pentagon_count = 5
carrier_component_count = 1
largest_carrier_component_count = 17
```

Role mapping:

```text
mixed_core = mixed_seam_boundary_face
pentagon_boundary = hp_boundary_face
```

Informal internal picture:

```text
The uncolored carrier is the patch / carrier region.
The role-colored signature is the internal role information.
The patch is the surface.
The role-color is the message.
```

## Known Results Before FU02g4c

### FU02g3 Null Specificity

Observed counts:

```text
carrier_count_random_patch:
  near = 17/1000
  strict = 0/1000

type_count_preserving_patch:
  near = 35/1000
  strict = 0/1000

connected_patch_seeded:
  near = 90/1000
  strict = 0/1000

role_count_preserving_connected_patch:
  near = 95/1000
  strict = 1/1000
```

Interpretation:

```text
Simple nulls rarely reproduce the reference.
Connected/role-aware nulls reproduce coarse near-reference more often.
Strict reproduction is absent or nearly absent.
```

Claim boundary:

```text
weak-to-moderate construction-qualified specificity against simple nulls,
not strong specificity against connected/role-aware decoys.
```

### FU02g4 Symmetry-Orbit Inspection

Automorphism/orbit results:

```json
{
  "automorphism_count_observed": 120,
  "carrier_orbit_size_observed": 120,
  "carrier_stabilizer_size_observed": 1,
  "role_colored_orbit_size_observed": 120,
  "role_colored_stabilizer_size_observed": 1,
  "node_match_preserves_cell_type": true,
  "status": "complete"
}
```

Sampled connected patch results:

```text
sample_count = 5000
carrier_signature_match_count = 1
near_carrier_signature_count = 10
role_colored_signature_match_count = 0
near_role_colored_signature_count = 0
```

Interpretation:

```text
The concrete location is not sacred.
The orbit/structure class is the relevant object.
```

Claim boundary:

```text
not a unique physical location
not exhaustive
not proof of real-structure memory
```

### FU02g4b Bounded Enumeration Attempt

Important correction:

```text
An initial runner emitted zero patches and falsely reported complete.
That run is discarded.
```

Valid patched bounded run:

```json
{
  "enumerated_connected_patch_count": 3682435,
  "enumeration_status": "partial_timeout_reached",
  "reference_is_connected": true,
  "target_patch_size": 17,
  "warnings_count": 0
}
```

Summary:

```text
carrier_signature_exact_match_count = 20
carrier_signature_exact_match_fraction ≈ 5.43e-6

carrier_signature_near_match_count = 127
carrier_signature_near_match_fraction ≈ 3.45e-5

role_colored_signature_exact_match_count = 0
role_colored_signature_exact_match_fraction = 0.0

role_colored_signature_near_match_count = 3
role_colored_signature_near_match_fraction ≈ 8.15e-7
```

Interpretation:

```text
The uncolored patch signature is rare but not unique.
The exact role-colored signature was not reproduced in 3.68M bounded patches.
Near role-colored matches exist but are extremely rare.
```

Claim boundary:

```text
bounded enumeration evidence, not exhaustive absence.
```

## FU02g4c Current Purpose

FU02g4c turns the long bounded run into a resumable chunked enumeration with optional orbit-canonical class counting under the 120 C60 automorphisms.

Important validity requirements for any chunk:

```text
warnings_count = 0
orbit_reduction_enabled_actual = true
automorphism_count_used = 120
reference_is_connected = true
```

A chunk with `partial_chunk_limit_reached` or `partial_timeout_reached` is valid only as a partial/chunk result. Exhaustive claims require complete contiguous coverage and a dedicated aggregation pass.

## Early FU02g4c Results

### Chunk 0

```text
chunk_id = chunk_0000000_0999999
raw_connected_patch_count_processed = 1,000,000
unique_orbit_patch_count_processed = 231,683
warnings_count = 0
orbit_reduction_enabled_actual = true
automorphism_count_used = 120

raw_carrier_exact = 12
raw_carrier_near = 78

raw_role_colored_exact = 0
raw_role_colored_near = 0

orbit_carrier_exact_classes = 1
orbit_carrier_near_classes = 9

orbit_role_colored_exact_classes = 0
orbit_role_colored_near_classes = 0
```

### Chunk 1

```text
chunk_id = chunk_1000000_1999999
raw_connected_patch_count_processed = 1,000,000
unique_orbit_patch_count_processed = 589,796
warnings_count = 0
orbit_reduction_enabled_actual = true
automorphism_count_used = 120

raw_carrier_exact = 2
raw_carrier_near = 17

raw_role_colored_exact = 0
raw_role_colored_near = 0

orbit_carrier_exact_classes = 1
orbit_carrier_near_classes = 8

orbit_role_colored_exact_classes = 0
orbit_role_colored_near_classes = 0
```

### Chunk 2

```text
chunk_id = chunk_2000000_2999999
raw_connected_patch_count_processed = 1,000,000
unique_orbit_patch_count_processed = 526,162
warnings_count = 0
orbit_reduction_enabled_actual = true
automorphism_count_used = 120

raw_carrier_exact = 6
raw_carrier_near = 26

raw_role_colored_exact = 0
raw_role_colored_near = 3

orbit_carrier_exact_classes = 1
orbit_carrier_near_classes = 8

orbit_role_colored_exact_classes = 0
orbit_role_colored_near_classes = 0
```

Cumulative raw count for chunks 0–2:

```text
raw connected patches processed = 3,000,000

raw carrier exact = 20
raw carrier near  = 121

raw role-colored exact = 0
raw role-colored near  = 3
```

Important: orbit-class counts must not be naively added across chunks, because the same canonical class may appear in multiple chunks.

## Current Script / Coverage Note

A V2 batch script correctly merged manifest and summary JSON, but it advanced by the nominal chunk size even when `enumeration_status = partial_timeout_reached`. This creates coverage gaps once a timeout occurs.

A V3 gap-safe script fixes this by setting:

```text
NEXT_SKIP = raw_patch_count_seen_including_skipped - 1
```

Therefore:

```text
Early chunks with full 1,000,000 processed chunks are usable as contiguous coverage.
Later V2 timeout logs are valid as late-window samples but not as lückenlos / contiguous coverage.
V3 gap-safe logs are the primary continuation for contiguous coverage after the first timeout.
```

## Deep Research Result: Candidate External Control Families

A recent Deep Research pass identified several useful external datasets / generator families:

1. `buckygen`
   - exhaustive fullerene generator
   - can emit planar code and dual graphs
   - suitable for all C60 fullerene isomers and C70/C80 extensions
   - key for testing whether the FU02f1 role-colored signature is specific to the chosen C60 structure or appears across fullerene isomer space

2. `plantri/fullgen`
   - exhaustive planary/cubic/fullerenic graph generator family
   - useful for planarity, cubicity, and spherical-topology controls
   - embedding-aware outputs are important for face/dual construction

3. `Program FULLERENE`
   - topology + coordinates + symmetry + Goldberg-Coxeter-related tests
   - useful for topology-to-geometry and mode-related follow-up tests
   - license is more restrictive than fully permissive datasets

4. Zenodo C20–C80 fullerene library
   - XYZ structures, xTB-optimized, CC BY 4.0
   - useful for geometry-aware fullerene tests after graph reconstruction

5. CaGe / NanoCap
   - useful for boundary-matched caps, nanotube caps, nanocones
   - can test whether local role signatures arise from boundary/defect constraints rather than closed C60 cage organization

6. QM9S / Hessian QM9 / PCQM4Mv2 / PubChemQC
   - negative chemical controls
   - ring-rich but non-spherical molecular families
   - useful to test whether the signature is merely generic chemoinformatic motif structure rather than fullerene/spherical topology

Proposed next block:

```text
BMS-FU03 — External Fullerene and Planar Control Families
```

Minimal first scope:

```text
BMS-FU03a:
  install/verify buckygen or obtain generated C60 fullerene list
  generate all C60 fullerene dual graphs
  compute basic graph metadata:
    node_count
    edge_count
    automorphism_count
    face/dual validity
    orbit partitions
  run first carrier-signature scan without role assignment

BMS-FU03b:
  role-colored signature transfer test across all C60 fullerene isomers
```

## What We Want From You, the Red Team

Please critique this project branch as harshly and constructively as possible.

We are not asking you to confirm the hypothesis. We want failure modes, hidden assumptions, weak controls, and better tests.

Please organize your answer into the following sections.

### 1. One-Paragraph Steelman

First, state the strongest defensible version of the current claim. Do not hype it. Give the best cautious formulation.

### 2. Immediate Red Flags

List the strongest reasons why the current result may be misleading, including but not limited to:

- C60-specific artifact
- face graph / dual graph artifact
- role-assignment artifact
- patch-size artifact
- connected-patch enumeration bias
- ordering / generator bias
- automorphism/orbit-counting error
- near-match definition too permissive or too narrow
- multiple-testing / cherry-picking risk
- mismatch between toy graph evidence and physical spacetime claims

### 3. Validity of the FU02g4c Evidence

Evaluate whether the following cautious statement is justified:

```text
In the first three valid FU02g4c chunks, the uncolored carrier signature occurs rarely but reproducibly, while no exact role-colored signature is observed; role-colored near cases are extremely rare at raw level and absent in orbit-canonical counts for these chunks. This supports a bounded, construction-qualified indication that role-colored structure is more constrained than the uncolored carrier footprint.
```

Please say:

- what is justified
- what is overstated
- what is missing
- what would make it stronger
- what wording should be changed

### 4. Coverage and Enumeration Risks

Critique the chunked enumeration approach.

Important known issue:

```text
V2 advanced by nominal million-chunk boundaries after partial_timeout_reached and therefore produced non-contiguous late-window samples.
V3 fixes this with NEXT_SKIP = raw_patch_count_seen_including_skipped - 1.
```

Questions:

- Is this fix logically sufficient?
- What coverage audit should be performed?
- How should V2 timeout logs be treated?
- How can we prove that no gaps or overlaps exist in the final primary contiguous set?
- What metadata should every chunk/segment store?

### 5. Role-Assignment Sensitivity

The current role-colored signature depends on:

```text
type_preferred_role_assignment
```

Please critique this.

Questions:

- Could the role-colored signal be an artifact of this assignment rule?
- What alternative role-assignment rules should be tested?
- Should the role assignment be learned, derived, randomized, or fixed a priori?
- What null models would directly attack the role-coloring step?

### 6. Orbit and Symmetry Controls

Current C60 automorphism count is 120, and the role-colored orbit size is also observed as 120 with stabilizer size 1.

Questions:

- What can and cannot be inferred from this?
- Is orbit-canonical counting the right reduction?
- Are there alternative group actions or equivalence classes that should be used?
- How should orbit-class counts be aggregated across chunks without double-counting?

### 7. External Control Roadmap

Critique the proposed BMS-FU03 roadmap.

Candidate controls:

```text
buckygen
plantri/fullgen
Program FULLERENE
Zenodo C20–C80 fullerene library
CaGe / NanoCap
QM9S / Hessian QM9 / PCQM4Mv2 / PubChemQC
```

Questions:

- Which control family should come first?
- Which one is most adversarial?
- Which one is most likely to expose a false positive?
- Which one is overkill or premature?
- What would be the minimal decisive external test?
- How should we compare across C60 isomers, C70/C80, planar non-fullerenes, caps/tubes, and ring-rich molecules?

### 8. Physical Interpretation Boundary

Please be very strict here.

We currently use the conceptual bridge:

```text
de-Broglie-like matter waves
→ relational correlations
→ stable carrier patches
→ role-colored structure
→ symmetry/orbit-aware structural class
→ geometrically readable order
```

Questions:

- Which parts are legitimate as mathematical/metaphorical framing?
- Which parts risk overclaiming physics?
- What would be needed to connect this toy graph evidence to actual physical wave mechanics, modes, metrics, curvature, or spacetime?
- Is the “early universe / pre-geometric relationship soup” analogy useful, dangerous, or both?
- How should the public-facing language be constrained?

### 9. Better Tests

Propose concrete next tests.

Please include:

- one minimal sanity test
- one strong adversarial null test
- one role-assignment sensitivity test
- one external fullerene-isomer test
- one non-fullerene planar control
- one chemistry negative control
- one spectral / vibrational bridge test
- one aggregation / coverage audit test

For each test, specify:

```text
Purpose
Input data
Method
Expected failure mode
What outcome would strengthen the claim
What outcome would weaken the claim
```

### 10. Recommended Claim Language

Please rewrite the current claim in three versions:

1. Internal working-language version
2. Defensive scientific manuscript version
3. Neighbor-friendly public explanation

The current candidate claim is:

```text
The current FU02/FU02g results provide bounded, construction-qualified evidence that the FU02f1 carrier region is not merely a generic connected patch. While uncolored carrier signatures occur rarely but reproducibly, the role-colored signature is more strongly constrained under the tested connected-patch and automorphism/orbit controls. This supports the working hypothesis that diagnostically relevant relational information may reside in role-bearing internal structure, not only in local carrier membership.
```

Please improve or weaken this statement as needed.

### 11. Final Verdict

End with a clear verdict:

```text
Continue / pause / redesign
```

And give the top three reasons.

## Constraints for Your Response

Please be critical and specific.

Please avoid generic encouragement.

Please do not assume the hypothesis is true.

Please distinguish:

```text
observed result
interpretation
hypothesis
open gap
overclaim
```

Please mark any place where additional data or code inspection would be needed before judgment.

Please suggest concrete modifications that can be implemented in the repository.
