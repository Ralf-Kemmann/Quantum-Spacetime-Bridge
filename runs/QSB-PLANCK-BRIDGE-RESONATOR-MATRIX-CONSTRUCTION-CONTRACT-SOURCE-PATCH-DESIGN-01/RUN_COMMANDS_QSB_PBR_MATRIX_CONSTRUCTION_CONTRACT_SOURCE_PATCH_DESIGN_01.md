# Run Commands

Commands run for this source-patch design package:

```bash
sed -n '1,340p' /home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PLANCK_BRIDGE_RESONATOR_MATRIX_CONSTRUCTION_CONTRACT_SOURCE_PATCH_DESIGN_01.md
sed -n '341,760p' /home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PLANCK_BRIDGE_RESONATOR_MATRIX_CONSTRUCTION_CONTRACT_SOURCE_PATCH_DESIGN_01.md
git status --short --untracked-files=all
git log --oneline -12
find runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-HUMAN-REVIEW-01 -type f
sed -n '1,120p' runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-HUMAN-REVIEW-01/data/review_summary.csv
sed -n '1,140p' runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-HUMAN-REVIEW-01/data/blocking_issues.csv
sed -n '1,120p' runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-HUMAN-REVIEW-01/data/source_patch_requirements_review.csv
sha256sum scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/12_K_validation_results.csv runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum/06_canonical_pair_basis_review.csv runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/09_delta_phi_staging_preflight.sqlite
sed -n '1,120p' runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-DESIGN-01/data/source_artifacts_to_patch.csv
sed -n '1,120p' runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-DESIGN-01/data/reconstruction_callable_contract.csv
sed -n '1,120p' runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-DESIGN-01/data/lag_policy_contract.csv
sed -n '1,120p' runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-DESIGN-01/data/numerical_validation_policy_contract.csv
mkdir -p runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-DESIGN-01/data runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-DESIGN-01/docs runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-DESIGN-01/validation
```

Note: `data/source_artifacts_to_patch.csv` was not present in the prior design run; this source-patch design creates that artifact.

