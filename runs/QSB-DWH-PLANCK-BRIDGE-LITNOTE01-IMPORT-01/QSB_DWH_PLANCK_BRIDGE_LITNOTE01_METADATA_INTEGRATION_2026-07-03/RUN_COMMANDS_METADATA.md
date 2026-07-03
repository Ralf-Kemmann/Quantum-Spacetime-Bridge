# QSB Planck Bridge LitNote01 Metadata Integration — Run Commands

cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

RUN="QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01"
META_ZIP="$HOME/Downloads/QSB_DWH_PLANCK_BRIDGE_LITNOTE01_METADATA_INTEGRATION_2026-07-03.zip"

# Unzip metadata package into the existing run folder
unzip -q "$META_ZIP" -d "runs/$RUN"

# Enter metadata package folder
cd "runs/$RUN/QSB_DWH_PLANCK_BRIDGE_LITNOTE01_METADATA_INTEGRATION_2026-07-03"

unset PGHOST
unset PGPASSWORD
export PGDATABASE=qsb_research_dwh
export PGUSER='ralf-kemmann'
export PGPORT=5432

mkdir -p validation

psql -v ON_ERROR_STOP=1   -f sql/20260703_qsb_planck_bridge_litnote01_metadata_integration.sql

psql -v ON_ERROR_STOP=1   -f sql/validate_planck_bridge_litnote01_metadata_integration.sql   | tee validation/validate_planck_bridge_litnote01_metadata_integration.log

# Repo checks
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
git status --short
git diff --check
