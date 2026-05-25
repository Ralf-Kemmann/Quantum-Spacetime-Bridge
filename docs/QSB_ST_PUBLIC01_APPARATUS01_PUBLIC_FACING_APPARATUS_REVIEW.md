# QSB-ST PUBLIC01 APPARATUS01 Public-Facing Apparatus Review

## 1. Purpose

This review checks the publication apparatus needed before release preparation for the PUBLIC01 public-facing method-gate note.

The focus is references, lists, transparency notes, footnotes/endnotes, and clear handling of explanatory visuals. This is a review only. The PUBLIC01 draft is not modified here.

## 2. Inputs inspected

Mandatory input inspected:

- `docs/QSB_ST_PUBLIC01_METHOD_GATE_RESEARCH_NOTE_DRAFT.md`

Additional inputs inspected:

- `docs/QSB_ST_PUBLIC01_READTHROUGH01_PUBLIC_FACING_POLISH_REVIEW.md`
- `docs/QSB_ST_PUBLIC01_PREVIEW02_LAYOUT_REVIEW_NOTE.md`
- `scripts/build_qsb_st_public01_preview.py`

No WIFM01E, WIFM02, or BRIDGE-NATURE-02 file was opened.

## 3. Current document-apparatus status

The draft currently has:

- title, author line, ORCID, and version note
- opening visual
- Figures 1-4 with captions and boundary sentences
- method-gate lineage section
- CPNS06 validation result section
- claim boundary section
- repository anchors table
- commit anchors table
- literature/context policy section
- next steps section

The draft currently does not have:

- formal Bibliography / References section
- List of Figures
- List of Tables
- AI assistance / transparency note
- figure-source or generated-image transparency note
- footnotes or endnotes

## 4. Bibliography / References review

The draft does not currently contain a formal `References` or `Bibliography` section.

The existing `Repository anchors` table already functions as a project-internal source trail. For a public-facing release, that table can remain useful, but it does not fully replace a References section if the note is released through a public repository, Zenodo-style record, or Academia.edu-style upload.

Recommended minimal approach:

- add a compact `References` section near the end
- include internal QSB-ST repository documents that are directly used in the draft
- include CPNS04 / CPNS06 internal schema and validator documents because the draft discusses them
- include IDSPACE and CPNS definition documents because the draft discusses IDSPACE and CPNS
- include MaxEnt literature only if the final draft keeps explicit MaxEnt context beyond internal method naming
- include de Broglie only if the release draft explicitly invokes de-Broglie-like motivation in the public narrative
- avoid literature padding

If exact external bibliographic details are not settled, use a clearly marked placeholder style such as:

```text
External literature references to be finalized before public release.
```

The draft should not invent authority by adding broad references that are not used by the text.

## 5. List of Figures review

The draft does not currently contain a List of Figures.

Recommended candidate entries:

- Opening visual: QSB-ST method-gate orientation
- Figure 1. Red thread through the method gate
- Figure 2. Fingerprint Space and Identity Space
- Figure 3. Same-looking fingerprints and unresolved ambiguity
- Figure 4. CPNS06 validation card

For public English readability, Figure 2 should either:

- keep the project terms with an English gloss: `Fingerprint-Raum / Identitaets-Raum (Fingerprint Space / Identity Space)`, or
- translate the caption title to `Fingerprint Space and Identity Space`.

The second option is cleaner for a public-facing note. The first option preserves project vocabulary.

## 6. List of Tables review

The draft contains markdown tables:

- `Repository anchors`
- `Commit anchors currently named in the planning line`

Because tables exist, a minimal List of Tables is justified if the draft is prepared as a formal release document.

Recommended candidate entries:

- Table 1. Repository anchors for PUBLIC01 method source trail
- Table 2. Commit anchors for release-preparation tracking

If the final release removes or reformats those tables into prose, a List of Tables is not needed.

## 7. AI assistance / transparency note review

The draft does not currently contain an AI assistance or AI transparency note.

Recommended concise note:

```text
AI-assisted drafting, editorial structuring, preview generation, and generated explanatory figures were used as support tools. Scientific responsibility, conceptual decisions, claim boundaries, and final review remain with the author.
```

