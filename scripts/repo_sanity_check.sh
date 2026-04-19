#!/usr/bin/env bash
set -euo pipefail

# repo_sanity_check.sh
#
# Non-destructive repository sanity check for:
# /home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
#
# Usage:
#   bash scripts/repo_sanity_check.sh
#   bash scripts/repo_sanity_check.sh /path/to/quantum-spacetime-bridge

PROJECT_ROOT="${1:-/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge}"
NUMERICS_ROOT="$PROJECT_ROOT/numerics/debroglie-phase-bridge"
DOCS_DIR="$PROJECT_ROOT/docs"
OUT_DIR="$DOCS_DIR/repo_checks"
STAMP="$(date +%Y-%m-%d_%H-%M-%S)"
RUN_DIR="$OUT_DIR/$STAMP"
REPORT_MD="$RUN_DIR/repo_sanity_report.md"
LATEST_LINK="$OUT_DIR/latest"

mkdir -p "$RUN_DIR"

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

[[ -d "$PROJECT_ROOT" ]] || fail "project root not found: $PROJECT_ROOT"
[[ -d "$NUMERICS_ROOT" ]] || fail "numerics root not found: $NUMERICS_ROOT"

# Helpers
status_ok() { printf -- "- [x] %s\n" "$1"; }
status_warn() { printf -- "- [ ] %s\n" "$1"; }

# Required root items
ROOT_ITEMS=(
  "README.md"
  "CITATION.cff"
  "LICENSE"
  "docs/project-overview.md"
  "docs/method-status.md"
  "docs/what-this-is-and-is-not.md"
  "docs/repository-map.md"
  "docs/current-result-status.md"
  "docs/numerics-location.md"
  "docs/numerics-cleanup-plan.md"
  "docs/quarantine-archive-summary.md"
  "docs/m33-structure-note.md"
  "links/public-links.md"
)

# Required numerics items
NUMERICS_ITEMS=(
  "docs/project/MASTERCHAT_CANONICAL.md"
  "_quarantine"
  "_archive_masterchat_noncanonical"
  "m33_v0_scaffold"
  "typ_b_analysis"
  "src"
  "scripts"
  "results"
  "tests"
)

# Known files that should no longer be in active paths
SHOULD_BE_GONE=(
  "typ_b_analysis/configs/run:.yaml"
  "typ_b_analysis/src/from __future__ import annotations.py"
  "typ_b_analysis/src/bridge_carrier_block_d.py.bak"
  "typ_b_analysis/src/bridge_carrier_leave_one_out.py.bak"
)

# Known files that should now be in archive/quarantine
SHOULD_BE_IN_QUARANTINE=(
  "_quarantine/run:.yaml"
  "_quarantine/from __future__ import annotations.py"
  "_quarantine/bridge_carrier_block_d.py.bak"
  "_quarantine/bridge_carrier_leave_one_out.py.bak"
)

SHOULD_BE_IN_MASTERCHAT_ARCHIVE=(
  "_archive_masterchat_noncanonical/MASTERCHAT_CANONICAL_backup_2026-03-30_M39x1.md"
  "_archive_masterchat_noncanonical/MASTERCHAT_CANONICAL.md"
  "_archive_masterchat_noncanonical/MASTERCHAT_CURRENT_STATUS_2026-04-09.md"
  "_archive_masterchat_noncanonical/masterchat_current_status_2026_04_09_v_2.md"
  "_archive_masterchat_noncanonical/MASTERCHAT_CURRENT_STATUS_2026-04-09_v2.md"
  "_archive_masterchat_noncanonical/MASTERCHAT_CURRENT_STATUS_2026-04-10_v3.md"
  "_archive_masterchat_noncanonical/MASTERCHAT_EINFUEGESTUECK_BRUECKE_KONSOLIDIERT_v1.md"
  "_archive_masterchat_noncanonical/MASTERCHAT_Gravitation_und_RaumZeit_v1.md"
  "_archive_masterchat_noncanonical/MASTERCHAT_RELOCATION_CURRENT_2026-04-05.md"
)

HEAVY_ARCHIVE_ITEM="m33_v0_scaffold/runs/M33_V0_alpha_peak_robustness/M35b_packet_kernel/_archive_heavy/source_curve_grid.csv"
ACTIVE_HEAVY_OLD_PATH="m33_v0_scaffold/runs/M33_V0_alpha_peak_robustness/M35b_packet_kernel/source_curve_grid.csv"

