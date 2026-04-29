# BMC-07 – Input Gap Note

## Befund
Der Runner scheitert aktuell an:
`FileNotFoundError: data/baseline_relational_table.csv`

## Interpretation
Der Codepfad selbst wurde erreicht; die fehlende Stelle liegt nicht im Startscript,
sondern im noch unvollständigen Inputsatz unter `data/`.

## Hypothese
Nach Einspielen von
- `data/baseline_relational_table.csv`
- `data/node_metadata.csv`
sollte der Runner mindestens bis zur nächsten offenen Validierungs- oder Laufstufe kommen.

## Offene Lücke
Noch offen bleibt, ob der Minimaldatensatz sofort ohne weitere Pfadanpassung läuft.
