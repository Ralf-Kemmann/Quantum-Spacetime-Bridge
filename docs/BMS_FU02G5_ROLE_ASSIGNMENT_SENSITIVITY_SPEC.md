# BMS-FU02g5 — Role-Assignment Sensitivity Controls

**Date:** 2026-05-06  
**Project:** Quantum–Spacetime Bridge / Gravitation und RaumZeit  
**Status:** Specification scaffold for next controlled run  
**Previous block:** BMS-FU02g4c/FU02g4d automorphic exact-match localization  
**Claim level:** combinatorial / methodological control only

---

## 1. Purpose

BMS-FU02g5 tests whether the FU02g4c/g4d role-colored exact/near-match findings are stable under controlled variants of the role-assignment rule.

The previous completed block established, within the primary-audited connected-patch enumeration, that the only observed raw role-colored exact match up to coverage `0 → 26,784,196` was localized, photographed, and identified as automorphic to the FU02f1 reference carrier.

FU02g5 asks the next narrower question:

> Does the role-colored rarity/localization signal depend strongly on the current v0 role assignment, or does a comparable signal survive under alternative, explicitly defined role-labeling conventions?

This is a sensitivity-control block, not a physical emergence claim.

---

## 2. Claim Boundary

### Allowed claim after FU02g5, if supported

```text
Within the tested C60 face-graph control space, the role-colored signature behavior is / is not stable under the specified role-assignment variants.
```

### Not allowed

```text
FU02g5 proves physical emergence.
FU02g5 proves a dynamical mechanism.
FU02g5 proves uniqueness outside all graph families.
FU02g5 proves the carrier is physically necessary.
```

### Safe language

Use:

- role-assignment dependent,
- robust within tested variants,
- fragile under tested variants,
- combinatorial sensitivity,
- C60 face-graph control space,
- no dynamical claim.

Avoid:

- discovery,
- proof,
- emergence shown,
- universal uniqueness,
- physically demonstrated mechanism.

---

## 3. Background Anchor

FU02g4c/g4d current anchor:

```text
exact match found
exact match localized
exact match photographed
exact match automorphic to reference
```

Reference FU02f1 carrier:

```text
H_07;H_09;H_11;H_12;H_13;H_14;H_15;H_16;H_17;H_18;H_19;H_20;P_07;P_08;P_09;P_10;P_11
```

Reference mixed_core:

```text
H_09;H_11;H_13;H_16;H_17;H_18;H_19;H_20
```

Reference pentagon_boundary:

```text
H_07;H_12;H_14;H_15;P_07;P_08;P_09;P_10;P_11
```

Localized automorphic candidate:

```text
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Candidate mixed_core:

```text
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09
```

Candidate pentagon_boundary:

```text
H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

---

## 4. Test Idea

The previous result used a role-colored signature. FU02g5 varies how roles are assigned and re-evaluates exact/near signature behavior.

The central diagnostic is not only whether an exact match exists, but how counts and localization change across role rules.

A useful internal picture:

```text
Same C60 face-graph.
Same 17-face connected patches.
Different colored stickers on the same graph objects.
Question: Does the Klunker survive sticker changes, or was he mostly a sticker artifact?
```

---

## 5. Required Input Classes

### 5.1 Graph input

The runner requires a C60 face graph:

```text
node = C60 face label, e.g. H_07 or P_03
edge = shared boundary between two faces
```

Supported input form:

```text
CSV edge list with two columns:
source,target
```

The script accepts the first two columns as endpoints if explicit `source,target` columns are absent.

### 5.2 Reference role sets

The config provides:

- `reference_carrier_nodes`
- `reference_mixed_core_nodes`
- `reference_pentagon_boundary_nodes`

### 5.3 Candidate/localized exact patch

The config provides:

- `localized_exact_patch_nodes`
- `localized_exact_patch_mixed_core_nodes`
- `localized_exact_patch_pentagon_boundary_nodes`

This permits a focused automorphic candidate sensitivity readout even when full enumeration is not run.

### 5.4 Enumeration control

For full or windowed enumeration:

- `patch_size`
- `skip_first_connected_patches`
- `max_connected_patches_this_run`
- `max_wall_seconds`
- `progress_every`

The default config is conservative and suitable for a smoke test. Large primary-scale enumeration should be chunked.

---

## 6. Role Assignment Variants

Initial FU02g5 variants:

### Variant A — `v0_type_preferred`

The current baseline role assignment.

```text
mixed_core        -> mixed_seam_boundary_face
pentagon_boundary -> hp_boundary_face
other carrier     -> carrier_other
outside carrier   -> outside
```

Purpose: reproduce the current role-colored reference signature rule.

### Variant B — `uncolored_carrier_only`

All carrier nodes receive one common carrier role.

```text
carrier -> carrier
outside -> outside
```

Purpose: separate pure carrier-shape effects from internal role coloring.

### Variant C — `face_type_only`

Roles are assigned only from face labels:

```text
H_* -> hexagon_face
P_* -> pentagon_face
```

Purpose: test whether the effect is already mostly driven by hexagon/pentagon composition.

### Variant D — `swap_core_boundary`

The two internal role sets are intentionally swapped.

```text
mixed_core        -> hp_boundary_face
pentagon_boundary -> mixed_seam_boundary_face
```

Purpose: negative-control style perturbation.

### Variant E — `core_erased`

