# QSB-OUTREACH01A Setup Result Note

## Befund

The QSB-OUTREACH01A side branch was added as an additive repository scaffold. The available scaffold contained PostgreSQL-oriented SQL drafts, while the current repository DWH line is SQLite-oriented and observation-centered. The setup therefore stores adapted SQLite DDL and view proposals as review artifacts and does not execute a database migration.

New branch scope:

- relational state identity
- observable recurrence classes
- forcing and response phase classes
- cycle instances
- lineage from raw observation references to harmonized state rows
- analytical and multilingual presentation views

## Interpretation

The adapted design follows the local DWH route:

```text
raw -> staging -> harmonized -> relational -> analytical -> presentation
```

The SQL proposal uses text primary keys, explicit UTC timestamp fields, lineage references, status fields, and view names in the local `qsb_v_*` presentation style. The multilingual layer is implemented only as view aliases. Canonical technical field names remain unchanged in storage tables and in `canonical_schema.json`.

## Hypothese

This scaffold may be sufficient as a first auditable container for an outreach/contact package about relational recurrence and period-doubled laser dynamics, provided later work supplies reproducible synthetic cases, controls, sensitivity checks, and a reviewed external technical note.

## Offene Luecke

- No real or synthetic demonstrator run was executed.
- No SQLite workcopy was migrated.
- No row-count parity, FK validation against a persistent database, or ERD export was performed.
- No external contact note or email draft was created in this setup step.
- The adapted DDL remains a proposal until reviewed against a frozen DWH workcopy and audit migration log.

## Claim Boundary

This setup does not validate QSB, does not establish a discrete time crystal, does not claim fundamental time discreteness, and does not provide evidence for emergent spacetime, gravitation, Lorentz compatibility, global uniqueness, or physical dynamics. It only creates a reviewable repository and DWH-design scaffold for a bounded methodological contact package.

## Files Created

- `docs/QSB_OUTREACH01A_01_SCOPE_AND_CONTACT_STRATEGY_SPEC.md`
- `docs/QSB_OUTREACH01A_02_RESEARCH_GROUP_FIT_MAPPING.md`
- `docs/QSB_OUTREACH01A_03_RELATIONAL_STATE_IDENTITY_MATHEMATICAL_SPEC.md`
- `docs/QSB_OUTREACH01A_04_DWH_AND_MULTILINGUAL_VIEW_SPEC.md`
- `docs/QSB_OUTREACH01A_05_SYNTHETIC_DEMONSTRATOR_CASE_DEFINITION.md`
- `docs/QSB_OUTREACH01A_09_CONTACT_GATE_CHECKLIST.md`
- `docs/QSB_OUTREACH01A_SETUP_RESULT_NOTE.md`
- `data/QSB-OUTREACH01A/canonical_schema.json`
- `data/QSB-OUTREACH01A/field_aliases.csv`
- `data/QSB-OUTREACH01A/001_qsb_outreach01a_sqlite_dwh_ddl.sql`
- `data/QSB-OUTREACH01A/002_qsb_outreach01a_sqlite_views.sql`
- `scripts/validate_qsb_outreach01a_scaffold.py`
- `runs/QSB-OUTREACH01A/.gitkeep`

## Files Modified

None.

## DWH Objects Proposed

Tables:

- `outreach_case`
- `outreach_raw_observation`
- `outreach_staging_state`
- `outreach_transformation_rule`
- `outreach_harmonized_state`
- `outreach_state_feature`
- `outreach_model_run`
- `outreach_relational_pair`
- `outreach_analytical_result`

Views:

- `qsb_v_outreach01a_state_en`
- `qsb_v_outreach01a_state_de`
- `qsb_v_outreach01a_state_ca`
- `qsb_v_outreach01a_relation_en`
- `qsb_v_outreach01a_relation_de`
- `qsb_v_outreach01a_relation_ca`

## Not Executed Migrations

- `data/QSB-OUTREACH01A/001_qsb_outreach01a_sqlite_dwh_ddl.sql`
- `data/QSB-OUTREACH01A/002_qsb_outreach01a_sqlite_views.sql`

The validator parses these SQL files in an in-memory SQLite database only. It does not modify any persistent DWH database.

## Commands Run

- `sed -n '1,240p' /home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_OUTREACH01A_SETUP.md`
- `pwd`
- `git status --short`
- `rg --files`
- `find /home/ralf-kemmann/Downloads -maxdepth 3 -iname '*OUTREACH01A*' -o -iname '*outreach01a*' -o -iname '*discrete*time*crystal*'`
- `find /home/ralf-kemmann/Downloads -maxdepth 3 -iname '*scaffold*validator*' -o -iname '*canonical*schema*' -o -iname '*field*alias*' -o -iname '*dwh*ddl*'`
- `unzip -l /home/ralf-kemmann/Downloads/QSB_OUTREACH01A_scaffold.zip`
- `find . -maxdepth 4 -type f \( -iname '*.sql' -o -iname '*dwh*' -o -iname '*db*' \)`
- `sed -n '1,240p' data/QSB-DB/schema/qsb_research_db_schema.sql`
- `sed -n '1,220p' runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/dwh01_target_research_dwh_schema_spec.md`
- `sed -n '220,520p' runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/dwh01_target_research_dwh_schema_spec.md`
- `sed -n '1,240p' runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/dwh03_raw_core_ddl.sql`
- `unzip -p ...` reads for scaffold docs, schema, aliases, SQL, and validator files
- `mkdir -p data/QSB-OUTREACH01A runs/QSB-OUTREACH01A`
- `python scripts/validate_qsb_outreach01a_scaffold.py`
- `python -m py_compile scripts/validate_qsb_outreach01a_scaffold.py`
- `find scripts/__pycache__ -maxdepth 1 -type f -name '*validate_qsb_outreach01a_scaffold*' -print`

