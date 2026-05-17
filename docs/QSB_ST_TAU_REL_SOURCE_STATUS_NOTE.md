# QSB-ST Resonance Matter Signature
## tau_rel Source Status Note

Guiding principle:

"Die Idee ins Licht. Die Grenzen ans Geländer. Die Details in den Maschinenraum."

## 1. Purpose

This note documents the current source status of `tau_rel(A,B)` for the future QSB-ST-LIC-01 Relational Lorentz Interval Candidate Test. Its positive purpose is to make the missing delay ingredient explicit, so LIC-01 can move toward a clean specification without pretending that a run-ready delay readout already exists.

This is not a result note, not a LIC-01 specification, and not an implementation. It records what exists, what does not yet exist, and what must be constructed or selected before LIC-01 can become run-ready.

## 2. Why tau_rel matters

LIC-01 needs `tau_rel(A,B)` because the candidate interval form requires both a distance component and a delay component:

```text
S_rel^2(A,B) = c_eff^2 * tau_rel(A,B)^2 - D(A,B)^2
```

Without `tau_rel`, LIC-01 cannot test interval-like stability. It can only remain a design-ready or distance-ready block.

The current honest labels are:

- `LIC01_distance_ready_delay_missing`
- `tau_rel_conceptual_ready_but_numerically_missing`
- `tau_rel_not_physical_time`
- `tau_rel_requires_construction`

## 3. Current search finding

The current repository search did not identify a canonical, ready-to-use numerical `tau_rel(A,B)` file or function.

It did identify:

- strong conceptual Relational Delay anchors;
- temporal-causal claim boundaries;
- Hartman / Dwell / Shapiro-like delay language;
- phase-difference / gauge-phase technical traces from QSB-BRIDGE-NUM-05B;
- older noncanonical delay / compatibility language.

A delay/phase-shift search found mostly conceptual and claim-boundary documents, not a ready numerical `tau_rel` readout.

The most relevant conceptual sources are:

- `docs/QSB_ST_RESONANCE_MATTER_SIGNATURE_CAUSALITY_ENTROPY_ANCHOR_NOTE.md`
- `docs/QSB_ST_RESONANCE_MATTER_SIGNATURE_BRIDGE_ARCHITECTURE_SYNTHESIS.md`
- `docs/QSB_ST_RELATIONAL_LORENTZ_INTERVAL_CANDIDATE_NOTE.md`
- `docs/QSB_ST_LIC01_PRE_SPEC_INGREDIENTS.md`
- `docs/QSB_ST_MARKER_VS_CARRIER_STATUS_TABLE.md`
- `docs/QSB_ST_LORENTZ_STATUS_NOTE.md`

The most relevant technical phase trace is:

- `scripts/run_qsb_bridge_num_05b_phase_gauge_flux_stress_test.py`

The older noncanonical trace is:

- `numerics/debroglie-phase-bridge/_archive_masterchat_noncanonical/MASTERCHAT_CURRENT_STATUS_2026-04-09.md`

## 4. What exists now

What exists now:

1. Relational Delay as conceptual temporal-causal entry point.
2. Delay treated as structured shift between correlation patterns.
3. Hartman / Dwell phasengeometric warning line.
4. Shapiro-like illustrative delay contrast.
5. Phase-difference and gauge-phase stress-test logic.
6. PADS-01 optional Relational Delay ordering placeholder.
7. Marker-vs-Carrier classification for Relational Delay as temporal / causal anchor candidate.

These sources make `tau_rel` conceptually ready to define, but not numerically ready to use.

## 5. What does not yet exist

What does not yet exist:

1. no canonical `tau_rel(A,B)` table;
2. no run-ready `tau_rel` computation script identified;
3. no declared pairwise `tau_rel` values;
4. no operational delay-source schema;
5. no asymmetry / directionality status table;
6. no no-signalling test tied to `tau_rel`;
7. no `c_eff`-calibrated delay component;
8. no validated phase-gradient-to-delay construction;
9. no causal cone or physical time interpretation.

This is not a failure. It is the current source status that must be respected before LIC-01 is specified.

## 6. Best current tau_rel status

`tau_rel(A,B)` should currently be classified as:

TEMPORAL / CAUSAL ANCHOR CANDIDATE

and

DIAGNOSTIC READOUT TO BE CONSTRUCTED

Claim-safe wording:

- "tau_rel is a planned relational-delay diagnostic candidate."
- "tau_rel is not physical time."
- "tau_rel is not yet run-ready."
- "LIC-01 remains distance-ready but delay-missing until tau_rel is constructed or selected."

The operational status is `LIC01_distance_ready_delay_missing` and `tau_rel_conceptual_ready_but_numerically_missing`.

## 7. Candidate source classes

| Candidate source class | Current availability | Possible construction | LIC-01 readiness | Warning |
| --- | --- | --- | --- | --- |
| Relational Delay readout | Conceptual only / no canonical numeric source found. | Pairwise structured shift between correlation patterns. | Not ready. | Delay is not causal order. |
| Phase-gradient-like readout | Not yet identified as canonical source. | Phase difference or phase gradient mapped to delay-like quantity. | Design candidate. | Phase gradient is not traversal time. |
| Pattern-shift between correlation states | Conceptual. | Compare `K_ij` or graph/readout state across perturbation or parameter step. | Design candidate. | Shift may be pipeline artifact. |
| Hartman / Dwell-inspired phasengeometric proxy | Conceptual / anchor language. | Phase-derived delay proxy inspired by Wigner/Smith/Hartman/Dwell concepts. | Not ready. | Phasengeometric delay is not ordinary time. |
| QSB-BRIDGE-NUM-05B phase gauge / loop flux trace | Technical phase-difference stress-test exists. | Possible starting point for phase-difference robustness, not `tau_rel` directly. | Partial technical ingredient. | Gauge-phase cancellation is not delay. |
| PADS-01 optional Relational Delay Ordering Change | Placeholder / optional readout. | Only after delay-like readout exists. | Not ready. | Optional placeholder is not data. |

