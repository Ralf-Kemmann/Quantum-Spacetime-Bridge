# QSB Projektzusammenfassung — Stand 2026-05-07

## Arbeitsmodus

QSB-Ankerverhalten bleibt aktiv: repo-orientiert, transparent, defensiv, keine versteckten Rechnungen, kein hidden code, keine Overclaims. Ergebnisse werden weiterhin strikt getrennt in:

```text
Befund
Interpretation
Hypothese
Offene Lücke
Claim Boundary
```

Standard-Repo:

```bash
/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

Der neue Workflow mit Codex ist als nützlich bestätigt, aber nur mit kurzer Leine:

```text
Nova:
Spezifikation, wissenschaftliche Logik, Claim Boundary, Review, Interpretation

Codex:
lokale Dateien lesen, neue Dateien erzeugen, Skripte/Configs/Docs bauen, Tests ausführen

Ralf:
Freigabe, Terminalkontrolle, Git-Status, letzter Forschungsentscheid
```

Wichtige Codex-Regel:

```text
Create exactly these files.
Do not edit existing files.
Do not touch closed FU02g4c/g5 anchor files.
Do not run git add or git commit.
Show git status.
```

Interne Kurzform:

```text
Codex darf schrauben.
Aber nur am markierten Bauteil.
```

---

## Literaturkontext: Aperiodic / Non-Lattice Spacetime

Aus dem Spektrum-Artikel und Deep Research wurde ein vorsichtiger Literaturkontext abgeleitet.

Kernbefund:

```text
Wir stehen nicht alleine im Nebel.
Es gibt ein reales Literaturfeld für:
nichtgitterartige Diskretheit,
aperiodische Ordnung,
Symmetrie ohne Periodengitter,
geometrische Lesbarkeit aus diskreten Strukturen.
```

Wichtige Abgrenzung:

```text
QSB ist kein Spacetime-Quasicrystal-Modell.
QSB ist methodisch benachbart zu nichtgitterartiger, aperiodischer,
symmetrie-kontrollierter diskreter Struktur.
```

Erzeugte Kontextdatei:

```text
docs/QSB_APERIODIC_NONLATTICE_CONTEXT_NOTE.md
```

Claim Boundary:

```text
Literatur ist Geländer, nicht Krone.
```

---

## FU02g4c / FU02g4d Abschlussanker

Bisheriger Abschlussbefund bleibt:

```text
exact match found
exact match localized
exact match photographed
exact match automorphic to reference
```

Primary-audited coverage:

```text
0 → 26,784,196 connected 17er-Patches
```

Aggregate raw counts:

```text
raw_carrier_signature_exact_match_count = 42
raw_carrier_signature_near_match_count  = 272
raw_role_colored_signature_exact_match_count = 1
raw_role_colored_signature_near_match_count  = 11
```

Bekannter raw role-colored exact match:

```text
raw_index / skip_first_raw_patches = 26,187,175
```

Fotografierter Patch:

```text
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Saubere Lesart:

```text
Der einzige bisher beobachtete raw role-colored exact match in der primary-audited Coverage
wurde lokalisiert, fotografiert und als automorph zur FU02f1-Referenz identifiziert.
```

Interne Kurzform:

```text
Der Klunker war kein fremder Kristall.
Es war unser eigener Klunker im Spiegelkabinett.
```

Nicht behaupten:

```text
zweiter unabhängiger Klunker gefunden
globale Einzigartigkeit bewiesen
physikalische Emergenz gezeigt
```

---

## FU02g5 — Role-Assignment Sensitivity Controls

FU02g5 testete die direkte Rollenvarianten-Stabilität zwischen:

```text
FU02f1 reference carrier
vs.
localized FU02g4c automorphic exact patch
```

Varianten:

```text
v0_type_preferred
uncolored_carrier_only
face_type_only
swap_core_boundary
core_erased
boundary_erased
```

Befund:

```text
localized_candidate_exact_match = True
localized_candidate_near_distance = 0
localized_candidate_near_match = True
```

