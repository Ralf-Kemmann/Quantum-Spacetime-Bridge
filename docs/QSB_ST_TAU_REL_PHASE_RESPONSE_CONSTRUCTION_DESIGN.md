# QSB-ST Tau-Rel Phase-Response Construction Design

**Block:** QSB-ST-LIC-01 / LIC01_tau_epsilon  
**Working status target:** `LIC01_tau_rel_route_selected_not_constructed`  
**Document type:** Construction design / pre-run specification  
**Date:** 2026-05-17  
**Scope:** Synthetic diagnostic design only. No physical time, Lorentz metric, or empirical validation claim.

---

## 1. Purpose

This document specifies a cautious construction route for a `tau_rel(A,B)` candidate in the QSB-ST / LIC01 line.

The immediate goal is not to construct spacetime, physical time, or a Lorentzian interval. The goal is to define a reproducible **phase-response / correlation-pattern delay candidate** that can later be tested numerically under controlled synthetic perturbations.

The preferred construction route is:

```text
K_ij baseline
→ controlled phase/correlation perturbation
→ phase-response / correlation-pattern shift
→ pairwise response score
→ tau_rel candidate
```

This keeps the construction internal to the existing QSB logic rather than importing Synge world functions, proper time, or Lorentz geometry as assumptions.

---

## 2. Motivation

Previous QSB-ST notes established that the distance-like side of the candidate interval is comparatively available:

```text
D(A,B)
```

can be read from the existing graph/cost/relational pipeline.

The missing ingredient is a defensible internal construction for:

```text
tau_rel(A,B)
```

LIC01 therefore focuses on whether a relational delay-like quantity can be built from a controlled response of the relational kernel/correlation structure to small perturbations.

The guiding idea is that if a local perturbation at or near node/pair `A` induces a reproducible, structured response at or near node/pair `B`, then the response profile may define a delay-like relational quantity. At this stage, the quantity is only a diagnostic candidate.

---

## 3. Non-goals and claim boundary

LIC01 does **not** claim:

- derivation of Lorentzian spacetime,
- construction of physical proper time,
- experimental validation,
- real-data correspondence,
- evidence for superluminal transport,
- replacement of relativity or quantum mechanics,
- proof that `tau_rel` is unique or canonical.

Allowed claim level:

> LIC01 defines a synthetic phase-response construction route for a relational-delay diagnostic candidate `tau_rel(A,B)`. The construction tests whether controlled perturbations of an existing QSB relational kernel produce reproducible pairwise response scores that can later be compared with distance-like graph diagnostics.

---

## 4. Core objects

### 4.1 Baseline relational kernel

Let

```text
K_ij
```

denote the baseline relational kernel or correlation-like matrix used in the local QSB-ST context.

For LIC01, `K_ij` is treated as an already-available baseline object. The first LIC01 design step does not prescribe a unique physical interpretation of `K_ij`; it only requires that the object be:

- finite,
- indexed by the same node/pair set used by the graph pipeline,
- reproducibly constructible,
- compatible with controlled perturbation,
- inspectable before and after perturbation.

### 4.2 Controlled perturbation

Introduce a small perturbation parameter:

```text
epsilon
```

`epsilon` is not a physical coupling constant at this stage. It is a synthetic control parameter used to probe the sensitivity of the relational kernel/correlation structure.

Candidate perturbation forms may include:

```text
K_ij(epsilon; A) = K_ij + epsilon * P_ij(A)
```

or, if phase information is explicitly represented:

```text
K_ij(epsilon; A) = K_ij * exp(i * epsilon * P_ij(A))
```

The exact perturbation operator `P_ij(A)` must be documented in the later runner/config and must remain fixed across comparable sweeps.

### 4.3 Response profile

For each perturbation centered on source object `A`, define a response profile over target objects `B`:

```text
R_A(B; epsilon)
```

A minimal response definition may be based on the magnitude of change:

```text
R_A(B; epsilon) = || Obs_B(K(epsilon; A)) - Obs_B(K(0)) ||
```

