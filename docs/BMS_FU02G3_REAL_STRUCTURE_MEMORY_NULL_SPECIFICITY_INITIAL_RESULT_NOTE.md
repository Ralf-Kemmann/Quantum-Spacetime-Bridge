# BMS-FU02g3 — Real-Structure Memory Null Specificity Initial Result Note

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G3_REAL_STRUCTURE_MEMORY_NULL_SPECIFICITY_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU02g3

---

## 1. Purpose

BMS-FU02g3 tests whether the FU02f1 C60 role-colored carrier region is cheap or
rare under selected same-C60 face-graph null patch families.

FU02g2 showed:

```text
The generic cell-level proxy finds compact connected interior patches in all
geometry-class controls.
```

FU02g3 therefore sharpened the question:

```text
Is the actual FU02f1 C60 carrier region, with its role color, cheap under nulls?
```

Internal formulation:

```text
Ist der richtige C60-Klunker mit Rollenfarbe billig?
```

---

## 2. Reference region

The FU02f1 reference sets were loaded successfully.

### 2.1 Mixed core

```text
mixed_core_set =
  H_09
  H_11
  H_13
  H_16
  H_17
  H_18
  H_19
  H_20
```

Count:

```text
mixed_core_count = 8
```

### 2.2 Pentagon-boundary / boundary role set

```text
pentagon_boundary_set =
  H_07
  H_12
  H_14
  H_15
  P_07
  P_08
  P_09
  P_10
  P_11
```

Count:

```text
pentagon_boundary_count = 9
```

### 2.3 Full reference carrier set

```text
carrier_face_count = 17
```

Internal image:

```text
8-face Hexagon-Mixed-Core
plus
9-face boundary role layer with 5 pentagons and 4 hexagons.
```

---

## 3. Generic FU02g2 proxy overlap

FU02g3 confirms the FU02g2 limitation:

```text
GENERIC PROXY OVERLAP

c60_reference
carrier_count = 10
overlap = 2
overlap_frac = 0.11764705882352941
mixed_overlap = 1
pent_boundary_overlap = 1
```

Interpretation:

```text
The generic FU02g2 proxy does not reconstruct the FU02f1 reference region.
It overlaps only 2 of 17 reference carrier faces.
```

This is even sharper than the earlier FU02g2 readout phrasing because the
denominator here is the full 17-face FU02f1 reference carrier set.

Allowed statement:

```text
The FU02g2 generic interior proxy has low overlap with the FU02f1 C60 carrier
reference and should not be used as a C60 memory-recovery diagnostic.
```

---

## 4. Null family summaries

### 4.1 carrier_count_random_patch

```text
near = 17 / 1000
near_frac = 0.017
strict = 0 / 1000
strict_frac = 0.0
median_overlap = 0.5294117647058824
max_overlap = 0.8235294117647058
min_role_dev = 0.0
median_role_dev = 2.0
median_compact = 1.0
label = near_reference_profiles_rare
```

Interpretation:

```text
Under random same-size carrier patches, near-reference profiles are rare.
Strict near-reference profiles are absent.
```

This supports that the FU02f1 reference profile is not reproduced cheaply by
unstructured carrier-count matching.

---

### 4.2 type_count_preserving_patch

```text
near = 35 / 1000
near_frac = 0.035
strict = 0 / 1000
strict_frac = 0.0
median_overlap = 0.5294117647058824
max_overlap = 0.7647058823529411
min_role_dev = 0.0
median_role_dev = 0.0
median_compact = 1.0
label = near_reference_profiles_rare
```

Interpretation:

```text
Even when hexagon/pentagon counts are preserved, near-reference profiles remain
rare and strict near-reference profiles are absent.
```

This is a stronger result than carrier-count matching alone because the null
already preserves type composition.

Important nuance:

```text
median_role_dev = 0.0
```

means type/role-count matching alone is easy in this null by construction, but
spatial/reference overlap remains limited.

---

### 4.3 connected_patch_seeded

```text
near = 90 / 1000
near_frac = 0.09
strict = 0 / 1000
strict_frac = 0.0
median_overlap = 0.5294117647058824
max_overlap = 0.8823529411764706
min_role_dev = 0.0
median_role_dev = 2.0
median_compact = 1.0
label = near_reference_profiles_reproduced
```

Interpretation:

```text
When connectedness is explicitly preserved, near-reference profiles are
reproduced at a non-negligible rate.
```

Strict profiles remain absent, but the near-reference threshold is no longer
rare enough to support a hard specificity statement.

This means:

```text
Connected compact same-size patches on the C60 face graph can partially mimic
the FU02f1 reference region.
```

---

### 4.4 role_count_preserving_connected_patch

```text
near = 95 / 1000
near_frac = 0.095
strict = 1 / 1000
strict_frac = 0.001
median_overlap = 0.5294117647058824
max_overlap = 0.8823529411764706
min_role_dev = 0.0
median_role_dev = 2.0
median_compact = 1.0
label = near_reference_profiles_reproduced
```

Interpretation:

```text
The strongest v0 decoy can reproduce near-reference profiles at about 9.5%.
Strict profiles are extremely rare but not absent.
```

This is the key limiting result.

It says:

```text
The FU02f1 region is not cheap under simple random/type nulls,
but it is partially reproducible under connected/role-aware decoys.
```

