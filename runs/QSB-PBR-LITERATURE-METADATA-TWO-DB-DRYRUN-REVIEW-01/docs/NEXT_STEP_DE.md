# Nächster Schritt

Empfohlener nächster Lauf:

```text
QSB-PBR-LITERATURE-METADATA-SEED-CSV-REPAIR-VALIDATION-01
```

Zuerst sollte die Seed-CSV-Spaltenverschiebung repariert und validiert werden. Danach kann erneut ein Zwei-DB-Dry-run-Review erfolgen. Erst nach einem grünen Dry-run-Review wäre ein Metadata-Schema-Mapping-Review oder eine spätere Execution-Design-Stufe sinnvoll.

Review-Befehl:

```bash
sed -n '1,120p' runs/QSB-PBR-LITERATURE-METADATA-TWO-DB-DRYRUN-REVIEW-01/data/claim_boundary_review.csv
```
