\
#!/usr/bin/env bash
set -euo pipefail

# BMS-FU02g4c remaining chunk runner
# Date: 2026-05-03
#
# Purpose:
#   Run the remaining BMS-FU02g4c connected-patch enumeration chunks sequentially.
#   For each chunk, this script:
#     1. activates the project .venv,
#     2. updates the YAML config chunk_id and skip_first_raw_patches,
#     3. runs the existing Python enumerator,
#     4. stores a per-chunk terminal log under runs/BMS-FU02g4c/chunk_batch_logs/,
#     5. checks the emitted JSON status,
#     6. stops when enumeration_status == "complete".
#
# Claim-boundary note:
#   This script only automates chunk execution. It does not create scientific
#   conclusions. Interpret results only after checking:
#     warnings_count
#     orbit_reduction_enabled_actual
#     automorphism_count_used
#     reference_is_connected
#     enumeration_status
#
# Usage from repo root:
#   source .venv/bin/activate   # optional; script also activates it
#   bash scripts/run_bms_fu02g4c_remaining_chunks.sh
#
# Optional environment variables:
#   START_SKIP=2000000 bash scripts/run_bms_fu02g4c_remaining_chunks.sh
#   CHUNK_SIZE=1000000 bash scripts/run_bms_fu02g4c_remaining_chunks.sh
#   MAX_CHUNKS=20 bash scripts/run_bms_fu02g4c_remaining_chunks.sh
#
# Examples:
#   # Continue from Chunk 2, i.e. skip first 2,000,000 raw patches:
#   START_SKIP=2000000 bash scripts/run_bms_fu02g4c_remaining_chunks.sh
#
#   # Safety-limited run of only 3 chunks:
#   START_SKIP=2000000 MAX_CHUNKS=3 bash scripts/run_bms_fu02g4c_remaining_chunks.sh

REPO_ROOT="${REPO_ROOT:-$HOME/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge}"
CONFIG_PATH="${CONFIG_PATH:-data/bms_fu02g4c_orbit_reduced_resumable_config.yaml}"
RUNNER_PATH="${RUNNER_PATH:-scripts/run_bms_fu02g4c_orbit_reduced_resumable_connected_patch_enumeration.py}"

CHUNK_SIZE="${CHUNK_SIZE:-1000000}"
START_SKIP="${START_SKIP:-2000000}"
MAX_CHUNKS="${MAX_CHUNKS:-0}"   # 0 means run until enumerator reports complete.

LOG_DIR_REL="${LOG_DIR_REL:-runs/BMS-FU02g4c/chunk_batch_logs}"

cd "$REPO_ROOT"

if [[ ! -d ".venv" ]]; then
  echo "ERROR: .venv directory not found in repo root: $REPO_ROOT" >&2
  exit 2
fi

# shellcheck disable=SC1091
source ".venv/bin/activate"

echo "=== BMS-FU02g4c remaining chunk runner ==="
echo "repo_root: $REPO_ROOT"
echo "python: $(command -v python)"
python - <<'PY'
import sys
print("python_executable:", sys.executable)
try:
    import networkx as nx
    print("networkx:", nx.__version__)
except Exception as exc:
    print("ERROR: networkx import failed:", repr(exc))
    raise SystemExit(3)
PY

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "ERROR: config not found: $CONFIG_PATH" >&2
  exit 2
fi

if [[ ! -f "$RUNNER_PATH" ]]; then
  echo "ERROR: runner not found: $RUNNER_PATH" >&2
  exit 2
fi

mkdir -p "$LOG_DIR_REL"

chunk_index=0
skip="$START_SKIP"

while true; do
  if [[ "$MAX_CHUNKS" != "0" && "$chunk_index" -ge "$MAX_CHUNKS" ]]; then
    echo "Reached MAX_CHUNKS=$MAX_CHUNKS. Stopping without claiming enumerator completion."
    exit 0
  fi

  end=$((skip + CHUNK_SIZE - 1))
  chunk_id=$(printf "chunk_%07d_%07d" "$skip" "$end")
  log_path="$LOG_DIR_REL/${chunk_id}.log"

  echo
  echo "=== Preparing $chunk_id ==="
  echo "skip_first_raw_patches=$skip"
  echo "max_raw_patches_this_run=$CHUNK_SIZE"
  echo "log_path=$log_path"

  python - "$CONFIG_PATH" "$chunk_id" "$skip" "$CHUNK_SIZE" <<'PY'
from pathlib import Path
import re
import sys

config_path = Path(sys.argv[1])
chunk_id = sys.argv[2]
skip = int(sys.argv[3])
chunk_size = int(sys.argv[4])

text = config_path.read_text(encoding="utf-8")

text_new = re.sub(
    r'(^\s*chunk_id:\s*)["\'][^"\']+["\']',
    rf'\1"{chunk_id}"',
    text,
    flags=re.MULTILINE,
)
text_new = re.sub(
    r'(^\s*skip_first_raw_patches:\s*)\d+',
    rf'\g<1>{skip}',
    text_new,
    flags=re.MULTILINE,
)
text_new = re.sub(
    r'(^\s*max_raw_patches_this_run:\s*)\d+',
    rf'\g<1>{chunk_size}',
    text_new,
    flags=re.MULTILINE,
)

