# Run commands for QSB-PLANCK-BRIDGE-LITERATURE-ADDENDUM-ASHREUROV-2014-01

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

RUN="QSB-PLANCK-BRIDGE-LITERATURE-ADDENDUM-ASHREUROV-2014-01"
ZIP="$HOME/Downloads/QSB_PLANCK_BRIDGE_LITERATURE_ADDENDUM_ASHREUROV_2014_2026-07-05.zip"

mkdir -p "runs/$RUN"
unzip -q "$ZIP" -d "runs/$RUN"

cd "runs/$RUN/QSB_PLANCK_BRIDGE_LITERATURE_ADDENDUM_ASHREUROV_2014_2026-07-05"

unset PGHOST
unset PGPASSWORD

export PGDATABASE=qsb_research_dwh
export PGUSER='ralf-kemmann'
export PGPORT=5432

mkdir -p validation

psql -v ON_ERROR_STOP=1   -f sql/20260705_qsb_planck_bridge_lit_addendum_ashreurov_2014_import.sql

psql -v ON_ERROR_STOP=1   -f sql/validate_planck_bridge_lit_addendum_ashreurov_2014_import.sql   | tee validation/validate_planck_bridge_lit_addendum_ashreurov_2014_import.log

psql -v ON_ERROR_STOP=1   -f sql/20260705_qsb_planck_bridge_lit_addendum_ashreurov_2014_metadata_integration.sql

psql -v ON_ERROR_STOP=1   -f sql/validate_planck_bridge_lit_addendum_ashreurov_2014_metadata_integration.sql   | tee validation/validate_planck_bridge_lit_addendum_ashreurov_2014_metadata_integration.log
```

## DBeaver checks

```sql
SELECT *
FROM qsb_literature.v_planck_bridge_lit_addendum_ashreurov_2014_claim_boundary;
```

```sql
SELECT *
FROM qsb_metadata.v_planck_bridge_lit_addendum_ashreurov_2014_metadata_dashboard;
```

## Git

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

git status --short
git diff --check

git add -f runs/QSB-PLANCK-BRIDGE-LITERATURE-ADDENDUM-ASHREUROV-2014-01

git commit -m "Add Ashtekar Reuter Rovelli quantum gravity literature addendum"

git push
```