ROOT_CHECKS="$RUN_DIR/root_checks.txt"
NUMERICS_CHECKS="$RUN_DIR/numerics_checks.txt"
ABSENT_ACTIVE_BAD_FILES="$RUN_DIR/absent_active_bad_files.txt"
PRESENT_QUARANTINE_FILES="$RUN_DIR/present_quarantine_files.txt"
PRESENT_MASTERCHAT_ARCHIVE_FILES="$RUN_DIR/present_masterchat_archive_files.txt"
MASTERCHAT_ACTIVE_SCAN="$RUN_DIR/masterchat_active_scan.txt"
HEAVY_CHECK="$RUN_DIR/heavy_archive_check.txt"
GIT_STATUS="$RUN_DIR/git_status_short.txt"
TOP_LEVEL_TREE="$RUN_DIR/top_level_tree.txt"
NUMERICS_TOP_TREE="$RUN_DIR/numerics_top_tree.txt"

: > "$ROOT_CHECKS"
: > "$NUMERICS_CHECKS"
: > "$ABSENT_ACTIVE_BAD_FILES"
: > "$PRESENT_QUARANTINE_FILES"
: > "$PRESENT_MASTERCHAT_ARCHIVE_FILES"
: > "$MASTERCHAT_ACTIVE_SCAN"
: > "$HEAVY_CHECK"

for item in "${ROOT_ITEMS[@]}"; do
  if [[ -e "$PROJECT_ROOT/$item" ]]; then
    echo "OK  $item" >> "$ROOT_CHECKS"
  else
    echo "MISS  $item" >> "$ROOT_CHECKS"
  fi
done

for item in "${NUMERICS_ITEMS[@]}"; do
  if [[ -e "$NUMERICS_ROOT/$item" ]]; then
    echo "OK  $item" >> "$NUMERICS_CHECKS"
  else
    echo "MISS  $item" >> "$NUMERICS_CHECKS"
  fi
done

for item in "${SHOULD_BE_GONE[@]}"; do
  if [[ -e "$NUMERICS_ROOT/$item" ]]; then
    echo "PRESENT_BAD  $item" >> "$ABSENT_ACTIVE_BAD_FILES"
  else
    echo "ABSENT_OK  $item" >> "$ABSENT_ACTIVE_BAD_FILES"
  fi
done

for item in "${SHOULD_BE_IN_QUARANTINE[@]}"; do
  if [[ -e "$NUMERICS_ROOT/$item" ]]; then
    echo "OK  $item" >> "$PRESENT_QUARANTINE_FILES"
  else
    echo "MISS  $item" >> "$PRESENT_QUARANTINE_FILES"
  fi
done

for item in "${SHOULD_BE_IN_MASTERCHAT_ARCHIVE[@]}"; do
  if [[ -e "$NUMERICS_ROOT/$item" ]]; then
    echo "OK  $item" >> "$PRESENT_MASTERCHAT_ARCHIVE_FILES"
  else
    echo "MISS  $item" >> "$PRESENT_MASTERCHAT_ARCHIVE_FILES"
  fi
done

if [[ -e "$NUMERICS_ROOT/$HEAVY_ARCHIVE_ITEM" ]]; then
  echo "OK  $HEAVY_ARCHIVE_ITEM" >> "$HEAVY_CHECK"
else
  echo "MISS  $HEAVY_ARCHIVE_ITEM" >> "$HEAVY_CHECK"
fi

if [[ -e "$NUMERICS_ROOT/$ACTIVE_HEAVY_OLD_PATH" ]]; then
  echo "PRESENT_BAD  $ACTIVE_HEAVY_OLD_PATH" >> "$HEAVY_CHECK"
else
  echo "ABSENT_OK  $ACTIVE_HEAVY_OLD_PATH" >> "$HEAVY_CHECK"
fi

find "$NUMERICS_ROOT" \
  -path "$NUMERICS_ROOT/_archive_masterchat_noncanonical" -prune -o \
  \( -iname 'MASTERCHAT*' -o -iname 'masterchat*' -o -iname '*CURRENT_STATUS*' -o -iname '*canonical*' \) \
  -print | sort > "$MASTERCHAT_ACTIVE_SCAN"

(
  cd "$PROJECT_ROOT"
  git status --short || true
) > "$GIT_STATUS"

find "$PROJECT_ROOT" -maxdepth 2 \( -type d -o -type f \) | sort > "$TOP_LEVEL_TREE"
find "$NUMERICS_ROOT" -maxdepth 2 \( -type d -o -type f \) | sort > "$NUMERICS_TOP_TREE"

root_miss="$(grep -c '^MISS' "$ROOT_CHECKS" || true)"
num_miss="$(grep -c '^MISS' "$NUMERICS_CHECKS" || true)"
bad_active_present="$(grep -c '^PRESENT_BAD' "$ABSENT_ACTIVE_BAD_FILES" || true)"
quarantine_miss="$(grep -c '^MISS' "$PRESENT_QUARANTINE_FILES" || true)"
masterchat_archive_miss="$(grep -c '^MISS' "$PRESENT_MASTERCHAT_ARCHIVE_FILES" || true)"
heavy_miss="$(grep -c '^MISS' "$HEAVY_CHECK" || true)"
heavy_bad_present="$(grep -c '^PRESENT_BAD' "$HEAVY_CHECK" || true)"

