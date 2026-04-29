#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge}"
INPUT_CSV="$PROJECT_ROOT/data/bmc01/bmc01_baseline_relational_table_template.csv"
SCRIPT_PATH="$PROJECT_ROOT/scripts/bmc01_weighted_relational_scramble.py"
STAMP="$(date +%Y-%m-%d_%H-%M-%S)"
OUT_ROOT="$PROJECT_ROOT/runs/BMC-01/matrix/$STAMP"
SUMMARY_CSV="$OUT_ROOT/bmc01_matrix_summary.csv"
SUMMARY_MD="$OUT_ROOT/bmc01_matrix_readout.md"

mkdir -p "$OUT_ROOT"

if [[ ! -f "$INPUT_CSV" ]]; then
  echo "ERROR: input CSV not found: $INPUT_CSV" >&2
  exit 1
fi

if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "ERROR: BMC-01 script not found: $SCRIPT_PATH" >&2
  exit 1
fi

VARIANTS=(
  "global_weight_permutation"
  "within_shell_weight_permutation"
  "within_local_group_weight_permutation"
)

STRENGTHS=(
  "low"
  "medium"
  "high"
)

echo "run_id,variant,strength,decision_label,marker_support_level,carrier_support_level,arrangement_signal_score,endpoint_load_shift_score,local_group_arrangement_shift_score,shell_arrangement_shift_score,pair_neighborhood_consistency_shift_score" > "$SUMMARY_CSV"

for variant in "${VARIANTS[@]}"; do
  for strength in "${STRENGTHS[@]}"; do
    RUN_ID="BMC01_${variant}_${strength}"
    RUN_DIR="$OUT_ROOT/$RUN_ID"

    python "$SCRIPT_PATH" \
      --input "$INPUT_CSV" \
      --output-dir "$RUN_DIR" \
      --variant "$variant" \
      --strength "$strength" \
      --seed 123 \
      --run-id "$RUN_ID"

    RUN_DIR_ENV="$RUN_DIR" RUN_ID_ENV="$RUN_ID" VARIANT_ENV="$variant" STRENGTH_ENV="$strength" python - <<'PY'
import json
import os
import pathlib

run_dir = pathlib.Path(os.environ["RUN_DIR_ENV"])
decision = json.loads((run_dir / "decision_summary.json").read_text(encoding="utf-8"))
summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
row = [
    os.environ["RUN_ID_ENV"],
    os.environ["VARIANT_ENV"],
    os.environ["STRENGTH_ENV"],
    decision.get("decision_label", ""),
    decision.get("marker_support_level", ""),
    decision.get("carrier_support_level", ""),
    summary.get("perturbed_arrangement_signal_score", ""),
    summary.get("endpoint_load_shift_score", ""),
    summary.get("local_group_arrangement_shift_score", ""),
    summary.get("shell_arrangement_shift_score", ""),
    summary.get("pair_neighborhood_consistency_shift_score", ""),
]
print(",".join(map(str, row)))
PY
  done
done >> "$SUMMARY_CSV"

SUMMARY_CSV_ENV="$SUMMARY_CSV" SUMMARY_MD_ENV="$SUMMARY_MD" OUT_ROOT_ENV="$OUT_ROOT" python - <<'PY'
import csv
import os
from pathlib import Path

summary_csv = Path(os.environ["SUMMARY_CSV_ENV"])
summary_md = Path(os.environ["SUMMARY_MD_ENV"])
out_root = Path(os.environ["OUT_ROOT_ENV"])

rows = list(csv.DictReader(summary_csv.open(encoding="utf-8")))

def fmt(v):
    try:
        return f"{float(v):.6f}"
    except Exception:
        return str(v)

lines = []
lines.append("# BMC-01 Matrix Readout\n")
lines.append(f"- Output root: `{out_root}`")
lines.append("")
lines.append("| run_id | variant | strength | decision | arrangement_signal | endpoint_load | local_group | shell | pair_neighborhood |")
lines.append("|---|---|---:|---|---:|---:|---:|---:|---:|")

for r in rows:
    lines.append(
        f"| `{r['run_id']}` | `{r['variant']}` | `{r['strength']}` | `{r['decision_label']}` | "
        f"{fmt(r['arrangement_signal_score'])} | {fmt(r['endpoint_load_shift_score'])} | "
        f"{fmt(r['local_group_arrangement_shift_score'])} | {fmt(r['shell_arrangement_shift_score'])} | "
        f"{fmt(r['pair_neighborhood_consistency_shift_score'])} |"
    )

lines.append("")
lines.append("## Short interpretation")
lines.append("")
lines.append("- Compare which variant/strength combinations produce the largest `arrangement_signal_score`.")
lines.append("- Pay particular attention to whether shell-sensitive or local-group-sensitive perturbations dominate.")
lines.append("- Treat this matrix as a probe map, not as final marker/carrier proof.")
lines.append("")

summary_md.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote matrix summary to: {summary_csv}")
print(f"Wrote matrix readout to: {summary_md}")
PY

echo
echo "Matrix run completed."
echo "Output root: $OUT_ROOT"
echo "Summary CSV: $SUMMARY_CSV"
echo "Summary MD:  $SUMMARY_MD"
