# QSB-ST Resonance Matter Signature
## tau_rel Deep Research Integration Note

Guiding principle:

"Die Idee ins Licht. Die Grenzen ans Geländer. Die Details in den Maschinenraum."

## 1. Purpose

This note integrates Deep Research input about possible `tau_rel` / relational-delay constructions for the future QSB-ST-LIC-01 Relational Lorentz Interval Candidate Test. Its positive purpose is to translate useful external route ideas into QSB-ST language while keeping the claim boundary clear.

This is not a result note, not a LIC-01 specification, not a proof, and not a literature review in final form. It is a careful translation and red-team integration note: what from the Deep Research report is useful for QSB-ST, what must be downgraded, and what should guide the next `tau_rel` construction.

## 2. Input status

The Deep Research report is useful as external idea input, but it is not adopted as a QSB-ST specification. It contains valuable physics vocabulary and candidate routes, including Synge world function / geometric proper time, radar and clock protocols, quantum clocks, Page-Wootters-like relational time, entangled clocks, field-correlator and QFT two-point correlation routes, qmetric / minimal-length ideas, phase / delay / Wigner-Smith / Hartman-like concepts, and operational no-signalling constraints.

Its strongest mismatch is that it often assumes the spacetime setting that QSB-ST would eventually like to test for readability or emergence:

- spacetime events A and B;
- Lorentz manifold `(M,g)`;
- metric interval / proper time;
- Lorentz covariance as background.

For QSB-ST this must be translated. QSB-ST does not start from spacetime events and a given metric. QSB-ST starts from relational correlation structure, `K_ij`, phase/coherence, graph/cost readouts, and candidate delay-like diagnostics.

## 3. Main takeaway

Deep Research confirms that tau_rel cannot be introduced as a loose time label. It must be tied to an explicit construction: phase/correlation response, field-correlator inversion, open-system/density-matrix response, graph propagation, or a classical proper-time anchor. For QSB-ST, the safest first route is not Synge proper time, but a phase/correlation-response delay candidate under PADS-01, no-signalling, and Geometry Anchor constraints.

Deep Research bestätigt: tau_rel darf nicht als loses Zeit-Etikett eingeführt werden. Es braucht eine explizite Konstruktion. Für QSB-ST ist der sauberste erste Weg nicht Synge/Eigenzeit, sondern ein phasen-/korrelationsbasierter Response-Delay-Kandidat unter PADS-01-, No-Signalling- und Geometry-Anchor-Geländern.

## 4. What Deep Research got right

The report is finally topic-relevant because it points to real construction classes rather than generic time language. It correctly emphasizes:

- `tau_rel` requires explicit assumptions and operational meaning;
- phase, clocks, correlations, field correlators, and response protocols are legitimate places to look for delay-like quantities;
- no-signalling and causal boundaries are essential;
- proper time / Synge world function is the clean classical reference structure;
- quantum clocks and open-system limitations warn against treating time order as automatically sharp;
- correlation-derived distances or delays require strong controls.

These points fit the current QSB-ST discipline: candidate, diagnostic, not physical time, not metric-derived, not Lorentz-derived, and not established.

## 5. What must be translated into QSB-ST language

Translation map:

- "space-time events A,B" -> QSB-ST pair objects / node pairs / relational states.
- "metric g" -> not given; only candidate geometry-readability / Geometry Anchor.
- "proper time" -> anchor or comparison target, not starting `tau_rel`.
- "Lorentz covariance" -> compatibility / target / later test, not current derivation.
- "`tau_rel` as Lorentz distance" -> `tau_rel` as relational-delay diagnostic candidate.
- "experimental clocks" -> external anchor class, not internal first-pass construction.

This translation is the central value of the integration note. It preserves useful physics vocabulary without importing a metric, a clock protocol, or a Lorentz result into QSB-ST before the project has earned it.

## 6. Candidate tau_rel routes from the report

| Route | Deep Research version | QSB-ST translation | Usefulness | Main risk | Status for LIC-01 |
| --- | --- | --- | --- | --- | --- |
| Synge / proper-time route | `tau = sqrt(2 sigma(A,B))` from world function. | Classical anchor / comparison target if geometry is already given. | High as reference, low as first internal construction. | Imports metric / spacetime interval. | `anchor_only` |
| Radar / operational clock route | Light signal / clock protocol. | External operational anchor candidate. | Medium for future validation. | Observer convention and background clock structure. | `later_external_anchor` |
| Quantum clocks / Page-Wootters route | Relational time from quantum clocks / finite clock resources. | Useful conceptual warning about non-primitive time and fuzzy ordering. | Medium. | Hard implementation, may drift away from current pipeline. | `theory_context` |
| Entangled clocks | Synchronization / coincidence-rate based relative timing. | Possible distant analogy for correlation-based timing. | Low-medium. | Easy to overread as signalling or causal timing. | `speculative_context` |
| Field-correlator / QFT two-point route | Infer interval-like information from two-point correlators. | Closest external analogy to `K_ij` / correlation-first geometry. | High. | Requires field model and invertibility; may import QFT background. | `strong_candidate_analogy` |
| Open-system / density-matrix response route | Clocks / decoherence / response timing. | Good fit to phase-coherent off-diagonal carrier candidate. | High. | Relaxation/decoherence time is not causal delay. | `strong_QSB_candidate` |
| Phase / Wigner-Smith / Hartman / Dwell route | Phase-derived delay concepts. | Good fit to phase/coherence and PADS-01 controls. | High. | Phase delay is not traversal time. | `strongest_first_design_route` |
| Graph / propagation response route | Response propagation / graph diffusion possible. | Pipeline-compatible `tau_rel` candidate if carefully controlled. | Medium-high. | Graph algorithm artifact or pipeline drift. | `backup_practical_route` |
| qmetric / minimal-length route | Modified world function with minimal length. | Literature context only for now. | Low for LIC-01 first pass. | Too speculative and metric-assuming. | `defer` |

