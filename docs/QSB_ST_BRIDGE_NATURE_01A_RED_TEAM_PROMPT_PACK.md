# QSB-ST-BRIDGE-NATURE-01A Red-Team Prompt Pack

## 1. Purpose

This document opens the Gutachterflur for QSB-ST-BRIDGE-NATURE-01A.

This is a prompt pack only. It creates no new numerics, no implementation, no WIFM02, no Bridge claim, no validation of a physical model, and no diagnostic specificity. Its purpose is to expose weaknesses, hidden assumptions, missing controls, unclear definitions, possible artifacts, and possible literature/context connections.

## 2. Current anchor and source basis

Current anchor:

`162097e Add QSB-ST COMP01 WIFM01D consolidation gate note`

Inspected source basis:

- WIFM01 result note: `docs/QSB_ST_COMP01_WIFM01_MINIMAL_METRIC_RESULT_NOTE.md`
- WIFM01B result note: `docs/QSB_ST_COMP01_WIFM01B_MINIMAL_METRIC_SENSITIVITY_SWEEP_RESULT_NOTE.md`
- WIFM01C result note: `docs/QSB_ST_COMP01_WIFM01C_ADVERSARIAL_AMBIGUITY_STRESS_RESULT_NOTE.md`
- WIFM01D gate note: `docs/QSB_ST_COMP01_WIFM01D_CONSOLIDATION_AND_GATE_NOTE.md`
- WIFM01 summary: `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/summary.json`
- WIFM01B summary: `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/summary.json`
- WIFM01C summary: `runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open/summary.json`

## 3. Minimal project briefing for reviewers

QSB-ST investigates whether relational wave/fingerprint structures can become geometrically readable. The current focus is not physical spacetime but a diagnostic Fingerprint-Raum.

WIFM distinguishes Fingerprint-Raum from Identitäts-Raum. A WIFM point is currently treated as a relational wave-pair fingerprint. Phase-like coordinates are treated circular/compact. Non-compact coordinates include `delta_k`, slope/intercept-like local form, and amplitude-type differences.

The current route is synthetic diagnostic testing only. Fingerprint-Raum and Identitäts-Raum remain distinct. The WIFM metric is diagnostic, not a physical spacetime metric. Phase is synthetic diagnostic, not physical phase. The Bridge is not confirmed. Diagnostic specificity is not established. The action/phase relation -> relational fingerprint structure -> geometrically readable diagnostic space idea is project-internal theory intuition only.

## 4. What WIFM01–D actually shows

WIFM01:

- 10 fingerprints.
- 5 comparison pairs.
- all_expected_behaviors_met: true
- warning_review_count: 0
- phase_wrap_case_count: 1
- phase_wrap_corrected_count: 1
- noncompact_separation_case_count: 2
- noncompact_separation_preserved_count: 2
- mixed_ambiguity_case_count: 1
- mixed_ambiguity_preserved_count: 1

WIFM01B:

- 19 curated variants.
- 10 weight variants.
- 9 scale variants.
- variant_count: 19
- all_variants_expected_behaviors_met: true
- variant_warning_review_count: 0
- variant_failure_review_count: 0
- phase_wrap_all_variants_corrected: true
- noncompact_separation_all_variants_preserved: true
- mixed_ambiguity_all_variants_preserved: true

WIFM01C:

- 24 stress fingerprints.
- 12 pair comparisons.
- 7 explicit stress cases.
- 5 baseline replay cases.
- stress_pair_count: 12
- expected_adversarial_behaviors_met: true
- diagnostic_failure_review_count: 0
- unexpected_overcleaning_clean_label_count: 0
- overcleaning_risk_detected_count: 1
- baseline_replay_expected_behavior_met: true

WIFM01D:

- WIFM01 minimal line is closed.
- No WIFM01E should be opened by default.
- WIFM02 is not opened by this prompt pack.
- Possible WIFM02 only after explicit scope decision.

## 5. What WIFM01–D explicitly does not show

- No real data.
- No real wavefunction input.
- No physical phase reconstruction.
- No physical compact dimensions.
- No physical metric.
- No physical spacetime geometry.
- No Lorentzian metric.
- No Hilbert-space reconstruction.
- No diagnostic specificity.
- No Bridge confirmation.
- No proof of wave identity.
- No Planck-space derivation.
- No string compactification claim.

## 6. Core question for the Gutachterflur

Is WIFM01–D merely a clean diagnostic fingerprint test, or does it expose a credible route toward understanding the nature of the Bridge?

Broader defensive question:

Can geometrically readable diagnostic structure emerge from quantized action/phase-related relational fingerprints without prematurely claiming physical spacetime, Bridge confirmation, or quantum gravity?

## 7. Shared red-team rules

