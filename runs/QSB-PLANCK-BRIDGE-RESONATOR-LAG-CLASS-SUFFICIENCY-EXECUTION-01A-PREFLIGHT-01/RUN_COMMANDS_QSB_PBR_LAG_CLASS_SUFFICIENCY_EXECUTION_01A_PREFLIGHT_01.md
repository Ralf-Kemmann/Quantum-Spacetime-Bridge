# Commands Run

```bash
cd /home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
git status --short --untracked-files=all
git log --oneline -16
sed -n '1,260p' '/home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PLANCK_BRIDGE_RESONATOR_LAG_CLASS_SUFFICIENCY_EXECUTION_01A_PREFLIGHT_01(1).md'
sed -n '261,620p' '/home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PLANCK_BRIDGE_RESONATOR_LAG_CLASS_SUFFICIENCY_EXECUTION_01A_PREFLIGHT_01(1).md'
find runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-DESIGN-UPDATE-01 -maxdepth 3 -type f
sed -n '1,220p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-DESIGN-UPDATE-01/data/explicit_placeholder_gate.csv
sed -n '1,220p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-DESIGN-UPDATE-01/data/updated_preflight_checks.csv
sed -n '1,220p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-DESIGN-UPDATE-01/data/updated_experiment_arm_mapping.csv
sed -n '1,220p' runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-IMPLEMENTATION-01/generated_contract/validation_summary.csv
python -m py_compile scripts/qsb_pbr_matrix_contract/reconstruct_k_candidate.py
python scripts/qsb_pbr_matrix_contract/reconstruct_k_candidate.py --help
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-IMPLEMENTATION-01/generated_contract/contract_field_export.csv
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-IMPLEMENTATION-01/generated_contract/lag_class_handoff.csv
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-IMPLEMENTATION-01/generated_contract/control_policy_export.csv
sha256sum runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv
python scripts/qsb_pbr_matrix_contract/reconstruct_k_candidate.py --mode dry-run --source-db runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/09_delta_phi_staging_preflight.sqlite --pair-basis runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum/06_canonical_pair_basis_review.csv --k-candidate runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv --expected-k-sha256 e1acdf0acf31e2faf68f8a517cbdbccb2f9af9e28fe974eeb01c0a7f0928754d --output-dir /tmp/qsb_pbr_execution_01a_preflight_dry_run
mkdir -p runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/data runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/docs runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/validation
```

Final validation commands:

```bash
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/data/preflight_summary.csv
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/data/preflight_gate_decisions.csv
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/data/placeholder_preflight_review.csv
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/data/hash_and_identity_checks.csv
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/data/go_no_go_decision.csv
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/validation/validation_results.csv
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/data/original_design_arm_preflight_mapping.csv
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/data/future_execution_requirements.csv
python -m csv runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/data/commands_run.csv
find runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01 -type f
wc -l runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/README.md runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/data/preflight_gate_decisions.csv runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/data/placeholder_preflight_review.csv runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/validation/validation_results.csv runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01.md
git diff --check
git status --short --untracked-files=all
git status --short --ignored=matching runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01A-PREFLIGHT-01/
git status --short --ignored=matching scripts/qsb_pbr_matrix_contract/
```
