# QSB-ST Resonance Matter Signature
## Relational Lorentz Source Findings

Guiding principle:

"Die Idee ins Licht. Die Grenzen ans Geländer. Die Details in den Maschinenraum."

## 1. Purpose

This document collects project-internal source findings for the QSB-ST relational Lorentz / interval question. Its positive purpose is to show where the project already contains useful material for future LIC-01 preparation, while keeping the source finding status separate from proof, validation, or implementation.

This is not a proof, not a result note, not a literature review, and not a LIC-01 specification. It is a careful findings map for Lorentz status, relational interval candidate framing, Geometry Anchor boundaries, Relational Delay, causal / no-signalling boundaries, aperiodic / nonlattice / causal-set context, BMC15 geometry-proxy warnings, and future LIC-01 preparation.

## 2. Why these findings matter

The Lorentz / interval question did not appear out of nowhere. The project already contains several source lines that point toward it:

- Bridge Architecture and Relational Delay language,
- Causality / Entropy Anchor conditions,
- Geometry Proxy and BMC15 warning lines,
- Lorentz Status and Relational Lorentz Interval Candidate notes,
- aperiodic / nonlattice / causal-set literature context,
- older numerical interval-map and Lorentz-filter traces.

The source findings are useful because they show a path for careful LIC-01 preparation. They do not establish Lorentz invariance, a spacetime interval, a causal cone, or physical bridge validation.

## 3. Search scope and limitation

The current findings come from a repository search focused on:

- Lorentz / Lorentzian / light cone / Minkowski,
- interval / Intervall,
- Relational Delay / delay,
- `c_eff` / `tau_rel` / `S_rel`,
- Geometry Anchor and causal/no-signalling boundaries.

A first broad search was too noisy because it caught `.venv`, `runs`, and generic interval library references. A filtered legacy-focused summary was therefore used. The cleaned search emphasized `docs/` and relevant `numerics/debroglie-phase-bridge/` locations, not external library files.

This note records source findings, not full manual source inspection. Some entries are manual check needed items.

## 4. High-level finding

The strongest finding is not an old proof of Lorentz transformation.

The strongest finding is a consistent project pattern: geometry-proxy results repeatedly warn that Lorentzian / causal / light-cone structure has not been tested yet, while Bridge Architecture and Causality/Entropy notes define exactly the conceptual place where Relational Delay, no-signalling, and future Lorentz-like checks would belong.

That pattern is valuable. It suggests that LIC-01 can be prepared from existing project architecture, provided the old traces are inspected and the claim boundary stays explicit.

## 5. Source groups

### A. Current QSB-ST Lorentz / interval control documents

- `docs/QSB_ST_LORENTZ_STATUS_NOTE.md`
- `docs/QSB_ST_RELATIONAL_LORENTZ_INTERVAL_CANDIDATE_NOTE.md`

Purpose: current status boundary and interval candidate framing.

### B. Bridge / delay / causal anchor documents

- `docs/QSB_ST_RESONANCE_MATTER_SIGNATURE_BRIDGE_ARCHITECTURE_SYNTHESIS.md`
- `docs/QSB_ST_RESONANCE_MATTER_SIGNATURE_CAUSALITY_ENTROPY_ANCHOR_NOTE.md`
- `docs/QSB_ST_BRIDGE_NATURE_WORKING_MODEL.md`

Purpose: defines Bridge as candidate translation layer and identifies Relational Delay as temporal-causal entry point.

### C. Geometry proxy / BMC15 warning documents

- `docs/BMC15_SERIES_GEOMETRY_PROXY_CONSOLIDATED_NOTE.md`
- `docs/BMC15E_GEOMETRY_CONTROL_NULLS_RESULT_NOTE.md`
- `docs/BMC15D_GEOMETRY_PROXY_RED_TEAM_INTEGRATION_NOTE.md`
- `docs/BMC15F1_NODE_ALIGNED_ENVELOPE_SENSITIVITY_RESULT_NOTE.md`
- `docs/BMC15F2_CONNECTEDNESS_TRANSITION_SWEEP_RESULT_NOTE.md`

Purpose: repeatedly marks that geometry-proxy results do not establish physical geometry, Lorentzian signature, causal structure, or light-cone structure.

### D. Literature / context documents

