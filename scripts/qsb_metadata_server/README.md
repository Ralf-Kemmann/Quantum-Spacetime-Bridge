# QSB Metadata Server

Read-only local metadata server for the PostgreSQL DWH `qsb_research_dwh`.

The server uses only the Python standard library and the `psql` CLI. It exposes
SELECT-only endpoints over `mart.*` and `metadata.*` views/tables.

Endpoints:

- `GET /health`
- `GET /`
- `GET /search?q=...`
- `GET /datasets`
- `GET /fields`
- `GET /validations`
- `GET /claims`

Smoke check:

```bash
python scripts/qsb_metadata_server/qsb_metadata_server.py --check
```

Run locally:

```bash
python scripts/qsb_metadata_server/qsb_metadata_server.py --host 127.0.0.1 --port 8765
```

No write endpoints are implemented.