für alle sechs Varianten.

Technische Reparaturen im FU02g5-Runner:

```text
1. full_face_graph_edges_csv auf reparierten FU02d1-Face-Adjacency-Graph gesetzt.
2. read_edge_csv liest korrekt face_a / face_b.
3. C60-Face-Graph geprüft: 32 Knoten, 90 Kanten, connected.
4. falsche Frontier-Pruning-Regel im connected_k_subgraphs-Generator entfernt.
5. partial_run-Semantik korrigiert.
6. stop_reason ins CSV-Readout aufgenommen.
```

---

## FU02g5b — First-500 Enumeration Smoke

Output:

```text
runs/BMS-FU02g5b/first500_enumeration_smoke/
```

Finaler Readout:

```text
enumerated_patch_count = 500
enumerated_exact_match_count = 0
enumerated_near_match_count = 0
partial_run = False
stop_reason = max_count_reached
```

für alle sechs Varianten.

Direkt sauber interpretierbar:

```text
uncolored_carrier_only
face_type_only
```

Dort:

```text
500 Patches
0 exact
0 near
0 warnings
stop_reason = max_count_reached
```

Interpretation:

```text
FU02g5b bestätigt, dass der reparierte Scaffold-Enumerator kleine deterministische
connected-17-Face-Patchfenster auf dem C60-Face-Graph verarbeitet.
In den ersten 500 Patches wurden unter den direkt interpretierbaren Varianten
keine exact oder near matches gefunden.
```

---

## Patch-Adjazenzliste

Für den lokalisierten FU02g4c-Patch wurde eine echte Nachbarschaftsliste aus dem reparierten C60-Face-Graph gezogen.

Output:

```text
runs/BMS-FU02g5b/first500_enumeration_smoke/exact_patch_adjacency_list.md
runs/BMS-FU02g5b/first500_enumeration_smoke/exact_patch_adjacency_list.csv
```

Visualisierungsregel:

```text
Node-Liste allein reicht nicht.
Eine strukturell korrekte Grafik muss die echte Adjazenzliste respektieren.
```

Bildlesart:

```text
PM-/Cover-Bild:
ästhetisch stark, aber methodisch riskant.

Dualgraph-Schema:
nüchterner, aber näher an Theorie und Face-Adjacency-Graph.
```

Interne Kurzform:

```text
Bild 1 ist der Trailer.
Bild 2 ist das Laborbuch.
```

---

## FU02g5c — Role-Transport Rule Specification

Erzeugte Datei:

```text
docs/BMS_FU02G5C_ROLE_TRANSPORT_RULE_SPEC.md
```

Zweck:

```text
Festlegen, wie mixed_core / pentagon_boundary Rollen auf beliebige connected
17-Face-Patches übertragen werden dürfen oder nicht.
```

Eingefrorene Regel:

```text
Primary arbitrary-patch enumeration:
use uncolored_carrier_only and face_type_only.

Role transport:
allowed only under explicit automorphy/isomorphism mapping.

Local structural role rules:
future work only, not accepted for current primary claims.
```

Interne Kurzform:

```text
Keine Etiketten auf fremde Klunker kleben.
Nur Spiegelklunker dürfen Referenzetiketten tragen.
```

---

## FU02g5d — Automorphy-Only Role Transport Check

Codex erzeugte sauber:

```text
docs/BMS_FU02G5D_AUTOMORPHY_ONLY_ROLE_TRANSPORT_FIELD_LIST.md
data/bms_fu02g5d_automorphy_only_role_transport_config.yaml
scripts/run_bms_fu02g5d_automorphy_only_role_transport.py
```

Output:

```text
runs/BMS-FU02g5d/automorphy_only_role_transport/
```

Befund:

```text
mapping_count = 1
transport_allowed = true
mixed_core_invariant_across_mappings = True
pentagon_boundary_invariant_across_mappings = True
```

Transportierte Kandidatenrollen:

