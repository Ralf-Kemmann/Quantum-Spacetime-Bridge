# bridge_minimal_model_io_v1

## 1. Ziel

Diese I/O-Spezifikation legt fest, welche Inputs das Minimalmodell der Brückenphysik benötigt, welche internen Zustandsgrößen es erzeugt und welche testbaren Outputs folgen müssen.

---

## 2. Input-Schicht

### Pflicht-Inputs
- `K`, `Kbar`, `G` (mindestens eine strukturtragende Matrix, bevorzugt `G`)
- Knoten-/Modusmenge
- optionale Graphstruktur:
  - adjacency
  - edge weights
  - edge length
  - d_rel
- optionale PairUnits
- Regimeparameter:
  - coarse_grain_strength
  - adapter_mode
  - `tau`
  - `a_theta_coupling`

### Minimaler Inputtyp
`BridgeModelInput` enthält:
- run_id
- dataset_id
- matrices
- graph_data
- pair_units
- regime
- parameters

---

## 3. Interne Zustandsgrößen

### `A`
coarse-grained Kohärenz-/Amplitudenproxy

### `theta`
Phasen-/Interferenzproxy

### `C_map`
Dokumentierte coarse-graining map:
- Inputstruktur -> `(A, theta)`

### `phi_geom`
aus `A` abgeleitete geometrienahe Größe

### `d_eff`
effektiver Distanzkandidat

---

## 4. Verarbeitungsschritte

1. Input Normalization  
2. Construction of `A`  
3. Construction of `theta`  
4. Coupling Layer  
5. Geometry Projection (`A -> phi_geom -> d_eff`)

---

## 5. Regime-Logik

### `macro`
- theta teilweise oder weitgehend ausgemittelt
- A dominiert

### `coherent`
- theta bleibt aktiv
- Interferenzstruktur sichtbar

### `mixed`
- beide Kanäle relevant

---

## 6. Output-Schicht

`BridgeModelOutput` enthält mindestens:

- run_id
- dataset_id
- regime
- state_fields:
  - A
  - theta
  - phi_geom
- effective_structure:
  - d_eff
  - neighborhoods
  - graph_proxy
- diagnostics:
  - structure_stability_score
  - phase_influence_score
  - geometry_readability_score
- testable_claims_ready

---

## 7. Pflicht-Diagnostiken

### structure_stability_score
Wie robust bleibt `A` unter kleinen Variationseingriffen?

### phase_influence_score
Wie stark beeinflusst `theta` die Ausbildung von `A` bzw. `phi_geom`?

### geometry_readability_score
Wie gut eignet sich `phi_geom` / `d_eff` als Kandidat für Geometrietests?

---

## 8. Pflicht-Dateioutputs

- `bridge_minimal_model_state.json`
- `bridge_minimal_model_readout.md`
- `bridge_minimal_model_claims.json`

---

## 9. Minimaler Erfolg

Die I/O-Spezifikation ist gelungen, wenn sie ermöglicht:

1. aus vorhandenen Projektinputs ein kleines Brückenmodell zu instanziieren  
2. `A`, `theta`, `phi_geom`, `d_eff` sauber zu unterscheiden  
3. die Regime `macro` und `coherent` explizit zu trennen  
4. direkte nächste Geometrietests daraus abzuleiten