The mixed-core role is erased into generic carrier.

```text
mixed_core        -> carrier_other
pentagon_boundary -> hp_boundary_face
```

Purpose: test dependence on the mixed-core label.

### Variant F — `boundary_erased`

The pentagon-boundary role is erased into generic carrier.

```text
mixed_core        -> mixed_seam_boundary_face
pentagon_boundary -> carrier_other
```

Purpose: test dependence on the boundary label.

### Variant G — `random_role_permutation_seeded`

Optional seeded random permutation of role labels among carrier nodes while preserving role counts.

Purpose: stochastic sensitivity control.

This should be reported separately and never mixed with deterministic variants.

---

## 7. Signature Design

The provided runner uses transparent NetworkX-based signatures.

### 7.1 Graph structure signature

A canonical hash of the induced 17-node patch graph.

Preferred implementation:

```text
networkx.weisfeiler_lehman_graph_hash
```

If NetworkX lacks this function, the script falls back to a deterministic coarse signature:

```text
node_count
edge_count
degree sequence
role-degree histogram
```

### 7.2 Role-colored signature

The induced patch graph is labeled with the variant-specific role assignment. Exact match means identical role-colored graph hash against the reference patch under the same assignment rule.

### 7.3 Near signature

The default near diagnostic is deliberately conservative and transparent:

```text
near_distance = Hamming-like distance between sorted role-degree histograms
near if near_distance <= near_distance_threshold
```

This near metric is a sensitivity diagnostic only. It is not automatically identical to the FU02g4c near-match rule unless the same near rule is explicitly configured.

---

## 8. Run Design

### 8.1 Smoke test

Run only the reference carrier and localized automorphic patch under all role variants.

Expected purpose:

- verify config,
- verify graph input,
- verify reference and candidate sets,
- inspect whether the localized automorphic candidate stays exact across role rules.

### 8.2 Windowed enumeration

Run selected windows of connected 17-patches.

Purpose:

- check whether exact/near counts shift strongly across role variants,
- avoid uncontrolled primary-scale runtime.

### 8.3 Primary-scale rerun, if justified

Only after smoke/windowed tests are clean:

- chunked enumeration,
- audit logs,
- no naive global summation of orbit-class counts,
- explicit primary interval accounting.

FU02g5 does not require orbit reduction in the first scaffold runner, but the output fields reserve columns for orbit information if a later optimized runner adds it.

---

## 9. Outputs

Default output directory:

```text
runs/BMS-FU02g5/role_assignment_sensitivity/
```

Runner writes:

```text
summary.json
variant_summary.csv
candidate_pair_summary.csv
result_note.md
config_resolved.yaml
```

### 9.1 `variant_summary.csv`

One row per role-assignment variant.

Core fields:

- `variant_id`
- `variant_description`
- `reference_role_colored_signature`
- `localized_candidate_role_colored_signature`
- `localized_candidate_exact_match`
- `localized_candidate_near_distance`
- `localized_candidate_near_match`
- `enumerated_patch_count`
- `enumerated_exact_match_count`
- `enumerated_near_match_count`
- `warnings_count`

### 9.2 `summary.json`

Machine-readable run summary including:

- config,
- timestamps,
- graph stats,
- reference stats,
- localized candidate stats,
- per-variant results,
- warnings.

### 9.3 `result_note.md`

Human-readable result note with required sections:

```text
Befund
Interpretation
Hypothese
Offene Lücke
Claim Boundary
Next Step
```

---

## 10. Defensive Result-Note Template

### Befund

State only what was counted or observed.

Example:

```text
Under the tested role-assignment variants, the localized FU02g4c exact patch remained exact for variants X and Y, but not for variants Z.
```

### Interpretation

Explain what the pattern suggests inside the tested scope.

Example:

```text
This suggests that the exact role-colored match is sensitive to the mixed_core / boundary distinction.
```

### Hypothese

Mark anything speculative.

Example:

```text
A plausible working hypothesis is that the role-colored rarity is partly carried by the mixed-core labeling convention rather than by uncolored patch topology alone.
```

### Offene Lücke

Always include:

```text
External graph-family controls are still open.
Near-match decoys remain to be inspected separately.
No physical dynamics is inferred from this control.
```

### Claim Boundary

Use:

```text
FU02g5 tests sensitivity of a combinatorial signature to role-assignment rules in the C60 face-graph control space.
```

---

## 11. Acceptance Criteria

FU02g5 scaffold is considered technically acceptable if:

1. The runner reads the config and graph input.
2. The reference and localized exact patch are validated as 17-node connected patches.
3. All configured role variants are applied deterministically, except explicitly seeded random variants.
4. Per-variant exact/near diagnostics are written to CSV and JSON.
5. The result note separates Befund, Interpretation, Hypothese, Offene Lücke, and Claim Boundary.
6. The script exits with clear errors if required graph/config inputs are missing.
7. No physical emergence or dynamical claim is emitted.

---

## 12. Immediate Terminal Command

After copying the generated files into the repo root, run:

```bash
cd /home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

python scripts/run_bms_fu02g5_role_assignment_sensitivity.py \
  --config data/bms_fu02g5_role_assignment_sensitivity_config.yaml
```

If the graph edge-list path in the config is not present locally, edit only:

```yaml
input:
  full_face_graph_edges_csv: ...
```

and rerun.