where `Obs_B` is a local observable or diagnostic readout around `B`.

Possible observables:

- local row/column change of `K`,
- graph-cost change involving `B`,
- local weighted-neighborhood diagnostic,
- spectral/local-response contribution,
- phase-shift response if phase is represented explicitly.

### 4.4 Pairwise response score

Define a pairwise score:

```text
rho_tau(A,B)
```

as a robust summary of the response of `B` to perturbation at `A`.

Candidate summaries:

- first nonzero response threshold crossing,
- response slope near epsilon = 0,
- normalized integrated response over epsilon sweep,
- peak response location if epsilon/tau sweep is two-dimensional,
- response-profile similarity lag under synthetic phase shift.

For LIC01 design, the preferred minimal construction is the small-epsilon slope:

```text
rho_tau(A,B) = d R_A(B; epsilon) / d epsilon |_(epsilon -> 0)
```

implemented numerically as a finite-difference estimate over small positive and possibly symmetric epsilon values.

### 4.5 tau_rel candidate

A preliminary tau-like candidate may be defined as an inverse or monotone transform of response strength:

```text
tau_rel(A,B) = Normalize(1 / (rho_tau(A,B) + eta))
```

or, alternatively, as a delay index extracted from a response curve if the runner introduces an explicit sweep variable.

For the first LIC01 construction design, `tau_rel` should remain a **candidate field**, not a final canonical quantity.

---

## 5. Candidate interval object

The longer LIC01 target is to prepare a testable candidate of the form:

```text
S_rel^2(A,B) = c_eff^2 * tau_rel(A,B)^2 - D(A,B)^2
```

where:

- `D(A,B)` is a graph/cost/relational distance-like quantity,
- `tau_rel(A,B)` is the phase-response / correlation-delay diagnostic candidate,
- `c_eff` is a normalized scale/sensitivity parameter.

At this stage:

- `S_rel^2` is only a candidate comparison object,
- `c_eff` is not the speed of light,
- `tau_rel` is not physical time,
- `D` is not assumed to be classical spatial distance.

---

## 6. Suggested minimal LIC01 implementation path

### Stage LIC01-A: Design freeze

Create this design document and commit it as the first LIC01 design anchor.

Expected status after this stage:

```text
LIC01_tau_rel_route_selected_not_constructed
```

### Stage LIC01-B: Config scaffold

Create a new config file under `data/`, for example:

```text
data/qsb_st_lic01_tau_epsilon_phase_response_config.yaml
```

The config should define:

- baseline source,
- perturbation family,
- epsilon sweep,
- source-target object selection,
- observable family,
- normalization rule,
- output directory,
- random seed if any,
- acceptance thresholds.

### Stage LIC01-C: Runner scaffold

Create a new script under `scripts/`, for example:

```text
scripts/run_qsb_st_lic01_tau_epsilon_phase_response.py
```

The runner should:

1. load config,
2. build/load baseline `K`,
3. apply controlled perturbations,
4. compute response profiles,
5. compute pairwise response scores,
6. optionally construct preliminary `tau_rel`,
7. write CSV/JSON/readout outputs,
8. print compact terminal summary.

### Stage LIC01-D: First synthetic open run

Expected run directory:

```text
runs/QSB-ST-LIC01/tau_epsilon_phase_response_open/
```

Expected output files:

```text
summary.json
readout.md
tau_epsilon_pairwise_response.csv
tau_epsilon_response_sweep.csv
tau_rel_candidate_matrix.csv
config_resolved.json
```

---

## 7. Proposed output field list

### 7.1 `tau_epsilon_pairwise_response.csv`

