# PBR Lineage Repair Design

## Befund

Der Run definiert nur ein Reparaturdesign fuer die zwei Lineage-Reparaturkandidaten `CAND-0127` und `CAND-0128`.

Die bekannten Kettenwerte bleiben erhalten:

- candidate_count_total=260
- admissible_for_testing=0
- dominant_blocker=not_pair_mappable
- dominant_blocker_count=257
- lineage_repair_candidates=2
- metadata_repair_candidates=1
- mechanism_testing_readiness=not_ready_no_admissible_candidates
- next_gate=lineage_repair_required
- physical_claim_release=blocked_no_physics_claim

## Interpretation

Das Design benennt fehlende Artefakte und Nachweise. Es repariert keine Kandidaten und fuehrt keine erneute Zulassungspruefung durch.

## Hypothese

Ein separater Ausfuehrungslauf kann die geforderten internen Artefakte suchen, hashen, dokumentieren und danach eine spaetere Admissibility-Pruefung vorbereiten.

## Offene Luecke

Fuer beide Kandidaten fehlen belastbare interne Nachweise fuer Source-Origin, Generator/Transformation, Version/Hash, Vor-Paar-Existenz und Pair-Mapping ohne Lag-/Pair-ID-Wertquelle.

## Claim Boundary

Deep Research bleibt Kriterienkontext und Reviewer-Risiko-Kontext. Deep Research ersetzt keine interne Lineage und hebt keinen Kandidaten hoch.

No physical claims are released.

`physical_claim_release=blocked_no_physics_claim`
