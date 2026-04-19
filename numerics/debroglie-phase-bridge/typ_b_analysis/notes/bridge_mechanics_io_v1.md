# bridge_mechanics_io_v1

## 1. Ziel

Diese I/O-Spezifikation legt fest, welche Inputs das Mechanikmodell der de-Broglie-Brücke benötigt, welche internen Zustandsgrößen es erzeugt und welche testbaren Outputs daraus folgen müssen.

`bridge_mechanics_io_v1` erweitert das Minimalmodell der Brücke um eine explizite Mechanikschicht:
Nicht nur `A`, `theta`, `phi_geom` und `d_eff` benennen, sondern systematisch abbilden, wie Kopplungsformen zwischen `theta` und `A` den Brückenzustand verändern, stabilisieren oder verschlechtern.

Leitfrage:

> Welche minimale Kopplungsmechanik zwischen interferenzieller Struktur (`theta`) und geometrienahem Proxy (`A`) erzeugt einen stabilen, kontrollierten und geometrie-kompatiblen Brückenzustand?

---

## 2. Input-Schicht

### 2.1 Pflicht-Inputs

`BridgeMechanicsInput` enthält mindestens:

- `run_id`
- `dataset_id`
- `export_class`
- `matrices`
  - `K`
  - `Kbar`
  - `G`
- `graph_data`
  - adjacency
  - edge weights
  - optional edge lengths
  - optional `d_rel`
- `pair_units` optional
- `regime`
  - `macro`
  - `coherent`
  - `mixed`
- `parameters`
  - `tau`
  - `coarse_grain_strength`
  - `adapter_mode`
  - `score_field`
  - `a_theta_coupling`
  - `coupling_mode`
  - `lambda`
  - optional `theta_transform`
  - optional `normalization_mode`

### 2.2 Minimaler Default-Input

Für erste Läufe soll die aktuell brauchbare kleine N1-Basis verwendet werden:

- `adapter_mode = adjacency_plus_threshold`
- `score_field = G`
- `tau = 0.025`
- `export_class in {negative, abs, positive}`
- `regime in {macro, coherent}`

### 2.3 Kleine Sweep-Inputs

Der Runner darf zusätzlich kleine kontrollierte Sweeps unterstützen:

- `lambda_values = [0.0, 0.05, 0.10, 0.20]`
- `coupling_modes in {additive, multiplicative, regime_gated, dual_channel}`
- optional kleine Variation von `tau`

Wichtig:
Die erste Serie soll klein und diszipliniert bleiben. Keine Grid-Explosion.

---

## 3. Interne Zustandsgrößen

### 3.1 Basiskomponenten

- `A0`
  - ungekoppelter coarse-grained Kohärenz-/Amplitudenproxy
- `theta0`
  - ungekoppelter Phasen-/Interferenzproxy

### 3.2 Mechanikkomponenten

- `A_eff`
  - effektiver, durch Kopplung modulierter Kohärenzproxy
- optional `A_bind`
  - bindungs-/stabilisierungsnaher Kanal
- optional `B_info`
  - informations-/übergangsnaher Kanal
- `C_mech`
  - dokumentierte Kopplungsabbildung
- `coupling_regime_label`
  - Kennzeichnung des aktiven Kopplungsregimes

### 3.3 Geometrienahe Projektion

- `phi_geom`
  - geometrienahe Projektion aus `A_eff` bzw. `A_bind`
- `d_eff`
  - effektiver Distanzkandidat

---

## 4. Zulässige Kopplungsmodi

### 4.1 `additive`

Form:
`A_eff = A0 + lambda * F(theta0)`

Lesart:
`theta0` liefert einen zusätzlichen Strukturbeitrag.

### 4.2 `multiplicative`

Form:
`A_eff = A0 * (1 + lambda * F(theta0))`

Lesart:
`theta0` moduliert vorhandene Kohärenz.

### 4.3 `regime_gated`

Form:
`A_eff = A0 * M(theta0, regime, tau, lambda)`

Lesart:
Kopplung hängt explizit vom Regime ab.

### 4.4 `competitive`

Form:
`A_eff = H(A0, theta0, lambda)`

Lesart:
Zu starke Interferenz kann geometrische Lesbarkeit auch stören.

### 4.5 `dual_channel`

Form:
- `A_bind = H1(A0, theta0, lambda)`
- `B_info = H2(A0, theta0, lambda)`

Lesart:
Bindung/Stabilisierung und Informations-/Übergangsstruktur werden explizit getrennt verfolgt.

---

## 5. Verarbeitungsschritte

### Schritt 1: Input Normalization

- Vollständigkeit der Pflicht-Inputs prüfen
- Matrixformen prüfen
- Graph- und PairUnit-Konsistenz prüfen
- numerische Stabilität prüfen
- Normalisierung anwenden

### Schritt 2: Basiskonstruktion

- `A0` aus coarse-grained strukturtragender Information erzeugen
- `theta0` aus phasen-/interferenzsensitiver Information erzeugen

### Schritt 3: Kopplungsanwendung

