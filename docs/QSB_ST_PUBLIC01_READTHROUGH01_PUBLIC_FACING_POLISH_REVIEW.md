# QSB-ST PUBLIC01 READTHROUGH01 Public-Facing Polish Review

## 1. Purpose

This review records a read-only public-facing polish check for PUBLIC01 after the magazine-style visual layer and PREVIEW02 path handling were added.

The review checks figure references, preview readiness, wording boundaries, and residual public-facing polish items. It does not rewrite the draft and does not create a public release.

## 2. Inputs inspected

Mandatory input inspected:

- `docs/QSB_ST_PUBLIC01_METHOD_GATE_RESEARCH_NOTE_DRAFT.md`

Additional inputs inspected:

- `docs/QSB_ST_PUBLIC01_PREVIEW02_LAYOUT_REVIEW_NOTE.md`
- `scripts/build_qsb_st_public01_preview.py`

No WIFM01E, WIFM02, or BRIDGE-NATURE-02 file was opened.

## 3. Current PUBLIC01 visual/document status

PUBLIC01 currently includes:

- an opening eyecatcher image framed as conceptual orientation
- magazine-style Figures 1-4 referenced from the draft
- captions and boundary sentences after each figure
- a PREVIEW02 builder that rewrites image paths only in the generated preview copy
- a PREVIEW02 HTML output that Ralf visually checked and found good
- no PDF preview, because no local PDF renderer was available

The source draft remains the article source. PREVIEW02 is a local layout aid only.

## 4. Figure path check

Current magazine figure paths found in the draft:

- `../figures/public01_eyecatcher_method_gate.png`
- `../figures/public01_figure01_method_route_magazine_v1.png`
- `../figures/public01_figure02_fingerprint_identity_magazine_v1.png`
- `../figures/public01_figure03_unresolved_ambiguity_magazine_v1.png`
- `../figures/public01_figure04_cpns06_validation_card_magazine_v1.png`

Discarded earlier figure paths were not found in the draft:

- `public01_figure01_red_thread_flow_v2.png`
- `public01_figure02_fingerprint_vs_identity_space_v2.png`
- `public01_figure03_unresolved_ambiguity_v2.png`
- `public01_figure04_cpns06_validation_card_v2.png`
- `public01_figure01_red_thread_flow.png`
- `public01_figure02_fingerprint_vs_identity_space.png`
- `public01_figure03_unresolved_ambiguity.png`
- `public01_figure04_cpns06_validation_card.png`

## 5. Public-facing readability check

The draft reads as a public method-gate note rather than as a technical run log. The abstract and plain-language orientation lead with the constructive idea: QSB-ST is a controlled diagnostic workflow that keeps readable fingerprints separate from identity resolution.

The visual guide remains coherent after the replacement with magazine-style figures. The figures are introduced as visual handrails, and the surrounding prose keeps the article logic visible: method route, fingerprint/identity distinction, unresolved ambiguity, and the narrow CPNS06 validator result.

The opening visual is framed as an orientation image. It is not used as evidence.

The terms `Fingerprint-Raum` and `Identitaets-Raum` remain visible as project terms. For public English readability, a minimal parenthetical translation could help, but leaving the terms is defensible if the draft wants to preserve the project vocabulary.

The phrase "draft figures" still appears in a few places. Because the current figures now read more like magazine-style public figures, a later minimal wording pass could change that phrase to "current figures" or "publication draft figures" where useful. No change was made in this review.

## 6. Claim-risk grep

The configured high-risk term-set was checked against the PUBLIC01 draft. No hits were found in the draft during the readthrough.

The same term-set should remain part of the release checklist. The review text itself avoids using the flagged phrases outside controlled check descriptions.

## 7. Overclaiming risk review

The draft keeps the intended boundary:

- PUBLIC01 is a public research note and method-gate note only.
- CPNS06 validates schema/example consistency only.
- There is no physical validation.
- There is no Bridge confirmation.
- There is no diagnostic specificity claim.
- There is no real degeneracy measurement.
- Ambiguity is treated as a valid state.
- `invalid_outside_scope` is not treated as successful identity resolution.

The figure captions and boundary sentences are particularly useful here: they give readers the visual orientation while immediately closing the stronger interpretations.

## 8. Suggested minimal edits, if any

Optional minimal edits for a later pass:

- Consider changing the version note so it names the current release-preparation anchor rather than the older visual-integration anchor.
- Consider adding a parenthetical English gloss after the first `Fingerprint-Raum` / `Identitaets-Raum` caption use.
- Consider replacing a few occurrences of "draft figure" with "publication draft figure" or "current figure" if the magazine-style visuals are now the intended public-facing set.
- Consider adding a short preview note outside the article draft, not inside the article text, stating that PREVIEW02 HTML looked good while PDF output still awaits a local renderer.

No edit is required before a claim-boundary review, but these are low-risk polish candidates.

## 9. Befund

The draft uses the current magazine-style image paths and does not reference the discarded earlier figure files.

The visual guide text is consistent with the new figures. The eyecatcher is described as conceptual orientation. CPNS06 remains described as schema/example consistency only. PREVIEW02 documents the HTML path repair and the missing PDF renderer.

## 10. Interpretation

PUBLIC01 is in a strong public-facing draft state for a method-gate note. The red thread is visible, the figure layer supports readability, and the claim boundaries remain compact and repeated at the right moments.

The most useful remaining polish is not scientific content change; it is final reader-facing smoothing around terminology, version anchoring, and the phrase "draft figures."

## 11. Offene Lücke

Open items:

- no PDF preview yet because no local PDF renderer was available
- no final public release file
- no upload
- no final citation/context pass recorded here
- no decision yet on whether to translate or gloss project terms in captions
- no final update of the repository commit anchor for release

## 12. Claim Boundary

This is a readthrough and polish review only.

- No public release.
- No upload.
- No final PDF.
- No new scientific result.
- No Bridge confirmation.
- No diagnostic specificity claim.
- No physical validation.
- No real degeneracy measurement.
- No proof of wave identity.
- No physical spacetime claim.
- No WIFM01E opening.
- No WIFM02 opening.
- No BRIDGE-NATURE-02 opening.

## 13. Consequence for next step

The next step is a small, explicitly authorized polish pass if the optional wording changes are desired. Otherwise, the draft can proceed to a release-preparation gate that checks commit anchor, citation/context wording, local HTML preview, and PDF-generation readiness.