- `docs/QSB_LITERATURE_CONTEXT_APERIODIC_NONLATTICE_SPACETIME_DEEP_RESEARCH_2026-05-07.md`
- `docs/QSB_APERIODIC_NONLATTICE_CONTEXT_NOTE.md`

Purpose: context for aperiodic / nonlattice / causal-set / Lorentz-compatible structures; useful background, not project proof.

### E. Matter-signature / Lorentz-filter and continuum traces

- `numerics/debroglie-phase-bridge/typ_b_analysis/notes/debroglie_matter_signature_lorentz_filter_v1.md`
- `numerics/debroglie-phase-bridge/notes/CONTINUUM_TO_PARTICULARITY_NOTE.md`
- `numerics/debroglie-phase-bridge/results/n1a_scan/interval_map/*.json`

Purpose: potential older technical traces that should be manually checked for relevance to LIC-01.

Warning: "interval" may refer to parameter intervals, theta intervals, or scan windows rather than Lorentz intervals.

## 6. Source findings table

| Source / path | Source group | Relevant signal | Current status | Useful for LIC-01? | Warning / claim boundary |
| --- | --- | --- | --- | --- | --- |
| `docs/QSB_ST_LORENTZ_STATUS_NOTE.md` | A | Classifies Lorentz-compatible / Lorentz-inspired / Lorentz-assumed / Lorentz-open / Lorentz-derived. | Current status boundary. | Yes, as claim boundary. | Not evidence. |
| `docs/QSB_ST_RELATIONAL_LORENTZ_INTERVAL_CANDIDATE_NOTE.md` | A | Defines `D(A,B)`, `tau_rel`, `c_eff`, `S_rel^2` candidate. | Current LIC framing. | Yes, as LIC-01 conceptual parent. | No test yet. |
| `docs/QSB_ST_RESONANCE_MATTER_SIGNATURE_CAUSALITY_ENTROPY_ANCHOR_NOTE.md` | B | Relational Delay, no-signalling, causal-readability, entropy/coherence boundaries. | Temporal-causal anchor. | Yes, for `tau_rel` and causality boundary. | Delay is not causal cone. |
| `docs/QSB_ST_RESONANCE_MATTER_SIGNATURE_BRIDGE_ARCHITECTURE_SYNTHESIS.md` | B | Bridge architecture includes interaction-like scaling and relational delay / causality structure. | Bridge architecture context. | Yes, for conceptual placement. | Synthesis is not validation. |
| `docs/QSB_ST_BRIDGE_NATURE_WORKING_MODEL.md` | B | Bridge as candidate translation layer. | Current bridge interpretation. | Yes. | Translation layer not established physical interaction. |
| `docs/QSB_ST_MARKER_VS_CARRIER_STATUS_TABLE.md` | B | Separates readout / marker / carrier / modifier. | Claim-discipline table. | Yes, to classify `S_rel^2` as diagnostic interval candidate. | Do not upgrade interval candidate to carrier. |
| `docs/BMC15_SERIES_GEOMETRY_PROXY_CONSOLIDATED_NOTE.md` | C | No Lorentzian signature or light-cone structure tested. | Warning / geometry-proxy boundary. | Yes, as negative boundary. | BMC15 geometry proxy is not Lorentz evidence. |
| `docs/BMC15D_GEOMETRY_PROXY_RED_TEAM_INTEGRATION_NOTE.md` | C | Red-team integration around geometry proxy and Lorentz caution. | Warning / red-team boundary. | Yes, for failure modes. | Not a positive Lorentz test. |
| `docs/BMC15E_GEOMETRY_CONTROL_NULLS_RESULT_NOTE.md` | C | Geometry-generated controls and no Lorentz-signature claim. | Geometry-control boundary. | Yes, for null logic. | Geometry compatibility is not physical geometry. |
| `docs/BMC15F1_NODE_ALIGNED_ENVELOPE_SENSITIVITY_RESULT_NOTE.md` | C | Construction sensitivity and no Lorentzian structure tested. | Warning. | Maybe, for transformation/readout sensitivity logic. | Envelope robustness not Lorentz invariance. |
| `docs/BMC15F2_CONNECTEDNESS_TRANSITION_SWEEP_RESULT_NOTE.md` | C | Connectedness transition, no causal/Lorentzian diagnostics. | Warning. | Maybe, for connectivity failure modes. | Connectedness is not light cone. |
| `docs/QSB_LITERATURE_CONTEXT_APERIODIC_NONLATTICE_SPACETIME_DEEP_RESEARCH_2026-05-07.md` | D | Causal-set and nonlattice Lorentz-context literature. | Literature context. | Yes, as external vocabulary and red-line context. | Literature analogy does not prove QSB. |
| `docs/QSB_APERIODIC_NONLATTICE_CONTEXT_NOTE.md` | D | Aperiodic / nonlattice context and caution. | Context. | Maybe, for comparison space. | Aperiodicity is not Lorentz invariance. |
| `numerics/debroglie-phase-bridge/typ_b_analysis/notes/debroglie_matter_signature_lorentz_filter_v1.md` | E | Possible older Lorentz-filter technical trace. | Needs manual reading. | Unknown / potentially yes. | Must check whether it is filter logic, claim text, or exploratory note. |
| `numerics/debroglie-phase-bridge/notes/CONTINUUM_TO_PARTICULARITY_NOTE.md` | E | Possible continuum-limit or particularity transition trace. | Needs manual reading. | Potentially yes for older Part I/II bridge. | Continuum wording may import assumptions. |
| `numerics/debroglie-phase-bridge/results/n1a_scan/interval_map/*.json` | E | interval-map files. | Technical artifact, likely parameter/theta intervals until proven otherwise. | Maybe, for scan-window logic. | "interval" is not automatically Lorentz interval. |

