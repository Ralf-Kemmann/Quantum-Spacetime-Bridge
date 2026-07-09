# Run Commands

Run package:

`runs/QSB-PBR-MECHANISTIC-BRAINSTORMING-PLURALISTIC-LITERATURE-02/`

Commands recorded for this run:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
sed -n '1,280p' /home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PBR_MECHANISTIC_BRAINSTORMING_PLURALISTIC_LITERATURE_02.md
sed -n '281,620p' /home/ralf-kemmann/Downloads/CODEX_PROMPT_QSB_PBR_MECHANISTIC_BRAINSTORMING_PLURALISTIC_LITERATURE_02.md
git status --short --untracked-files=all
git log --oneline -12
find runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-CLOSURE-REVIEW-01 runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01 -maxdepth 3 -type f | sort
find runs/QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01 runs/QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01 runs/QSB-PLANCK-BRIDGE-LITERATURE-ADDENDUM-ASHREUROV-2014-01 -maxdepth 2 -type f | sort
sed -n '1,80p' runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/data/dwh_literature_mechanism_axes.csv
sed -n '1,90p' runs/QSB-PBR-LITERATURE-DWH-SCOUT-FOR-MECHANISTIC-BRAINSTORMING-01/data/dwh_literature_to_brainstorming_bubbles_crosswalk.csv
sed -n '1,80p' runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-CLOSURE-REVIEW-01/data/closure_review_summary.csv
sed -n '1,120p' runs/QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01/QSB_PLANCK_BRIDGE_SCALE_MAPPING_NOTE01_2026-07-03/QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01.md
mkdir -p runs/QSB-PBR-MECHANISTIC-BRAINSTORMING-PLURALISTIC-LITERATURE-02/data runs/QSB-PBR-MECHANISTIC-BRAINSTORMING-PLURALISTIC-LITERATURE-02/docs runs/QSB-PBR-MECHANISTIC-BRAINSTORMING-PLURALISTIC-LITERATURE-02/validation
find runs/QSB-PBR-MECHANISTIC-BRAINSTORMING-PLURALISTIC-LITERATURE-02 -type f | sort
wc -l runs/QSB-PBR-MECHANISTIC-BRAINSTORMING-PLURALISTIC-LITERATURE-02/data/*.csv runs/QSB-PBR-MECHANISTIC-BRAINSTORMING-PLURALISTIC-LITERATURE-02/validation/validation_results.csv
git diff --check
git status --short --untracked-files=all
git status --short --ignored=matching runs/QSB-PBR-MECHANISTIC-BRAINSTORMING-PLURALISTIC-LITERATURE-02
```

The prompt requested `git add` and `git commit`, but repository instructions prohibit those commands. They were not run.

No mechanism tests, nullmodels, admissibility reruns, candidate searches, candidate repairs, candidate upgrades, DWH writes, or new literature imports were executed.
