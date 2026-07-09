# Run Commands

Commands run for this implementation:

```bash
sed -n '1,360p' /home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PLANCK_BRIDGE_RESONATOR_MATRIX_CONSTRUCTION_CONTRACT_SOURCE_PATCH_IMPLEMENTATION_01.md
sed -n '361,780p' /home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PLANCK_BRIDGE_RESONATOR_MATRIX_CONSTRUCTION_CONTRACT_SOURCE_PATCH_IMPLEMENTATION_01.md
git status --short --untracked-files=all
find scripts -maxdepth 2 -type f
find tests -maxdepth 2 -type f
find docs -maxdepth 2 -type f
sed -n '1,120p' runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-DESIGN-REVIEW-01/data/implementation_authorization_decision.csv
sed -n '1,140p' runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-DESIGN-REVIEW-01/data/implementation_prompt_requirements.csv
mkdir -p runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-IMPLEMENTATION-01/data runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-IMPLEMENTATION-01/docs runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-IMPLEMENTATION-01/validation
python scripts/qsb_pbr_matrix_contract/reconstruct_k_candidate.py --mode dry-run --source-db runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/09_delta_phi_staging_preflight.sqlite --pair-basis runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum/06_canonical_pair_basis_review.csv --k-candidate runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv --expected-k-sha256 e1acdf0acf31e2faf68f8a517cbdbccb2f9af9e28fe974eeb01c0a7f0928754d --output-dir runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-IMPLEMENTATION-01/generated_contract
python -m py_compile scripts/qsb_pbr_matrix_contract/reconstruct_k_candidate.py
python scripts/qsb_pbr_matrix_contract/reconstruct_k_candidate.py --mode export --source-db runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/09_delta_phi_staging_preflight.sqlite --pair-basis runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum/06_canonical_pair_basis_review.csv --k-candidate runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv --expected-k-sha256 e1acdf0acf31e2faf68f8a517cbdbccb2f9af9e28fe974eeb01c0a7f0928754d --output-dir runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-IMPLEMENTATION-01/generated_contract
python scripts/qsb_pbr_matrix_contract/reconstruct_k_candidate.py --mode validate --source-db runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/09_delta_phi_staging_preflight.sqlite --pair-basis runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum/06_canonical_pair_basis_review.csv --k-candidate runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv --expected-k-sha256 e1acdf0acf31e2faf68f8a517cbdbccb2f9af9e28fe974eeb01c0a7f0928754d --output-dir runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-IMPLEMENTATION-01/generated_contract
```

Final check commands are recorded in `validation/validation_results.csv` and the final response.
