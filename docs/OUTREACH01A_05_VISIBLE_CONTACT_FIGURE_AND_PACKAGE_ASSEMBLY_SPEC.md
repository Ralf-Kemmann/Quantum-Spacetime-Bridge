# OUTREACH01A-05 Visible Contact Figure and Package Assembly Spec

## 1. Status and Scope

package_id = OUTREACH01A_CONTACT_PACKAGE_V1
outreach_id = OUTREACH01A-05
package_title = Visible Contact Figure and Contact-Package Assembly
package_status = assembled_not_released
package_ready_for_red_team = true
package_ready_for_send = false
contact_message_present = false
contact_send_allowed = false
user_release_required_before_send = true

This specification covers the OUTREACH01A-05 contact-package assembly only. The block is a synthetic demonstrator view over the existing OUTREACH01A-DTC-DEMO01 records. It does not introduce a contact message, a send action, an experimental result, or a physical claim.

## 2. Existing Artifact Group

The visible package is assembled from the existing `artifacts/OUTREACH01A-05/` group. The visible files are the English and Spanish state-identity figures, the language-layer architecture figure, two compact tables and two full two-page technical notes. Preview and validation files support review but are not counted as technical notes.

technical_note_en_role = full_two_page_technical_note
technical_note_es_role = full_two_page_technical_note
preview_en_role = compact_package_preview
preview_es_role = compact_package_preview
technical_note_content_source = OUTREACH01A-04_reviewed_two_page_notes
technical_note_shortening_applied = false
technical_note_role_mismatch_present = false

## 3. Reproducible Build

The reproducible builder is `scripts/run_outreach01a_05_build_contact_package.py`. It loads the canonical synthetic records and English/Spanish alias files from `data/OUTREACH01A-DTC-DEMO01/`, copies the reviewed OUTREACH01A-04 two-page notes into the package technical-note slots, inserts stable question-ID comments, checks the existing artifacts, verifies hashes, renders the SVGs through a local renderer and writes a bounded run directory.

## 4. Visible Figures

The main contact figures show `DTC_A`, `DTC_B` and `BOUNDARY_AB`. The two DTC records share the declared dynamic equivalence class while keeping record identity, phase position and domain assignment separate. The boundary remains an open representation option.

The architecture figure shows one canonical dataset feeding two reading layers. It is a language-layer picture, not a second dataset and not a change in logic.

## 5. Visual Validation

The builder validates SVG XML, checks for scripts, embedded raster images, external assets and absolute local paths, and renders all three SVG files. The render output is temporary and is written only below `/tmp/outreach01a05_render_check/`.

Automatic rendering is not a human visual review. The builder may report `svg_render_check_performed`, `svg_render_check_passed`, renderer identity, render success flags, expected dimensions, detected record IDs, detected phase offsets, detected domain labels and detected boundary-option text. It sets `automatic_text_clipping_detection_performed = false` because no glyph- or bounding-box-based clipping detector is implemented.

Human readability, Spanish text fit, primary-label overlap and caveat readability are accepted only through `--visual-review-attestation`. Without that external attestation, `manual_visual_review_performed = false`, `manual_visual_review_passed = not_applicable`, `manual_visual_review_required = true` and `package_ready_for_red_team = false`.

## 6. Personal Style Application

personal_style_reference_applied = true
style_reference_scope = rhythm_transitions_human_tone_explanatory_flow
source_content_from_style_reference_used = false
generic_ai_pattern_review_performed = true
automatic_generic_phrase_scan_performed = true
manual_style_review_required = false
style_localization_changes_canonical_content = false
style_localization_changes_claim_boundaries = false
style_localization_changes_technical_questions = false

The style pass is limited to rhythm, transitions, human explanatory tone and movement from example to question. It does not import source content or unsupported scientific statements from any outside reference.

The builder performs an automatic generic-phrase scan over the English note, Spanish note, previews and README. Human style review is documented only through `--style-review-attestation`. The scan and the external review are separate checks.

The full English technical note is part of the first-contact review package. The Spanish technical note demonstrates the parallel language layer. Compact previews are package overviews only and do not replace either technical note.

## 7. Package Manifest and Hashes

The manifest and file list record seven visible package hashes. Hash validation is computed against the current files during the run, rather than assumed from the manifest alone. The manifest keeps `package_id = OUTREACH01A_CONTACT_PACKAGE_V1` separate from `package_title = Visible Contact Figure and Contact-Package Assembly`.

## 8. Cross-Language Package Check

The cross-language check compares canonical record identifiers, record order, canonical table values, figure geometry, figure record identifiers, relation structure, stable question IDs, question order, caveat set and display-language boundaries. It may set `technical_question_mapping_matches = true` when the stable IDs and order match. It must set `automatic_semantic_equivalence_proven = false`.

## 9. Red-Team Gate

The package is ready for red-team review only if rendering, hash validation, cross-language checking, external visual review, external style review, generic-phrase scanning and claim-risk checks pass. This gate is internal review readiness, not permission to send.

## 10. Send Gate

package_ready_for_send = false
contact_message_present = false
contact_send_allowed = false
user_release_required_before_send = true

No email text is present in this block. No contact action is approved.

## 11. Limitations

The records are synthetic and non-experimental. The visual package supports reading and review of the demonstrator structure only. It does not validate a laser experiment, a domain-wall model, a physical time-crystal mechanism, or any send decision.
