# Run Commands

Commands run for this source-alignment review:

```bash
sed -n '1,320p' /home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PLANCK_BRIDGE_RESONATOR_MATRIX_CONSTRUCTION_CONTRACT_SOURCE_ALIGNMENT_01.md
sed -n '321,680p' /home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PLANCK_BRIDGE_RESONATOR_MATRIX_CONSTRUCTION_CONTRACT_SOURCE_ALIGNMENT_01.md
git status --short --untracked-files=all
git log --oneline -12
rg -n "K_candidate|K candidate|matrix construction|kernel|lag_class|lag class|pair_id|pair policy|diagonal policy|PSD|rank|eigen|spectrum|projector|P_l|lag-preserving|lag preserving" runs data scripts docs --glob '*.{py,sql,md,csv,json}'
find runs data scripts docs -type f
sed -n '1,260p' scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py
sed -n '260,620p' scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py
sed -n '1,240p' scripts/qsb_extract02a/human_freeze_resolution_authorization_check.py
find runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum -maxdepth 1 -type f
sed -n '1,120p' runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/12_K_validation_results.csv
sed -n '1,120p' runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/10_phase_response_vector_summary.csv
sed -n '1,120p' runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/09_tensor_schema_runtime_mapping.csv
sed -n '1,120p' runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/07_source_selection_result.csv
sed -n '1,140p' runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/23_lineage_and_hash_audit.csv
sed -n '1,120p' runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/01_extract03a_r1_run_manifest.json
sha256sum scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/01_extract03a_r1_run_manifest.json runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/07_source_selection_result.csv runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/08_canonical_pair_split_assignment.csv runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/09_tensor_schema_runtime_mapping.csv runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/10_phase_response_vector_summary.csv runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/12_K_validation_results.csv runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/23_lineage_and_hash_audit.csv runs/QSB-EXTRACT02A/input/human_freeze_decisions.json runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum/06_canonical_pair_basis_review.csv
wc -l scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/10_phase_response_vector_summary.csv
sed -n '1,80p' runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum/06_canonical_pair_basis_review.csv
sed -n '1,80p' runs/QSB-EXTRACT02A/input/human_freeze_decisions.json
mkdir -p runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-ALIGNMENT-01/data runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-ALIGNMENT-01/docs runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-ALIGNMENT-01/validation
```

Validation commands are recorded in `validation/VALIDATION_RESULTS.md`.

