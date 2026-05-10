# Neuer Chat Startprompt — QSB / Übergang FU02g4c → FU02g5

Wir arbeiten im Projekt **Quantum–Spacetime Bridge / Gravitation und RaumZeit**. Bitte im Stil eines vorsichtigen theoretischen Physik-Kollaborators arbeiten: deutsch, anschaulich, repo-orientiert, defensiv, ohne Hype. Keine versteckten Rechnungen, keine versteckten Dateien, kein hidden code. Befund / Interpretation / Hypothese / offene Lücke strikt trennen.

Repo-Root:

```bash
/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

Repo-Struktur strikt respektieren:

```text
docs/     Spezifikationen, Result Notes, Feldlisten
data/     Configs, Inputs, CSV/JSON/YAML-Artefakte
scripts/  ausführbare Skripte
runs/     Run Outputs
```

Keine Fantasieordner. Lange Inhalte als Dateien mit Downloadlink und konkretem `cp`-Befehl. Keine Overclaims.

## Projektkontext

Der Referenzanker ist materieseitig / carrierseitig motiviert. Im C60-Face-Graphen testen wir connected 17er-Patches auf Signaturübereinstimmung mit der FU02f1-Carrier-Region.

Graph bedeutet hier: C60-Fläche = Knoten, gemeinsame Kante zwischen Flächen = Graphkante.

FU02f1 Reference carrier:

```text
H_07;H_09;H_11;H_12;H_13;H_14;H_15;H_16;H_17;H_18;H_19;H_20;P_07;P_08;P_09;P_10;P_11
```

Reference mixed_core:

```text
H_09;H_11;H_13;H_16;H_17;H_18;H_19;H_20
```

Reference pentagon_boundary:

```text
H_07;H_12;H_14;H_15;P_07;P_08;P_09;P_10;P_11
```

## Abgeschlossener Stand FU02g4c/FU02g4d

Primary-audited coverage:

```text
0 → 26,784,196 connected 17er-Patches
```

Aggregate raw counts over primary-valid logs:

```text
raw_carrier_exact = 42
raw_carrier_near  = 272
raw_role_colored_exact = 1
raw_role_colored_near  = 11
```

Wichtig: Orbit-class counts bleiben segment-local und werden nicht global naiv aufsummiert.

Der einzige raw role-colored exact match wurde durch Replay lokalisiert:

```text
100k-Fenster:  26,179,015 → 26,279,015
10k-Fenster:   26,179,015 → 26,189,015
1k-Fenster:    26,187,015 → 26,188,015
100er-Fenster: 26,187,115 → 26,187,215
10er-Fenster:  26,187,175 → 26,187,185
Einzelfenster: 26,187,175 → 26,187,176
```

Einzelkandidat:

```text
skip_first_raw_patches = 26,187,175
raw_connected_patch_count_processed = 1
warnings_count = 0
orbit_reduction_enabled_actual = true
automorphism_count_used = 120
raw_role_colored_signature_exact_match_count = 1
orbit_role_colored_signature_exact_match_class_count = 1
```

Patch-Foto wurde erzeugt mit:

```text
scripts/inspect_bms_fu02g4c_single_exact_patch.py
```

Outputs:

```text
runs/BMS-FU02g4c/patch_photos/bms_fu02g4c_exact_patch_26187175.json
runs/BMS-FU02g4c/patch_photos/bms_fu02g4c_exact_patch_26187175_nodes.csv
runs/BMS-FU02g4c/patch_photos/bms_fu02g4c_exact_patch_26187175_edges.csv
runs/BMS-FU02g4c/patch_photos/bms_fu02g4c_exact_patch_26187175_result_note.md
runs/BMS-FU02g4c/patch_photos/single_exact_patch_26187175_26187176.yaml
```

Fotografierter Kandidat:

```text
candidate carriers:
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07

candidate mixed_core:
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09

candidate pentagon_boundary:
H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Automorphy result:

```json
{
  "networkx_available": true,
  "role_colored_patch_automorphic_to_reference": true,
  "uncolored_patch_automorphic_to_reference": true
}
```

## Saubere Lesart

Befund:

```text
Der einzige bisher beobachtete raw role-colored exact match in der primary-audited Coverage bis 26,784,196 wurde lokalisiert, fotografiert und als automorph zur FU02f1-Referenz identifiziert.
```

Interpretation:

```text
Der Treffer ist kein neuer, strukturell unabhängiger zweiter Klunker,
sondern ein Symmetrie-Zwilling des FU02f1-Referenzankers im C60-Face-Graphen.
```

Nicht sagen:

```text
Wir haben einen zweiten unabhängigen role-colored Klunker gefunden.
```

Sauberer Claim:

```text
Within the primary-audited connected-patch enumeration, the only observed role-colored exact match was localized to a single patch and identified as automorphic to the FU02f1 reference carrier.
```

## Nächste Aufgabe im neuen Chat

Bitte jetzt den nächsten Arbeitsblock spezifizieren:

```text
BMS-FU02g5 — Role-Assignment Sensitivity Controls
```

Gewünschte Outputs:

```text
1. docs/BMS_FU02G5_ROLE_ASSIGNMENT_SENSITIVITY_SPEC.md
2. docs/BMS_FU02G5_ROLE_ASSIGNMENT_SENSITIVITY_FIELD_LIST.md
3. data/bms_fu02g5_role_assignment_sensitivity_config.yaml
4. scripts/run_bms_fu02g5_role_assignment_sensitivity.py
```

Ziel von FU02g5:

```text
Prüfen, ob die role-colored exact/near Befunde robust gegen Varianten der Rollenzuweisung sind
oder wesentlich von der v0 type_preferred_role_assignment abhängen.
```

Claim Boundary:

```text
FU02g5 darf keine physikalische Entstehung behaupten.
Es prüft nur die Sensitivität eines Signaturbefunds gegen Rollenzuweisungsregeln im C60-Face-Graph-Kontrollraum.
```
