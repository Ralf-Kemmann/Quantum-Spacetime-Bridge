# QSB Chat-Umzug — BMS-FU02g4c Abschlussstand / Übergang zu FU02g5

Datum: 2026-05-06  
Projekt: Quantum–Spacetime Bridge / Gravitation und RaumZeit  
Arbeitsmodus: intern, repo-orientiert, wissenschaftlich defensiv

## 1. Repo-Kontext

Standard-Repo-Root:

```bash
/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

Strukturregeln:

```text
docs/     Spezifikationen, Result Notes, Feldlisten
data/     Configs, Inputs, CSV/JSON/YAML-Artefakte
scripts/  ausführbare Skripte
runs/     Run Outputs
```

Arbeitsregeln:

- Keine versteckten Rechnungen, keine versteckten Dateien, kein hidden code.
- Befund, Interpretation, Hypothese und offene Lücke strikt trennen.
- Keine Overclaims.
- Bei langen Inhalten vollständige Dateien mit Downloadlink und konkretem `cp`-Befehl liefern.
- Originalrunner nicht hektisch überschreiben; neue Prüf-/Foto-Skripte separat halten.

## 2. Wissenschaftlicher Kontext

Wir untersuchen im aktuellen Toy-/Kontrollrahmen role-colored carrier regions im C60-Face-Graphen.

Kernfrage:

```text
Ist die FU02f1-C60-Carrier-Region lediglich ein generischer connected patch,
oder trägt sie eine ungewöhnlich eingeschränkte role-colored Struktur-Signatur
unter connected-patch-, Nullmodell- und Automorphie-Kontrollen?
```

Der Referenzanker ist materieseitig / carrierseitig motiviert. Der Graph-/Patch-Test fragt anschließend, wie selten oder robust dieser Fingerabdruck im relationalen Patch-Raum ist.

Anschaulich:

```text
Materieseitiger Anker
→ relationaler C60-Face-Graph-Suchraum
→ connected 17er-Patches
→ Signaturvergleich
→ Seltenheit / Automorphie / Decoy-Frage
```

Graph bedeutet hier schlicht:

```text
Fläche des C60-Fußballs = Knoten
Flächen berühren sich   = Kante / Nachbarschaft
```

## 3. FU02f1 Referenzanker

Reference carrier set:

```text
H_07;H_09;H_11;H_12;H_13;H_14;H_15;H_16;H_17;H_18;H_19;H_20;P_07;P_08;P_09;P_10;P_11
```

Mixed core:

```text
H_09;H_11;H_13;H_16;H_17;H_18;H_19;H_20
```

Pentagon boundary:

```text
H_07;H_12;H_14;H_15;P_07;P_08;P_09;P_10;P_11
```

Carrier facts:

```text
carrier_face_count = 17
carrier_hexagon_count = 12
carrier_pentagon_count = 5
carrier_component_count = 1
largest_carrier_component_count = 17
```

Role mapping:

```text
mixed_core        = mixed_seam_boundary_face
pentagon_boundary = hp_boundary_face
```

## 4. FU02g4c / FU02g4d bisherige Lauf- und Audit-Befunde

BMS-FU02g4c ist die orbit-reduced / resumable connected-patch enumeration.

BMS-FU02g4d ist die coverage and log audit Ebene.

Aktueller primary-audited Stand:

```text
primary_interval_start = 0
primary_interval_end_exclusive = 26,784,196
raw_connected_patch_count_processed = 26,784,196
primary_log_count = 28
```

Aggregate raw counts über primary-valid logs:

```text
raw_carrier_signature_exact_match_count = 42
raw_carrier_signature_near_match_count  = 272
raw_role_colored_signature_exact_match_count = 1
raw_role_colored_signature_near_match_count  = 11
```

Wichtig:

```text
Orbit-Klassen werden NICHT global naiv aufsummiert.
Segment-local orbit counts bleiben segment-local.
```

Global primary rate für raw role-colored exact:

```text
1 / 26,784,196 ≈ 3.73 × 10^-8
```

## 5. Einkreisung des role-colored exact Treffers

Der einzige bisher beobachtete raw role-colored exact match wurde über Replay-Fenster lokalisiert.

Einkreisung:

```text
100k-Fenster:  26,179,015 → 26,279,015
10k-Fenster:   26,179,015 → 26,189,015
1k-Fenster:    26,187,015 → 26,188,015
100er-Fenster: 26,187,115 → 26,187,215
10er-Fenster:  26,187,175 → 26,187,185
Einzelfenster: 26,187,175 → 26,187,176
```

Bestätigtes Einzel-Inspection-Log:

```text
runs/BMS-FU02g4c/inspect_window_26187175_26187176.log
```

Einzelkandidat:

```text
chunk_id = inspect_window_26187175_26187176
skip_first_raw_patches = 26,187,175
raw_connected_patch_count_processed = 1
raw_patch_count_seen_including_skipped = 26,187,177
warnings_count = 0
orbit_reduction_enabled_actual = true
automorphism_count_used = 120
raw_carrier_signature_exact_match_count = 1
raw_role_colored_signature_exact_match_count = 1
orbit_carrier_signature_exact_match_class_count = 1
orbit_role_colored_signature_exact_match_class_count = 1
unique_orbit_patch_count_processed = 1
```

Interpretation:

```text
Der role-colored exact Treffer wurde reproduzierbar auf einen einzelnen enumerierten connected 17er-Patch lokalisiert.
```

## 6. Foto-Skript / Patch-Foto

Separates Foto-Skript wurde gebaut, ohne den Originalrunner anzufassen:

```text
scripts/inspect_bms_fu02g4c_single_exact_patch.py
```

Feldliste:

```text
docs/inspect_bms_fu02g4c_single_exact_patch_FIELD_LIST.md
```

Standardziel:

```text
skip_first_raw_patches = 26,187,175
max_raw_patches_this_run = 1
```

Output-Verzeichnis:

```text
runs/BMS-FU02g4c/patch_photos/
```

Erzeugte Outputs:

```text
runs/BMS-FU02g4c/patch_photos/bms_fu02g4c_exact_patch_26187175.json
runs/BMS-FU02g4c/patch_photos/bms_fu02g4c_exact_patch_26187175_nodes.csv
runs/BMS-FU02g4c/patch_photos/bms_fu02g4c_exact_patch_26187175_edges.csv
runs/BMS-FU02g4c/patch_photos/bms_fu02g4c_exact_patch_26187175_result_note.md
runs/BMS-FU02g4c/patch_photos/single_exact_patch_26187175_26187176.yaml
```

## 7. Fotografierter Kandidat

Candidate carriers:

```text
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Candidate mixed_core:

