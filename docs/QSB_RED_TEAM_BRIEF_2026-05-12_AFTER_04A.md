# QSB Red-Team Brief — After QSB-BRIDGE-NUM-04A

Date: 2026-05-12  
Project: Quantum–Spacetime Bridge / Gravitation und RaumZeit  
Current local/repo anchor after 04A: `273513a Add QSB bridge phase-sensitive toy diagnostic`

---

## 1. Role for the Red Team

You are asked to act as a critical but constructive scientific red team for the QSB project.

Your task is **not** to endorse the project and **not** to decide whether QSB is a completed physical theory. Treat the project as a methodological research framework investigating whether wave-based relational input structures can support geometrically readable organization under controlled graph/geometry/phase diagnostics.

Please look for weaknesses, overclaims, missing controls, ambiguous terminology, hidden assumptions, and opportunities for stronger tests.

Use a skeptical, method-focused standard. Prefer precise objections over broad dismissal.

---

## 2. Current Project Status Relevant for This Review

The project has recently introduced a bridge-physics framing:

- Wave-based / de-Broglie-like relational input intuition.
- Magnitude-based relational distance-like constructions.
- Phase-sensitive or interference-like diagnostics kept conceptually separate from magnitude-only geometry proxies.
- Candidate stable relational structures such as cores, carrier patches, backbone envelopes, and geometry-readable graph structures.
- Strong internal claim boundary: current results are methodological diagnostics and numerical consistency checks, not physical proof of spacetime emergence.

Recent committed block:

`QSB-BRIDGE-NUM-04A Phase-Sensitive Toy Diagnostic`

Purpose of 04A:

- Construct a deterministic toy example where all phase variants share the same magnitude matrix `|K_ij|`.
- Define distance-like diagnostics from magnitude only.
- Vary only phase patterns `phi_ij`.
- Check that magnitude-only distance/graph diagnostics remain invariant.
- Check that phase-sensitive toy diagnostics change across phase variants.
- Preserve a strict toy-level claim boundary.

Main 04A reported result:

```text
magnitude_invariance_passed: True
all_hermitian_checks_passed: True
phase_sensitive_diagnostics_changed: True
max_distance_diff_across_phase_variants: 0.0
max_graph_jaccard_loss: 0.0
variant_count: 5
n_nodes: 12
tau: 0.35
l0: 2.0
```

04A interpretation currently intended:

- Magnitude-only distance-like readability is invariant under pure phase changes in this toy construction.
- Phase-sensitive diagnostics respond to phase pattern changes.
- This supports only a methodological separation between magnitude-derived geometry proxies and phase-sensitive/interference-like diagnostics.

04A claim boundary:

- `K_ij` and `D_ij` are toy objects in 04A.
- `D_ij` is distance-like, not a physical spacetime metric.
- Phase-sensitive diagnostics are toy interference-like diagnostics, not real quantum dynamics.
- No physical emergence, metric recovery, causal structure, or de-Broglie confirmation is claimed.

---

## 3. Files / Artifacts to Inspect

Please inspect or request the following if available:

```text
data/qsb_bridge_num_04a_phase_sensitive_toy_config.yaml
docs/QSB_BRIDGE_NUM_04A_PHASE_SENSITIVE_TOY_SPEC.md
docs/QSB_BRIDGE_NUM_04A_RESULT_NOTE.md
scripts/run_qsb_bridge_num_04a_phase_sensitive_toy.py
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/summary.json
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/readout.md
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/phase_toy_variant_summary.csv
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/phase_toy_pairwise_diagnostics.csv
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/phase_toy_config_resolved.json
```

If you cannot inspect the files directly, base your review on the description above and clearly state that limitation.

---

## 4. Specific Review Questions

### A. Internal logic of 04A

1. Does the toy construction really isolate magnitude-only diagnostics from phase-sensitive diagnostics?
2. Are the diagnostics chosen in a way that makes the result nontrivial, or is the invariance purely definitional?
3. Is it useful despite being partly definitional? If yes, what exactly does it usefully certify?
4. Are Hermiticity and phase conventions handled adequately?
5. Are there phase patterns missing that would stress the diagnostic more strongly?
6. Are the toy diagnostics too weak, too ad hoc, or too dependent on the selected parameters `n=12`, `tau=0.35`, `l0=2.0`?

### B. Claim-risk audit

Look for wording that could be read as implying:

- spacetime emergence has been shown,
- a physical metric has been recovered,
- causal structure has been derived,
- de-Broglie physics has been confirmed,
- phase diagnostics are real quantum dynamics rather than toy diagnostics,
- geometry proxies are already physical geometry.

Flag any such wording and propose safer replacements.

### C. Methodological value

Please assess whether 04A is useful as:

- a reproducibility anchor,
- a logic-freeze for magnitude/phase separation,
- a preflight check for later real-data phase or spectral diagnostics,
- a bridge between earlier geometry-proxy work and later wave/interference-sensitive tests.

If you think it is not useful, explain what a better minimal diagnostic would look like.

### D. Controls and next tests

Suggest concrete follow-up controls. Especially consider:

1. Varying `tau`, `l0`, and graph size.
2. Testing more phase families, including gauge-like transformations, random high-frequency patterns, vortex/closure-rich patterns, and near-degenerate variants.
3. Testing whether phase-sensitive diagnostics remain stable under relabeling/permutation.
4. Comparing magnitude-identical but phase-different variants with known analytic expectations.
5. Introducing null families where phase response should vanish or become equivalent.
6. Extending from toy objects to real spectral, vibrational, molecular, or materials datasets.

### E. Real-data relevance

Please identify external datasets or systems that could support the next QSB bridge-physics checks. Prioritize data that provide at least some combination of:

- graph or bonding structure,
- 3D coordinates or crystal geometry,
- vibrational/phonon/spectral information,
- symmetry or automorphism-relevant metadata,
- downloadable machine-readable files.

Relevant candidate domains include:

- C60 and fullerene families,
- graphene / nanotubes / graphite / diamond and other carbon allotropes,
- molecular vibration datasets,
- crystal structure databases,
- phonon/band-structure materials datasets,
- isospectral or near-isospectral graph/geometry examples.

For each recommended data source, please include:

- source name,
- what fields are available,
- access method,
- expected QSB use,
- limitations,
- priority from 1 to 5.

---

## 5. Required Output Format

Please structure your review in the following sections:

```text
1. Executive red-team verdict
2. Strongest part of the current 04A block
3. Weakest or most vulnerable part
4. Possible overclaims or wording risks
5. Hidden assumptions
6. Missing controls
7. Suggested immediate fixes, if any
8. Recommended next numerical block
9. Recommended real-data block
10. Conservative claim boundary after review
```

Please separate clearly:

- **Befund / Finding**: what is directly shown by the available material.
- **Interpretation**: what may reasonably be inferred.
- **Hypothesis**: what remains speculative.
- **Open gap**: what is not yet demonstrated.
- **Claim boundary**: what should not be claimed.

---

## 6. Desired Tone

Be strict, but not dismissive. The project explicitly prefers finding weaknesses early.

Do not use generic statements such as “more work is needed” without specifying what work, what file, what test, or what control would improve the result.

Prefer actionable criticism.

