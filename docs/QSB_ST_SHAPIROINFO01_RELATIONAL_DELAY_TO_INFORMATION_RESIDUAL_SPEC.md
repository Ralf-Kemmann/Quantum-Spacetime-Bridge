# QSB-ST-SHAPIROINFO01 — Relational Delay to Information Residual Spec

**Document type:** QSB-ST specification note  
**Status:** planning / diagnostic specification only  
**Created:** 2026-05-28  
**Repo target:** `docs/QSB_ST_SHAPIROINFO01_RELATIONAL_DELAY_TO_INFORMATION_RESIDUAL_SPEC.md`  
**Current anchor dependency:** `QSB_ST_INTERFACE03_RT_QM_CAUSALITY_ROSETTA_TRANSLATOR_SPEC.md`  

---

## 0. Purpose

This note specifies a cautious diagnostic route from known relativistic delay language toward a possible information-residual search question.

The document does **not** modify the standard Shapiro effect. It does **not** reinterpret general relativity. It does **not** introduce a new physical detection claim.

The purpose is narrower:

> Can a standard relativistic propagation-delay setting be used as a controlled diagnostic environment for asking whether any reproducible signal-fingerprint residual remains after established corrections are accounted for?

The intended role is a first use case for the QSB-ST interface vocabulary developed in `INTERFACE03`.

---

## 1. Project context

QSB-ST is framed as an interface layer between two mature theory domains:

- relativistic geometry / causal propagation on the RT side,
- quantum and wave-structure language on the QM side.

The project does not treat either side as broken. The working picture is technical rather than grand-unifying: two well-tested systems may require a translator layer because their base languages differ.

`INTERFACE03` introduced three relevant elements:

1. vocabulary mapping by structural role, not direct identity;
2. causality formation as an interface problem;
3. `c` as a Rosetta-style candidate connecting causal geometry with wave, phase, frequency, wavelength, energy, and momentum language.

`SHAPIROINFO01` now uses a known relativistic delay setting as a first cautious diagnostic testbed.

---

## 2. Standard Shapiro effect boundary

The Shapiro effect is treated here as a standard general-relativistic propagation-delay phenomenon.

Within this note:

- the standard relativistic delay is accepted as background physics;
- the known geometrical interpretation is not challenged;
- the delay term is not replaced by a QSB-ST term;
- any later diagnostic must subtract or model the known delay before any extra question is asked.

The QSB-ST question starts only after the standard physics layer is respected.

---

## 3. Interface question

The core question is:

> After standard propagation, medium, source, instrument, and modelling effects are accounted for, does any reproducible information-bearing fingerprint difference remain between two otherwise comparable signals?

This is not a claim that such a residual exists.

It is a controlled search question.

---

## 4. Signal-pair model

The diagnostic model begins with two signal records.

### 4.1 Reference signal A

`A` is a reference signal travelling through a less perturbed or better-controlled propagation environment.

It may be:

- an actual comparison path,
- a calibrated reference channel,
- a model-corrected baseline,
- or a synthetic benchmark constructed from known propagation physics.

### 4.2 Affected signal B

`B` is a signal travelling through a stronger gravitational or geometrically relevant environment.

It is not assumed to carry any non-standard effect. It is only the candidate signal whose record must be compared against `A` after corrections.

### 4.3 Minimal comparison form

The intended baseline form is:

```text
B_observed = A_reference + known_effects + residual
```

The diagnostic question concerns the last term only after the known-effect layer has been treated carefully.

---

## 5. Known-effect correction layer

Before any QSB-ST residual language is allowed, the following families must be treated as known or conventional correction layers.

### 5.1 Relativistic propagation

- Shapiro delay,
- geometric path length,
- source/observer geometry,
- ephemeris and coordinate-model dependencies,
- gravitational redshift or related standard relativistic terms where applicable.

### 5.2 Medium and propagation environment

- plasma dispersion,
- interstellar or interplanetary medium effects,
- atmospheric or ionospheric delay,
- scattering,
- absorption,
- frequency-dependent phase shifts.

### 5.3 Source behaviour

- source variability,
- intrinsic modulation drift,
- emission mechanism variability,
- pulse-profile evolution,
- spectral evolution.

### 5.4 Instrument and measurement chain

- calibration drift,
- clock and timing errors,
- detector response,
- sampling rate effects,
- digitisation artefacts,
- filtering and pipeline effects,
- synchronisation and reference-frame handling.

### 5.5 Modelling and analysis choices

- window selection,
- alignment method,
- de-trending,
- noise model,
- null construction,
- control selection,
- parameter degeneracy.

A residual candidate is not admissible until these layers are explicitly addressed.

---

## 6. Candidate observables

This section lists possible observable families. They are placeholders for future design, not finished measurement definitions.

### 6.1 Timing layer

- arrival-time difference,
- residual delay after known corrections,
- time-of-arrival pattern deformation,
- multi-frequency timing consistency.

