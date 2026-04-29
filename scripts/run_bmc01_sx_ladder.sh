#!/usr/bin/env bash
set -euo pipefail

# BMC-01-SX strength ladder runner
#
# Runs a matched preserving-vs-crossing ladder for:
# - within_shell_weight_permutation
# - shell_crossing_weight_permutation with adjacent_shell_crossing
#
# Strengths:
# - low
# - medium
# - high
#
# Expected input:
#   data/bmc01/bmc01_baseline_relational_table_template.csv
#
# Output root:
#   runs/BMC-01-SX/ladder/<STAMP>/

PROJECT_ROOT="${1:-/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge}"
INPUT_CSV="$PROJECT_ROOT/data/bmc01/bmc01_baseline_relational_table_template.csv"
SCRIPT_PATH="$PROJECT_ROOT/scripts/bmc01_shell_crossing_probe.py"
STAMP="$(date +%Y-%m-%d_%H-%M-%S)"
OUT_ROOT="$PROJECT_ROOT/runs/BMC-01-SX/ladder/$STAMP"
SUMMARY_CSV="$OUT_ROOT/bmc01_sx_ladder_summary.csv"
SUMMARY_MD="$OUT_ROOT/bmc01_sx_ladder_readout.md"

mkdir -p "$OUT_ROOT"

if [[ ! -f "$INPUT_CSV" ]]; then
  echo "ERROR: input CSV not found: $INPUT_CSV" >&2
  exit 1
fi

if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "ERROR: BMC-01-SX script not found: $SCRIPT_PATH" >&2
  exit 1
fi

STRENGTHS=(
  "low"
  "medium"
  "high"
)

echo "run_id,mode,strength,decision_label,shell_order_support_level,marker_support_level,carrier_support_level,arrangement_signal_score,shell_arrangement_shift_score,shell_boundary_disruption_score,shell_crossing_fraction,shell_distance_mean,endpoint_load_shift_score,pair_neighborhood_consistency_shift_score" > "$SUMMARY_CSV"

for strength in "${STRENGTHS[@]}"; do
  # preserving
  RUN_ID="BMC01SX_within_shell_${strength}"
  RUN_DIR="$OUT_ROOT/$RUN_ID"

  python "$SCRIPT_PATH" \
    --input "$INPUT_CSV" \
    --output-dir "$RUN_DIR" \
    --variant within_shell_weight_permutation \
    --strength "$strength" \
    --seed 123 \
    --run-id "$RUN_ID" >/dev/null

  RUN_DIR_ENV="$RUN_DIR" RUN_ID_ENV="$RUN_ID" MODE_ENV="within_shell" STRENGTH_ENV="$strength" python - <<'PY'
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ENV"])
decision = json.loads((run_dir / "decision_summary.json").read_text(encoding="utf-8"))
summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))

row = [
    os.environ["RUN_ID_ENV"],
    os.environ["MODE_ENV"],
    os.environ["STRENGTH_ENV"],
    decision.get("decision_label", ""),
    decision.get("shell_order_support_level", ""),
    decision.get("marker_support_level", ""),
    decision.get("carrier_support_level", ""),
    summary.get("perturbed_arrangement_signal_score", ""),
    summary.get("shell_arrangement_shift_score", ""),
    summary.get("shell_boundary_disruption_score", ""),
    summary.get("shell_crossing_fraction", ""),
    summary.get("shell_distance_mean", ""),
    summary.get("endpoint_load_shift_score", ""),
    summary.get("pair_neighborhood_consistency_shift_score", ""),
]
print(",".join(map(str, row)))
PY

  # crossing
  RUN_ID="BMC01SX_shell_crossing_adjacent_${strength}"
  RUN_DIR="$OUT_ROOT/$RUN_ID"

  python "$SCRIPT_PATH" \
    --input "$INPUT_CSV" \
    --output-dir "$RUN_DIR" \
    --variant shell_crossing_weight_permutation \
    --shell-crossing-policy adjacent_shell_crossing \
    --strength "$strength" \
    --seed 123 \
    --run-id "$RUN_ID" >/dev/null

  RUN_DIR_ENV="$RUN_DIR" RUN_ID_ENV="$RUN_ID" MODE_ENV="shell_crossing_adjacent" STRENGTH_ENV="$strength" python - <<'PY'
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR_ENV"])
decision = json.loads((run_dir / "decision_summary.json").read_text(encoding="utf-8"))
summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))

row = [
    os.environ["RUN_ID_ENV"],
    os.environ["MODE_ENV"],
    os.environ["STRENGTH_ENV"],
    decision.get("decision_label", ""),
    decision.get("shell_order_support_level", ""),
    decision.get("marker_support_level", ""),
    decision.get("carrier_support_level", ""),
    summary.get("perturbed_arrangement_signal_score", ""),
    summary.get("shell_arrangement_shift_score", ""),
    summary.get("shell_boundary_disruption_score", ""),
    summary.get("shell_crossing_fraction", ""),
    summary.get("shell_distance_mean", ""),
    summary.get("endpoint_load_shift_score", ""),
    summary.get("pair_neighborhood_consistency_shift_score", ""),
]
print(",".join(map(str, row)))
PY

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
lines.append("# BMC-01-SX Strength Ladder Readout\n")
lines.append(f"- Output root: `{out_root}`")
lines.append("")
lines.append("| run_id | mode | strength | decision | shell_order | arrangement | shell_arrangement | shell_boundary | crossing_fraction | endpoint_load | pair_neighborhood |")
lines.append("|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|")

for r in rows:
    lines.append(
        f"| `{r['run_id']}` | `{r['mode']}` | `{r['strength']}` | `{r['decision_label']}` | "
        f"{fmt(r['shell_order_support_level'])} | {fmt(r['arrangement_signal_score'])} | "
        f"{fmt(r['shell_arrangement_shift_score'])} | {fmt(r['shell_boundary_disruption_score'])} | "
        f"{fmt(r['shell_crossing_fraction'])} | {fmt(r['endpoint_load_shift_score'])} | "
        f"{fmt(r['pair_neighborhood_consistency_shift_score'])} |"
    )

lines.append("")
lines.append("## Short interpretation")
lines.append("")
lines.append("- Compare each strength pair directly: within-shell vs shell-crossing-adjacent.")
lines.append("- Ask whether shell-crossing stays consistently more destructive across low/medium/high.")
lines.append("- Treat this as a ladder readout, not as final proof of shell carrier status.")
lines.append("")

summary_md.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote ladder summary to: {summary_csv}")
print(f"Wrote ladder readout to: {summary_md}")
PY

echo
echo "BMC-01-SX strength ladder completed."
echo "Output root: $OUT_ROOT"
echo "Summary CSV: $SUMMARY_CSV"
echo "Summary MD:  $SUMMARY_MD"
