# K-only Callable Design

## Befund

Der spaetere Patch soll einen scoped Callable bereitstellen:

`scripts/qsb_pbr_matrix_contract/reconstruct_k_candidate.py`

## Anforderungen

- Explizite Inputargumente.
- Keine hidden state inputs.
- Read-only Zugriff auf Source-Artefakte.
- Schreibzugriff nur in explizites Output-Verzeichnis.
- Dry-run Mode.
- Validation Mode.
- Hash- oder Similarity-Gate.

## Claim Boundary

Ein Callable rekonstruiert technische Reproduzierbarkeit; er erzeugt keinen physikalischen Claim.