- `source_id` — string — source object/node/pair for perturbation.
- `target_id` — string — target object/node/pair whose response is measured.
- `epsilon_min` — float — smallest epsilon used for finite-difference response.
- `epsilon_max` — float — largest epsilon used in the local response estimate.
- `response_slope` — float — estimated small-epsilon response slope.
- `response_integral` — float — optional integrated response over epsilon sweep.
- `response_peak_epsilon` — float or null — epsilon value at maximum observed response.
- `rho_tau` — float — normalized pairwise response score.
- `tau_rel_candidate` — float or null — preliminary monotone transform of `rho_tau`.
- `normalization_family` — string — normalization rule used.
- `status` — string — diagnostic status label for the pair.

### 7.2 `tau_epsilon_response_sweep.csv`

- `source_id` — string — source object/node/pair for perturbation.
- `target_id` — string — target object/node/pair.
- `epsilon` — float — perturbation strength.
- `response_value` — float — raw response value.
- `response_value_normalized` — float — normalized response value.
- `observable_family` — string — local observable used.
- `perturbation_family` — string — perturbation operator family.
- `status` — string — row-level diagnostic status.

### 7.3 `tau_rel_candidate_matrix.csv`

- `source_id` — string — matrix row/source object.
- `target_id` — string — matrix column/target object.
- `tau_rel_candidate` — float — candidate relational-delay value.
- `rho_tau` — float — underlying response score.
- `distance_D` — float or null — existing distance-like comparator if available.
- `S_rel2_candidate` — float or null — optional interval-like candidate value.
- `c_eff` — float or null — scale parameter used if `S_rel2_candidate` is computed.
- `status` — string — diagnostic status.

### 7.4 `summary.json`

- `block_id` — string — fixed block identifier, expected `QSB-ST-LIC01`.
- `run_id` — string — specific run label.
- `status` — string — run status.
- `construction_route` — string — selected tau-rel construction route.
- `baseline_source` — string — baseline input source.
- `perturbation_family` — string — perturbation operator family.
- `observable_family` — string — response observable family.
- `epsilon_values` — list[float] — epsilon sweep values.
- `pair_count` — integer — number of source-target pairs analyzed.
- `tau_rel_constructed` — boolean — whether a tau candidate matrix was produced.
- `S_rel2_constructed` — boolean — whether an interval-like candidate was produced.
- `claim_boundary` — string — explicit bounded claim statement.
- `warnings` — list[string] — warnings and known limitations.

---

## 8. Acceptance checks

A first LIC01 synthetic run should pass the following minimal checks:

1. Repo status is clean before implementation.
2. All files are newly created unless an explicit edit instruction exists.
3. Config parses successfully.
4. Runner executes without hidden external dependencies.
5. `summary.json` exists and includes required keys.
6. CSV files parse with Python `csv.DictReader`.
7. Pairwise output has nonzero row count.
8. Epsilon values in outputs match resolved config.
9. Result readout separates:
   - Befund,
   - Interpretation,
   - Hypothese,
   - Offene Lücke,
   - Claim Boundary.
10. Claim-risk grep finds no unbounded physical validation language.

Suggested claim-risk grep terms:

```bash
grep -RniE "proved|proven|validates spacetime|physical time|proper time|Lorentzian metric derived|speed of light|experimental validation|real-data validation|superluminal" docs/ runs/ || true
```

---

## 9. Defensive interpretation template

### Befund

The runner produced reproducible synthetic response scores under a fixed perturbation family and epsilon sweep.

### Interpretation

A structured response pattern may support `tau_rel` as a candidate relational-delay diagnostic within the synthetic QSB-ST framework.

### Hypothese

If the response score remains stable under controls and parameter variation, it may become a useful internal companion to the existing distance-like quantity `D(A,B)`.

### Offene Lücke

The construction does not yet show uniqueness, physical time interpretation, Lorentzian structure, or empirical relevance.

### Claim Boundary

LIC01 remains a synthetic diagnostic construction route. It does not establish a spacetime metric, proper time, relativistic interval, or physical validation.

---

## 10. Recommended next action

After committing this design note, proceed to a config scaffold only.

Recommended next file:

```text
data/qsb_st_lic01_tau_epsilon_phase_response_config.yaml
```

Do not create the runner before the config fields and output schema have been accepted.
