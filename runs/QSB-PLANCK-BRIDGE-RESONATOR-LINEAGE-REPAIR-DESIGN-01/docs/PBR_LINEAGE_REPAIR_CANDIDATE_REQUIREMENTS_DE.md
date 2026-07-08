# PBR Lineage Repair Candidate Requirements

## Befund

Die beiden Lineage-Reparaturkandidaten sind:

- `CAND-0127`: `data/bmc01/bmc01_baseline_relational_table_template.csv`
- `CAND-0128`: `data/bmc04/bmc04_baseline_relational_table_template.csv`

Beide stehen in der Klasse `candidate_admissible_only_after_lineage_repair`.

## Interpretation

Diese Klasse bedeutet nicht Zulassung. Sie bedeutet, dass eine spaetere Reparaturausfuehrung pruefen muss, ob interne Source-Lineage und Nicht-Alias-Evidenz ueberhaupt herstellbar sind.

## Hypothese

Erfolg ist nur moeglich, wenn interne Source-Manifeste, Transformationsketten, Hash-/Versionsdaten, Vor-Paar-Existenz und Pair-Mapping-Basis nachweisbar sind.

## Offene Luecke

Post-hoc Pair-Reparatur ist ein Risiko. Ein Mapping darf nicht nachtraeglich aus Lag, Pair-ID oder Indexordnung als Wertquelle konstruiert werden.

## Claim Boundary

Kein Kandidat wird in diesem Design-Run hochgestuft.