### 6.2 Phase layer

- phase residual,
- phase drift,
- phase curvature,
- coherence change,
- cross-correlation phase offset.

### 6.3 Frequency and spectral layer

- frequency shift residual,
- spectral-line deformation,
- bandwidth-dependent residual structure,
- sideband changes,
- spectral entropy or shape diagnostics.

### 6.4 Polarisation layer

- polarisation-angle residual,
- mode mixing,
- birefringence-like artefact screening,
- Faraday-rotation correction residuals.

### 6.5 Modulation and information layer

- modulation-pattern stability,
- encoded waveform fingerprint,
- pulse-shape residual,
- cross-channel mutual information,
- compression-distance or pattern-similarity diagnostics,
- feature-space residual after known corrections.

### 6.6 Relational fingerprint layer

- relation graph between time, frequency, phase, and amplitude features,
- neighbourhood drift in feature space,
- spectral-graph change,
- local compatibility-map residual,
- structured deviation from matched controls.

The relational fingerprint layer is the most directly QSB-ST-relevant layer, but it is also the most vulnerable to false structure from preprocessing choices. It therefore requires hostile controls before interpretation.

---

## 7. Residual logic

### 7.1 Null-consistent outcome

If the comparison is consistent with:

```text
B_observed = A_reference + known_effects
```

then the result is:

```text
no additional information-residual candidate observed
```

This is a valid outcome and must be documented as such.

### 7.2 Candidate-residual outcome

If the comparison is more consistent with:

```text
B_observed = A_reference + known_effects + structured_residual
```

then the residual may only be labelled:

```text
candidate information residual
```

This label is permitted only if the residual is:

- reproducible,
- robust under preprocessing variation,
- stable across relevant controls,
- not explained by standard correction families,
- not caused by source, medium, instrument, or model artefacts,
- not a single-channel anomaly,
- not a post-hoc selected pattern.

### 7.3 Stronger language gate

No stronger language is permitted in this block.

The highest allowed interpretation is a candidate diagnostic residual requiring further control and independent replication.

---

## 8. Connection to causality formation

`INTERFACE03` framed causality formation as a possible transition:

```text
correlation -> stable relation -> directed order -> causally readable geometry
```

`SHAPIROINFO01` does not test this full transition.

It only asks whether a standard propagation-delay environment can provide a structured setting in which timing, phase, frequency, modulation, and relational fingerprints may be compared under a known relativistic effect.

The causal-language connection is therefore indirect:

- standard Shapiro delay belongs to the RT propagation layer;
- wave, phase, and frequency observables belong to the QM/wave-language side;
- a residual fingerprint, if ever observed, would be a candidate interface diagnostic, not a direct causality-formation result.

---

## 9. Rosetta role of `c`

In `INTERFACE03`, `c` was treated as a Rosetta-style interface candidate:

```text
c = lambda * f
c = omega / k
c = E / p   [massless limit]
c = lambda_C * f_C   [Compton-scale relation]
```

For this ShapiroInfo specification, the relevance is not the numerical value of `c`.

The relevance is its structural role:

- on the RT side, `c` sets the causal propagation norm;
- on the wave side, `c` connects wavelength and frequency;
- on the energy-momentum side, `c` connects energy and momentum for massless carriers;
- in the interface vocabulary, `c` marks where propagation, phase, and causal readability share a common conversion role.

This motivates looking at signal records not only as arrival times, but also as coupled phase-frequency-pattern objects.

---

## 10. Old-trace integration

This block should later connect to earlier project traces without importing unsupported claims.

Relevant trace families include:

- relational delay and causality without time;
- earlier delay-map sketches;
- Shapiro-delay illustration scripts;
- de-Broglie phase structure;
- interference to correlations;
- correlations to relational geometry;
- the `INTERFACE01` / `INTERFACE02` / `INTERFACE03` line.

Old files should be treated as conceptual and methodological traces unless separately rechecked.

No old result should be upgraded into evidence by citation alone.

---

## 11. Minimal future record schema

A later implementation or dataset-facing block should not begin with raw interpretation. It should begin with a minimal record schema.

Recommended future fields:

| Field name | Type | Description |
|---|---:|---|
| `record_id` | string | Unique signal-pair or comparison record identifier. |
| `signal_a_id` | string | Reference signal identifier. |
| `signal_b_id` | string | Affected or comparison signal identifier. |
| `source_type` | string | Source class or synthetic source class. |
| `path_model_id` | string | Identifier for propagation or geometry model. |
| `standard_delay_model` | string | Standard delay model used for correction. |
| `medium_model` | string | Medium/plasma/atmospheric correction model. |
| `instrument_model` | string | Instrument/calibration model. |
| `observable_family` | string | Timing, phase, frequency, polarisation, modulation, or relational fingerprint. |
| `observable_name` | string | Specific observable. |
| `raw_difference` | float | Raw A/B difference before full correction. |
| `corrected_difference` | float | Difference after known-effect correction. |
| `residual_score` | float | Diagnostic residual score. |
| `control_family` | string | Control/null family used. |
| `control_result` | string | Summary label from controls. |
| `candidate_residual_flag` | boolean | True only for controlled candidate residuals. |
| `standard_explanation_flag` | boolean | True if standard correction families explain the difference. |
| `notes` | string | Human-readable caution notes. |