```text
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09
```

Candidate pentagon_boundary:

```text
H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Automorphy result:

```json
{
  "networkx_available": true,
  "note": "Automorphy check compares labeled full face graphs. True means the candidate is automorphic to the FU02f1 reference under the tested labeling.",
  "role_colored_patch_automorphic_to_reference": true,
  "uncolored_patch_automorphic_to_reference": true
}
```

## 8. Wichtigste wissenschaftliche Lesart

Befund:

```text
Der einzige bisher beobachtete raw role-colored exact match in der primary-audited Coverage bis 26,784,196 wurde lokalisiert, fotografiert und als automorph zur FU02f1-Referenz identifiziert.
```

Interpretation:

```text
Der Treffer ist kein neuer, strukturell unabhängiger zweiter Klunker,
sondern ein Symmetrie-Zwilling des FU02f1-Referenzankers im C60-Face-Graphen.
```

Anschaulich:

```text
Der Klunker war kein fremder Kristall.
Es war unser eigener Klunker im Spiegelkabinett.
```

Claim Boundary:

Nicht sagen:

```text
Wir haben einen zweiten unabhängigen role-colored Klunker gefunden.
```

Sauber sagen:

```text
Within the primary-audited connected-patch enumeration, the only observed role-colored exact match was localized to a single patch and identified as automorphic to the FU02f1 reference carrier.
```

## 9. Konsequenz für den nächsten Arbeitsblock

FU02g4c/FU02g4d kann jetzt als methodisch sauberer Abschlussbefund behandelt werden:

```text
exact match found
exact match localized
exact match photographed
exact match automorphic to reference
```

Nächste harte Fragen:

```text
1. Gibt es außerhalb der Automorphieklasse weitere role-colored exact oder near-exact Signaturen?
2. Wie sensitiv ist der Befund gegen die v0-Rollenzuweisung?
3. Ist das Ergebnis C60-spezifisch oder in externen Graphfamilien wiederzufinden?
```

Empfohlener nächster Block:

```text
BMS-FU02g5 — Role-Assignment Sensitivity Controls
```

Danach:

```text
BMS-FU03a — externe Fullerene-/Planargraph-Kontrollen
```

## 10. Nächster Start im neuen Chat

Im neuen Chat direkt weiter mit:

```text
Wir haben FU02g4c/FU02g4d abgeschlossen: Der einzige role-colored exact match wurde auf skip_first_raw_patches=26,187,175 lokalisiert, fotografiert und als automorph zur FU02f1-Referenz identifiziert. Jetzt bitte den nächsten Block FU02g5 Role-Assignment Sensitivity Controls spezifizieren: Ziel, Claim Boundary, Inputs, Outputs, Feldliste, Run-Design, defensive Result-Note-Struktur.
```
