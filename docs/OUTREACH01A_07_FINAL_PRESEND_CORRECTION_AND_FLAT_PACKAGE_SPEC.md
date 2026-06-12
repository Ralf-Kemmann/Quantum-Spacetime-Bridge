# OUTREACH01A-07 Final Pre-Send Correction and Flat Contact Package Spec

outreach_id = OUTREACH01A-07
package_id = OUTREACH01A_FINAL_FLAT_SEND_PACKAGE_V1
document_type = final_presend_package_preparation
contact_send_allowed = false
ready_for_send = false
user_release_required_before_send = true

## 1. Purpose

This block prepares a flat external contact package from the reviewed OUTREACH01A-05 and OUTREACH01A-06 materials. It applies the final pre-send wording corrections to the contact letter, verifies the recipient data, excludes repository machinery from the external package, and writes a bounded validation run.

No email is sent. No Gmail draft is created. The output is prepared for final user review only.

## 2. Verified Recipient

recipient_name = Svetlana Gurevich
recipient_title = Professor
institution = University of Münster
institute = Institute of Theoretical Physics
email = gurevics@uni-muenster.de
theory_group_confirmed = true

Official contact source:

```text
https://www.uni-muenster.de/Physik.TP/people/en/svetlana_gurevich.html
```

Official research-field source:

```text
https://www.uni-muenster.de/Physik.TP/en/research/gurevich/forschungsgebiete.html
```

## 3. Flat External Package

The builder writes exactly six files under:

```text
artifacts/OUTREACH01A-07/send_package/
```

Expected files:

```text
01_Contact_Letter_Ralf_Kemmann_to_Professor_Svetlana_Gurevich.md
02_Research_Context_Note.md
03_Competence_and_Boundaries_Profile.md
04_Technical_Note.md
05_State_Identity_Figure.svg
06_Compact_Three_Record_Table.md
```

No subdirectories are allowed. No manifest, validation, run, script, spec, schema, debug, internal or audit file is part of the external package.

## 4. Attachment Roles

```text
01 Contact Letter = required entry point
02 Research Context = wider context
03 Competence and Boundaries = sender context
04 Technical Note = primary technical attachment
05 State Identity Figure = visual entry attachment
06 Compact Table = precision/checking attachment
```

## 5. Claim Boundary

The package must not claim a time-crystal explanation by QSB, a QSB model of the reported laser experiment, a QSB domain-wall prediction, experimental validation by QSB, or a new DTC theory. It must not request collaboration, supervision, validation or endorsement.

The contact letter must avoid the old unidiomatic group-fit phrase and must not attribute an experimental system personally to the recipient. It must refer instead to the physical systems studied by the group.

## 6. Send Gate

formal_red_team_passed = true
ready_for_final_user_review = true
ready_for_send = false
contact_send_allowed = false
user_release_required_before_send = true

The package is prepared for final user review, not for sending.

## 7. OUTREACH01A-07A External Text Cleanup

The external long-text attachments in the flat send package are cleaned for external readability while preserving the scientific claim boundary. Internal project IDs, workflow labels, Red-Team/Gate language, stale runner/hash wording, visible internal question IDs and references to a non-included Spanish presentation layer are not shown in:

```text
02_Research_Context_Note.md
03_Competence_and_Boundaries_Profile.md
04_Technical_Note.md
```

The Research Context Note carries exactly one disclosure footer:

```text
Prepared with an internal consistency and claim-boundary review. AI-assisted tools supported drafting and technical preparation; all scientific decisions and final approval remain with the author.
```

The disclosure is not included in the contact letter, competence profile, technical note, figure or compact table. The phrase `AI-generated` is not used.

Additional 07A validation fields:

```text
external_long_text_cleanup_passed = true
internal_project_identifiers_visible = false
stale_workflow_text_visible = false
question_ids_visible_in_external_files = false
review_ai_disclosure_present = true
review_ai_disclosure_count = 1
review_ai_disclosure_only_in_research_context = true
theoretical_chemistry_present = true
physical_chemical_phrase_present = false
ready_for_final_user_review = true
ready_for_send = false
contact_send_allowed = false
```

The contact letter, state-identity figure and compact three-record table remain unchanged by the 07A cleanup.

## 8. OUTREACH01A-07B Final English Smoothing

The external long-text attachments use idiomatic English for the Gurevich group reference. The phrase `AG Gurevich` is not visible in the external long texts. The group-fit wording remains methodological and does not imply any existing connection between the group and QSB.

Additional 07B validation fields:

```text
ag_gurevich_phrase_visible = false
gurevich_group_phrase_used = true
reported_experiment_phrase_used = true
presumed_qsb_connection_claimed = false
methodological_fit_only = true
works_close_to_phrase_present = false
your_laser_system_phrase_present = false
submissive_closing_phrase_present = false
contact_letter_hash_unchanged = true
figure_hash_unchanged = true
compact_table_hash_unchanged = true
ready_for_final_user_review = true
ready_for_send = false
contact_send_allowed = false
```

This pass changes language only. Scientific content, claim boundaries and the three technical questions remain unchanged.

## 9. OUTREACH01A-07C Final Micro-Smoothing

The final micro-smoothing pass removes remaining non-idiomatic external wording without changing scientific content, claim boundaries, canonical data or the three technical questions.

Additional 07C validation fields:

```text
institutional_ag_affiliation_phrase_present = false
institutional_affiliation_wording_natural = true
dtc_vocabulary_phrase_present = false
dtc_context_overlap_wording_present = true
run_oriented_documentation_phrase_present = false
workflow_documentation_phrase_present = true
audit_oriented_representation_phrase_present = false
traceable_representation_phrase_present = true
technical_question_wording_unchanged = true
contact_letter_hash_unchanged = true
figure_hash_unchanged = true
compact_table_hash_unchanged = true
review_ai_disclosure_count = 1
review_ai_disclosure_only_in_research_context = true
ready_for_final_user_review = true
ready_for_send = false
contact_send_allowed = false
```

No email draft is created or sent.