if text_new == text:
    print("WARNING: config text unchanged; verify YAML field names.", file=sys.stderr)

config_path.write_text(text_new, encoding="utf-8")
print(f"updated_config={config_path}")
PY

  echo "--- Config check ---"
  grep -nE 'chunk_id|skip_first_raw_patches|max_raw_patches_this_run|timeout_seconds|enabled' "$CONFIG_PATH"

  echo "--- Running $chunk_id ---"
  set +e
  python "$RUNNER_PATH" --config "$CONFIG_PATH" 2>&1 | tee "$log_path"
  run_rc=${PIPESTATUS[0]}
  set -e

  if [[ "$run_rc" -ne 0 ]]; then
    echo "ERROR: runner failed with exit code $run_rc for $chunk_id" >&2
    echo "Log kept at: $log_path" >&2
    exit "$run_rc"
  fi

  echo "--- Parsing status for $chunk_id ---"
  status_report=$(python - "$log_path" <<'PY'
from pathlib import Path
import json
import sys

log_path = Path(sys.argv[1])
text = log_path.read_text(encoding="utf-8", errors="replace")

decoder = json.JSONDecoder()
objects = []
i = 0
while i < len(text):
    j = text.find("{", i)
    if j < 0:
        break
    try:
        obj, end = decoder.raw_decode(text[j:])
        objects.append(obj)
        i = j + end
    except json.JSONDecodeError:
        i = j + 1

if not objects:
    print("PARSE_ERROR no_json_objects_found")
    raise SystemExit(4)

# Prefer the last JSON object, because the runner emits manifest and summary.
summary = objects[-1]

fields = {
    "chunk_id": summary.get("chunk_id"),
    "enumeration_status": summary.get("enumeration_status"),
    "warnings_count": summary.get("warnings_count"),
    "orbit_reduction_enabled_actual": summary.get("orbit_reduction_enabled_actual"),
    "automorphism_count_used": summary.get("automorphism_count_used"),
    "reference_is_connected": summary.get("reference_is_connected"),
    "raw_connected_patch_count_processed": summary.get("raw_connected_patch_count_processed"),
    "unique_orbit_patch_count_processed": summary.get("unique_orbit_patch_count_processed"),
    "raw_carrier_signature_exact_match_count": summary.get("raw_carrier_signature_exact_match_count"),
    "raw_carrier_signature_near_match_count": summary.get("raw_carrier_signature_near_match_count"),
    "raw_role_colored_signature_exact_match_count": summary.get("raw_role_colored_signature_exact_match_count"),
    "raw_role_colored_signature_near_match_count": summary.get("raw_role_colored_signature_near_match_count"),
    "orbit_role_colored_signature_exact_match_class_count": summary.get("orbit_role_colored_signature_exact_match_class_count"),
    "orbit_role_colored_signature_near_match_class_count": summary.get("orbit_role_colored_signature_near_match_class_count"),
}

for key, value in fields.items():
    print(f"{key}={value}")

validity_errors = []

if fields["warnings_count"] != 0:
    validity_errors.append(f"warnings_count={fields['warnings_count']}")
if fields["orbit_reduction_enabled_actual"] is not True:
    validity_errors.append(f"orbit_reduction_enabled_actual={fields['orbit_reduction_enabled_actual']}")
if fields["automorphism_count_used"] != 120:
    validity_errors.append(f"automorphism_count_used={fields['automorphism_count_used']}")
if fields["reference_is_connected"] is not True:
    validity_errors.append(f"reference_is_connected={fields['reference_is_connected']}")

if validity_errors:
    print("VALIDITY_STATUS=CHECK_REQUIRED")
    print("VALIDITY_ERRORS=" + ";".join(validity_errors))
else:
    print("VALIDITY_STATUS=OK")

print("STOP_STATUS=" + str(fields["enumeration_status"]))
PY
)

  echo "$status_report"

  validity_status=$(printf '%s\n' "$status_report" | awk -F= '/^VALIDITY_STATUS=/{print $2}' | tail -n 1)
  stop_status=$(printf '%s\n' "$status_report" | awk -F= '/^STOP_STATUS=/{print $2}' | tail -n 1)

  if [[ "$validity_status" != "OK" ]]; then
    echo "ERROR: validity checks failed for $chunk_id. Stopping for inspection." >&2
    echo "Log kept at: $log_path" >&2
    exit 5
  fi

  if [[ "$stop_status" == "complete" ]]; then
    echo
    echo "Enumerator reported complete at $chunk_id."
    echo "Do not make an exhaustive scientific claim until chunk coverage and output files have been reviewed."
    exit 0
  fi

  if [[ "$stop_status" != "partial_chunk_limit_reached" && "$stop_status" != "partial_timeout_reached" ]]; then
    echo "WARNING: unexpected enumeration_status=$stop_status for $chunk_id" >&2
    echo "Stopping for inspection." >&2
    exit 6
  fi

  chunk_index=$((chunk_index + 1))
  skip=$((skip + CHUNK_SIZE))
done
