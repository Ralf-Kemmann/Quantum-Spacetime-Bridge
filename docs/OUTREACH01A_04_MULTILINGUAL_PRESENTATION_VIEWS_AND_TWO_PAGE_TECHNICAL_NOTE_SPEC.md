# OUTREACH01A-04 — Multilingual Presentation Views and Two-Page Technical Note Spec

## 1. Status and Scope

```text
outreach_id = OUTREACH01A-04
canonical_dataset_count = 1
presentation_language_count = 2
presentation_languages = [en, es]
canonical_dataset_shared_across_languages = true
language_specific_dataset_copies_created = false
schema_change_required_for_new_language = false
logic_change_required_for_new_language = false
contact_message_present = false
contact_send_allowed = false
cross_language_comparison_mode = canonical_projection_comparison_of_generated_views
tautological_self_comparison_used = false
hardcoded_positive_consistency_flags_used = false
```

This block creates English and Spanish human-readable presentation layers over the same canonical synthetic demonstrator dataset. It does not create a contact message, does not render a figure, and does not alter the schema, records, validation logic, keys, joins, or canonical controlled values.

## 2. Canonical Dataset

The only canonical dataset is:

```text
data/OUTREACH01A-DTC-DEMO01/dtc_state_identity_records.json
```

It contains exactly:

```text
DTC_A
DTC_B
BOUNDARY_AB
```

Language-specific dataset copies are not created. Presentation views read the same records in the same order and display only localized field aliases and controlled-value aliases.

## 3. Presentation Layers

English presentation artifacts:

- `data/OUTREACH01A-DTC-DEMO01/field_aliases_en.json`
- `data/OUTREACH01A-DTC-DEMO01/compact_contact_table_en.md`
- `docs/OUTREACH01A_04_TWO_PAGE_TECHNICAL_NOTE_DRAFT_EN.md`

Spanish presentation artifacts:

- `data/OUTREACH01A-DTC-DEMO01/field_aliases_es.json`
- `data/OUTREACH01A-DTC-DEMO01/compact_contact_table_es.md`
- `docs/OUTREACH01A_04_TWO_PAGE_TECHNICAL_NOTE_DRAFT_ES.md`

Both alias files use the same structure:

```text
field_aliases
value_aliases
presentation_metadata
```

## 4. Cross-Language Consistency

The builder must compare canonical projections of the generated English and Spanish views. Each presentation row carries display text plus the canonical record values used to create it. Consistency is established from the English canonical projection versus the Spanish canonical projection, not by comparing the canonical dataset to itself.

The builder must compute:

```text
canonical_record_ids_match = true
canonical_record_order_matches = true
canonical_field_set_matches = true
canonical_value_set_matches = true
record_count_matches = true
logic_results_match = true
validation_results_match = true
only_display_language_differs = true
```

No language layer may add records, remove records, alter canonical values, change result logic, or introduce different identity or equivalence claims. Alias completeness is checked for the declared presentation fields and for controlled values actually present in the canonical demonstrator. Validation-result consistency is checked by comparing the shared canonical validation-source reference used by both language layers.

## 5. Technical Notes

The English and Spanish technical-note drafts must cover the same content:

1. Purpose / Propósito
2. Why This Representation / Por qué esta representación
3. The Three Records / Los tres registros
4. Identity, Equivalence and Phase Offset / Identidad, equivalencia y desfase
5. Boundary Representation as an Open Question / La representación de la frontera como cuestión abierta
6. Technical Questions / Preguntas técnicas
7. Scope and Limitations / Alcance y limitaciones

Each note must contain exactly three technical questions. The notes are draft presentation material only and are not contact messages.

## 6. Figure Content

The figure content specification is language-neutral:

```text
figure_content_language_neutral = true
caption_localization_required = true
supported_caption_languages = [en, es]
figure_rendered = false
```

No graphic is rendered in this block.

## 7. Limitations

- Both language views are presentation layers over one canonical dataset.
- Neither language view changes the schema, logic, keys, joins, or validation results.
- The demonstrator remains synthetic and is not a model of the reported laser experiment.
- Dynamic equivalence is declared for method demonstration.
- The separate boundary record remains an open representation option.
- No figure is rendered.
- No contact message is drafted or sent.
