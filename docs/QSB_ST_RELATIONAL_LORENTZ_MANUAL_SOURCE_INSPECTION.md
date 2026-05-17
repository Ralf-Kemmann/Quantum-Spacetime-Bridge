# QSB-ST Resonance Matter Signature
## Relational Lorentz Manual Source Inspection

Guiding principle:

"Die Idee ins Licht. Die Grenzen ans Geländer. Die Details in den Maschinenraum."

## 1. Purpose

This note records a manual inspection of three high-value source traces for the QSB-ST relational Lorentz / interval question. Its positive purpose is to keep useful older material available while preventing old source traces from being overread as Lorentz proof, interval evidence, or LIC-01 implementation.

This is not a proof, not a result note, and not a LIC-01 specification. It is a careful classification note that follows the previous source-findings map and clarifies which traces are useful for future work and which are only boundary or conceptual context.

## 2. Inspection scope

The inspection read:

- the first relevant part of `numerics/debroglie-phase-bridge/typ_b_analysis/notes/debroglie_matter_signature_lorentz_filter_v1.md`;
- the full conceptual content of `numerics/debroglie-phase-bridge/notes/CONTINUUM_TO_PARTICULARITY_NOTE.md` as captured in the inspection output;
- JSON schemas / top-level keys of:
  - `k0_theta_intervals_t1.json`
  - `n1a_alpha_0p5_theta_intervals_t1.json`
  - `n1a_alpha_2p0_theta_intervals_t1.json`
  - `theta_comparison.json`

If any of these older traces later become inputs to LIC-01, the next step remains Herkunft und Nachvollziehbarkeit klären, alte Runs sauber zuordnen, Fundstellen und Reproduzierbarkeit prüfen, alte Ergebnisdateien nachvollziehbar einordnen, and klären, welche alten Runs reproduzierbar sind.

## 3. Summary finding

The manual inspection did not find an old hidden Lorentz proof.

It found:

- a useful Lorentz / relativity consistency filter;
- a conceptual continuity-to-particularity bridge note;
- `interval_map` JSON files that are theta/parameter/topology interval artifacts, not Lorentz interval artifacts.

This is a positive result because it prevents future confusion and tells the project which source traces are useful for LIC-01 and which are only boundary/context material.

## 4. Manual inspection table

| Source | What it contains | Current classification | LIC-01 relevance | Warning / boundary |
| --- | --- | --- | --- | --- |
| `numerics/debroglie-phase-bridge/typ_b_analysis/notes/debroglie_matter_signature_lorentz_filter_v1.md` | Lorentz-/Relativitäts-Filter; checks preferred frame, absolute simultaneity, instantaneous coupling, causality warning, relativistic consistency. | Lorentz / relativity consistency filter. | High for claim boundary, failure modes, admissible transformation criteria. | Not a derivation of Lorentz transformations and not an interval test. |
| `numerics/debroglie-phase-bridge/notes/CONTINUUM_TO_PARTICULARITY_NOTE.md` | Conceptual bridge line from relational continuity to coherent readable particularity. | Conceptual bridge / emergence note. | Medium for conceptual framing; helps think about stable articulation and readability. | Does not define `D(A,B)`, `tau_rel`, `c_eff`, `S_rel^2`, Lorentz invariance, or interval stability. |
| `numerics/debroglie-phase-bridge/results/n1a_scan/interval_map/k0_theta_intervals_t1.json` | `theta_min`, `theta_max`, `theta_rep`, `theta_crit`, `n_edges`, `n_components`, `graph_diameter`, `connected_pairs`, `topology_label`. | Theta / parameter interval map. | Possible support for readout variation and topology sensitivity. | Not a Lorentz interval. |
| `numerics/debroglie-phase-bridge/results/n1a_scan/interval_map/n1a_alpha_0p5_theta_intervals_t1.json` | Same schema family as above, for alpha 0.5. | Theta / parameter interval map. | Possible support for readout variation and topology sensitivity. | Not a Lorentz interval. |
| `numerics/debroglie-phase-bridge/results/n1a_scan/interval_map/n1a_alpha_2p0_theta_intervals_t1.json` | Same schema family as above, for alpha 2.0. | Theta / parameter interval map. | Possible support for readout variation and topology sensitivity. | Not a Lorentz interval. |
| `numerics/debroglie-phase-bridge/results/n1a_scan/interval_map/theta_comparison.json` | List of theta rows comparing k0, n1a_alpha_0p5, and n1a_alpha_2p0. | Theta comparison / parameter sweep summary. | Possible support for controlled readout variation. | Not a Lorentz transformation and not `S_rel^2`. |

