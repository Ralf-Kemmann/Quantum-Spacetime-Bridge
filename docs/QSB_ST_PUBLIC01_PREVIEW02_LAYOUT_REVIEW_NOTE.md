# QSB-ST PUBLIC01 PREVIEW02 Layout Review Note

## 1. Purpose

This note records PREVIEW02 for the PUBLIC01 draft.

PREVIEW02 fixes the local preview-rendering issue from PREVIEW01: image paths are rewritten only inside the generated preview so that figures copied into the preview output directory can render from the HTML location. The source draft remains unchanged.

## 2. Inputs inspected

Mandatory inputs inspected:

- `docs/QSB_ST_PUBLIC01_METHOD_GATE_RESEARCH_NOTE_DRAFT.md`
- `figures/public01_eyecatcher_method_gate.png`
- `figures/public01_figure01_method_route_magazine_v1.png`
- `figures/public01_figure02_fingerprint_identity_magazine_v1.png`
- `figures/public01_figure03_unresolved_ambiguity_magazine_v1.png`
- `figures/public01_figure04_cpns06_validation_card_magazine_v1.png`

Existing preview context inspected:

- `scripts/build_qsb_st_public01_preview.py`

No WIFM01E, WIFM02, or BRIDGE-NATURE-02 file was opened.

## 3. Preview files created

Preview outputs:

- `runs/QSB-ST-PUBLIC01-PREVIEW02/layout_preview_open/public01_preview.html`
- `runs/QSB-ST-PUBLIC01-PREVIEW02/layout_preview_open/preview_build_readout.md`
- `runs/QSB-ST-PUBLIC01-PREVIEW02/layout_preview_open/figures/public01_eyecatcher_method_gate.png`
- `runs/QSB-ST-PUBLIC01-PREVIEW02/layout_preview_open/figures/public01_figure01_method_route_magazine_v1.png`
- `runs/QSB-ST-PUBLIC01-PREVIEW02/layout_preview_open/figures/public01_figure02_fingerprint_identity_magazine_v1.png`
- `runs/QSB-ST-PUBLIC01-PREVIEW02/layout_preview_open/figures/public01_figure03_unresolved_ambiguity_magazine_v1.png`
- `runs/QSB-ST-PUBLIC01-PREVIEW02/layout_preview_open/figures/public01_figure04_cpns06_validation_card_magazine_v1.png`

PDF status:

- `runs/QSB-ST-PUBLIC01-PREVIEW02/layout_preview_open/public01_preview.pdf` was not created because no local `weasyprint` or `wkhtmltopdf` executable was available.

Source/review files created or updated:

- updated: `scripts/build_qsb_st_public01_preview.py`
- created: `docs/QSB_ST_PUBLIC01_PREVIEW02_LAYOUT_REVIEW_NOTE.md`

## 4. Build method

The builder reads the PUBLIC01 source draft from:

```text
docs/QSB_ST_PUBLIC01_METHOD_GATE_RESEARCH_NOTE_DRAFT.md
```

It then creates a temporary preview rendering path in memory, converts the markdown to HTML with local handling for headings, paragraphs, images, code blocks, lists, and tables, and writes the preview into:

```text
runs/QSB-ST-PUBLIC01-PREVIEW02/layout_preview_open/
```

The source draft is not modified.

## 5. Path handling

For preview rendering only, the builder rewrites markdown image paths:

```text
../figures/<filename>
```

to:

```text
figures/<filename>
```

Each referenced local figure is copied from the repository `figures/` directory into:

```text
runs/QSB-ST-PUBLIC01-PREVIEW02/layout_preview_open/figures/
```

The generated HTML therefore uses local preview paths such as:

```text
figures/public01_figure01_method_route_magazine_v1.png
```

This is a preview-only path repair. It does not rewrite the source markdown.

## 6. Visual/layout checks

Eyecatcher placement:

- The eyecatcher is expected to render near the article opening because `public01_eyecatcher_method_gate.png` is copied into the preview figures directory and referenced locally from the HTML.

Figure 1 magazine-style method route:

- Figure 1 is expected to render from `figures/public01_figure01_method_route_magazine_v1.png`.
- The preview check concerns layout visibility and route-map placement only.

Figure 2 magazine-style fingerprint/identity figure:

- Figure 2 is expected to render from `figures/public01_figure02_fingerprint_identity_magazine_v1.png`.
- The preview check concerns whether the image appears in the article flow after path rewriting.

Figure 3 magazine-style ambiguity figure:

- Figure 3 is expected to render from `figures/public01_figure03_unresolved_ambiguity_magazine_v1.png`.
- The preview check concerns whether ambiguity remains visually presented as a valid state rather than an error.

Figure 4 magazine-style CPNS06 validation card:

- Figure 4 is expected to render from `figures/public01_figure04_cpns06_validation_card_magazine_v1.png`.
- The preview check concerns the narrow schema/example consistency framing and the absence of a physical-result implication.

Image path rewriting:

- The generated HTML contains `figures/public01_...` image references.
- The copied files are present in the preview figures directory.

PDF generation:

- PDF generation did not succeed because no local PDF renderer was available.
- HTML preview remains available.

Preview status:

- This remains a preview only.

## 7. Befund

PREVIEW02 resolves the prior local image-path problem at the preview-build layer. The HTML preview is expected to render the eyecatcher and four magazine-style figures from the copied local preview assets.

The PDF output is missing due to unavailable local PDF rendering tools, and this limitation is recorded in the build readout.

## 8. Interpretation

The source draft can keep repository-relative markdown paths suitable for the `docs/` location, while the preview builder creates a self-contained local HTML preview directory.

This separates source authorship from preview mechanics and avoids changing scientific or publication text just to fix a preview-output path issue.

## 9. Offene Lücke

Open items:

- PDF generation still requires an available local renderer such as `weasyprint` or `wkhtmltopdf`.
- Browser-based visual inspection of `public01_preview.html` remains the next practical layout check.
- This note does not decide whether the preview is publication-ready.

## 10. Claim Boundary

This is a preview/review step only.

- No public release.
- No upload.
- No final PDF.
- No new scientific result.
- No Bridge confirmation.
- No diagnostic specificity claim.
- No physical validation.
- No real degeneracy measurement.

## 11. Consequence for next step

The next step is to open the generated HTML preview locally and inspect whether the eyecatcher and Figures 1-4 render with the intended visual rhythm. If a PDF preview is required, a local PDF renderer must be installed or an approved alternative renderer must be selected.
