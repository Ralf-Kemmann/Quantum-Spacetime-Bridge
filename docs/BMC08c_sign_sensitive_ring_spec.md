# BMC-08c – Sign-sensitive Ring (Spezifikation)

## Status
Spezifikationsschritt vor Implementierung.

## Zweck
BMC-08c prüft, ob der in BMC-08a beobachtete und in BMC-08b kollabierte Effekt
durch **Informationsverlust im Ring-Featuremapping** verursacht wurde.

Kernidee:
- BMC-08a war **sign-blind** im Ringblock (`p` und `-p` wurden auf identische Featurevektoren abgebildet)
- BMC-08b entfernte die Spiegelpartner vollständig
- BMC-08c soll stattdessen die **Richtungsinformation erhalten**, ohne die Ringfamilie künstlich zu verdoppeln oder Artefakte zu erzeugen

## Ausgangspunkt

### Letzter belastbarer Befund
- BMC-08a: `off_backbone_result_robust`
- BMC-08b: nach Entfernung der Ring-Spiegelsymmetrie nur noch `still_weak_or_mixed`

### Projektinterne Lesart
Der robuste Off-Backbone-Befund aus BMC-08a war **nicht robust** gegen kontrollierte Veränderung
der Ring-Symmetriebehandlung.

### Offene Kernfrage
War das Problem:
1. **Spiegeldegenerazie** durch identische Ring-Featurevektoren,
oder
2. der völlige **Informationsverlust** durch Wegwerfen der negativen Ringzustände?

BMC-08c adressiert genau diese Frage.

## Prinzip

### Konstant zu halten
- dieselben Cavity-Moden
- dieselben Membran-Moden
- dieselbe BMC-08-Variantenlogik
- dieselben fairen Backbone-Basisvarianten
- dieselbe offene Build- und Run-Architektur

### Kontrolliert zu ändern
Nur die Ring-Featuredefinition.

## BMC-08a vs BMC-08b vs BMC-08c

### BMC-08a
- Ringzustände: `p = -3,-2,-1,1,2,3`
- ringbezogene Features sign-blind
- `p` und `-p` werden identisch

### BMC-08b
- Ringzustände spiegelreduziert
- nur `p > 0`
- keine Signalinformation mehr

### BMC-08c
- Ringzustände bleiben vollständig erhalten:
  - `p = -3,-2,-1,1,2,3`
- aber die Ring-Featurebasis wird **sign-sensitive**

## Konkrete Mappingregel für den Ringblock

## Beibehaltete Ringknoten
Für BMC-08c bleiben die Knoten:
- `ring_p_-3`
- `ring_p_-2`
- `ring_p_-1`
- `ring_p_1`
- `ring_p_2`
- `ring_p_3`

## Sign-sensitive Startregel

### R-F1 – `feature_mode_frequency`
Nicht mehr:
- `p^2 / 2`

sondern:
- `feature_mode_frequency = p`

Begründung:
- erhält die Richtungsinformation direkt
- bleibt offen und klein
- vermeidet die Spiegelidentität von `p` und `-p`

### R-F2 – `feature_length_scale`
Beibehalten:
- `feature_length_scale = 1 / |p|`

Begründung:
- Größen-/Skaleninformation bleibt unabhängig vom Vorzeichen lesbar
- keine unnötige neue Modellkomplexität

### R-F3 – `feature_spectral_index`
Beibehalten als Rang von `|p|`:
- `|p| = 1 -> 1`
- `|p| = 2 -> 2`
- `|p| = 3 -> 3`

Begründung:
- offen
- klein
- keine neue Readout-Nähe

### R-F4 – `feature_shape_factor`
Beibehalten:
- `feature_shape_factor = 1.0`

Begründung:
- keine versteckte Geometrie in den Ringblock einschmuggeln

## Warum `feature_mode_frequency = p` und nicht `sign(p) * p^2 / 2`?
Für Version 1 von BMC-08c wird die **einfachere** Regel bevorzugt:

- `p` ist direkter
- weniger konstruiert
- behält Vorzeicheninformation ohne zusätzliche nichtlineare Verzerrung

Die Variante
- `sign(p) * p^2 / 2`
kann später als BMC-08c.1 oder Sensitivitätsvariante geprüft werden, aber nicht im ersten Schritt.

## Erwartungen

### Fall A – Off-Backbone kehrt robust zurück
Dann war in BMC-08b vor allem das Wegwerfen der Richtungsinformation problematisch.

### Fall B – Ergebnis bleibt weak/mixed
Dann war der ursprüngliche BMC-08a-Effekt vor allem ein Symmetrie-/Homogenitätsartefakt und nicht durch einfache Sign-Information rettbar.

### Fall C – Neues Bild (z. B. Coupling oder Backbone)
Dann trägt die Richtungsinformation echte neue Struktur.

## Zu ändernde Dateien

### Neu
- `scripts/build_bmc08c_feature_table_from_m39x1_sign_sensitive_ring.py`
- `data/bmc08c_m39x1_sign_sensitive_ring_config.yaml`
- `data/bmc08c_realdata_config.yaml`
- `scripts/run_bmc08c_realdata_open.sh`

### Wiederverwendet
- `scripts/build_bmc08a_realdata_inputs.py`
- `scripts/bmc07_backbone_variation_runner.py`

## Backbone-Varianten
Weiterhin nur faire Basisvarianten:
- `strength_topk_6`
- `strength_topalpha_025`
- `strength_topalpha_050`

## Outputvertrag
Wie bei BMC-08a/BMC-08b:
- `runs/BMC-08/BMC08c_realdata_open/readout.md`
- `runs/BMC-08/BMC08c_realdata_open/backbone_variant_summary.csv`
- `runs/BMC-08/BMC08c_realdata_open/summary.json`

## Befund
Noch keiner. Diese Datei ist reine Spezifikation.

## Interpretation
BMC-08c ist ein kontrollierter Informationserhaltungstest:
nicht Symmetrie entfernen, sondern Richtungsinformation offen behalten.

## Hypothese
Wenn die Richtungsinformation physikalisch relevant ist, sollte BMC-08c informativer sein als BMC-08b,
ohne die offensichtliche Spiegeldegenerazie von BMC-08a zu reproduzieren.

## Offene Lücke
Noch fehlen:
- Implementierung des neuen Ring-Featuretable-Scripts
- Realdaten-Config
- Run-Script
- danach der Kontrolllauf
