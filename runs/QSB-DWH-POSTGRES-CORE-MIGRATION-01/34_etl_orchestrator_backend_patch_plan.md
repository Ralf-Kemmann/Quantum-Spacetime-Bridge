# ETL Orchestrator Backend Patch Plan

Befund: Ein separater PostgreSQL-Orchestrator liegt unter `scripts/qsb_dwh_pg/`.

Interpretation: Bestehende SQLite-/DWH-Skripte wurden nicht umgebaut. Eine spaetere Integration sollte Backend-Auswahl, Connection-Konfiguration, Dry-Run-Modus und Claim-Boundary-Checks als explizite Schnittstelle einfuehren.

Claim Boundary: Backend-Patch-Plan ist Architekturarbeit, keine wissenschaftliche Auswertung.
