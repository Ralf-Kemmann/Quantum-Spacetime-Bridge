#!/usr/bin/env bash
set -euo pipefail

# inventory_numerics_cleanup.sh
#
# Non-destructive inventory script for the consolidated numerics subtree.
# It creates readable cleanup reports and file lists.
#
# Default project root:
#   /home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
#
# Usage:
#   bash scripts/inventory_numerics_cleanup.sh
#   bash scripts/inventory_numerics_cleanup.sh /path/to/quantum-spacetime-bridge

PROJECT_ROOT="${1:-/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge}"
NUMERICS_DIR="$PROJECT_ROOT/numerics/debroglie-phase-bridge"
OUT_DIR="$PROJECT_ROOT/docs/numerics_inventory"
STAMP="$(date +%Y-%m-%d_%H-%M-%S)"
RUN_DIR="$OUT_DIR/$STAMP"

if [[ ! -d "$PROJECT_ROOT" ]]; then
  echo "ERROR: project root not found: $PROJECT_ROOT" >&2
  exit 1
fi

if [[ ! -d "$NUMERICS_DIR" ]]; then
  echo "ERROR: numerics subtree not found: $NUMERICS_DIR" >&2
  exit 1
fi

mkdir -p "$RUN_DIR"

ALL_FILES="$RUN_DIR/all_files.txt"
ALL_DIRS="$RUN_DIR/all_dirs.txt"
BAK_FILES="$RUN_DIR/backup_files.txt"
SUSPICIOUS_NAMES="$RUN_DIR/suspicious_names.txt"
DUPLICATE_BASENAMES="$RUN_DIR/duplicate_basenames.txt"
LARGE_FILES="$RUN_DIR/large_files_over_10MB.txt"
MD_FILES="$RUN_DIR/markdown_files.txt"
JSON_FILES="$RUN_DIR/json_files.txt"
CSV_FILES="$RUN_DIR/csv_files.txt"
RUN_DIRS="$RUN_DIR/run_like_directories.txt"
REPORT_MD="$RUN_DIR/numerics_inventory_report.md"
LATEST_LINK="$OUT_DIR/latest"

find "$NUMERICS_DIR" -type f | sort > "$ALL_FILES"
find "$NUMERICS_DIR" -type d | sort > "$ALL_DIRS"

find "$NUMERICS_DIR" -type f \( -name "*.bak" -o -name "*~" -o -name "*.tmp" -o -name "*.orig" \) | sort > "$BAK_FILES"

{
  find "$NUMERICS_DIR" -type f | grep -E '/from __future__ import annotations\.py$' || true
  find "$NUMERICS_DIR" -type f | grep -E '/run:\.yaml$' || true
  find "$NUMERICS_DIR" -type f | grep -E '/.*[[:space:]].*\.(py|md|json|yaml|yml|csv|txt)$' || true
} | sort -u > "$SUSPICIOUS_NAMES"

find "$NUMERICS_DIR" -type f -printf "%f\n" | sort | uniq -d > "$DUPLICATE_BASENAMES"

find "$NUMERICS_DIR" -type f -size +10M -printf "%s\t%p\n" | sort -nr > "$LARGE_FILES"

find "$NUMERICS_DIR" -type f -name "*.md" | sort > "$MD_FILES"
find "$NUMERICS_DIR" -type f -name "*.json" | sort > "$JSON_FILES"
find "$NUMERICS_DIR" -type f -name "*.csv" | sort > "$CSV_FILES"

find "$NUMERICS_DIR" -type d | grep -E '/(runs|results|run_|.*_run_.*|.*_run[0-9].*|.*smoke_test.*)$' | sort > "$RUN_DIRS" || true

count_lines() {
  local f="$1"
  if [[ -f "$f" ]]; then
    wc -l < "$f" | tr -d ' '
  else
    echo 0
  fi
}

TOTAL_FILES="$(count_lines "$ALL_FILES")"
TOTAL_DIRS="$(count_lines "$ALL_DIRS")"
COUNT_BAK="$(count_lines "$BAK_FILES")"
COUNT_SUSPICIOUS="$(count_lines "$SUSPICIOUS_NAMES")"
COUNT_DUP_BASENAMES="$(count_lines "$DUPLICATE_BASENAMES")"
COUNT_LARGE="$(count_lines "$LARGE_FILES")"
COUNT_MD="$(count_lines "$MD_FILES")"
COUNT_JSON="$(count_lines "$JSON_FILES")"
COUNT_CSV="$(count_lines "$CSV_FILES")"
COUNT_RUN_DIRS="$(count_lines "$RUN_DIRS")"

cat > "$REPORT_MD" <<EOF
# Numerics Inventory Report

## Scope

Project root:
\`$PROJECT_ROOT\`

Numerics subtree:
\`$NUMERICS_DIR\`

Inventory run:
\`$STAMP\`

Output directory:
\`$RUN_DIR\`

## Summary

- Total files: $TOTAL_FILES
- Total directories: $TOTAL_DIRS
- Markdown files: $COUNT_MD
- JSON files: $COUNT_JSON
- CSV files: $COUNT_CSV
- Backup-like files: $COUNT_BAK
- Suspicious filenames: $COUNT_SUSPICIOUS
- Duplicate basenames: $COUNT_DUP_BASENAMES
- Large files over 10 MB: $COUNT_LARGE
- Run-like/result-like directories: $COUNT_RUN_DIRS

## Generated files

- \`all_files.txt\`
- \`all_dirs.txt\`
- \`backup_files.txt\`
- \`suspicious_names.txt\`
- \`duplicate_basenames.txt\`
- \`large_files_over_10MB.txt\`
- \`markdown_files.txt\`
- \`json_files.txt\`
- \`csv_files.txt\`
- \`run_like_directories.txt\`

## First interpretation

This report is intentionally non-destructive.
It does not move, rename, or delete anything.

Its purpose is to support a transparent cleanup workflow:
1. inventory
2. classify
3. document
4. archive or remove only after review

## Suggested next manual review order

1. suspicious filenames
2. backup files
3. duplicate basenames
4. very large files
5. run-like directories and deep result trees

EOF

rm -f "$LATEST_LINK"
ln -s "$RUN_DIR" "$LATEST_LINK"

echo "Inventory created:"
echo "  $REPORT_MD"
echo
echo "Latest symlink updated:"
echo "  $LATEST_LINK"
echo
echo "Open the report with:"
echo "  xdg-open \"$REPORT_MD\" 2>/dev/null || true"
