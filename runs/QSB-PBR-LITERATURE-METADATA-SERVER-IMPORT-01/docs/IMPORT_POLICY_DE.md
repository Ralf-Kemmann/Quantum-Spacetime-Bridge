# Import-Policy

Diese Literaturdaten sind Kontext- und Suchraum-Metadaten.
Sie sind keine interne Evidenz für QSB/PBR.
Sie autorisieren keine physikalischen oder mechanistischen Claims.

## Ausführungsmodus

Der Default ist `dry-run` beziehungsweise `prepare-only`.

Keine Datenbank wurde in diesem Run beschrieben. Ein Execute-Import darf erst nach expliziter Auswahl des DB-Ziels erfolgen.

## Schutzregeln

- Keine Physikanalyse.
- Keine Änderung an Matrix-, Nullmodell-, Lag-Klassen-, Kandidaten- oder Physikresultat-Tabellen.
- Kein Überschreiben bestehender Literaturzeilen ohne explizite Merge-Logik.
- Kein Webzugriff.
- Transaktion mit Rollback bei Validierungsfehlern.

## Fehlender Quellbericht

`deep-research-report(3).md` wurde im Repository nicht gefunden. Die Source-Copy im Run-Paket enthält nur die im Task-Prompt angegebenen Seed-Zeilen. Fehlende DOI-, arXiv- und URL-Felder wurden nicht erfunden.