```text
candidate mixed_core:
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09

candidate pentagon_boundary:
H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Interpretation:

```text
Der lokalisierte FU02g4c-Kandidat ist nicht bloß per Konvention role-colored.
Seine Rollen können durch das eindeutige face-type-preserving Mapping
von der FU02f1-Referenz transportiert werden.
```

Erzeugte Result Note:

```text
docs/BMS_FU02G5D_AUTOMORPHY_ONLY_ROLE_TRANSPORT_RESULT_NOTE.md
```

Interne Kurzform:

```text
Nur Spiegelklunker dürfen Referenzetiketten tragen.
Dieser Spiegelklunker trägt sie eindeutig.
```

---

## FU02g5e1 — Near-Match Candidate Localization / Photo

Ziel:

```text
Die 11 raw role-colored near matches aus FU02g4c lokalisieren/fotografieren.
```

Vorherige Log-Landkarte:

```text
2,000,000–2,999,999      → 3 near matches
18,000,000–18,999,999    → 1 near match
26,000,000–26,999,999    → 7 near matches
```

Codex erzeugte sauber:

```text
docs/BMS_FU02G5E1_NEAR_MATCH_LOCALIZATION_FIELD_LIST.md
data/bms_fu02g5e1_near_match_localization_config.yaml
scripts/inspect_bms_fu02g5e1_near_match_candidates.py
```

Output:

```text
runs/BMS-FU02g5e1/near_match_localization/
```

Wichtige Run-Bremse:

```text
Run label: scaffold localization
fu02g4c_order_guarantee = False
```

Befund:

```text
near_match_candidate_count = 11
exact_match_count = 1
max_raw_index_visited = 26784197
```

Interpretation:

```text
Die 11 Near-Kandidaten wurden als Kandidaten-Foto-Set lokalisiert.
Da die exakte FU02g4c-Replay-Order nicht garantiert ist,
sind die Rohindizes Scaffold-Enumerator-Indizes und noch keine final zertifizierten
FU02g4c-Raw-Indizes.
```

Kandidatenverteilung:

```text
early_2m_3m                  3 near, 0 exact
mid_17987055_18925223        1 near, 0 exact
exact_zone_25979015_26784197 7 near, 1 exact
```

Bekannter exact Spiegelklunker:

```text
raw_index = 26187175
exact_match = True
near_distance = 0
nodes =
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Alle 11 Kandidaten teilen das grobe Carrier-Profil:

```text
n = 17
H = 12
P = 5
candidate_connected = True
internal_edge_count = 37
nbtype = {"hexagon": 10, "pentagon": 13}
```

Near-Kandidaten-Kategorien aus g5e1:

```text
1 exact Spiegelklunker:
26187175, exact=True, near_distance=0

1 coarse-distance-0 non-exact candidate:
26157530, exact=False, near_distance=0

2 distance-1 near candidates:
26161006
26167866

7 distance-2 near candidates:
2338804
2338805
2839553
18575893
26157529
26187327
26328307
```

Wichtige Interpretation:

```text
Die Near-Kandidaten sind nicht bloß wildes Rauschen.
Sie teilen ein stark ähnliches grobes Carrier-Profil,
unterscheiden sich aber in feineren Signaturmerkmalen.
```

Offene Lücke:

```text
FU02g4c raw-order certification bleibt offen.
g5e1 ist ein Scaffold-Foto-Set, kein finaler FU02g4c-Replay-Audit.
```

---

## Aktueller wissenschaftlicher Status

Die FU02-Kette lautet jetzt:

```text
FU02g4c/g4d:
exact match found, localized, photographed, automorphic to reference.

FU02g5:
direct role-assignment sensitivity test stable across configured variants.

FU02g5b:
scaffold enumerator repaired; first 500 window clean; no exact/near in directly interpretable modes.

FU02g5c:
role-transport rule frozen defensively:
no transport except under explicit automorphy/isomorphism.

FU02g5d:
localized exact candidate passes automorphy-only role transport with mapping_count = 1;
transported role sets are unique.

FU02g5e1:
11 near-match candidates photographed in scaffold localization;
1 exact Spiegelklunker, 10 near-decoys pending classification.
```

