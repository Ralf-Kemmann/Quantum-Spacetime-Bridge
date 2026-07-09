# Validation Harness Design

## Befund

Die Validation Harness ist in `data/validation_harness_design.csv` spezifiziert.

## Checks

- Contract fields exported.
- K reproduction or hash/similarity check.
- Pair table identity.
- Lag class identity.
- PSD check.
- Rank check.
- CSV schema check.
- No hidden state check.
- Claim boundary check.

## Interpretation

Jeder Check ist ein Gate fuer spaetere Implementation und Review.

## Claim Boundary

Validierung prueft Reproduzierbarkeit und Auditregeln, keine physikalische Realitaet.