cat > "$REPORT_MD" <<EOF
# Repository Sanity Report

## Scope

Project root:
\`$PROJECT_ROOT\`

Numerics root:
\`$NUMERICS_ROOT\`

Run timestamp:
\`$STAMP\`

## Summary

- Missing expected root items: $root_miss
- Missing expected numerics items: $num_miss
- Bad active files still present: $bad_active_present
- Missing quarantine files: $quarantine_miss
- Missing non-canonical masterchat archive files: $masterchat_archive_miss
- Heavy archive missing checks: $heavy_miss
- Heavy artifact still present in active run path: $heavy_bad_present

## Root-level project checks

EOF

while IFS= read -r line; do
  if [[ "$line" == OK* ]]; then
    status_ok "${line#OK  }" >> "$REPORT_MD"
  else
    status_warn "${line#MISS  }" >> "$REPORT_MD"
  fi
done < "$ROOT_CHECKS"

cat >> "$REPORT_MD" <<EOF

## Numerics subtree checks

EOF

while IFS= read -r line; do
  if [[ "$line" == OK* ]]; then
    status_ok "${line#OK  }" >> "$REPORT_MD"
  else
    status_warn "${line#MISS  }" >> "$REPORT_MD"
  fi
done < "$NUMERICS_CHECKS"

cat >> "$REPORT_MD" <<EOF

## Files that should no longer remain in active paths

EOF

while IFS= read -r line; do
  if [[ "$line" == ABSENT_OK* ]]; then
    status_ok "${line#ABSENT_OK  }" >> "$REPORT_MD"
  else
    status_warn "${line#PRESENT_BAD  } still present in active path" >> "$REPORT_MD"
  fi
done < "$ABSENT_ACTIVE_BAD_FILES"

cat >> "$REPORT_MD" <<EOF

## Quarantine checks

EOF

while IFS= read -r line; do
  if [[ "$line" == OK* ]]; then
    status_ok "${line#OK  }" >> "$REPORT_MD"
  else
    status_warn "${line#MISS  }" >> "$REPORT_MD"
  fi
done < "$PRESENT_QUARANTINE_FILES"

cat >> "$REPORT_MD" <<EOF

## Non-canonical masterchat archive checks

EOF

while IFS= read -r line; do
  if [[ "$line" == OK* ]]; then
    status_ok "${line#OK  }" >> "$REPORT_MD"
  else
    status_warn "${line#MISS  }" >> "$REPORT_MD"
  fi
done < "$PRESENT_MASTERCHAT_ARCHIVE_FILES"

cat >> "$REPORT_MD" <<EOF

## Heavy artifact check

EOF

while IFS= read -r line; do
  if [[ "$line" == OK* || "$line" == ABSENT_OK* ]]; then
    status_ok "${line#OK  }${line#ABSENT_OK  }" >> "$REPORT_MD"
  else
    status_warn "${line#PRESENT_BAD  } still present in active path" >> "$REPORT_MD"
  fi
done < "$HEAVY_CHECK"

cat >> "$REPORT_MD" <<EOF

## Remaining masterchat-like files outside non-canonical archive

EOF

if [[ -s "$MASTERCHAT_ACTIVE_SCAN" ]]; then
  while IFS= read -r line; do
    printf -- "- %s\n" "$line" >> "$REPORT_MD"
  done < "$MASTERCHAT_ACTIVE_SCAN"
else
  echo "- none found" >> "$REPORT_MD"
fi

cat >> "$REPORT_MD" <<EOF

## Git status snapshot

\`\`\`text
$(cat "$GIT_STATUS")
\`\`\`

## Generated companion files

- \`root_checks.txt\`
- \`numerics_checks.txt\`
- \`absent_active_bad_files.txt\`
- \`present_quarantine_files.txt\`
- \`present_masterchat_archive_files.txt\`
- \`heavy_archive_check.txt\`
- \`masterchat_active_scan.txt\`
- \`git_status_short.txt\`
- \`top_level_tree.txt\`
- \`numerics_top_tree.txt\`

## Interpretation

This check is intentionally non-destructive. It is meant to answer two practical questions:

1. Is the repository structurally where we expect it to be?
2. Are the already-cleaned-up files actually in their intended locations?

A “clean” outcome here means:
- key root files exist
- numerics subtree exists and contains expected structure
- known malformed/backup files are no longer in active locations
- quarantine and archive locations contain the expected moved files
- the heavy artifact is archived and not left in the active run surface

EOF

rm -f "$LATEST_LINK"
ln -s "$RUN_DIR" "$LATEST_LINK"

echo "Sanity check created:"
echo "  $REPORT_MD"
echo
echo "Latest symlink updated:"
echo "  $LATEST_LINK"
