# QSB-META02 Cross-Mart Key Mapping and Transformation Registry Specification

## Purpose

QSB-META02 creates a metadata architecture layer for controlled cross-mart joins. A single mart carries only part of the QSB answer: META01 describes metadata structure, CAUSALITY07 carries cyclic/directional calibration records, CORRCORE01 carries correlation-core objects and claim boundaries, IDSPACE/CPNS carries identity and ambiguity safeguards, and future marts may carry Shapiro, C60/structure, tunneling, or interface-synthesis material.

Cross-mart use is therefore useful only when keys, transformations, unit and dimension decisions, lineage, validation state, identity semantics, and claim boundaries are explicit.

## Core Rule

A cross-mart join is not scientifically valid merely because SQL can join two fields. Field-name similarity, label equality, or matching text values are not sufficient. A join contract must state:

- source and target mart,
- source and target object/table/view,
- source and target field,
- field type,
- key role,
- technical transformation,
- semantic relation,
- unit conversion,
- dimension compatibility,
- identity compatibility,
- lineage/provenance,
- validation status,
- claim-boundary propagation,
- evidence role,
- review status.

Unknown, ambiguous, or missing conditions must keep a join pending, blocked, or out of scope.

## Transformation Discipline

Transformation rules are registered separately from mappings. A mapping references a rule such as exact text match, case/whitespace normalization, prefix stripping, decimal casting, symbol normalization, SI-prefix conversion, label-to-phase-class mapping, or explicit blocking rules. This avoids hidden code paths and prevents later runs from treating a transformation as obvious when it is not documented.

## Unit And Dimension Discipline

Numerical joins require quantity-kind and dimension compatibility before value comparison. Unit conversions require explicit source unit, target unit, conversion expression, and precision status. Dimensionless fields are not semantically equivalent by default. Model time remains unmapped unless a later block defines a valid mapping. Angles/radians remain dimensionless but retain angle convention.

String-to-integer conversion for keys is a key transformation, not a unit conversion.

## Identity And Label Discipline

META02 distinguishes same label, same phase class, same fingerprint key, same state class, same state instance, same identity candidate, and same causal generation. This is needed for later recurrence and causality checks such as distinguishing `A_n -> B_n -> A_n` from `A_n -> B_n -> A_{n+1}`. META02 does not implement a physics law; it supplies metadata structure for later validation.

## Claim-Boundary Propagation

Every join must carry claim boundaries forward. Required boundaries include technical join not scientific equivalence, same label not same identity, diagnostic similarity not identity resolution, conceptual context not evidence transfer, unit conversion not physical validation, dimension compatibility not same quantity, model time not physical time, cross-mart convergence not proof, planned mapping not active join, and blocked join not negative evidence.

## Later Convergence Arguments

META02 supports later convergence arguments by making joins auditable. Convergence can increase plausibility only when independent marts are linked through validated mappings and retained claim boundaries. It is not proof, and it does not validate QSB, an Interface layer, physical causality, or physical spacetime emergence.

## Keeping Cross-Mart Mapping Tables Current

Cross-mart mapping tables become stale because marts evolve independently. A mart update can add, remove, rename, or reclassify objects, result tables, result records, fields, units, dimensions, aliases, validation states, lineage records, and claim boundaries. Any of those changes can invalidate a join that was previously technically possible or reviewed as scientifically usable.

The META02 refresh workflow is therefore report-only by default:

```text
scan -> compare -> report -> propose candidates -> do not mutate registry
```

The refresh process scans current catalog metadata and compares it against the stored registry. It must inspect mart, work-package, object, field, result-table, result-record, quantity-kind, unit, validation, claim, claim-result-link, lineage, record-lineage, and alias metadata. For each known mapping it records schema and record fingerprints for source and target sides, existence checks, unit/dimension change status, claim-boundary change status, validation-status change status, mapping freshness status, required action, and review status.

Where exact field-level references are not yet available, the refresh report records `field_level_reference_incomplete` rather than pretending the mapping has been fully checked.

Candidate mappings must never be auto-approved. Candidate discovery may use identical canonical names, identical `source_result_key`, shared quantity kind, shared dimension vector, alias matches, transformation-rule applicability, or table-role compatibility. Every candidate defaults to `new_candidate_unreviewed` and cannot be used as evidence until reviewed.

Stale mappings are retained for audit with required actions such as `review_mapping`, `rebuild_mapping`, `block_mapping`, or `retire_mapping`. Blocked mappings are not deleted: their blocked state is part of the scientific audit trail and prevents a later synthesis step from silently reviving an unsafe join.

This maintenance layer supports future controlled synthesis by making mapping drift visible before any convergence argument is attempted. It does not itself establish convergence or proof.

## DWH Practice

The design follows established cross-mart integration practice: keys and transformations are data, not implicit code; lineage and validation are first-class; unit/dimension semantics are checked before numerical use; and unresolved mappings remain explicitly blocked or pending rather than silently joined.
