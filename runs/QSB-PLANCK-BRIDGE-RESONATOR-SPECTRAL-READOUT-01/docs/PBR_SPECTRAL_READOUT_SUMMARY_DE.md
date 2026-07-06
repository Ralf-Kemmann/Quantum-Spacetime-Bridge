# PBR Spectral Readout Zusammenfassung

## Befund

Die `K_candidate`-Matrix ist nicht nur PSD innerhalb numerischer Toleranz, sondern zeigt eine klare gerichtete Lag-/Differenzstruktur.

42 gerichtete Pair-Features entstehen aus 7 Basiselementen ohne Diagonale:

```text
7 * 6 = 42
```

Die Features kollabieren formal auf 6 effektive Lag-Achsen, weil `+k` und `-k` antiparallel sind.

Das erklaert formal:

- `rank = 6`
- `nullity = 36`
- `parallel_count = 70`
- `antiparallel_count = 91`

## Interpretation

Dies ist ein formaler Matrixstruktur-Befund. Alle physikalischen Claims bleiben gesperrt.

## Claim Boundary

- `claim_status = formal_matrix_structure_readout_only`
- `physical_claim_release = blocked_no_physics_claim`
- `review_status = requires_human_review`

The spectral readout supports only a formal matrix-structure statement:
the K_candidate matrix is consistent with a rank-6 directed lag-class Gram structure.
All physical claims remain blocked.

