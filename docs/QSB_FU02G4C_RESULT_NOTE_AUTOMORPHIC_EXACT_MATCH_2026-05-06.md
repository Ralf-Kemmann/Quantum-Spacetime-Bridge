# Result Note — BMS-FU02g4c/FU02g4d Automorphic Exact Match

Datum: 2026-05-06

## Befund

In der primary-audited connected-patch enumeration wurde bis `primary_interval_end_exclusive = 26,784,196` genau ein raw role-colored exact match beobachtet.

Aggregate primary raw counts:

```text
raw_connected_patch_count_processed = 26,784,196
raw_carrier_signature_exact_match_count = 42
raw_carrier_signature_near_match_count = 272
raw_role_colored_signature_exact_match_count = 1
raw_role_colored_signature_near_match_count = 11
```

Der exact role-colored Treffer wurde über Replay-Fenster lokalisiert:

```text
100k → 10k → 1k → 100er → 10er → Einzelpatch
```

Finales Einzelfenster:

```text
inspect_window_26187175_26187176
skip_first_raw_patches = 26,187,175
raw_connected_patch_count_processed = 1
warnings_count = 0
orbit_reduction_enabled_actual = true
automorphism_count_used = 120
raw_role_colored_signature_exact_match_count = 1
orbit_role_colored_signature_exact_match_class_count = 1
```

## Foto / Patch-Identität

Fotografierter Patch:

```text
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Mixed core:

```text
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09
```

Pentagon boundary:

```text
H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Automorphy:

```json
{
  "networkx_available": true,
  "role_colored_patch_automorphic_to_reference": true,
  "uncolored_patch_automorphic_to_reference": true
}
```

## Interpretation

Der beobachtete exact role-colored Treffer ist kein neuer, strukturell unabhängiger Signatur-Decoy, sondern ein automorpher Symmetrie-Zwilling der FU02f1-Referenz im C60-Face-Graphen.

Anschaulich:

```text
Der Klunker war kein fremder Kristall.
Es war der Referenzklunker im Spiegelkabinett der C60-Symmetrie.
```

## Claim Boundary

Nicht behaupten:

```text
Es wurde ein zweiter unabhängiger role-colored Klunker gefunden.
```

Sauber behaupten:

```text
Within the primary-audited connected-patch enumeration, the only observed role-colored exact match was localized to a single patch and identified as automorphic to the FU02f1 reference carrier.
```

## Offene Lücken

1. Role-assignment sensitivity ist noch nicht getestet.
2. Near-exact role-colored Treffer außerhalb der Automorphieklasse müssen separat geprüft werden.
3. C60-Spezifität ist offen; externe Fullerene-/Planargraph-Kontrollen stehen aus.
4. Keine Aussage über physikalische Dynamik oder Entstehung; der Befund ist kombinatorisch-methodisch.

## Nächster Block

```text
BMS-FU02g5 — Role-Assignment Sensitivity Controls
```