## Tests And Checks

- `python scripts/validate_qsb_outreach01a_scaffold.py` passed.
- `python -m py_compile scripts/validate_qsb_outreach01a_scaffold.py` passed.
- SQLite DDL and views parsed in an in-memory SQLite database through the validator.
- No persistent DWH migration was executed.

## Output Directory

- `runs/QSB-OUTREACH01A/`

## Generated Ignored Artifact

The syntax check generated `scripts/__pycache__/validate_qsb_outreach01a_scaffold.cpython-312.pyc`. It was not removed in this task because deletion was not explicitly instructed.

## Open Decisions

- Whether OUTREACH01A should later be integrated into the current QSB-DWH consolidated snapshot or kept as a standalone review scaffold.
- Whether persistent IDs should be minted by deterministic content hashes or by an explicit run manifest.
- Which synthetic demonstrator generator and sensitivity configuration should be used.
- Whether language aliases should remain CSV-only or be loaded into a future alias table.

## Correction Run 2026-06-09

### Befund

The targeted correction run synchronized the mathematical specification, DWH schema proposal, views, alias catalog, and validator. The run remained limited to QSB-OUTREACH01A files and did not execute a persistent migration.

### Interpretation

The scaffold now separates state descriptions from historical event instances:

```text
X_k = (O_k, phi_k, r_k, h_k)
E_k = (e_k, c_k, X_k)
```

`model_version` is no longer part of the canonical state-view field list. It remains on `outreach_model_run`, and model-derived relation/result rows preserve provenance through model-run references.

### Hypothese

The corrected scaffold is more internally consistent as a review target because descriptor recurrence, event-instance identity, delay-history representation, model-run provenance, and case-bound pair construction are now explicitly separated.

### Offene Luecke

- No real laser data were used.
- No synthetic demonstrator run was executed.
- No physical threshold calibration was performed.
- Catalan technical display labels remain marked `not_yet_reviewed`.
- The SQL remains a proposal until reviewed against a frozen DWH workcopy.

### Claim Boundary

The correction does not add physical interpretation. It does not validate QSB, does not establish a discrete time crystal, does not claim fundamental time discreteness, and does not provide evidence for emergent spacetime, gravitation, Lorentz compatibility, global uniqueness, or physical dynamics.

### Mathematical Corrections

- Replaced the single mixed state record `S_k=(O_k, phi_k, c_k, r_k, h_k)` with descriptor `X_k` and event instance `E_k`.
- Added the rule that a state description may recur, while a historical event instance does not recur as the same instance.
- Typed history representation as `none`, `finite_history_features`, `delay_window`, or `embedded_history_vector`.
- Added the delay-history function form `x_t(theta) = x(t + theta), theta in [-tau, 0]`.
- Replaced the single comparison `K_(i,i+2) > K_(i,i+1)` with robust lag summary `R(q) = median_{i in I_q} K_(i,i+q)`.
- Declared symmetric minimal pair logic with canonical pair storage.

### DWH Corrections

- Added event/descriptor separation fields: `event_instance_id` and `state_descriptor_id`.
- Added background fields: `background_state_type` and `background_state_json`.
- Added history fields: `history_representation_type`, `history_descriptor_json`, `history_window_start`, `history_window_end`, `history_embedding_method`, and `history_embedding_version`.
- Added `source_checksum_algorithm` and a DDL check that checksum and algorithm are supplied together or both omitted.
- Added composite case-integrity foreign keys on `outreach_relational_pair`.
- Added `state_i_id < state_j_id` and uniqueness constraints for symmetric pair logic.
- Split alias catalog columns into `sql_alias` and `display_label`.
- Kept Catalan SQL aliases ASCII-safe while allowing accented Catalan display labels.

### Tests And Checks

- `python scripts/validate_qsb_outreach01a_scaffold.py` passed.
- `python -m py_compile scripts/validate_qsb_outreach01a_scaffold.py` passed.
- The validator parsed DDL and views in an in-memory SQLite database with `PRAGMA foreign_keys = ON`.
- The validator checked expected tables, views, canonical state-view columns, alias uniqueness, required languages, enum values, JSON sample payloads, self-pair rejection, mirror-pair rejection, and positive/negative case-integrity fixtures.

### Persistent Actions

- No persistent migration was executed.
- No commit was executed.
- No non-OUTREACH01A files were modified by the correction run.
