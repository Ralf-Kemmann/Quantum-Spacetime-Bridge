# OUTREACH01A-06 Contact Letter and Research-Context Note Spec

outreach_id = OUTREACH01A-06
document_type = contact_material_preparation
contact_message_present = yes
contact_message_drafting_allowed = yes
contact_send_allowed = no
contact_sent = no
user_release_required_before_send = yes
package_ready_for_red_team = false
package_ready_for_send = false

## 1. Purpose

This block prepares contact material for the already assembled OUTREACH01A-05 package. It creates a draft contact letter, a research-context note, a competence-and-boundaries profile, public profile link records, a source inventory, and a validator.

No email is sent. No mail draft is created outside the repository. The new material requires separate Red-Team review before any send decision.

## 2. Material Boundary

The contact material may mention:

- Ralf Kemmann as an independent researcher.
- A Diploma in Chemistry with physical-chemical and solid-state orientation.
- Experience in software development, data architecture, statistics, scientific modelling, and reproducible pipelines.
- QSB as an independent, data-driven, relational, reproducible research framework.
- The OUTREACH01A-DTC-DEMO01 demonstrator as a deliberately small synthetic method example.

The material must not claim:

- that time crystals are explained by QSB;
- that the reported laser system is modelled by QSB;
- that QSB provides a new DTC theory;
- that the AG is being asked to validate QSB;
- that collaboration, endorsement, supervision, or institutional affiliation is requested.

## 3. Requested Assessment Scope

full_QSB_program_assessment_requested = no
question_request_scope_limited = yes
collaboration_requested = false
validation_requested = false
endorsement_requested = false
supervision_requested = false

The requested assessment is limited to the three stable question IDs already present in the OUTREACH01A-05 technical note:

- Q1_IDENTITY_EQUIVALENCE_PHASE
- Q2_BOUNDARY_REPRESENTATION
- Q3_MINIMUM_PHYSICAL_INFORMATION

The wording may refer to a brief indication of whether the distinction is useful, trivial, misleading, or incomplete. It must not ask the group to assess the wider QSB programme.

## 4. Public Source Boundary

The current public-source inventory uses only publicly accessible sources checked on 2026-06-11. The AG Gurevich research and contact pages are treated as official institutional sources. The arXiv record is used only as public DTC-context evidence. Public profile links establish accessibility and identity matching only where that is directly visible.

## 5. Validation Outputs

The validator writes exactly seven files under:

```text
runs/OUTREACH01A-06/contact_materials_validation/
```

Expected final technical status:

```text
contact_letter_and_research_context_prepared
```

This status means that the contact material is prepared for separate review. It does not mean that sending is approved.

Claim detection is a defensive text check. Negation handling is sentence-local with a bounded look-back window:

```text
negation_detection_scope = sentence_local_bounded_window
semantic_proof_performed = false
```

The validator reports positive, negated and ambiguous pattern hits separately. It also derives `full_QSB_program_assessment_requested` from text patterns such as requests to assess, evaluate or review the wider/full/complete QSB programme, with negated boundary statements reported separately.