## 8. Technical phase-difference / gauge-phase trace

The script `scripts/run_qsb_bridge_num_05b_phase_gauge_flux_stress_test.py` is useful as a technical phase trace.

Current reading:

- global phase cancels from pairwise phase differences;
- local gauge phase uses `theta_i - theta_j`;
- individual edges can appear phase-shifted;
- loop flux may remain near zero under gauge-like shifts.

This is useful for understanding phase-difference robustness and gauge-like controls. It is not yet tau_rel.

It could inform future `tau_rel` controls, especially phase gauge-like shifts and loop-consistency checks. It should not be treated as a delay computation unless a new construction explicitly maps phase-difference behavior to a declared delay-like diagnostic.

## 9. Conceptual Relational Delay anchors

The Causality / Entropy Anchor Note treats Relational Delay as the clearest temporal-causal entry point. In the current architecture, delay is a structured shift between correlation patterns, not primitive elapsed time.

Future causality requires asymmetry, perturbation response, no-signalling compatibility, and operational testability.

Bridge Architecture Synthesis frames Hartman / Wigner / Smith / Shapiro-like delay language as anchor families, not direct derivations. These ideas are useful for designing a `tau_rel` candidate, but they do not supply a canonical numerical readout by themselves.

## 10. LIC-01 consequence

LIC-01 cannot yet be run as a full interval test.

Current status should be:

`LIC01_distance_ready_delay_missing`

The next step is not to force a `tau_rel` into existence, but to construct or select one explicitly before the LIC-01 Spec.

Until that is done, `S_rel^2` remains a candidate formula with a missing delay ingredient.

## 11. Requirements for a future tau_rel construction

A future `tau_rel` construction needs at least:

- `pair_id` field;
- `tau_rel_value` field;
- `delay_source_id`;
- construction method;
- symmetric/directed/unresolved status;
- phase dependence;
- perturbation source if any;
- no-signalling status;
- normalization;
- uncertainty or stability score;
- warning flag;
- claim-safe interpretation.

Proposed future file:

`data/QSB-ST-LIC-01/tau_rel_candidate_sources.csv`

Do not create it now.

Field list:

| field name | field type | field description |
| --- | --- | --- |
| `source_id` | string | identifier for candidate delay source |
| `source_type` | string | relational_delay / phase_gradient / pattern_shift / Hartman_Dwell_proxy / gauge_phase_trace |
| `source_path` | string | path to source artifact or document |
| `numerical_ready` | boolean | whether pairwise `tau_rel` values can be produced now |
| `directionality_status` | string | symmetric/directed/unresolved |
| `phase_dependence_status` | string | phase_dependent/phase_independent/unknown |
| `no_signalling_status` | string | not_tested/passed/failed/not_applicable |
| `normalization_required` | boolean | whether normalization is required |
| `LIC01_readiness` | string | ready/design_candidate/not_ready |
| `warning` | string | warning text |
| `note` | string | short note |

## 12. Failure and warning modes

Important failure and warning modes:

- treating conceptual Relational Delay as numeric `tau_rel`;
- treating phase difference as physical delay;
- treating gauge-phase shift as traversal time;
- treating Hartman / Dwell analogy as operational delay;
- using `tau_rel` without directionality/asymmetry status;
- using `tau_rel` without no-signalling boundary;
- fitting `c_eff` to compensate for weak `tau_rel`;
- treating `LIC01_distance_ready_delay_missing` as a failure rather than honest status;
- claiming light cone or causality from delay-like ordering.

These warnings should remain attached to LIC-01 until a numerical `tau_rel` source is built and checked.

## 13. Compact Claim Boundary

Claim Boundary:

This note does not:

- define final `tau_rel`;
- compute `tau_rel(A,B)`;
- validate physical time;
- validate causal order;
- establish a light cone;
- establish no-signalling compatibility;
- establish `S_rel^2`;
- implement LIC-01;
- prove Lorentz invariance.

The current status is candidate, diagnostic, not physical time, not run-ready, requires construction, and not established.

## 14. Recommended next steps

1. Push any outstanding local commit before new work if repository is ahead.
2. Select whether `tau_rel` should first be built from phase-difference, pattern-shift, or Hartman/Dwell-inspired logic.
3. Inspect QSB-BRIDGE-NUM-05B outputs for reusable phase-difference fields.
4. Draft a minimal `tau_rel` candidate schema.
5. Only then draft QSB-ST-LIC-01 Spec.
6. Keep LIC-01 status as `LIC01_distance_ready_delay_missing` until `tau_rel` is constructed.

For any old-run material later used near `tau_rel`, keep the practical discipline: Herkunft und Nachvollziehbarkeit klären, alte Runs sauber zuordnen, Fundstellen und Reproduzierbarkeit prüfen, alte Ergebnisdateien nachvollziehbar einordnen, and klären, welche alten Runs reproduzierbar sind.
