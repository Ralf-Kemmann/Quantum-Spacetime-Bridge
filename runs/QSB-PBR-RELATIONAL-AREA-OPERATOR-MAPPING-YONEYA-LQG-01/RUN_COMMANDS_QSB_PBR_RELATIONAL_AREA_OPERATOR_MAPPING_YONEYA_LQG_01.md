# Run Commands

Run package:

`runs/QSB-PBR-RELATIONAL-AREA-OPERATOR-MAPPING-YONEYA-LQG-01/`

Commands recorded for this mapping-design run:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
sed -n '1,300p' /home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PBR_RELATIONAL_AREA_OPERATOR_MAPPING_YONEYA_LQG_01.md
sed -n '301,680p' /home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PBR_RELATIONAL_AREA_OPERATOR_MAPPING_YONEYA_LQG_01.md
git status --short --untracked-files=all
git log --oneline -12
find runs/QSB-PBR-MECHANISTIC-BRAINSTORMING-PLURALISTIC-LITERATURE-02 runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01 runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-CLOSURE-REVIEW-01 -maxdepth 3 -type f | sort
find runs/QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01 runs/QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01 runs/QSB-PLANCK-BRIDGE-LITERATURE-ADDENDUM-ASHREUROV-2014-01 -maxdepth 2 -type f | sort
sed -n '1,90p' runs/QSB-PBR-MECHANISTIC-BRAINSTORMING-PLURALISTIC-LITERATURE-02/data/pluralistic_mechanism_bubbles.csv
sed -n '1,70p' runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/data/dwh_literature_mechanism_axes.csv
sed -n '1,90p' runs/QSB-PBR-MECHANISTIC-BRAINSTORMING-PLURALISTIC-LITERATURE-02/data/testability_and_claim_risk.csv
sed -n '1,80p' runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-CLOSURE-REVIEW-01/data/closure_review_summary.csv
mkdir -p runs/QSB-PBR-RELATIONAL-AREA-OPERATOR-MAPPING-YONEYA-LQG-01/data runs/QSB-PBR-RELATIONAL-AREA-OPERATOR-MAPPING-YONEYA-LQG-01/docs runs/QSB-PBR-RELATIONAL-AREA-OPERATOR-MAPPING-YONEYA-LQG-01/validation
find runs/QSB-PBR-RELATIONAL-AREA-OPERATOR-MAPPING-YONEYA-LQG-01 -type f | sort
wc -l runs/QSB-PBR-RELATIONAL-AREA-OPERATOR-MAPPING-YONEYA-LQG-01/data/*.csv runs/QSB-PBR-RELATIONAL-AREA-OPERATOR-MAPPING-YONEYA-LQG-01/validation/validation_results.csv
git diff --check
git status --short --untracked-files=all
git status --short --ignored=matching runs/QSB-PBR-RELATIONAL-AREA-OPERATOR-MAPPING-YONEYA-LQG-01/
```

No `git add`, `git commit`, or `git push` command was run.
No candidate search, candidate repair, candidate upgrade, admissibility rerun, mechanism test, nullmodel, DWH write, or literature import was executed.