- Be critical, not encouraging.
- Identify hidden assumptions.
- Identify possible metric artifacts.
- Identify tuning risks.
- Identify missing controls.
- Distinguish fatal flaw / serious weakness / fixable gap / future research question.
- Do not overstate support.
- Do not treat synthetic toy success as validation of a physical model.
- Do not collapse Fingerprint-Raum and Identitäts-Raum.
- Preserve claim boundaries.
- Suggest concrete falsification or stress tests where possible.

## 8. Prompt A — Hard Method Red Team

Ready-to-copy prompt:

```text
You are a hard-method red-team reviewer. Do not try to confirm the project. Your task is to find the strongest methodological weaknesses in the QSB-ST WIFM01–D line.

Project briefing:
- WIFM01 used 10 synthetic fingerprints and 5 comparison pairs.
- WIFM01B used 19 curated weight/scale variants.
- WIFM01C used 24 stress fingerprints, 12 pair comparisons, 7 explicit stress cases, and 5 baseline replay cases.
- WIFM01D closed the WIFM01 minimal line.
- The result is synthetic diagnostic only.
- Fingerprint-Raum and Identitäts-Raum remain distinct.
- The metric is diagnostic, not a physical spacetime metric.
- The Bridge is not confirmed and diagnostic specificity is not established.

Please answer critically:
1. What is the strongest methodological criticism of WIFM01–D?
2. Could WIFM01C be toy-designed to pass?
3. Are the labels merely restating the construction?
4. Are weight/scale choices hiding the real issue?
5. Are phase compactness and circular metric trivial rather than informative?
6. What counterexamples would break the line?
7. What controls are missing?
8. What would be required before opening WIFM02?
9. What should not be claimed?

Classify each issue as fatal flaw, serious weakness, fixable gap, or future research question. Suggest concrete tests that would expose artifacts.
```

## 9. Prompt B — Theory Red Team

Ready-to-copy prompt:

```text
You are a theoretical-physics red-team reviewer. Your role is to identify conceptual category errors, overreach, and missing definitions in the QSB-ST WIFM01–D line.

Project briefing:
- WIFM separates Fingerprint-Raum from Identitäts-Raum.
- A point in Fingerprint-Raum is currently treated as a relational wave-pair fingerprint.
- Phase-like coordinates are handled circularly.
- Non-compact coordinates remain ordinary diagnostic axes.
- The route is synthetic diagnostic testing, not a physical spacetime metric.
- The Bridge is not confirmed.

Please critique:
1. Is the distinction Fingerprint-Raum / Identitäts-Raum meaningful?
2. Is a relational wave-pair fingerprint a defensible point object?
3. Is circular phase handling theoretically natural or merely computational?
4. What is required to move from diagnostic metric to geometry?
5. What would be needed before connecting this to pregeometry, emergent spacetime, or quantum gravity?
6. Where are the conceptual category errors?
7. What must remain parked?

Do not soften the critique. Separate bounded methodological value from theory claims that are not currently supported.
```

## 10. Prompt C — Literature / Deep Research Map

Ready-to-copy prompt:

```text
You are doing a literature/context map, not a confirmation search. Map the QSB-ST WIFM01–D idea against established areas and point out both useful analogies and major differences.

Core project idea to contextualize:
- Diagnostic Fingerprint-Raum for relational wave-pair fingerprints.
- Circular/compact handling of phase-like coordinates.
- Non-compact diagnostic axes for delta_k, local form, and amplitude-type differences.
- Project-internal outlook: action/phase relation -> relational fingerprint structure -> geometrically readable diagnostic space.
- No Bridge confirmation, no diagnostic specificity, no physical spacetime metric.

Research axes:
- action-phase relation and geometry
- path integral phase S/hbar
- geometric phase / Berry phase / holonomy
- phase-space geometry
- information geometry
- relational quantum mechanics
- quantum reference frames
- modular variables / compact phase coordinates
- spectral geometry
- graph-based relational diagnostics
- pregeometry and emergent spacetime
- holography / description-level separation
- AdS/CFT as description-level separation only
- shape from spectra
- quantum graph / network geometry

Please provide:
1. Established references.
2. Possible analogies.
3. Major differences from WIFM01–D.
4. Red flags.
5. Terminology risks.
6. Which references should be used only as background.
7. Which references should be avoided as support.

Do not turn analogies into evidence. Keep the map defensive.
```

## 11. Prompt D — Louis-style cautious theory commentary

Ready-to-copy prompt:

```text
Please respond as a cautious European-style theory colleague: collegial, skeptical, constructive, no hype, and human readable.

Context:
- QSB-ST WIFM01–D is a synthetic diagnostic line.
- It treats relational wave-pair fingerprints as points in a diagnostic Fingerprint-Raum.
- It handles phase-like coordinates circularly and keeps non-compact diagnostic differences visible.
- WIFM01D closes the minimal line.
- The action/phase relation -> relational fingerprint structure -> geometrically readable diagnostic space idea is project-internal theory intuition only.

Please comment:
1. What is intellectually promising?
2. What sounds overreaching?
3. What would a cautious theorist accept as a bounded methodological result?
4. What would trigger immediate skepticism?
5. How should the action/phase intuition be phrased defensively?
6. What wording would be suitable for an internal theory note?

Keep the answer plain and precise. Do not hype. Do not claim physical spacetime, Bridge confirmation, or diagnostic specificity.
```

