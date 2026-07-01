#!/usr/bin/env python3
"""Read-only QSB metadata server backed by PostgreSQL via psql CLI."""

from __future__ import annotations

import argparse
import json
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


DEFAULT_DB = "qsb_research_dwh"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def run_query(sql: str, db: str = DEFAULT_DB) -> list[dict]:
    cmd = ["psql", "-d", db, "-At", "-F", "\t", "-c", sql]
    proc = subprocess.run(cmd, check=False, text=True, capture_output=True, timeout=20)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    rows = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        rows.append({"row": line.split("\t")})
    return rows


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class MetadataHandler(BaseHTTPRequestHandler):
    db_name = DEFAULT_DB

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        try:
            if parsed.path == "/health":
                rows = run_query("SELECT 'ok', current_database();", self.db_name)
                json_response(self, 200, {"status": "ok", "database": rows[0]["row"][1] if rows else self.db_name})
            elif parsed.path == "/":
                json_response(self, 200, {"service": "qsb_metadata_server", "read_only": True, "endpoints": ["/health", "/search?q=", "/datasets", "/fields", "/validations", "/claims"]})
            elif parsed.path == "/search":
                q = (params.get("q") or [""])[0].replace("'", "''")
                rows = run_query(f"SELECT record_type, record_id, search_text, domain_guess FROM mart.v_qsb_global_search WHERE search_text ILIKE '%{q}%' LIMIT 50;", self.db_name)
                json_response(self, 200, {"rows": rows})
            elif parsed.path == "/datasets":
                rows = run_query("SELECT dataset_id, dataset_name, domain FROM mart.v_qsb_dataset_overview ORDER BY dataset_id;", self.db_name)
                json_response(self, 200, {"rows": rows})
            elif parsed.path == "/fields":
                rows = run_query("SELECT canonical_name, display_label_de FROM mart.v_qsb_metadata_aliases_de ORDER BY canonical_name LIMIT 200;", self.db_name)
                json_response(self, 200, {"rows": rows})
            elif parsed.path == "/validations":
                rows = run_query("SELECT validation_status, COUNT(*) FROM mart.v_qsb_validation_status GROUP BY validation_status ORDER BY validation_status;", self.db_name)
                json_response(self, 200, {"rows": rows})
            elif parsed.path == "/claims":
                rows = run_query("SELECT claim_boundary, claim_status FROM mart.v_qsb_claim_boundaries ORDER BY claim_boundary;", self.db_name)
                json_response(self, 200, {"rows": rows})
            else:
                json_response(self, 404, {"error": "not_found"})
        except Exception as exc:
            json_response(self, 500, {"error": str(exc)})

    def do_POST(self) -> None:
        json_response(self, 405, {"error": "read_only"})

    do_PUT = do_POST
    do_PATCH = do_POST
    do_DELETE = do_POST

    def log_message(self, fmt: str, *args) -> None:
        return


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only QSB metadata server")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    MetadataHandler.db_name = args.db
    if args.check:
        rows = run_query("SELECT COUNT(*) FROM mart.v_qsb_global_search;", args.db)
        print(json.dumps({"status": "ok", "global_search_rows": rows[0]["row"][0] if rows else "0"}, sort_keys=True))
        return 0
    server = ThreadingHTTPServer((args.host, args.port), MetadataHandler)
    print(f"qsb_metadata_server listening on http://{args.host}:{args.port}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
