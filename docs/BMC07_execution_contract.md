# BMC-07 – Execution Contract

## Status
Verbindlicher offener Ausführungsvertrag für den BMC-07-Restart.

## Regeln
1. Keine versteckten Rechenwege.
2. Keine Ergebnisbehauptung ohne offenen Startbefehl.
3. Keine Zwischenverarbeitung außerhalb von `scripts/` und `data/`.
4. Kein Schreiben in Fantasieordner.
5. Läufe schreiben ausschließlich nach `runs/`.

## Startweg
### Offener Shell-Start
```bash
bash scripts/run_bmc07_minimal_readouts_open.sh
```

### Direkter Python-Start
```bash
python3 scripts/bmc07_backbone_scaffold_isolation_runner_minimal_readouts.py --config data/bmc07_config_minimal_readouts.yaml
```

## Erwartete Repo-Struktur
```text
quantum-spacetime-bridge/
├── docs/
├── scripts/
├── data/
└── runs/
```

## Pflichtprüfung vor Start
- Liegt `baseline_relational_table.csv` in `data/`?
- Liegt `node_metadata.csv` in `data/`?
- Liegt `bmc07_config_minimal_readouts.yaml` in `data/`?
- Verweist die Config auf `runs/<run_id>/`?
- Liegt der Runner in `scripts/`?
- Liegt das Shell-Script in `scripts/`?

## Befund
Noch keiner.

## Interpretation
Keine. Dieser Vertrag definiert nur den offenen Rechenweg.

## Hypothese
Nicht anwendbar.

## Offene Lücke
Schema-Validierung der JSON-Outputs kann als späterer Zusatzblock ergänzt werden.
