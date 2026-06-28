# QSB-META01-03 Final Result Note

## Befund

QSB-META01-03 adds a repository-local metadata generator for the CAUSALITY07 pilot mart. The created runner reads the META01-02 schema, controlled-vocabulary file, unit/dimension registry, pilot config, and CAUSALITY07 repository artifacts. It writes a local SQLite metadata catalog and audit CSVs under `runs/QSB-META01-03/causality07_pilot_metadata/`.

The generator registers mart, work-package, object, object-version, field, lineage, validation, result, claim-link, alias, unit, quantity-kind, and vocabulary metadata. It uses repository-relative paths and content checksums.

## Interpretation

The pilot provides an audit-ready metadata catalog for CAUSALITY07 without modifying CAUSALITY07 scientific artifacts. It separates explicit source metadata, rule-derived metadata, human-curated mappings, unresolved mappings, and presentation aliases.

Model-time quantities are not converted to SI units. Reduced-state distance, drift proxy, and threshold-like fields are retained as unresolved where the audited artifacts do not provide explicit physical-unit or normalization evidence.

## Hypothese

The generated catalog can serve as a first META01 metadata architecture pilot for reviewing CAUSALITY07 lineage, result-to-claim relationships, unresolved unit decisions, and human-review items. Later blocks can harden mappings or vocabulary activation decisions without changing this pilot's claim boundary.

## Offene Lücke

Some CAUSALITY07 fields do not expose explicit unit, dimension, or normalization declarations in the audited artifacts. Those fields remain searchable unresolved metadata and require human review before any stronger physical interpretation.

Some META01-02 vocabulary domains are represented by schema/CHECK domains rather than active rows in the controlled-vocabulary JSON file. The pilot records this distinction locally and does not auto-activate new scientific vocabulary entries.

## Claim Boundary

QSB-META01-03 is a metadata-generation and lineage-registration pilot. It does not establish physical causality, emergent time, full chemical-state identity, global uniqueness, global rarity, or laboratory validation. CAUSALITY07 result claims remain bounded to the reduced model outputs and runner semantics documented in the source artifacts.
