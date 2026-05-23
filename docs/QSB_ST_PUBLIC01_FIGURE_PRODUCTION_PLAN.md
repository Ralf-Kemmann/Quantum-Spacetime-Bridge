# QSB-ST PUBLIC01 Figure Production Plan

## 1. Purpose

This document plans the visual layer for the PUBLIC01 research note.

The core idea is simple: the figures should help readers follow the method gate from diagnostic readability to identity-space safeguards. They should make the red thread visible before the text becomes technical.

This is a figure-production plan only. No figures are created here.

## 2. Visual publication mode

Target mode:

- Spektrum der Wissenschaft / Scientific American style
- visually guided public research note
- clear orientation before technical detail
- calm, curious, and disciplined
- explanatory diagrams rather than decorative artwork

The figures should help a reader understand why IDSPACE/CPNS exists: not as machinery for its own sake, but as a safeguard against over-reading diagnostic fingerprints.

## 3. Visual style guide

Use a restrained visual language:

- clean line diagrams
- few colors, with semantic meaning
- readable labels
- no dark mystery aesthetics
- no cosmic spectacle
- no dramatic physics-result framing
- no ornamental complexity

Recommended visual tone:

- one main accent color for the method path
- a second color for guardrails or boundaries
- neutral background
- compact explanatory captions
- enough white space for public readability

The figures should invite curiosity and orientation, not suggest completion.

## 4. Figure list overview

Required figures:

1. Figure 1: Red-thread flow diagram
2. Figure 2: Fingerprint-Raum vs Identitaets-Raum
3. Figure 3: Same-looking fingerprints and unresolved ambiguity
4. Figure 4: CPNS06 validation card

Optional figure:

5. Figure 5: IDSPACE/CPNS guardrail

The four required figures should be enough for a first visual public draft. Figure 5 can be used if the layout benefits from a warmer orientation image.

## 5. Figure 1: Red-thread flow diagram

Figure title:

```text
The method-gate route from WIFM01-D to CPNS06
```

Purpose:

Show the public red thread of the current repository line.

Visual brief:

A left-to-right route diagram with five stations:

```text
WIFM01-D closure -> BRIDGE-NATURE-01B gate -> IDSPACE/CPNS definitions -> CPNS04 schema scaffold -> CPNS06 validator
```

The route should look like a cautious method path, not a ladder of discoveries. Each node should have one short public label.

Suggested labels:

- WIFM01-D: minimal diagnostic route closed
- BRIDGE-NATURE-01B: gate held
- IDSPACE/CPNS: identity and ambiguity safeguards
- CPNS04: schema scaffold
- CPNS06: schema/example validator

Caption draft:

Figure 1. The current QSB-ST method-gate route. WIFM01-D closes the minimal synthetic diagnostic line; BRIDGE-NATURE-01B prevents automatic escalation; IDSPACE and CPNS then introduce identity-space and ambiguity safeguards before CPNS04 and CPNS06 make the schema scaffold auditable.

Allowed support:

The figure may support the sequence and public red thread of the method gate.

Must not imply:

It must not imply Bridge confirmation, diagnostic specificity, physical validation, or a discovery pipeline.

Visual style notes:

Use a simple horizontal route with clear nodes and modest arrows. Avoid glowing arrows, triumphant progression cues, or achievement badges.

Later file-name suggestion:

```text
figures/public01_figure01_red_thread_flow.png
```

## 6. Figure 2: Fingerprint-Raum vs Identitaets-Raum

Figure title:

```text
Readable fingerprints are not identity resolution
```

Purpose:

Show the distinction between the diagnostic fingerprint layer and the operational identity layer.

Visual brief:

A two-layer diagram. The lower layer is Fingerprint-Raum, with diagnostic points, distances, and neighborhoods. The upper layer is Identitaets-Raum, with decision states. Between them, show a guarded passage requiring maps, equivalence rules, and ambiguity handling.

Suggested labels:

- Fingerprint-Raum: diagnostic readability
- Identitaets-Raum: identity-level decision layer
- representation map
- observation map
- equivalence relation
- ambiguity state

Caption draft:

Figure 2. Fingerprint-Raum is the diagnostic space in which relational fingerprints may become readable. Identitaets-Raum is the operational layer where identity candidates are compared. The passage from one layer to the other requires declared maps, equivalence rules, and ambiguity handling.

Allowed support:

The figure may support the distinction between diagnostic structure and identity-level interpretation.

Must not imply:

It must not imply that a geometric-looking diagnostic space is already a physical space or that readability resolves identity.