## 7. QSB-ST ranking of tau_rel construction routes

Ranking for the first `tau_rel` construction:

1. Phase / Wigner-Smith / Hartman / Dwell inspired phase-response route.
2. Open-system / density-matrix off-diagonal coherence response route.
3. Field-correlator / `K_ij` inversion analogy.
4. Graph / perturbation response route.
5. Quantum-clock context as conceptual support.
6. Radar / operational clocks as later external anchor.
7. Synge / proper time as classical target / anchor only.
8. qmetric / minimal length as deferred speculative context.

Synge is physically clean but backwards for QSB-ST because it assumes the metric. QSB-ST should first try a `tau_rel` source that arises from phase/correlation response, because that connects to the current candidate carrier: phase-coherent off-diagonal relational correlation structure.

## 8. Why Synge / proper time is an anchor, not the starting point

Synge world function and proper time are clean in a setting where spacetime events and a metric are already given. That makes them valuable as reference language and possible later comparison targets.

They are not the right first internal construction for QSB-ST because QSB-ST begins before that metric status. The project currently has `K_ij`, phase/coherence structure, candidate geometry-readability, and candidate delay-like diagnostics. A Synge-first route would import the very geometry that LIC-01 is meant to test for invariant-like readability.

For QSB-ST, Synge / proper time should therefore remain an anchor, not a starting `tau_rel`.

## 9. Recommended QSB-ST tau_rel route

First `tau_rel` construction should be:

phase/correlation-response delay candidate.

Working idea:

Start from `K_ij` or a phase/coherence readout. Apply a controlled perturbation, phase deformation, parameter step, or phase-gradient-like construction. Measure pairwise or local response shift / phase response / correlation-pattern lag. Define `tau_rel` as a diagnostic response-delay score, not physical time.

Possible status label:

`tau_rel_phase_response_design_candidate`

Possible minimal formula language:

`tau_rel(A,B)` may be defined from a predeclared phase-response functional `R_phase(A,B)`, normalized to a dimensionless delay-like score.

Do not give a final formula unless the source is fixed. Keep formula language as a design placeholder until the construction, inputs, normalization, and controls are declared.

## 10. Controls and failure modes

Controls to carry into the next construction note:

- global phase should cancel where only phase differences matter;
- local gauge-like phase shifts need loop/closure checks;
- phase-random controls;
- spectrum-matched phase controls;
- amplitude-only controls;
- amplitude-preserved / phase-randomized controls;
- label/family shuffles;
- topology-preserving graph controls;
- perturbation controls;
- no-signalling boundary;
- `c_eff` sensitivity;
- component-dominance check: `S_rel^2` must not merely mirror `D` or `tau_rel`.

Failure modes:

- treating Synge as QSB result;
- importing the metric;
- treating phase delay as traversal time;
- treating graph propagation as causal signal;
- fitting `c_eff` to force stability;
- reading entanglement timing as signalling;
- treating correlation strength as distance without invertibility and controls;
- calling invariant-like stability Lorentz invariance.

## 11. Consequences for LIC-01

LIC-01 should not yet run until `tau_rel` is constructed or selected.

Current status remains:

`LIC01_distance_ready_delay_missing`

After this integration, the preferred construction direction is:

`tau_rel_phase_response_design_candidate`

Proposed next internal label:

`LIC01_tau_rel_route_selected_not_constructed`

LIC-01 first smoke test should only happen after:

- `D(A,B)` source is selected;
- `tau_rel` phase/correlation-response construction is specified;
- `c_eff` handling is predeclared;
- readout/frame-like transformations are fixed;
- controls are fixed.

## 12. Compact Claim Boundary

Claim Boundary:

This integration note does not:

- adopt the Deep Research report as QSB-ST theory;
- define final `tau_rel`;
- compute `tau_rel(A,B)`;
- validate physical time;
- validate Synge/proper time inside QSB-ST;
- establish `S_rel^2`;
- establish Lorentz invariance;
- prove Lorentz covariance;
- establish light cones;
- validate the Bridge physically;
- replace PADS-01, Geometry Anchor, or LIC-01.

The current status is Deep Research input translated into QSB-ST language: candidate, diagnostic, not physical time, not metric-derived, not Lorentz-derived, and not established.

## 13. Recommended next steps

1. Push any outstanding local commits before new work if repository is ahead.
2. Create a `tau_rel` construction design note focused on phase/correlation-response.
3. Inspect QSB-BRIDGE-NUM-05B outputs for phase-difference and loop-flux fields.
4. Decide whether `tau_rel` will use pairwise phase response, loop response, or perturbation-response lag.
5. Choose one `D(A,B)` source.
6. Then draft QSB-ST-LIC-01 Spec.

For older runs or recovered traces that later support this route, keep the practical discipline: Herkunft und Nachvollziehbarkeit klären, alte Runs sauber zuordnen, Fundstellen und Reproduzierbarkeit prüfen, alte Ergebnisdateien nachvollziehbar einordnen, and klären, welche alten Runs reproduzierbar sind.
