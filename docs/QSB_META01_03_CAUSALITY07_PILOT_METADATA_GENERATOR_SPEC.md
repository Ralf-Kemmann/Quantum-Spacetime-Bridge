# QSB-META01-03 — CAUSALITY07 Pilot Metadata Generator Spec

## Purpose

QSB-META01-03 implements a first productive metadata-generation pilot for the existing `QSB-CAUSALITY07` datamart. The pilot reads repository-local CAUSALITY07 artifacts, registers them under the META01-02 canonical metadata schema, and writes a local SQLite metadata catalog plus audit CSVs.

The task is metadata registration only. It does not migrate, rewrite, reinterpret, or selectively retain CAUSALITY07 scientific data.

## Inputs

The runner reads:

- META01-02 schema: `data/QSB-META01-02/canonical_metadata_schema.sql`
- META01-02 controlled vocabularies: `data/QSB-META01-02/controlled_vocabularies.json`
- META01-02 unit and dimension registry: `data/QSB-META01-02/unit_dimension_registry.json`
- Pilot config: `data/QSB-META01-03/causality07_pilot_metadata_config.json`
- Human-curated pilot mapping: `data/QSB-META01-03/causality07_metadata_mapping.json`
- Discovered CAUSALITY07 artifacts under `docs/`, `data/`, `scripts/`, and `runs/`

Discovery is token-based for `QSB-CAUSALITY07`, `QSB_CAUSALITY07`, `CAUSALITY07`, `07-01`, `07-02`, and `07-03`. Repository-relative paths are used for all stored paths.

## Outputs

The required command is:

```bash
.venv/bin/python \
  scripts/run_qsb_meta01_03_causality07_pilot_metadata_generator.py \
  --input-root . \
  --output-dir runs/QSB-META01-03/causality07_pilot_metadata \
  --overwrite
```

The runner writes exactly:

1. `resolved_pilot_config.json`
2. `canonical_object_registry.csv`
3. `canonical_field_registry.csv`
4. `lineage_edge_registry.csv`
5. `record_lineage_registry.csv`
6. `validation_result_registry.csv`
7. `result_claim_link_registry.csv`
8. `qsb_metadata_catalog.sqlite`
9. `run_summary.json`
10. `readout.md`

## Identity Rules

Stable logical identifiers are deterministic hashes over repository-relative object or field references. They do not use timestamps, file modification times, row order as identity source, German aliases, or absolute paths.

The generator keeps separate:

- mart identity
- work-package identity
- logical object identity
- object-version identity
- run identity
- result-record identity

Object versions are tied to content checksums.

## Metadata Status

Generated registry rows distinguish:

- `explicit_source`
- `rule_derived`
- `human_curated_mapping`
- `unresolved`
- `not_applicable`

Confidence classes are recorded as `high`, `medium`, `low`, or `not_applicable`.

Filename and keyword matching are treated as signals for metadata registration, not scientific evidence.

## Unit and Dimension Policy

The ordered dimension vector is `[L, M, T, I, Theta, N, J]`.

CAUSALITY07 model time remains `model_unit_unmapped` unless an explicit SI mapping is present in audited artifacts. The generator does not convert model time to seconds. Counts and ordinal indices are registered as dimensionless counts. Phase labels and phase sequences are categorical. Reduced-state distance, drift proxy, and threshold-like fields remain unresolved unless explicit normalization or physical dimension metadata is present.

## German Alias Policy

German aliases are inserted only into `meta_alias` and German SQLite views. They are presentation metadata and are not used for identity, joins, calculations, transformation logic, or lineage.

The required German views are:

- `v_de_physikalische_groessen`
- `v_de_lineage`
- `v_de_validierungsergebnisse`
- `v_de_ergebnis_claim_beziehungen`
- `v_de_offene_pruefpunkte`

## Result and Claim Policy

The generator registers CAUSALITY07 result objects and materialized record lineage for baseline and control result rows where available. Claims are limited to statements present in or faithfully bounded by CAUSALITY07 readouts and result notes:

- recurrence under a predefined phase sequence
- control selectivity against reverse and scrambled sequences
- recurrence not establishing full state identity
- no independent reconstruction of global cycle order
- threshold not empirically calibrated

No global QSB claim is generated.

## Validation

The runner validates core catalog integrity, foreign keys, work-package representation, checksum presence, mandatory German aliases, result-to-claim links, model-unit handling, and retention of unresolved review items. Failed required checks cause a non-zero exit.

## Claim Boundary

This pilot is a metadata and lineage-registration artifact. It does not establish physical causality, emergent time, full chemical-state identity, global uniqueness, global rarity, or laboratory validation.