Visual style notes:

Use two calm horizontal bands or layers. Make the gap between them visible. Avoid making the upper layer look like a final truth layer.

Later file-name suggestion:

```text
figures/public01_figure02_fingerprint_vs_identity_space.png
```

## 7. Figure 3: Same-looking fingerprints and unresolved ambiguity

Figure title:

```text
Same-looking can remain unresolved
```

Purpose:

Show that ambiguity is a valid result state.

Visual brief:

Show two or more diagnostic fingerprints that are visually close or nearly identical. Connect them to a decision marker labeled `ambiguous_unresolved`. Add a small note that IDSPACE definitions and CPNS constraints are needed before alternatives can be counted or bounded.

Suggested labels:

- same-looking fingerprint A
- same-looking fingerprint B
- current observables do not separate
- ambiguous_unresolved
- constraints not yet sufficient

Caption draft:

Figure 3. Same-looking or near-looking fingerprints may remain unresolved. In QSB-ST, ambiguity is kept as a valid state until identity definitions and CPNS constraints determine what alternatives remain possible.

Allowed support:

The figure may support the idea that `ambiguous_unresolved` is valid, informative, and not a failed check.

Must not imply:

It must not imply that unresolved cases support or refute a physical interpretation.

Visual style notes:

Use paired or clustered marks with small uncertainty brackets. Avoid warning colors that make ambiguity look like an error.

Later file-name suggestion:

```text
figures/public01_figure03_unresolved_ambiguity.png
```

## 8. Figure 4: CPNS06 validation card

Figure title:

```text
What CPNS06 checked
```

Purpose:

Summarize the actual CPNS06 validation result without overstating it.

Visual brief:

A compact validation card with four rows:

```text
passed=true
failed_checks=[]
warning=degeneracy placeholders only
all boundary flags=false
```

The card should be labeled clearly:

```text
schema/example consistency only
```

Suggested labels:

- CPNS06 validator
- schema/example consistency only
- passed=true
- failed_checks=[]
- placeholder degeneracy only
- boundary flags=false
- ambiguous_unresolved accepted
- invalid_outside_scope is non-success

Caption draft:

Figure 4. CPNS06 validates the CPNS04 schema and illustrative examples for internal consistency. The run passed its schema checks, but the degeneracy fields remain placeholders and all claim-boundary flags remain false.

Allowed support:

The figure may support the narrow CPNS06 result: schema/example consistency validation.

Must not imply:

It must not imply real degeneracy measurement, Bridge confirmation, diagnostic specificity, or physical validation.

Visual style notes:

Use a small card or dashboard style with sober colors. Avoid a large green success emblem. The warning row should be visible and calm.

Later file-name suggestion:

```text
figures/public01_figure04_cpns06_validation_card.png
```

## 9. Optional Figure 5: IDSPACE/CPNS guardrail

Figure title:

```text
The guardrail between readability and identity claims
```

Purpose:

Give a visually accessible summary of the whole safeguard idea.

Visual brief:

On the left, show diagnostic readability: structured fingerprints, distances, or neighborhoods. On the right, show stronger identity claims. Between them, place IDSPACE/CPNS as the guardrail requiring definitions, constraints, and ambiguity checks before crossing.

Suggested labels:

- diagnostic readability
- IDSPACE definitions
- CPNS constraints
- ambiguity check
- identity claim
- guardrail

Caption draft:

Figure 5. IDSPACE/CPNS acts as a methodological guardrail between readable diagnostic fingerprints and stronger identity-level claims. Its purpose is to slow interpretation until alternatives and ambiguity have been made explicit.

Allowed support:

The figure may support the central public message that safeguards are part of the method, not an afterthought.

Must not imply:

It must not imply that the identity-claim side has already been reached.

Visual style notes:

Use a simple explanatory metaphor, not a dramatic barrier. The guardrail should feel protective and methodological, not prohibitive or theatrical.

Later file-name suggestion:

```text
figures/public01_figure05_idspace_cpns_guardrail.png
```

## 10. Design constraints

Design constraints:

- figures guide the reader; they do not decorate the note
- captions must carry claim boundaries in plain language
- no figure should look like an empirical result plot
- no figure should display fabricated numerical data
- no figure should imply real degeneracy measurement
- no figure should imply physical validation
- no figure should turn the method gate into a discovery ladder
- color should clarify roles, not dramatize the topic

Accessibility:

- captions must be understandable without the image
- labels should remain legible at small sizes
- color should not be the only carrier of meaning
- use direct wording instead of private abbreviations where possible