## 12. Prompt E — Claim-risk and wording audit

Ready-to-copy prompt:

```text
You are a wording and claim-risk auditor. Review QSB-ST WIFM01–D language for phrases that could overclaim. Identify risky phrases and rewrite them defensively.

Risky phrase examples:
- Bridge confirmation
- emergent spacetime
- Planck-space derivation
- physical phase
- compact dimensions
- quantum gravity evidence
- proof of wave identity
- Hilbert-space reconstruction
- metric of spacetime
- from h to space

Require safer replacements such as:
- diagnostic fingerprint geometry
- geometrically readable diagnostic structure
- synthetic toy setting
- project-internal hypothesis
- action/phase-related intuition
- no validation of a physical model
- no diagnostic specificity

For each risky phrase:
1. Explain why it is risky.
2. Suggest a safer replacement.
3. State the strongest claim that remains allowed.
4. State what must not be claimed.
```

## 13. Response template for reviewers

Reviewers should fill this template:

```text
Summary judgment:

Strongest criticism:

Possible artifact mechanisms:

Missing controls:

Conceptual category risks:

Literature connections:

Literature warnings:

What can be claimed:

What cannot be claimed:

Suggested next test:

Gate recommendation:
- stop WIFM line
- keep WIFM01 closed, open WIFM02 with narrow scope
- move to BRIDGE-NATURE-01 synthesis
- return to earlier route
- insufficient information
```

## 14. Evaluation rubric for incoming reviews

Score each dimension from 0 to 3:

- Methodological validity: 0 means unusable method; 3 means bounded method is coherent for its stated diagnostic purpose.
- Artifact risk: 0 means low apparent artifact risk; 3 means high risk that construction, labels, weights, or toy cases drive the result.
- Conceptual clarity: 0 means unclear or category-confused; 3 means distinctions are sharp and consistently used.
- Literature alignment: 0 means weak or misleading context; 3 means careful alignment with relevant background and clear differences.
- Claim safety: 0 means high overclaim risk; 3 means conservative, bounded wording.
- Next-step usefulness: 0 means no actionable critique; 3 means concrete tests, controls, or gate recommendations.

High artifact risk lowers readiness. High claim safety does not compensate for weak methodology. A useful review may be sharply negative if it identifies concrete failure modes.

## 15. Synthesis plan after reviews

After collecting responses, Nova should produce:

`docs/QSB_ST_BRIDGE_NATURE_01B_RED_TEAM_AND_DEEP_RESEARCH_SYNTHESIS_GATE.md`

Future synthesis should include:

- Befund.
- Red-team criticisms.
- Literature/context map.
- Claim-risk findings.
- Revised hypothesis.
- Gate decision.
- Whether WIFM02 should be opened.
- Whether BRIDGE-NATURE-02 should be defined.
- Whether to stop/park this line.

BRIDGE-NATURE-02 is not opened here. WIFM02 is not opened here.

## 16. Claim Boundary

- Prompt pack only.
- No new result.
- No physical phase.
- No physical metric.
- No physical manifold.
- No physical compact dimensions.
- No Planck-space claim.
- No string compactification claim.
- No validation of a physical model.
- No diagnostic specificity.
- No Hilbert-space reconstruction.
- No conversion of fingerprint metric into spacetime metric.
- No proof of wave identity.
- No Bridge confirmation.
- WIFM02 is not opened here.
- BRIDGE-NATURE-02 is not opened here.
- specificity_established: false
- phase_is_physical: false
- phase_is_synthetic_diagnostic: true
- physical_metric_established: false
- physical_compact_dimensions_established: false
- hilbert_space_reconstruction: false
- bridge_confirmation: false

## 17. Files created / checked

This task creates only:

- `docs/QSB_ST_BRIDGE_NATURE_01A_RED_TEAM_PROMPT_PACK.md`

Checked docs:

- `docs/QSB_ST_COMP01_NEXT_ROUTE_SEED_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE.md`
- `docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_SPEC.md`
- `docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_RUNNER_SPEC.md`
- `docs/QSB_ST_COMP01_WIFM01_MINIMAL_METRIC_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01_WIFM01B_MINIMAL_METRIC_SENSITIVITY_SWEEP_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01_WIFM01C_ADVERSARIAL_AMBIGUITY_STRESS_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01_WIFM01D_CONSOLIDATION_AND_GATE_NOTE.md`

Checked summaries:

- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/summary.json`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/summary.json`
- `runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open/summary.json`