The note should be placed so that it is visible but not intrusive. It should not imply that AI produced scientific findings, physical validation, or numerical results.

## 8. Footnotes / endnotes review

The draft currently has no footnotes or endnotes.

Sparse footnotes or endnotes could help only where they reduce clutter. Useful candidates:

- CPNS06 validation means schema/example consistency only.
- Generated figures are explanatory visualizations, not empirical data.
- AI assistance was used for drafting, structuring, preview support, and explanatory visuals, with author responsibility retained.

Excessive notes are not recommended. The PUBLIC01 draft reads best when the main line remains uncluttered.

## 9. Figure-source and generated-image transparency

The draft currently does not include a compact figure-source or generated-image transparency note.

Recommended note:

```text
Figures are explanatory/generated visualizations for orientation. They are not empirical data, not numerical validation outputs, and not evidence for QSB-ST claims.
```

This note should cover:

- opening eyecatcher
- magazine-style Figures 1-4
- local preview generation and copied figure assets

It should distinguish visual communication from scientific support.

## 10. Evidence vs explanatory visuals

The article already uses figure boundary sentences well. The opening visual is framed as conceptual orientation, and Figure 4 explicitly states the narrow CPNS06 scope.

Still, a release apparatus should add one compact global sentence:

```text
The figures are explanatory visualizations for orientation; they are not empirical evidence or numerical validation outputs.
```

This is especially useful because magazine-style figures can look visually polished. The apparatus should prevent polish from being read as stronger support.

## 11. Suggested minimal additions to the draft

Suggested APPARATUS02 patch, if approved:

- add a short List of Figures
- add a short List of Tables if the repository and commit anchor tables remain in the release draft
- add compact AI assistance / transparency note
- add compact explanatory/generated-figures note
- add minimal References section, or a clearly marked `References to be finalized before public release` note
- optionally gloss `Fingerprint-Raum` / `Identitaets-Raum` for English readers
- keep the apparatus lean
- avoid a literature cemetery

No draft change is executed in APPARATUS01.

## 12. Suggested placement in the draft

Suggested placements:

- List of Figures: after the version note and opening visual, or just before `Visual guide for the public note`
- List of Tables: after List of Figures, if tables remain
- AI assistance / transparency note: near the end, before `References`
- Figure-source / generated-image transparency note: near the visual guide or near the end with the AI note
- References: near the end, after `Literature/context policy` or before `Next steps`
- Footnotes/endnotes: only if used sparingly; otherwise omit

The most compact release structure would be:

```text
List of Figures
List of Tables
...
Figure and AI Transparency
References
Next steps
```

## 13. Befund

The draft is strong as a public method-gate narrative but still light on formal release apparatus.

It has an internal source trail through repository-anchor tables and clear claim boundaries. It lacks a formal References section, List of Figures, List of Tables, AI transparency note, and generated-image disclosure.

The visual layer is explanatory and well bounded in the prose, but a single global transparency note would make the distinction easier for readers.

## 14. Interpretation

PUBLIC01 does not need a heavy academic apparatus. It needs a small public-release apparatus that makes source trail, figure status, AI support, and visual evidence boundaries explicit.

The best route is a compact APPARATUS02 patch rather than a large literature expansion.

## 15. Offene Lücke

Open items:

- no formal References section yet
- no List of Figures yet
- no List of Tables yet, despite existing markdown tables
- no AI assistance / transparency note yet
- no generated-image transparency note yet
- no final decision on whether to gloss or translate `Fingerprint-Raum` / `Identitaets-Raum`
- no PDF preview yet because local PDF rendering tools were unavailable

## 16. Claim Boundary

This is an apparatus review only.

- No public release.
- No upload.
- No final PDF.
- No new scientific result.
- No Bridge confirmation.
- No diagnostic specificity claim.
- No physical validation.
- No real degeneracy measurement.
- No claim that generated figures are evidence.
- No claim that AI produced scientific findings.
- No WIFM01E opening.
- No WIFM02 opening.
- No BRIDGE-NATURE-02 opening.

## 17. Consequence for next step

The next step, if approved, is APPARATUS02: a minimal draft patch adding List of Figures, List of Tables if retained, AI/figure transparency, and a compact References section or release-ready References placeholder.

That patch should remain lean, public-facing, and bounded.