- `coupling_mode` auswählen
- `lambda` anwenden
- `A_eff` berechnen
- bei `dual_channel` zusätzlich `A_bind` und `B_info` berechnen

### Schritt 4: Geometrieprojektion

- `A_eff -> phi_geom`
- `phi_geom -> d_eff`

### Schritt 5: Diagnostik

- Stabilität
- Phaseneinfluss
- Bindungskanal
- Informationskanal
- Geometrie-Lesbarkeit
- Delta gegen Baseline

### Schritt 6: Vergleich

- gegen ungekoppelten Baseline-Zustand
- zwischen `negative`, `abs`, `positive`
- zwischen `macro`, `coherent`, optional `mixed`

### Schritt 7: Claims-Readout

- Kurzentscheidungen erzeugen
- tragfähige vs. unbrauchbare Kopplungsformen markieren
- Geometry-Response festhalten

---

## 6. Output-Schicht

`BridgeMechanicsOutput` enthält mindestens:

- `run_id`
- `dataset_id`
- `export_class`
- `regime`
- `coupling_mode`
- `lambda`
- `state_fields`
  - `A0`
  - `theta0`
  - `A_eff`
  - optional `A_bind`
  - optional `B_info`
  - `phi_geom`
- `effective_structure`
  - `d_eff`
  - neighborhoods
  - graph_proxy
- `diagnostics`
  - `phase_influence_score`
  - `structure_stability_score`
  - `binding_channel_score`
  - `information_channel_score`
  - `geometry_readability_score`
  - `delta_vs_baseline`
  - optional `regime_response_score`
- `claim_readout`
- `testable_claims_ready`

---

## 7. Pflicht-Diagnostiken

### 7.1 `phase_influence_score`

Wie stark verändert `theta0` den Basiskanal?

### 7.2 `structure_stability_score`

Bleibt der Brückenzustand unter kleiner Parameteränderung stabil?

### 7.3 `binding_channel_score`

Wie stark unterstützt die Kopplung geometrienahe Bindung/Stabilisierung?

### 7.4 `information_channel_score`

Wie stark zeigt sich ein separater Informations-/Übergangskanal?

### 7.5 `geometry_readability_score`

Wird `phi_geom` bzw. `d_eff` unter Kopplung geometrisch lesbarer oder unlesbarer?

### 7.6 `delta_vs_baseline`

Verbessert oder verschlechtert die Kopplung den ungekoppelten Zustand?

### 7.7 `coupling_selectivity_score` optional

Wie selektiv reagiert die Kopplung über Exportklassen und Regime hinweg?

---

## 8. Pflicht-Dateioutputs

Der Runner schreibt mindestens:

- `bridge_mechanics_state.json`
- `bridge_mechanics_readout.md`
- `bridge_mechanics_claims.json`
- `bridge_mechanics_coupling_scan.csv`

Optional zusätzlich:

- `bridge_mechanics_summary.json`
- `bridge_mechanics_geometry_probe.json`

---

## 9. Minimaler Erfolg

Die I/O-Spezifikation ist gelungen, wenn sie ermöglicht:

1. aus vorhandenen Projektinputs ein kleines Mechanikmodell zu instanziieren
2. `A0`, `theta0`, `A_eff`, optional `B_info`, `phi_geom`, `d_eff` sauber zu unterscheiden
3. verschiedene `coupling_mode`-Varianten explizit zu testen
4. die Regime `macro` und `coherent` kontrolliert zu vergleichen
5. direkte nächste Geometrietests daraus abzuleiten

---

## 10. Testbare Claims-Readiness

Die I/O-Schicht muss mindestens die Grundlage dafür liefern, folgende Fragen testbar zu machen:

- Gibt es eine nichttriviale, aber kontrollierte Kopplung zwischen `theta` und `A`?
- Stabilisiert eine Kopplungsform den Brückenzustand?
- Bleiben Bindung/Stabilisierung und Informationsstruktur partiell getrennt?
- Reagieren `negative` und `abs` günstiger als `positive`?
- Verbessert eine Kopplung die geometrische Lesbarkeit von `d_eff`?

---

## 11. Minimaler Run-Plan

### Run A
- Datensätze: `k0`, `theta_0.03`
- Exportklassen: `negative`, `abs`, `positive`
- Regime: `macro`
- Modi: `additive`, `multiplicative`, `dual_channel`

### Run B
- wie Run A
- Regime: `coherent`

### Run C
- Datensatz: `n1a_alpha`
- nur beste Kopplungsform aus A/B
- prüfen, ob dieselbe Mechanik trägt oder zerfällt

---

## 12. Bottom line

`bridge_mechanics_io_v1` definiert die I/O-Schicht für den Übergang von

> Brückenzustand beschreiben

zu

> Brückenmechanik testbar machen

Die operative Leitformel lautet:

> Wir testen, welche minimale Kopplung zwischen `theta` und `A` einen stabilen, geometrie-kompatiblen und funktional gegliederten Brückenzustand hervorbringt.
