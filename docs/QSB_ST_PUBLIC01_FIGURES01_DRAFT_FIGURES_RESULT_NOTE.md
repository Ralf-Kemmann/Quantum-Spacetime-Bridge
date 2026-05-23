# QSB-ST PUBLIC01 Figures01 Draft Figures Result Note

## 1. Purpose

This note records the first deterministic draft-figure layer for the PUBLIC01 public research note.

The figures are meant as reader guidance: they make the red thread visible, separate diagnostic readability from identity resolution, and show CPNS06 as a narrow schema/example consistency check. They are explanatory draft diagrams only, not a public release layer and not a scientific-result layer.

## 2. Inputs inspected

Primary inputs inspected:

- `docs/QSB_ST_PUBLIC01_FIGURE_PRODUCTION_PLAN.md`
- `docs/QSB_ST_PUBLIC01_METHOD_GATE_RESEARCH_NOTE_DRAFT.md`
- `runs/QSB-ST-IDSPACE-CPNS06/minimal_schema_validation_open/summary.json`
- `runs/QSB-ST-IDSPACE-CPNS06/minimal_schema_validation_open/readout.md`

CPNS06 factual anchors used:

- `passed=true`
- `failed_checks=[]`
- `warning_checks=["degeneracy_readouts_are_placeholders_only:not_real_degeneracy_measurements"]`
- `degeneracy_measurement_status=placeholder_status_only`
- `ambiguity_valid_state=true`
- `invalid_outside_scope_handled_as_non_success=true`
- boundary flags remain false:
  - `bridge_confirmation=false`
  - `diagnostic_specificity_claim=false`
  - `physical_validation=false`
  - `wifm01e_opened=false`
  - `wifm02_opened=false`
  - `bridge_nature_02_opened=false`

## 3. Files created

- `scripts/generate_qsb_st_public01_draft_figures.py`
- `figures/public01_figure01_red_thread_flow.png`
- `figures/public01_figure02_fingerprint_vs_identity_space.png`
- `figures/public01_figure03_unresolved_ambiguity.png`
- `figures/public01_figure04_cpns06_validation_card.png`
- `docs/QSB_ST_PUBLIC01_FIGURES01_DRAFT_FIGURES_RESULT_NOTE.md`

No Figure 5 was created.

## 4. Figure summary

Figure 1, `public01_figure01_red_thread_flow.png`, shows the method route:

```text
WIFM01-D closure -> BRIDGE-NATURE-01B gate -> IDSPACE/CPNS definitions -> CPNS04 schema scaffold -> CPNS06 validator
```

It is drawn as a cautious method path, not as a success ladder.

Figure 2, `public01_figure02_fingerprint_vs_identity_space.png`, separates Fingerprint-Raum from Identitaets-Raum. A guarded passage marks that diagnostic readability requires maps, equivalence rules, and ambiguity handling before any identity-level decision state is assigned.

Figure 3, `public01_figure03_unresolved_ambiguity.png`, shows same-looking or near-looking fingerprints leading to `ambiguous_unresolved`. Ambiguity is presented as a valid result state, not as an error.

Figure 4, `public01_figure04_cpns06_validation_card.png`, summarizes the narrow CPNS06 result:

- `passed=true`
- `failed_checks=[]`
- `warning=placeholder degeneracy only`
- `boundary flags=false`
- schema/example consistency only
- `ambiguous_unresolved` accepted
- `invalid_outside_scope` handled as non-success

## 5. Method summary

The figures were generated deterministically with a local Python script using `matplotlib`. They are clean explanatory diagrams with a light background, a restrained color set, and readable labels.

The generator reads the CPNS06 `summary.json` so that Figure 4 is anchored to actual run-output values. The figures do not contain measured physical quantities and do not compute real degeneracy.

## 6. Befund

The draft-figure layer now exists for PUBLIC01 Figures 1-4.

The generated figures support public orientation around the method gate:

- a red-thread route through WIFM01-D, BRIDGE-NATURE-01B, IDSPACE/CPNS, CPNS04, and CPNS06
- the distinction between diagnostic fingerprints and identity-space decisions
- ambiguity as a disciplined valid state
- the CPNS06 result as schema/example consistency only

## 7. Interpretation

The visual layer helps the PUBLIC01 draft become more public-facing without changing its scientific status. The diagrams give readers a way into the method before technical details accumulate.

The central message remains: QSB-ST currently provides a controlled diagnostic workflow for asking whether relational fingerprints can be made geometrically readable without treating readability as identity resolution.

## 8. Hypothese

The figures may make the method gate easier to read in a Spektrum der Wissenschaft / Scientific American style note, especially for readers who need a visual separation between diagnostic structure, identity-space safeguards, and narrow validation checks.

This remains a presentation hypothesis for the publication draft, not a new scientific claim.

## 9. Offene Lücke

The figures still need visual review for label balance, publication layout, and accessibility. Figure 5 was intentionally not produced.

No real degeneracy measurement exists yet. The CPNS06 warning remains active: degeneracy readouts are placeholders only, not real measurements.

## 10. Claim Boundary

These are draft explanatory figures only.

- No public release.
- No PDF.
- No new scientific result.
- No Bridge confirmation.
- No diagnostic specificity claim.
- No physical validation.
- No proof of wave identity.
- No physical spacetime claim.
- No real degeneracy measurement.
- No WIFM01E opening.
- No WIFM02 opening.
- No BRIDGE-NATURE-02 opening.

## 11. Consequence for next step

The next step is visual review of Figures 1-4 against the PUBLIC01 draft. A later approved block may refine labels, layout, or add the optional guardrail Figure 5, but that would require an explicit follow-up instruction.
