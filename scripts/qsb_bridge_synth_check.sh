#!/usr/bin/env bash
# qsb_bridge_synth_check.sh
#
# Read-only acceptance helper for QSB-BRIDGE-SYNTH blocks.
#
# Usage:
#   bash scripts/qsb_bridge_synth_check.sh 01a
#   bash scripts/qsb_bridge_synth_check.sh 01b
#   bash scripts/qsb_bridge_synth_check.sh 01c
#   bash scripts/qsb_bridge_synth_check.sh 01d
#
# Safety:
# - Does not modify files.
# - Does not run numerical tests.
# - Does not create runs/.
# - Does not git add/commit/push/reset.
# - Only prints status, line counts, result notes, table heads, field lists,
#   and basic git diff checks.

set -u
set -o pipefail

BLOCK="${1:-}"

print_section() {
  printf '\n===== %s =====\n' "$1"
}

require_repo_root() {
  if [ ! -d ".git" ]; then
    echo "ERROR: Please run this script from the repo root:"
    echo "  ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge"
    exit 2
  fi
}

print_file_if_exists() {
  local label="$1"
  local path="$2"
  local lines="${3:-220}"

  print_section "$label"
  if [ -f "$path" ]; then
    sed -n "1,${lines}p" "$path"
  else
    echo "MISSING: $path"
  fi
}

head_file_if_exists() {
  local label="$1"
  local path="$2"
  local lines="${3:-20}"

  print_section "$label"
  if [ -f "$path" ]; then
    head -n "$lines" "$path"
  else
    echo "MISSING: $path"
  fi
}

wc_if_exists() {
  print_section "LINE COUNTS"
  local any_missing=0
  for path in "$@"; do
    if [ ! -f "$path" ]; then
      echo "MISSING: $path"
      any_missing=1
    fi
  done
  if [ "$any_missing" -eq 0 ]; then
    wc -l "$@"
  fi
}

common_git_checks() {
  print_section "GIT STATUS"
  git status --short

  print_section "RECENT COMMITS"
  git log --oneline -5

  print_section "GIT DIFF CHECK"
  git diff --check || true
}

check_01a() {
  common_git_checks

  wc_if_exists \
    data/qsb_bridge_synth_01a_existing_result_index.csv \
    data/qsb_bridge_synth_01a_marker_axis_map.csv

  print_file_if_exists "01A RESULT NOTE" \
    docs/QSB_BRIDGE_SYNTH_01A_RESULT_NOTE.md 260

  head_file_if_exists "01A EXISTING RESULT INDEX HEAD" \
    data/qsb_bridge_synth_01a_existing_result_index.csv 20

  head_file_if_exists "01A MARKER AXIS MAP HEAD" \
    data/qsb_bridge_synth_01a_marker_axis_map.csv 30

  print_file_if_exists "01A EXISTING RESULT INDEX FIELD LIST" \
    docs/QSB_BRIDGE_SYNTH_01A_EXISTING_RESULT_INDEX_FIELD_LIST.md 220

  print_file_if_exists "01A MARKER AXIS MAP FIELD LIST" \
    docs/QSB_BRIDGE_SYNTH_01A_MARKER_AXIS_MAP_FIELD_LIST.md 220
}

check_01b() {
  common_git_checks

  wc_if_exists \
    data/qsb_bridge_synth_01b_cross_test_pattern_matrix.csv

  print_file_if_exists "01B RESULT NOTE" \
    docs/QSB_BRIDGE_SYNTH_01B_RESULT_NOTE.md 260

  head_file_if_exists "01B CROSS TEST PATTERN MATRIX HEAD" \
    data/qsb_bridge_synth_01b_cross_test_pattern_matrix.csv 20

  print_file_if_exists "01B CROSS TEST PATTERN MATRIX FIELD LIST" \
    docs/QSB_BRIDGE_SYNTH_01B_CROSS_TEST_PATTERN_MATRIX_FIELD_LIST.md 220
}

check_01c() {
  common_git_checks

  wc_if_exists \
    data/qsb_bridge_synth_01c_evidence_binding_table.csv

  print_file_if_exists "01C RESULT NOTE" \
    docs/QSB_BRIDGE_SYNTH_01C_RESULT_NOTE.md 260

  head_file_if_exists "01C EVIDENCE BINDING TABLE HEAD" \
    data/qsb_bridge_synth_01c_evidence_binding_table.csv 25

  print_file_if_exists "01C EVIDENCE BINDING TABLE FIELD LIST" \
    docs/QSB_BRIDGE_SYNTH_01C_EVIDENCE_BINDING_TABLE_FIELD_LIST.md 220
}

check_01d() {
  common_git_checks

  wc_if_exists \
    data/qsb_bridge_synth_01d_c60_candidate_gate_table.csv \
    data/qsb_bridge_synth_01d_replay_certification_ladder.csv \
    data/qsb_bridge_synth_01d_null_family_normalization_table.csv \
    data/qsb_bridge_synth_01d_proxy_marker_source_binding.csv

  print_file_if_exists "01D RESULT NOTE" \
    docs/QSB_BRIDGE_SYNTH_01D_RESULT_NOTE.md 260

  head_file_if_exists "01D C60 CANDIDATE GATE TABLE HEAD" \
    data/qsb_bridge_synth_01d_c60_candidate_gate_table.csv 20

  head_file_if_exists "01D REPLAY CERTIFICATION LADDER HEAD" \
    data/qsb_bridge_synth_01d_replay_certification_ladder.csv 20

  head_file_if_exists "01D NULL FAMILY NORMALIZATION TABLE HEAD" \
    data/qsb_bridge_synth_01d_null_family_normalization_table.csv 20

  head_file_if_exists "01D PROXY MARKER SOURCE BINDING HEAD" \
    data/qsb_bridge_synth_01d_proxy_marker_source_binding.csv 20

  print_file_if_exists "01D C60 CANDIDATE GATE FIELD LIST" \
    docs/QSB_BRIDGE_SYNTH_01D_C60_CANDIDATE_GATE_TABLE_FIELD_LIST.md 180

  print_file_if_exists "01D REPLAY CERTIFICATION LADDER FIELD LIST" \
    docs/QSB_BRIDGE_SYNTH_01D_REPLAY_CERTIFICATION_LADDER_FIELD_LIST.md 180

  print_file_if_exists "01D NULL FAMILY NORMALIZATION FIELD LIST" \
    docs/QSB_BRIDGE_SYNTH_01D_NULL_FAMILY_NORMALIZATION_TABLE_FIELD_LIST.md 180

  print_file_if_exists "01D PROXY MARKER SOURCE BINDING FIELD LIST" \
    docs/QSB_BRIDGE_SYNTH_01D_PROXY_MARKER_SOURCE_BINDING_FIELD_LIST.md 180
}

usage() {
  cat <<'EOF'
Usage:
  bash scripts/qsb_bridge_synth_check.sh 01a
  bash scripts/qsb_bridge_synth_check.sh 01b
  bash scripts/qsb_bridge_synth_check.sh 01c
  bash scripts/qsb_bridge_synth_check.sh 01d

This script is read-only. It does not modify files or perform git write actions.
EOF
}

require_repo_root

case "$BLOCK" in
  01a|01A) check_01a ;;
  01b|01B) check_01b ;;
  01c|01C) check_01c ;;
  01d|01D) check_01d ;;
  -h|--help|"") usage ;;
  *)
    echo "ERROR: Unknown block: $BLOCK"
    usage
    exit 2
    ;;
esac
