# QSB-META01-01 Existing Metadata Lineage Inventory and Canonical Contract Spec

## 1. Ziel und Scope

QSB-META01-01 inventories existing repository patterns for metadata, provenance, lineage, units, dimensions, validation, results, evidence, aliases, views, and claim boundaries. It prepares a draft canonical metadata contract for later human review.

This block is read-only with respect to existing datamarts. It creates a bounded inventory and a draft contract, but it does not migrate schemas, rewrite existing files, modify raw data, or write a productive database.

## 2. Abgrenzung zu produktiver Implementierung und Migration

The runner scans configured repository paths and writes only its own run outputs under:

```text
runs/QSB-META01-01/repository_metadata_inventory/
```

The result is not a productive metadata generator. Detected signals are inventory evidence only. File names, short excerpts, and repeated field names do not prove final semantics.

## 3. Normalisierte Datamart-Kette

The canonical chain stages for META01 are:

```text
research_question
raw_source
import
normalization
coherent_si_conversion
mapping_and_domain_rules
calculation
formal_mathematical_validation
unit_validation
dimensional_validation
physical_validation
canonical_dataset
human_readable_view
analysis
result_table
evidence_classification
scientific_claim
```

An object may map to more than one stage in later work. In this first inventory, the runner emits one primary detected stage per file and marks the mapping confidence as `explicit`, `strongly_inferred`, `weakly_inferred`, or `unknown`.

## 4. Inventurmethodik

The runner:

- scans only configured include paths;
- excludes `.git`, `.venv`, caches, and its own output directory;
- skips symlinks and does not leave the repository root;
- parses only configured text-like extensions;
- limits text reads by `max_text_bytes_per_file`;
- computes hashes only when configured and practical;
- emits short excerpts for detected signals;
- separates detected repository patterns from proposed canonical contract objects.

Weak or unknown inference is not treated as established architecture.

## 5. Kanonische Metaobjekte

The draft contract contains these logical objects:

```text
meta_mart
meta_object
meta_field
meta_key
meta_source
meta_pipeline_run
meta_transformation_rule
meta_unit
meta_dimension
meta_validation_rule
meta_validation_result
meta_lineage_edge
meta_result_table
meta_result_record
meta_evidence
meta_claim
meta_alias
```

The fields are draft fields for review. They are not yet a final database schema.

## 6. Identitäts- und Schlüsselprinzipien

Object identifiers should be deterministic and derived from object type plus normalized repository path or canonical name. Human-readable aliases must not define identity. German aliases and other localized labels remain presentation metadata only.

The contract must keep key metadata separate from display names:

```text
meta_key.key_type
meta_key.field_order
meta_key.referenced_object_id
meta_key.identity_scope
```

## 7. Einheiten- und Dimensionsmodell

Physical quantities must carry unit and dimension metadata where applicable. Display units and coherent SI calculation units are separate:

```text
display_unit_id
coherent_si_unit_id
```

The draft dimension signature uses the exponent vector:

```text
L, M, T, I, Theta, N, J
```

for length, mass, time, electric current, thermodynamic temperature, amount of substance, and luminous intensity. Dimensionless values have all exponents set to zero and `is_dimensionless = true`.

## 8. Validierungsmodell

Formal mathematical validity and physical validity are separate. The draft validation classes include:

```text
schema
referential_integrity
range
unit_conversion
unit_algebra
dimensional_consistency
numerical
formal_mathematical
physical_assumption
physical_boundary_condition
physical_plausibility
evidence_completeness
claim_boundary
```

Validation results can be `passed`, `failed`, `warning`, `not_applicable`, `not_tested`, or `requires_human_review`.

## 9. Lineage-Modell

`meta_lineage_edge` is designed for object, field, and optional record lineage:

```text
lineage_scope = object | field | record
lineage_status = available | not_available | not_implemented | requires_human_review
```

Missing record lineage must not be invented. It must be recorded as unavailable, not implemented, or requiring human review.

## 10. Vollständige Ergebnisaufnahme

All result directions must remain representable. The draft `result_class` vocabulary includes:

```text
supports
contradicts
neutral
inconclusive
not_comparable
missing
invalid
```

Claims must be able to reference supporting, contradicting, and neutral result tables. Selecting only hypothesis-supporting rows is outside the contract boundary.

## 11. Alias- und Mehrsprachigkeitsregel

`meta_alias` records presentation labels:

```text
alias_id
canonical_object_type
canonical_object_id
language_code
alias_text
presentation_scope
```

Alias text may not control logic, identity, joins, or lineage.

## 12. Suchperspektive für spätere blockübergreifende Läufe

Later META01 blocks can use this inventory to decide which blocks already have reusable patterns for source inventories, run summaries, field lists, result notes, schema objects, validation checks, evidence rows, and claim boundaries.

The next stage should not migrate files automatically. It should first define human-reviewed acceptance criteria for mart IDs, object IDs, field-level lineage, record-level lineage, unit/dimension completeness, and claim-linking rules.

## 13. Grenzen und offene Entscheidungen

Limitations:

- bounded text scanning can miss patterns beyond the configured read limit;
- terms in file names are only signals;
- existing patterns are not assumed complete;
- raw record lineage is not assumed unless explicitly present;
- the contract is a draft and requires human review.

Open decisions:

- Human decision required: canonical mart naming convention.
- Human decision required: minimum metadata completeness gate per datamart type.
- Human decision required: when record-level lineage is mandatory.
- Human decision required: how to extend controlled vocabularies per scientific domain.