---

## Nächster sinnvoller Block

```text
BMS-FU02g5e2 — Near-Match Decoy Classification
```

Ziel:

```text
Für jeden der 11 g5e1-Kandidaten prüfen:
1. uncolored isomorphic to reference?
2. face-type-preserving isomorphic to reference?
3. mapping_count?
4. role_transport_allowed?
5. transported roles invariant?
6. Klassifikation:
   - known_exact_spiegelklunker
   - automorphic_reference_twin
   - coarse_signature_twin_but_not_exact
   - local_near_decoy_distance_1
   - near_decoy_distance_2
   - non_transportable_near_candidate
   - scaffold_only_candidate_pending_fu02g4c_replay_validation
```

Wissenschaftliche Erwartung:

```text
Die Near-Wolke teilt grobe Carrier-Merkmale.
Nur der exact Spiegelklunker trägt Referenzrollen zulässig,
falls die übrigen Kandidaten nicht face-type-preserving isomorphic zur Referenz sind.
```

---

## Git-/Repo-Hygiene

Altes Repo `debroglie-phase-bridge` wurde bereinigt:

```text
git restore debroglie-phase-bridge
lokale venv/cache/helper files in .git/info/exclude
kaputter Ordner '-' als Duplikat-/Umzugsartefakt identifiziert/entfernt
typ_b_analysis lokal behalten und aus Git-Warnung genommen
```

Finaler Status:

```text
Auf Branch master
nichts zu committen, Arbeitsverzeichnis unverändert
```

Neues QSB-Repo hat viele untracked Projektartefakte aus FU02g1–g5. Diese sind nicht automatisch Fehler. Wichtig bleibt:

```text
kein git add .
kein blindes Löschen
gezielt adden/committen nach Blockabschluss
```

---

## Offene Lücken

```text
1. FU02g5e2 Near-Match Decoy Classification.
2. FU02g4c raw-order certification für die g5e1 Scaffold-Kandidaten.
3. Near-exact role-colored Decoys außerhalb der Automorphieklasse sauber prüfen.
4. Local structural role rule bleibt future work, nicht primär akzeptiert.
5. Externe Fullerene-/Planar-/Sphären-Graphkontrollen als FU03a.
6. Größere FU02g5b/g5e Fenster erst nach klarer Klassifikationslogik.
7. Keine physikalische Dynamik-, Lorentz- oder Raumzeit-Emergenzbehauptung aus FU02 ableiten.
```

---

## Aktueller Claim-Stand

Erlaubt:

```text
The localized FU02g4c exact candidate is automorphic to the FU02f1 reference carrier.
```

Erlaubt:

```text
Under automorphy-only role transport, this candidate admits exactly one
face-type-preserving mapping and receives unique transported mixed_core and
pentagon_boundary role sets.
```

Erlaubt:

```text
BMS-FU02g5e1 provides a scaffold-localization inventory of 11 role-colored
near-match candidates, including the known exact candidate, but does not yet
certify exact FU02g4c replay order.
```

Nicht erlaubt:

```text
global uniqueness
global rarity proof
physical emergence
Lorentz compatibility
spacetime dynamics
QSB = spacetime quasicrystal
all near matches are real FU02g4c replay candidates without certification
non-isomorphic patches may receive reference roles by analogy
```

---

## Interner Stand in Bildern

```text
Der Spiegelklunker ist sauber identifiziert.
Seine Etiketten kommen vom eindeutigen Spiegelmapping.
Die falschen Klunker liegen jetzt auf dem Tisch.
Ob sie Spiegel, Glas oder echte Steine sind, entscheidet g5e2.
```

Tagesabschluss:

```text
Klunker fotografiert.
Rollenbrille geprüft.
Etikettenregel eingefroren.
Spiegelklunker eindeutig etikettiert.
Near-Klunker aus dem Keller geholt.
Codex als Schrauber brauchbar, aber nur mit kurzer Leine.
```
