# PostgreSQL Local Setup Instructions

Befund: Dieser Run fuehrt keine sudo-/apt-Installation aus.

Wenn PostgreSQL lokal fehlt, installiere und starte PostgreSQL ausserhalb dieses Runs nach lokaler Systempraxis. Danach sollte `psql --version`, `pg_isready` und `psql -d postgres -c "SELECT version();"` funktionieren.

Ziel-Datenbank: `qsb_research_dwh`. Schemas: `admin`, `raw`, `staging`, `canonical`, `metadata`, `validation`, `mart`.

Bei Peer-Auth-/Passwortproblemen nicht blind herumprobieren; Auth-Modus gezielt dokumentieren und freigeben.
