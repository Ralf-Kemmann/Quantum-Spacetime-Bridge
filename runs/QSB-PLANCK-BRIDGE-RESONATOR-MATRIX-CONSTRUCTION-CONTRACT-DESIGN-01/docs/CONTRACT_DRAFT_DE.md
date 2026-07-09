# Contract Draft

## C0 - Metadata

Draft ID: `QSB-PBR-K-CANDIDATE-MATRIX-CONSTRUCTION-CONTRACT-DRAFT-01`.

Status: `draft_contract_ready_for_human_review`.

## C1 - Source and Lineage

Die Codequelle und K-Export-Hashes sind dokumentiert. Die Lineage bleibt reviewpflichtig, weil sie ueber mehrere Artefakte verteilt ist.

## C2 - Input Identity

Pair-ID und Endpoint-Spalten sind belegt. Direct input table, Duplicate Policy und Missing Policy muessen explizit freigegeben werden.

## C3 - Pair and Diagonal Policy

Ordered non-diagonal pairs sind belegt. Symmetrisierung und Diagonal-Setzung stammen aus Code-Spuren und muessen als Contract-Text bestaetigt werden.

## C4 - Lag Policy

Lag-Class-Komponenten sind nicht dokumentiert und duerfen nicht erraten werden.

## C5 - Matrix Rule

Die belegte Formel ist dot product normalisierter Phase-Response-Vektoren. Aggregation und Symmetrisierung sind code-derived.

## C6 - Numerical Policy

PSD-Minimumstoleranz, Shape, Symmetrie, Diagonal und Range sind belegt. Rank und Metriken fehlen.

## C7 - Controls

Randomization und Controls bleiben reviewpflichtig.

## C8 - Callable

Ein K-only Callable fehlt.

## C9 - Review

Alle blockierenden Fragen stehen in `data/human_review_checklist.csv`.

