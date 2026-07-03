# Run Commands — QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
mkdir -p runs/QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01
# Paketinhalt nach runs/QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01/ kopieren oder entpacken.

cd runs/QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01
export PGDATABASE=qsb_research_dwh
export PGUSER='ralf-kemmann'
export PGHOST=localhost
export PGPORT=5432

psql -v ON_ERROR_STOP=1 -f sql/20260703_qsb_planck_bridge_litnote01_import.sql
psql -v ON_ERROR_STOP=1 -f sql/validate_planck_bridge_litnote01_import.sql
```

## DBeaver Quick Check

```sql
SELECT *
FROM qsb_literature.v_planck_bridge_litnote01_claim_boundary;

SELECT pillar_label, COUNT(*)
FROM qsb_literature.reference_source
WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01'
GROUP BY pillar_label
ORDER BY pillar_label;
```
