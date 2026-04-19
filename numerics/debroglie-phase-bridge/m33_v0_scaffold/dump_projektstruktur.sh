#!/usr/bin/env bash

OUTFILE="$HOME/Downloads/projektstruktur.txt"

echo "Schreibe nach: $OUTFILE"

{
  echo "=== PWD ==="
  pwd
  echo

  echo "=== TOP LEVEL ==="
  ls -la
  echo

  echo "=== SRC / SCRIPTS / CONFIGS / RUNS ==="
  for d in src scripts configs runs; do
    echo "--- $d ---"
    if [ -d "$d" ]; then
      find "$d" -maxdepth 3 -type f | sort
    else
      echo "Ordner nicht vorhanden"
    fi
    echo
  done

  echo "=== QUICK INDEX ==="
  find . -maxdepth 4 \
    -not -path '*/.git/*' \
    -not -path '*/.venv/*' \
    -not -path '*/__pycache__/*' \
    -not -name '*.pyc' \
    | sort
} > "$OUTFILE"

echo "Fertig."
ls -l "$OUTFILE"
