# README – BMC-07d Legitimation Matrix

## Status
Offene CSV-Matrix der methodischen Legitimationseinstufungen aus BMC-07d.

## Zweck
Diese Datei überführt die qualitative Legitimationsmatrix in ein maschinenlesbares CSV-Format
für repo-saubere Weiterverarbeitung in `docs/`.

## Enthaltene Datei
- `BMC07d_backbone_variant_legitimation_matrix.csv`

## Feldliste
- `variant_name` — string — Name der Backbone-Variante.
- `definition_short` — string — Kurzbeschreibung der Segmentierungsregel.
- `ex_ante_plausibility` — string — qualitative Einstufung der ex-ante Begründbarkeit.
- `readout_proximity` — string — qualitative Nähe zur späteren Messlogik.
- `coupling_risk` — string — Risiko einer Definition-Readout-Kopplung.
- `transparency` — string — qualitative Transparenzbewertung.
- `status` — string — projektinterner Legitimationsstatus.
- `comment` — string — kurze interpretative Einordnung.

## Befund
Kein neuer numerischer Befund. Das Artefakt ist reine methodische Strukturierung.

## Interpretation
Die CSV eignet sich als kompakte Referenz für spätere interne Notizen, Vergleiche
und mögliche Reviewer-orientierte Methodikdiskussionen.

## Hypothese
Wenn die fairen Basisvarianten auch auf realeren Inputs konsistent bleiben, wird die
methodische Tragfähigkeit des Off-Backbone-Befunds wachsen.

## Offene Lücke
Noch offen ist eine spätere Erweiterung um zusätzliche Spalten wie
`decision_label_on_minimal_run` oder `recommended_use`.
