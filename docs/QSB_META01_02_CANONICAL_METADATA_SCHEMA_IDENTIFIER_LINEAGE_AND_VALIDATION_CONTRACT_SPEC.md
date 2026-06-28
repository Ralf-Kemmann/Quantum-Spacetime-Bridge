# QSB-META01-02 Canonical Metadata Schema, Identifier Lineage and Validation Contract Spec

## Scope

QSB-META01-02 converts the META01-01 inventory findings into a precise canonical metadata contract and a SQLite-compatible schema skeleton. It is part of ETL design because metadata must be produced together with import, normalization, SI conversion, lineage, validation, result classification, and claim linkage. Post-hoc documentation alone cannot provide field-level or record-level auditability.

This block performs no mart migration, renaming, schema rewrite, or production metadata-generation implementation.

## Datamart, Work Package, Object, Version, Run

- A datamart is the subject-level metadata namespace, such as `qsb.causality.07`.
- A work package is a task-level unit inside a datamart, such as `qsb.causality.07.03`.
- An object is a logical metadata object inside a mart namespace.
- A version is a version-specific identity for a logical object.
- A run is an execution identity and remains separate from logical and version identity.

Human-facing repository identifiers remain unchanged. Canonical machine namespaces are lowercase and machine-safe. Display labels are never identifiers.

## Identifier Rules

The contract separates:

```text
mart_code
work_package_code
object_code
object_version_id
run_id
```

Stable logical IDs must not depend on timestamps, file modification times, row order, display aliases, or local absolute paths. Version IDs may include schema version and content checksum. Run IDs may include execution tokens but must not replace object identity.

## Field Lineage

Field lineage is mandatory for canonical mart tables, calculation tables, validation tables, result tables, and claim-link tables.

Allowed derivation classes:

```text
direct_copy
renamed_copy
unit_conversion
normalized_value
derived_expression
constant_with_rule
lookup_mapping
aggregation
classification
presentation_alias
```

Every non-presentation target field must declare source objects, source fields where applicable, transformation rule, expression or mapping reference, source unit, calculation unit, display unit, dimension vector, validation references, and ETL/run reference. A derived field without dependencies fails validation.

## Record Lineage

The contract uses four lineage modes:

```text
materialized
reconstructable
aggregate_membership
not_applicable
```

`materialized` is required for result rows, claim-used rows, inclusions, exclusions, manually adjudicated records, and transformations where exact source membership cannot otherwise be reconstructed.

`reconstructable` is allowed for deterministic one-to-one transformations when source key, target key, run, and rule are sufficient.

`aggregate_membership` requires explicit membership or a reproducible selection predicate plus source snapshot/checksum and group key.

`not_applicable` is limited to schema-only, vocabulary-only, or documentation-only objects.

## Units and Dimensions

Source, calculation, and display units are separate:

```text
unit_original
unit_calculation
unit_display
```

Calculations use coherent SI units where the model has a mapped physical unit. Display may use useful SI-prefixed units such as `ms`, `nm`, or `kHz`. Model units must use an explicit status such as `model_unit_unmapped` and must not be silently promoted to seconds or metres.

The dimension vector is ordered:

```text
[L, M, T, I, Theta, N, J]
```

Dimensions are algebraic validation inputs. Dimensionless values still require `quantity_kind`, such as ratio, probability, count, index, angle, or phase.

## German Aliases

Canonical technical field names remain language-neutral. German aliases are stored in the presentation-alias layer and exposed in the field registry:

| Canonical field | German alias |
|---|---|
| `quantity_kind` | `Groessenart` |
| `value_original` | `Originalwert` |
| `unit_original` | `Originaleinheit` |
| `value_calculation` | `Berechnungswert` |
| `unit_calculation` | `Berechnungseinheit` |
| `value_display` | `Anzeigewert` |
| `unit_display` | `Anzeigeeinheit` |
| `dimension_vector` | `Dimensionsvektor` |
| `conversion_rule_id` | `Umrechnungsregel-ID` |
| `unit_status` | `Einheitenstatus` |
| `dimension_status` | `Dimensionsstatus` |

German aliases do not define identity, keys, joins, lineage, transformation inputs, or calculations. Additional languages can be added by alias registry entries without changing canonical field names.

## Validation Architecture

`meta_validation_result` is a first-class object. Validation layers include schema, syntax, referential integrity, unit conversion, unit algebra, dimension, formal mathematics, numerical checks, physical assumptions, physical boundary conditions, physical plausibility, evidence, and claim boundary.

Physical validity is stricter than mathematical validity. A result must never be marked physically valid solely because formal mathematics and dimensions pass.

## Result-to-Claim Linkage

Claims do not point directly to raw files. The required chain is:

```text
claim -> claim_result_link -> result table/result row -> lineage -> mart objects -> source
```

Link relations include `supports`, `contradicts`, `qualifies`, `limits`, and `context_only`. Supporting, neutral, contradictory, inconclusive, non-comparable, and invalidated results remain searchable.

## Later Search Runs

Later search runs can query the metadata catalog as a scientific index: by mart, work package, source, result class, validation state, unit/dimension status, lineage mode, evidence class, and claim relation. This block defines the contract surface but does not implement search indexing.

## What Remains for META01-03

META01-03 should define a small pilot migration or generator-readiness gate, benchmark record-lineage storage strategy, and decide domain-specific quantity-kind extensions. It should still avoid broad automatic migration until human-reviewed acceptance criteria are met.

## Limitations

- This is a canonical contract and schema skeleton, not production metadata-generation tooling.
- No mart migration was performed.
- The unit registry is intentionally minimal and extensible.
- Domain-specific quantity kinds and validation rules require later block-specific review.
- Record-lineage volume and storage strategy have not yet been benchmarked.
- Search indexing has not yet been implemented.