This schema is intentionally minimal and conservative.

---

## 12. Hostile controls required before interpretation

Any later computational block must include hostile controls.

Minimum control families:

1. **Null timing controls**  
   Matched records with no expected extra residual.

2. **Medium-dominated controls**  
   Cases where propagation medium effects should dominate apparent residuals.

3. **Instrument controls**  
   Calibration and pipeline artefact tests.

4. **Source-variability controls**  
   Tests where intrinsic source changes mimic signal fingerprints.

5. **Permutation / alignment controls**  
   Tests for spurious structure created by windowing, alignment, or phase matching.

6. **Synthetic injected controls**  
   Known injected differences used to test whether the pipeline detects what it should detect and rejects what it should reject.

No residual interpretation is allowed without controls.

---

## 13. Befund / Interpretation / Hypothese / Offene Lücke / Claim Boundary

### 13.1 Befund

A known relativistic delay setting provides a structured environment where propagation time, phase, frequency, modulation, and relational fingerprints can in principle be compared between reference and affected signals.

### 13.2 Interpretation

QSB-ST can use such a setting as a diagnostic interface testbed, provided the standard physical layers are respected first.

### 13.3 Hypothese

A possible information-residual search may be meaningful if a signal travelling through a different geometrical or gravitational environment retains a reproducible fingerprint difference after known effects are accounted for.

### 13.4 Offene Lücke

No dataset, observable implementation, control family, or measured residual is established by this note.

The main open tasks are:

- define signal-pair datasets or synthetic benchmarks;
- define correction models;
- define observables;
- define hostile controls;
- define admissible null outcomes;
- define reproducibility criteria.

### 13.5 Claim Boundary

This note is a specification only.

Allowed labels:

- diagnostic search question;
- candidate residual, only after controls;
- interface vocabulary use case;
- planning-level ShapiroInfo route.

Disallowed upgrades:

- no Bridge confirmation;
- no physical validation statement;
- no replacement of general relativity;
- no replacement of quantum mechanics;
- no new causal theory;
- no established spacetime-emergence result;
- no explanation of the numerical value of `c`.

---

## 14. Required flags

For this block, all claim-status flags remain false.

```text
bridge_confirmation_flag=false
physical_validation_flag=false
diagnostic_specificity_flag=false
spacetime_emergence_flag=false
qg_theory_claim_flag=false
c_value_explanation_flag=false
shapiro_reinterpretation_flag=false
```

---

## 15. Acceptance checks

### 15.1 File check

```bash
test -f docs/QSB_ST_SHAPIROINFO01_RELATIONAL_DELAY_TO_INFORMATION_RESIDUAL_SPEC.md
```

### 15.2 Claim-risk grep

Use a split shell pattern so the check command does not become self-matching text in documentation.

```bash
PATTERN="pro""ves|derives ""c|explains the ""value of c|validated ""physics|confirms the ""Bridge|establishes ""spacetime|solves ""quantum gravity|Theory of ""Everything|break""through"

grep -Eni "$PATTERN" docs/QSB_ST_SHAPIROINFO01_RELATIONAL_DELAY_TO_INFORMATION_RESIDUAL_SPEC.md || true
```

Expected result:

```text
no entries
```

### 15.3 Whitespace check

```bash
git diff --check
```

Expected result:

```text
no output
```

### 15.4 Status check

```bash
git status --short
```

Expected result before commit:

```text
?? docs/QSB_ST_SHAPIROINFO01_RELATIONAL_DELAY_TO_INFORMATION_RESIDUAL_SPEC.md
```

---

## 16. Suggested commit message

```text
Add QSB-ST ShapiroInfo residual specification
```

---

## 17. Next possible blocks

After this specification is committed, the next possible blocks are:

1. `QSB-ST-SHAPIROINFO02` — observable and control taxonomy;
2. `QSB-ST-SHAPIROINFO03` — synthetic signal-pair benchmark design;
3. `QSB-ST-SHAPIROINFO04` — minimal record-schema implementation;
4. `QSB-ST-SHAPIROINFO05` — hostile-control runner design.

No implementation should begin until the observable taxonomy and control logic are specified.

---

## 18. One-sentence summary

`SHAPIROINFO01` treats the standard Shapiro-delay setting as a cautious diagnostic environment for asking whether any controlled, reproducible information-fingerprint residual remains after known relativistic, medium, source, instrument, and modelling effects are accounted for.
