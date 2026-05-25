# QSB-ST PUBLIC01 PDF01 Release PDF Layout Builder Result Note

## 1. Purpose

This note records PDF01: a dedicated release-PDF layout builder for the PUBLIC01 method-gate note.

The goal is to produce a release-style HTML/PDF render without preview banners, browser headers, local path footers, or awkward figure/table handling. The source draft is not modified by the builder.

## 2. Inputs inspected

Inputs inspected:

- `docs/QSB_ST_PUBLIC01_METHOD_GATE_RESEARCH_NOTE_DRAFT.md`
- `scripts/build_qsb_st_public01_preview.py`
- `docs/QSB_ST_PUBLIC01_PREVIEW02_LAYOUT_REVIEW_NOTE.md`
- `docs/QSB_ST_PUBLIC01_APPARATUS02_MINIMAL_DRAFT_ADDITIONS_RESULT_NOTE.md`

No WIFM01E, WIFM02, or BRIDGE-NATURE-02 file was opened.

## 3. Files created

Source/review files:

- `scripts/build_qsb_st_public01_release_pdf.py`
- `docs/QSB_ST_PUBLIC01_PDF01_RELEASE_PDF_LAYOUT_BUILDER_RESULT_NOTE.md`

Release output files:

- `runs/QSB-ST-PUBLIC01-PDF01/release_pdf_open/public01_release.html`
- `runs/QSB-ST-PUBLIC01-PDF01/release_pdf_open/QSB_ST_PUBLIC01_Method_Gate_Route_2026-05-25.pdf`
- `runs/QSB-ST-PUBLIC01-PDF01/release_pdf_open/pdf_build_readout.md`
- `runs/QSB-ST-PUBLIC01-PDF01/release_pdf_open/figures/`

The release figures directory contains copied local figure assets used by the release HTML/PDF.

## 4. Build method

The builder reads:

```text
docs/QSB_ST_PUBLIC01_METHOD_GATE_RESEARCH_NOTE_DRAFT.md
```

It creates a temporary release-render transformation in memory, rewrites image paths from:

```text
../figures/<filename>
```

to:

```text
figures/<filename>
```

It then copies every referenced figure into the release output directory and writes a clean release HTML file.

## 5. Release-PDF transformations

The release render removes preview-only framing by not using the PREVIEW02 banner or preview footer at all.

The release HTML:

- contains no `PREVIEW02` banner
- contains no `Preview only` text
- contains no local `file://` references in visible HTML
- keeps the source-draft article content
- keeps local figure paths under `figures/`
- avoids duplicate visible image alt-text before figures

Scientific content is not rewritten by the builder.

## 6. Figure layout handling

The builder treats the opening visual and Figures 1-4 as figure blocks.

For Figures 1-4, the builder wraps each heading, image, caption paragraph, explanatory paragraph, and boundary paragraph into a release figure block. CSS uses `page-break-inside: avoid` and `break-inside: avoid` to reduce heading/image/caption separation.

Images are sized to remain readable while avoiding the oversized page breaks seen in browser-style previews.

## 7. Table layout handling

The repository-anchor and commit-anchor tables are rendered in the release HTML as compact two-column source lists.

This preserves the source trail while improving PDF wrapping. The source draft tables are not changed.

## 8. PDF renderer used

PDF01 used local `wkhtmltopdf`.

The mandatory local-file option was used:

```text
--enable-local-file-access
```

The PDF was generated as A4 with 18 mm margins.

## 9. Checks performed

Checks performed by the builder and follow-up commands:

- source draft was read without modification
- image paths were rewritten only in release output
- referenced figures were copied into the release output directory
- release HTML was created
- release PDF was created with `wkhtmltopdf`
- release readout was created
- preview-only strings were checked in the release HTML
- local release image references were checked in the release HTML
- diff hygiene and claim-risk grep were run

## 10. Befund

PDF01 successfully created a release-style HTML and PDF output.

The release render is separate from PREVIEW02. It is intended to remove the local-preview feel and to improve figure and table behavior in the PDF.

## 11. Interpretation

PUBLIC01 now has a dedicated release-PDF build path. The PDF is still a release candidate artifact, not a public release.

The build route is better suited than browser printing because it suppresses browser-local headers/footers and applies document-specific figure/table layout rules.

## 12. Offene Lücke

Open items:

- the generated PDF still needs human visual inspection page by page
- any final release metadata and commit-anchor wording still need release-gate review
- external references remain to be finalized before public release

## 13. Claim Boundary

This is a PDF layout/build step only.

- No public release.
- No upload.
- No new scientific result.
- No Bridge confirmation.
- No diagnostic specificity claim.
- No physical validation.
- No real degeneracy measurement.
- Figures remain explanatory visualizations only.
- AI assistance did not produce scientific findings.
- No WIFM01E opening.
- No WIFM02 opening.
- No BRIDGE-NATURE-02 opening.

## 14. Consequence for next step

The next step is a visual release-candidate inspection of:

```text
runs/QSB-ST-PUBLIC01-PDF01/release_pdf_open/QSB_ST_PUBLIC01_Method_Gate_Route_2026-05-25.pdf
```

If the page breaks and figure blocks are acceptable, a later release-preparation gate can decide whether to update release metadata and prepare a public-facing release package.