## 7. What looks useful for LIC-01

Useful LIC-01 source findings:

- Lorentz Status Note: claim boundary.
- Relational Lorentz Interval Candidate Note: conceptual test frame.
- Causality / Entropy Anchor Note: `tau_rel` and no-signalling boundary.
- Geometry Anchor Conditions: `D(A,B)` boundary.
- BMC15 geometry-proxy notes: null and failure-mode logic.
- Old Lorentz-filter / continuum / interval-map files: manual check candidates.

These sources do not yet define a test. They suggest where a future LIC-01 specification should draw its definitions, controls, and warnings.

## 8. What is mainly warning / claim-boundary material

Main warning material:

- BMC15 "no Lorentzian signature" statements.
- Light-cone not tested statements.
- Geometry-proxy not physical geometry statements.
- Literature context red lines.
- Current status notes that prevent overclaiming.

These warnings are useful because they keep source finding language from becoming a hidden claim. A warning source can be essential for LIC-01 even when it is not positive evidence.

## 9. What still needs manual checking

Manual check needed items:

1. Open and inspect `debroglie_matter_signature_lorentz_filter_v1.md`.
2. Open and inspect `CONTINUUM_TO_PARTICULARITY_NOTE.md`.
3. Inspect `interval_map` JSON schema and determine whether "interval" means theta/parameter interval or physical interval candidate.
4. Compare old Part II PDF wording to current Lorentz Status Note.
5. Identify whether any old code computes delay-like readouts.
6. Identify whether any old code defines an effective `c`, propagation speed, or frame-like transform.
7. Keep all findings at source-finding status until checked.

If older runs become relevant, the practical discipline is to Herkunft und Nachvollziehbarkeit klären, alte Runs sauber zuordnen, Fundstellen und Reproduzierbarkeit prüfen, alte Ergebnisdateien nachvollziehbar einordnen, and klären, welche alten Runs reproduzierbar sind.

## 10. Compact Claim Boundary

Claim Boundary:

This findings note does not:

- prove Lorentz invariance;
- derive Lorentz transformations;
- establish a spacetime interval;
- establish causal cones;
- validate physical geometry;
- validate the Bridge physically;
- show that `interval_map` files are Lorentz intervals;
- replace manual source inspection;
- replace future LIC-01 specification or tests.

The current status is source finding, candidate relevance, warning material, manual check needed, and not established.

## 11. Recommended next steps

1. Manually inspect the two older technical notes:
   - `debroglie_matter_signature_lorentz_filter_v1.md`
   - `CONTINUUM_TO_PARTICULARITY_NOTE.md`
2. Inspect `interval_map` JSON files and classify their "interval" meaning.
3. Create a small table of old Part II Lorentz statements and current status correction.
4. Define candidate `tau_rel` sources.
5. Define candidate `D(A,B)` source and Geometry Anchor status.
6. Only then draft QSB-ST-LIC-01 Spec.
