# QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01

DWH-Importpaket für `QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01`.

## Zweck

Dieses Paket registriert die BibTeX-Bibliografie der Literature Note 01 im PostgreSQL-DWH als prüfbaren Literatur- und Claim-Mapping-Bestand.

## Claim Boundary

Die Referenzen motivieren die Interface-Frage. Sie beweisen nicht die Existenz eines Planck-Bridge-Resonators.

`physical_claim_status = blocked_no_physics_claim`

## Zielobjekte

Schema: `qsb_literature`

Tabellen / View:

- `qsb_literature.litnote_run`
- `qsb_literature.reference_source`
- `qsb_literature.reference_claim_map`
- `qsb_literature.v_planck_bridge_litnote01_claim_boundary`

## Inhalt

- Referenzen: 14
- Claim-Mapping-Zeilen: 14
- Source SHA256: `78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27`

## Import

Aus Repo-Root oder aus diesem Paketordner:

```bash
export PGDATABASE=qsb_research_dwh
export PGUSER='ralf-kemmann'
export PGHOST=localhost
export PGPORT=5432
psql -v ON_ERROR_STOP=1 -f sql/20260703_qsb_planck_bridge_litnote01_import.sql
psql -v ON_ERROR_STOP=1 -f sql/validate_planck_bridge_litnote01_import.sql
```

Optional:

```bash
python3 scripts/load_planck_bridge_litnote01_to_postgres.py
```

## Erwartete Validierung

- `reference_source`: 14 Zeilen für den Run
- `reference_claim_map`: 14 Zeilen für den Run
- `physical_claim_release`: ausschließlich `blocked_no_physics_claim`

## DWH-Haltung

Das Paket gibt methodische Literatur-Readiness, aber keine physikalische Claim-Freigabe.
