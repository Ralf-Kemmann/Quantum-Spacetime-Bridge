# Run Commands

Run package:

`runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01/`

Commands recorded:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
sed -n '1,320p' /home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PLANCK_BRIDGE_RESONATOR_LAG_CLASS_SUFFICIENCY_EXECUTION_01.md
sed -n '321,760p' /home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PLANCK_BRIDGE_RESONATOR_LAG_CLASS_SUFFICIENCY_EXECUTION_01.md
rg -n "matrix construction|matrix_construction|pair identifier|pair_id|lag_class|lag class|diagonal policy|pair symmetry|K_candidate|baseline" runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-DESIGN-01 runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01 runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01 runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01 runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01
find runs -maxdepth 2 -type f -iname '*lag*' | sort
find data docs scripts -maxdepth 3 -type f | rg -n "lag|pbr|matrix|spectral|psd|rank"
sed -n '1,260p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01/scripts/run_pbr_lag_mechanism_execution.py
sed -n '1,40p' runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv
sed -n '1,120p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01/data/lag_mechanism_execution_manifest.json
sed -n '1,80p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01/data/lag_mechanism_test_results.csv
sha256sum runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-DESIGN-01/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-DESIGN-01.md runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-DESIGN-01/data/experiment_arms.csv runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-CLOSURE-REVIEW-01/data/closure_review_summary.csv runs/QSB-PBR-RELATIONAL-AREA-OPERATOR-MAPPING-YONEYA-LQG-01/data/claim_boundaries.csv runs/QSB-PBR-RELATIONAL-AREA-OPERATOR-MAPPING-YONEYA-LQG-01/QSB-PBR-RELATIONAL-AREA-OPERATOR-MAPPING-YONEYA-LQG-01.md runs/QSB-PBR-MECHANISTIC-BRAINSTORMING-PLURALISTIC-LITERATURE-02/data/pluralistic_mechanism_bubbles.csv runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01/scripts/run_pbr_lag_mechanism_execution.py
wc -l runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv
sed -n '1,80p' runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01/data/lag_mechanism_required_inputs.csv
mkdir -p runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01/data runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01/docs runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01/validation
git diff --check
git status --short --untracked-files=all
git status --short --ignored=matching runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01/
```

No computation arms were executed after the failed preflight.
No `git add`, `git commit`, or `git push` command was run.
