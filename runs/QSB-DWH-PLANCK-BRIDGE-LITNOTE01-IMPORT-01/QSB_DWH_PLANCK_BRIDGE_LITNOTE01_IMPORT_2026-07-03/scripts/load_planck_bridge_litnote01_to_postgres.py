#!/usr/bin/env python3
"""Optional loader for QSB Planck-Bridge LitNote01 DWH import.

Default behavior: run the generated SQL file against PostgreSQL using psql.
Environment variables:
  PGDATABASE=qsb_research_dwh
  PGUSER=ralf-kemmann
  PGHOST=localhost
  PGPORT=5432
"""
from __future__ import annotations
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SQL = ROOT / "sql" / "20260703_qsb_planck_bridge_litnote01_import.sql"
VALIDATE = ROOT / "sql" / "validate_planck_bridge_litnote01_import.sql"

def run_psql(sql_file: pathlib.Path) -> None:
    cmd = ["psql", "-v", "ON_ERROR_STOP=1", "-f", str(sql_file)]
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)

def main() -> int:
    missing = [k for k in ["PGDATABASE", "PGUSER", "PGHOST", "PGPORT"] if not os.environ.get(k)]
    if missing:
        print("Hinweis: folgende PG*-Variablen sind nicht gesetzt:", ", ".join(missing))
        print("Nutze psql-Defaults oder setze z.B.:")
        print("  export PGDATABASE=qsb_research_dwh")
        print("  export PGUSER=ralf-kemmann")
        print("  export PGHOST=localhost")
        print("  export PGPORT=5432")
    run_psql(SQL)
    run_psql(VALIDATE)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
