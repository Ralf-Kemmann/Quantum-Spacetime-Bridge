#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge"
INPUT="$ROOT/data/bmc04/bmc04_baseline_relational_table_template.csv"
SCRIPT="$ROOT/scripts/bmc04_distribution_preserving_organization_scramble_v3_1.py"
OUT_ROOT="$ROOT/runs/BMC-04/v3_1_seed_series"

mkdir -p "$OUT_ROOT"

SEEDS=(101 123 211 307 509)

for SEED in "${SEEDS[@]}"; do
  RUN_ID="BMC04_v3_1_seed_${SEED}"
  python "$SCRIPT" \
    --input "$INPUT" \
    --output-dir "$OUT_ROOT/$RUN_ID" \
    --variant degree_strength_weight_preserved \
    --seed "$SEED" \
    --strength-target-min 0.99 \
    --strength-hard-min 0.965 \
    --organization-readable-threshold 0.25 \
    --repair-iterations 12000 \
    --repair-patience 1500
done

python - <<'PY'
import csv, json
from pathlib import Path

out_root = Path("/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge/runs/BMC-04/v3_1_seed_series")
rows = []
for run_dir in sorted(p for p in out_root.iterdir() if p.is_dir()):
    pres = list(csv.DictReader((run_dir / "preservation_summary.csv").open()))[0]
    org = list(csv.DictReader((run_dir / "organization_disruption_summary.csv").open()))[0]
    dec = json.loads((run_dir / "decision_summary.json").read_text(encoding="utf-8"))
    rows.append({
        "run_id": run_dir.name,
        "seed": run_dir.name.split("_")[-1],
        "strength_preservation_score": pres["strength_preservation_score"],
        "arrangement_signal_score": org["arrangement_signal_score"],
        "decision_label": dec["decision_label"],
        "preservation_status": pres["preservation_status"],
    })

summary_csv = out_root / "bmc04_v3_1_seed_series_summary.csv"
with summary_csv.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

md = out_root / "bmc04_v3_1_seed_series_readout.md"
lines = [
    "# BMC-04-v3.1 Seed Series Readout",
    "",
    f"- Output root: `{out_root}`",
    "",
    "| run_id | seed | strength_preservation | arrangement_signal | decision | preservation |",
    "|---|---:|---:|---:|---|---|",
]
for r in rows:
    lines.append(
        f"| `{r['run_id']}` | `{r['seed']}` | {float(r['strength_preservation_score']):.6f} | {float(r['arrangement_signal_score']):.6f} | `{r['decision_label']}` | `{r['preservation_status']}` |"
    )
md.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote seed-series summary to: {summary_csv}")
print(f"Wrote seed-series readout to: {md}")
PY
