# Run Commands — PBR State Spec 01

Assumed repo root:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

## 1. Copy package into runs

```bash
mkdir -p runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01
cp -a /path/to/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01/. runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01/
```

## 2. Local package validation

```bash
python3 runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01/scripts/validate_pbr_state_spec.py \
  runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01
```

## 3. PostgreSQL import

Use local Unix socket unless your setup requires TCP.

```bash
unset PGHOST
psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01/sql/001_create_qsb_pbr_state_spec.sql
psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01/sql/002_insert_qsb_pbr_state_spec.sql
psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01/sql/003_validation_queries.sql
```

## 4. DBeaver sanity check

```sql
SELECT current_database() AS db, current_user AS db_user, current_schema() AS current_schema;
```

Expected:

```text
qsb_research_dwh | ralf-kemmann | public
```

Then:

```sql
SELECT *
FROM qsb_planck_bridge.v_pbr_state_spec01_claim_boundary
ORDER BY boundary_type, boundary_id;

SELECT *
FROM qsb_planck_bridge.v_pbr_state_spec01_psd_gate
ORDER BY field_name;
```

## 5. Optional PSD gate template

After confirming the real matrix path:

```bash
python3 runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01/scripts/psd_gate_template.py \
  runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv \
  --matrix-id QSB-EXTRACT03A-R1-11-K-candidate \
  --output runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01/validation/psd_gate_result_11_K_candidate_matrix.csv
```

## 6. Git add / commit

```bash
git status --short
git diff --check
git add runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01
git commit -m "Add Planck Bridge resonator state spec"
```