## 11. Claim boundaries per figure

Compact boundary table:

| Figure | Allowed support | Must not imply |
| --- | --- | --- |
| Figure 1 | Method-gate sequence | Bridge confirmation or discovery pipeline |
| Figure 2 | Fingerprint/identity distinction | Diagnostic geometry as physical space |
| Figure 3 | Ambiguity as valid state | Unresolved cases as physical evidence |
| Figure 4 | CPNS06 schema/example validation | Real degeneracy measurement or diagnostic specificity |
| Figure 5 | IDSPACE/CPNS as safeguard | Identity claims already reached |

Global boundary flags:

```text
bridge_confirmation=false
diagnostic_specificity_claim=false
physical_validation=false
wifm01e_opened=false
wifm02_opened=false
bridge_nature_02_opened=false
```

## 12. Suggested production sequence

Suggested later sequence:

1. Produce rough monochrome sketches for Figures 1-4.
2. Check each sketch against the "must not imply" rule.
3. Draft captions before final styling.
4. Review the CPNS06 card against `summary.json`.
5. Decide whether optional Figure 5 helps or repeats the message.
6. Generate final image files only after explicit approval.
7. Re-run wording and claim-risk checks before any public release.

No image files are created by this plan.

## 13. Acceptance criteria for later generated figures

Later generated figures are acceptable only if:

- they match their figure slot and caption
- they use the Spektrum / Scientific American style target without hype
- they preserve the positive idea first and the boundary afterward
- they do not contain unsupported physical language
- Figure 4 includes `passed=true`, `failed_checks=[]`, placeholder degeneracy warning, and false boundary flags
- ambiguity is shown as a valid state
- `invalid_outside_scope` is not shown as successful identity resolution
- captions distinguish schema validation from scientific result
- no figure suggests that real degeneracy has been measured

## 14. Befund

The PUBLIC01 draft already contains figure slots in text form. CPNS06 gives a concrete validation card anchor:

```text
passed=true
failed_checks=[]
warning_checks:
  - degeneracy_readouts_are_placeholders_only:not_real_degeneracy_measurements
degeneracy_measurement_status=placeholder_status_only
```

The CPNS06 summary also records:

```text
ambiguity_valid_state=true
invalid_outside_scope_handled_as_non_success=true
```

The required boundary flags remain false.

## 15. Interpretation

The visual layer should make the method easier to understand without making the claim stronger. The figures should let readers see why the project pauses at IDSPACE/CPNS before moving from readable fingerprints toward identity-level statements.

The best visual story is not "we found the answer." It is "we built a guardrail before asking the next question."

## 16. Hypothese

Working hypothesis, visual-publication level only:

```text
If the public draft uses a clear visual red thread, readers can grasp
the method-gate idea without mistaking CPNS06 schema validation for
physical validation or diagnostic specificity.
```

This is a communication hypothesis, not a scientific result.

## 17. Offene Lücke

Open gaps:

- no figures have been created
- no figure files exist
- no final visual style sheet exists
- no public release exists
- no PDF exists
- no real degeneracy measurement exists
- no physical validation exists
- no diagnostic specificity claim exists
- no Bridge confirmation exists

## 18. Claim Boundary

This is a figure-production plan only.

Not created here:

- figures
- public release
- PDF
- script
- data
- config
- run

Not claimed here:

- Bridge confirmation
- diagnostic specificity
- physical validation
- wave-identity proof
- physical spacetime geometry
- real degeneracy measurement
- WIFM01E opening
- WIFM02 opening
- BRIDGE-NATURE-02 opening

Required factual anchors:

- CPNS06 validates schema/example consistency only.
- CPNS06 has `passed=true` and `failed_checks=[]`.
- CPNS06 warning: degeneracy placeholders only, not real measurements.
- `ambiguous_unresolved` is a valid state.
- `invalid_outside_scope` is not successful identity resolution.

## 19. Consequence for next step

The next step, only after explicit approval, may be to generate draft figure files for Figures 1-4.

Recommended first output set, if later approved:

```text
figures/public01_figure01_red_thread_flow.png
figures/public01_figure02_fingerprint_vs_identity_space.png
figures/public01_figure03_unresolved_ambiguity.png
figures/public01_figure04_cpns06_validation_card.png
```

Optional later output:

```text
figures/public01_figure05_idspace_cpns_guardrail.png
```

Any later figure generation must preserve the current claim boundaries and should be reviewed before public release.
