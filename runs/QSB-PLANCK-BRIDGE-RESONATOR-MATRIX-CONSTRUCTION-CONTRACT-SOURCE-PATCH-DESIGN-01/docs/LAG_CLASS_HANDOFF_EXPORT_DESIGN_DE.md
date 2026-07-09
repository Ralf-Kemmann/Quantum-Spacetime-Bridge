# Lag-Class Handoff Export Design

## Befund

Lag-Class-Handoff ist einer der Hauptblocker.

## Exportdesign

Der spaetere Patch soll `lag_class_handoff.csv` erzeugen oder pinnen mit:

- `canonical_pair_id`
- `lag_value`
- `lag_class`
- `lag_class_definition`
- Sort order
- Cardinality export
- Alias exclusion rule

## Validation

Eine spaetere Validation muss eine Zeile pro Pair-ID, keine fehlenden Klassen und korrekte Cardinality-Summen pruefen.

## Claim Boundary

Lag-Class-Handoff ist ein mathematisches/auditives Join-Design, kein Mechanismusbeweis.

