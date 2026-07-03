# Run commands — QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

RUN="QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01"
ZIP="$HOME/Downloads/QSB_PLANCK_BRIDGE_SCALE_MAPPING_NOTE01_2026-07-03.zip"

mkdir -p "runs/$RUN"
unzip -q "$ZIP" -d "runs/$RUN"

cd "runs/$RUN/QSB_PLANCK_BRIDGE_SCALE_MAPPING_NOTE01_2026-07-03"

python3 scripts/validate_scale_mapping_dimensions.py | tee validation/validate_scale_mapping_dimensions.log

unset PGHOST
unset PGPASSWORD
export PGDATABASE=qsb_research_dwh
export PGUSER='ralf-kemmann'
export PGPORT=5432

psql -v ON_ERROR_STOP=1   -f sql/20260703_qsb_planck_bridge_scale_mapping_note01_import.sql

psql -v ON_ERROR_STOP=1   -f sql/validate_planck_bridge_scale_mapping_note01_import.sql   | tee validation/validate_planck_bridge_scale_mapping_note01_import.log

psql -v ON_ERROR_STOP=1   -f sql/20260703_qsb_planck_bridge_scale_mapping_note01_metadata_integration.sql

psql -v ON_ERROR_STOP=1   -f sql/validate_planck_bridge_scale_mapping_note01_metadata_integration.sql   | tee validation/validate_planck_bridge_scale_mapping_note01_metadata_integration.log
```

## DBeaver checks

```sql
SELECT *
FROM qsb_scale_mapping.v_planck_bridge_scale_mapping_dashboard;
```

```sql
SELECT *
FROM qsb_metadata.v_planck_bridge_scale_mapping_note01_metadata_dashboard;
```

## Git

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

git status --short
git diff --check

git add -f runs/QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01

git commit -m "Add Planck Bridge scale mapping note"

git push
```
