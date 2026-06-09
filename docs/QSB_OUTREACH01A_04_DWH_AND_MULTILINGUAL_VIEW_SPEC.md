# QSB-OUTREACH01A-04 - DWH And Multilingual View Specification

## Data Route

```text
raw -> staging -> harmonized -> relational -> analytical -> presentation
```

The local repository DWH line is SQLite-oriented and observation-centered. The original scaffold SQL was PostgreSQL-oriented; this branch stores adapted SQL as a reviewable design artifact and does not execute migrations.

## Design Rules

1. Raw records remain immutable.
2. Every derived record retains source lineage.
3. Canonical technical field names remain stable.
4. Language-specific names exist only in views and alias catalogs.
5. SQL aliases remain ASCII-safe.
6. Human display labels are stored separately from SQL aliases.
7. Transformations, descriptor representations, and model runs are versioned.
8. Result tables distinguish observed, derived, and interpreted fields.
9. Migration execution requires a separate freeze/workcopy/audit step.

## DWH Alignment

| OUTREACH01A object | DWH layer | Local convention |
| --- | --- | --- |
| `outreach_case` | audit/provenance sidecar | text primary key, status fields, UTC timestamps |
| `outreach_raw_observation` | raw / entrance | immutable source payload reference, checksum, checksum algorithm |
| `outreach_staging_state` | raw-to-core staging | source-local event and descriptor candidate |
| `outreach_harmonized_state` | core / observation-centered | event instance plus state descriptor fields with lineage |
| `outreach_state_feature` | observation / signal fact | one row per state feature |
| `outreach_model_run` | audit/provenance sidecar | run code, model version, config JSON text |
| `outreach_relational_pair` | bridge / connection-style relation | case-bound symmetric pairwise score and class flags |
| `outreach_analytical_result` | result / evaluation | derived result payload with interpretation level |
| presentation views | report / view layer | SQL-safe language aliases only |

## Descriptor Versus Instance

The DWH stores both:

- `event_instance_id`: the unique historical event or state-instance identifier.
- `state_descriptor_id`: the descriptor identity for the represented dynamic state.

The cycle index belongs to the event instance. Recurrence claims must refer to descriptor recurrence, not event-instance recurrence.

## History And Background Fields

The harmonized state layer declares:

- `background_state_type`
- `background_state_json`
- `history_representation_type`
- `history_descriptor_json`
- `history_window_start`
- `history_window_end`
- `history_embedding_method`
- `history_embedding_version`

Allowed `history_representation_type` values are:

- `none`
- `finite_history_features`
- `delay_window`
- `embedded_history_vector`

The field `history_descriptor_json` may contain compressed or partial descriptors. It is not automatically equivalent to a full delay-system history function.

## Model-Run Provenance

`model_version` belongs to `outreach_model_run`, not to the canonical state field list. States are linked to model outputs through `outreach_relational_pair` and `outreach_analytical_result`, both of which reference `outreach_model_run`.

## Case Integrity Rule

`outreach_relational_pair` stores `outreach_case_id` and uses composite foreign keys so that:

- the model run belongs to the same case as the pair;
- `state_i_id` belongs to the same case as the pair;
- `state_j_id` belongs to the same case as the pair.

This prevents silent cross-case relation rows in SQLite when `PRAGMA foreign_keys = ON`.

## Symmetric Pair Rule

The minimal scaffold uses symmetric pair logic:

```text
K_ij = K_ji
```

The DDL stores only canonical pair order by requiring:

```text
state_i_id < state_j_id
```

Self-pairs and duplicate mirror pairs are rejected.

## Core Entities

- `outreach_case`
- `outreach_raw_observation`
- `outreach_staging_state`
- `outreach_harmonized_state`
- `outreach_state_feature`
- `outreach_transformation_rule`
- `outreach_model_run`
- `outreach_relational_pair`
- `outreach_analytical_result`

## Presentation Views

- `qsb_v_outreach01a_state_en`
- `qsb_v_outreach01a_state_de`
- `qsb_v_outreach01a_state_ca`
- `qsb_v_outreach01a_relation_en`
- `qsb_v_outreach01a_relation_de`
- `qsb_v_outreach01a_relation_ca`

## Catalan View Principle

Catalan SQL aliases remain ASCII-safe. Catalan `display_label` values in `field_aliases.csv` may contain accents and typographic apostrophes for human display. Catalan technical translations are marked as requiring specialist language review before external use.

## Migration Boundary

The SQL files in `data/QSB-OUTREACH01A/` are not applied to any persistent database in this correction step. They are DDL proposals for later review against the current QSB-DWH workcopy process.
