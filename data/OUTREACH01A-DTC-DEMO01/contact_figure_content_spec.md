# OUTREACH01A-DTC-DEMO01 Contact Figure Content Specification

```text
figure_content_language_neutral = true
caption_localization_required = true
supported_caption_languages = [en, es]
figure_rendered = false
canonical_dataset_count = 1
language_specific_dataset_copies_created = false
```

The later figure should show one shared canonical dataset with three records:

- `DTC_A`: synthetic state configuration in `DOMAIN_A`, phase offset `0`.
- `DTC_B`: synthetic state configuration in `DOMAIN_B`, phase offset `1`.
- `BOUNDARY_AB`: separate boundary record connecting `DOMAIN_A` and `DOMAIN_B`.

Suggested visual structure:

1. Left domain box: `DOMAIN_A`, record `DTC_A`, phase offset `0`.
2. Right domain box: `DOMAIN_B`, record `DTC_B`, phase offset `1`.
3. Center boundary marker: `BOUNDARY_AB`, representation-choice-open status.
4. Shared equivalence bracket over `DTC_A` and `DTC_B`: `DTC_EQ_CLASS_01`.
5. Caveat strip: synthetic method demonstrator, no experimental data, no laser-model claim.

No graphic is rendered in this block. Only the language-neutral content specification is created.