---

## 5. Main result

BMS-FU02g3 gives a mixed but useful result.

### 5.1 Positive side

```text
Simple unstructured nulls rarely reproduce the FU02f1 reference profile.

carrier_count_random_patch:
  near_reference_fraction = 0.017

type_count_preserving_patch:
  near_reference_fraction = 0.035
```

This supports a weak-to-moderate construction-qualified specificity indication
against simple nulls.

### 5.2 Limiting side

```text
Connected and role-aware nulls reproduce near-reference profiles more often.

connected_patch_seeded:
  near_reference_fraction = 0.09

role_count_preserving_connected_patch:
  near_reference_fraction = 0.095
```

This prevents a strong specificity claim at FU02g3-v0 level.

### 5.3 Strict criterion

```text
strict near-reference profiles:

carrier_count_random_patch:
  0 / 1000

type_count_preserving_patch:
  0 / 1000

connected_patch_seeded:
  0 / 1000

role_count_preserving_connected_patch:
  1 / 1000
```

Strict reproduction is absent or nearly absent.

This is meaningful, but it should be interpreted cautiously because strict
thresholds are construction-dependent.

---

## 6. Befund / Interpretation / Hypothesis / Open Gap

### Befund

```text
The FU02f1 C60 carrier reference is rarely reproduced by simple same-size or
type-preserving random patches, but near-reference profiles are reproduced at
about 9-10% by connected and role-aware connected decoys.
```

### Interpretation

```text
The FU02f1 profile is not merely a random same-size or type-count artifact.
However, compact connected C60 face-graph patches already carry enough
structure to partially mimic the reference profile.
```

### Hypothesis

```text
The relevant specificity may not lie in compactness alone or in role counts
alone, but in symmetry/orbit relation, exact role placement, and possibly
higher-order patch structure.
```

### Open gap

```text
FU02g3-v0 does not yet determine whether the FU02f1 region is a representative
of a nontrivial C60 automorphism orbit class or a patch type common among
connected same-size C60 face subgraphs.
```

---

## 7. Claim boundary

Allowed:

```text
FU02g3-v0 supports a construction-qualified weak-to-moderate specificity
indication against simple same-size and type-preserving C60 face-patch nulls.
```

Allowed:

```text
The result does not support a strong specificity claim against connected and
role-aware connected decoys, because near-reference profiles are reproduced at
about 9-10%.
```

Allowed:

```text
Strict near-reference reproduction is absent or nearly absent across the tested
null families.
```

Not allowed:

```text
FU02g3 proves real-structure memory.
FU02g3 proves C60 symmetry recovery.
FU02g3 proves physical spacetime.
FU02g3 proves that the reference profile is impossible under nulls.
FU02g3 provides a universal p-value.
```

---

## 8. Methodological consequence

FU02g3 tells us the next sharpening direction.

Not enough:

```text
same size
same type count
connectedness
role count
```

Need next:

```text
symmetry-orbit inspection
canonical patch signatures
exact role-placement comparison
automorphism-equivalent copy count
stabilizer / orbit size
```

Internal formulation:

```text
Die Attrappen können grob die Rollenfarbe treffen,
wenn man ihnen Verbundenheit und Rollenanzahl schenkt.

Jetzt müssen wir fragen:
Ist unser Klunker nur irgendein verbundener Patch,
oder eine besondere Orbit-/Symmetrieklasse?
```

---

## 9. Recommended next block

Proceed to:

```text
BMS-FU02g4 — Symmetry-Orbit Inspection of the C60 Reference Carrier Region
```

Purpose:

```text
Determine whether the FU02f1 reference carrier region is:
  unique,
  one representative of a symmetry-equivalent orbit class,
  or common among connected same-size C60 face patches.
```

Candidate readouts:

```text
carrier_region_canonical_signature
automorphism_orbit_size
stabilizer_size
equivalent_patch_count
inversion_partner_overlap
role_colored_orbit_signature
exact_role_colored_match_count
```

If full automorphism machinery is too heavy, a fallback FU02g3b can be used:

```text
BMS-FU02g3b — Exact Patch Signature and Stronger Connected Decoy Test
```

with:

```text
exact carrier set overlap
exact role-colored overlap
edge boundary profile
internal adjacency profile
cell-type boundary sequence
shell distribution from mixed core
```

---

## 10. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02G3_REAL_STRUCTURE_MEMORY_NULL_SPECIFICITY_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU02G3_REAL_STRUCTURE_MEMORY_NULL_SPECIFICITY_INITIAL_RESULT_NOTE.md

git status --short
```

Commit:

```bash
git add docs/BMS_FU02G3_REAL_STRUCTURE_MEMORY_NULL_SPECIFICITY_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02g3 null specificity result note"

git push
```

---

## 11. Internal summary

```text
FU02g3:

  Simple nulls:
    near rare
    strict absent

  Connected / role-aware nulls:
    near reproduced around 9-10%
    strict almost absent

Conclusion:
  Kein harter Sieg.
  Aber auch kein Kollaps.

  Der richtige Klunker mit Rollenfarbe ist nicht völlig billig,
  aber Verbundenheit + Rollenanzahl erklären schon einiges.

Next:
  Symmetrie-Orbit / Patch-Signatur.
```