## 5. Source 1: Matter Signature Lorentz filter

The Lorentz filter defines a useful early admissibility layer. It asks whether a candidate mechanism remains relativistically thinkable:

- no unmotivated preferred frame;
- no absolute simultaneity across separated regions;
- no uncontrolled instantaneous coupling;
- no supra-causal bridge logic;
- compatibility with finite causal structure.

Current classification: Lorentz-compatible / Lorentz-open governance material.

This source supports the Lorentz Status Note and future LIC-01 failure modes. It can help define what a candidate interval test should not violate. It does not support a Lorentz-derived claim, does not derive Lorentz transformations, and does not define a relational interval.

## 6. Source 2: Continuum-to-Particularity note

The Continuum-to-Particularity note is conceptually valuable because it frames the Bridge as the place where organized relation may become coherent, differentiated, readable, and stable enough to sustain particularity.

It supports the idea that Bridge structure may be about stable readability rather than a simple continuum/discrete cut. That is useful conceptual context for LIC-01, because a candidate interval would also be a readability question: does a combined distance-delay object remain stable under declared transformations?

But this source is not an operational interval document. It does not define `D(A,B)`, `tau_rel`, `c_eff`, `S_rel^2`, Lorentz invariance, or interval stability. It should not be used as evidence for Lorentz invariance.

## 7. Source 3: interval_map JSON files

The `interval_map` files use "interval" in the sense of theta/parameter intervals or scan windows. The schema fields show graph/topology readouts:

- `theta_min`
- `theta_max`
- `theta_rep`
- `theta_crit`
- `n_edges`
- `n_components`
- `largest_component_size`
- `graph_diameter`
- `connected_pairs`
- `disconnected_pairs`
- `defined_pair_count`
- `defined_pair_fraction`
- `standard_pairs`
- `topology_label`

These files should not be treated as Lorentz interval candidates.

They may still be useful for LIC-01 as examples of controlled readout variation under theta changes. In that role, they are topology and parameter-sweep artifacts that can inspire sensitivity logic, not inputs for `S_rel^2`.

## 8. Consequences for LIC-01

Consequences for future LIC-01 preparation:

1. LIC-01 should not treat `interval_map` JSONs as `S_rel^2` inputs.
2. LIC-01 may use theta/readout variation logic inspired by `interval_map` structure.
3. The Lorentz filter should be imported as a failure-mode checklist.
4. The continuum-to-particularity note can be cited as conceptual context only.
5. LIC-01 still needs fresh definitions of:
   - `D(A,B)`
   - `tau_rel(A,B)`
   - `c_eff`
   - `S_rel^2`
   - admissible readout/frame-like transformations
6. No old source currently supplies a complete relational Lorentz interval test.

The clean path is to treat these sources as support for framing, warnings, and design discipline, not as data or completed tests.

## 9. Failure and warning modes

Important failure and warning modes:

- treating Lorentz filter as Lorentz derivation;
- treating continuum-to-particularity as formal proof;
- treating theta intervals as Lorentz intervals;
- treating `graph_diameter` as spacetime distance;
- treating `connected_pairs` as causal connectivity;
- treating `topology_label` as light-cone structure;
- overreading old Part II or old notes without current status correction;
- using "interval" keyword hits without schema inspection.

These warning modes should stay visible if LIC-01 is later drafted.

## 10. Compact Claim Boundary

Claim Boundary:

This note does not:

- derive Lorentz transformations;
- prove Lorentz covariance;
- establish `S_rel^2`;
- establish a spacetime interval;
- establish causal cones;
- validate physical geometry;
- validate the Bridge physically;
- turn `interval_map` JSONs into Lorentz interval evidence;
- replace future LIC-01 specification or tests.

The current status is manual inspection, classification, not a Lorentz interval for the theta maps, consistency filter for the Lorentz filter, conceptual context for the continuum note, and not established.

## 11. Recommended next steps

1. Update the source-findings interpretation mentally: `interval_map` is theta/parameter interval, not Lorentz interval.
2. Extract the Lorentz filter as a future LIC-01 warning checklist.
3. Define candidate `tau_rel` sources.
4. Define a candidate `D(A,B)` source and Geometry Anchor status.
5. Decide `c_eff` handling: fixed convention, calibrated parameter, derived attempt, or sensitivity parameter.
6. Draft QSB-ST-LIC-01 only after these ingredients are fixed.
