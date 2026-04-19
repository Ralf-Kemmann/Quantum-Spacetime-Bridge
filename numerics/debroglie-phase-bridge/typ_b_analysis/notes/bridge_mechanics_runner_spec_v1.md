# bridge_mechanics_runner_spec_v1

## 1. Ziel

Diese Spezifikation definiert die minimale Runner-Struktur für `bridge_mechanics_v1`.

Der Runner soll nicht bloß ein theoretisches Modell referenzieren, sondern einen **konkret ausführbaren kleinen Mechanikblock** bereitstellen, der:

- vorhandene Projektinputs übernimmt,
- `A0`, `theta0` und die Kopplungsschicht konstruiert,
- verschiedene `coupling_mode`-Varianten testet,
- `phi_geom` und `d_eff` ableitet,
- diagnostische Scores erzeugt,
- und einen klaren Readout für die weitere Projektentscheidung schreibt.

Die Spezifikation ist bewusst klein gehalten:
erst launchable Mechanik, dann spätere Ausbaustufen.

---

## 2. Runner-Name und Position

Empfohlener Runner-Name:

`src/bridge_mechanics_runner_v1.py`

Optional ergänzende Hilfsdateien:

- `src/bridge_mechanics_core_v1.py`
- `src/bridge_mechanics_metrics_v1.py`
- `src/bridge_mechanics_io_v1.py`

Konfigurationsdateien:

- `configs/bridge_mechanics_run_a.yaml`
- `configs/bridge_mechanics_run_b.yaml`
- `configs/bridge_mechanics_run_c.yaml`

Outputs:

- `results/bridge_mechanics/<run_id>/...`

---

## 3. CLI-Schnittstelle

Minimaler Aufruf:

```bash
python src/bridge_mechanics_runner_v1.py --config configs/bridge_mechanics_run_a.yaml
```

Optionale CLI-Parameter:

- `--config <path>`
- `--output-dir <path>`
- `--run-id <string>`
- `--dataset-id <string>`
- `--regime <macro|coherent|mixed>`
- `--coupling-mode <additive|multiplicative|regime_gated|competitive|dual_channel>`
- `--lambda <float>`
- `--export-class <negative|abs|positive>`
- `--dry-run`

Empfehlung:
Im ersten Schritt primär config-getrieben arbeiten, CLI-Overrides nur ergänzend zulassen.

---

## 4. Erwartete Inputs

Der Runner erwartet pro Lauf mindestens:

- `run_id`
- `dataset_id`
- `export_class`
- `regime`
- `matrices`
  - `K`
  - `Kbar`
  - `G`
- `graph_data`
  - adjacency
  - weights
  - optional `d_rel`
- optionale `pair_units`
- `parameters`
  - `tau`
  - `coarse_grain_strength`
  - `adapter_mode`
  - `score_field`
  - `a_theta_coupling`
  - `coupling_mode`
  - `lambda_values`
  - optional `theta_transform`
  - optional `normalization_mode`

Minimaler Default-Kontext:

- `adapter_mode = adjacency_plus_threshold`
- `score_field = G`
- `tau = 0.025`

---

## 5. Interne Modulstruktur

### 5.1 `load_inputs()`
Lädt Konfiguration, Matrizen, Graphdaten und optionale PairUnits.

### 5.2 `normalize_inputs()`
Prüft:

- Pflichtfelder vorhanden
- Matrixformen konsistent
- Graphdaten konsistent
- keine offensichtlichen `nan`/`inf`
- sinnvolle Normalisierung

### 5.3 `construct_A0()`
Erzeugt den ungekoppelten coarse-grained Kohärenz-/Amplitudenproxy.

### 5.4 `construct_theta0()`
Erzeugt den ungekoppelten Phasen-/Interferenzproxy.

### 5.5 `apply_coupling()`
Wendet pro `coupling_mode` und `lambda` die Kopplung an.

Rückgabe:

- `A_eff`
- optional `A_bind`
- optional `B_info`
- `C_mech`

### 5.6 `project_geometry()`
Leitet aus `A_eff` bzw. `A_bind` ab:

- `phi_geom`
- `d_eff`
- neighborhoods
- optional graph proxy

### 5.7 `compute_diagnostics()`
Berechnet mindestens:

- `phase_influence_score`
- `structure_stability_score`
- `binding_channel_score`
- `information_channel_score`
- `geometry_readability_score`
- `delta_vs_baseline`
- optional `regime_response_score`

### 5.8 `write_outputs()`
Schreibt JSON-, CSV- und Markdown-Ausgaben.

### 5.9 `build_readout()`
Erzeugt einen maschinenraumtauglichen Kurzreadout mit:
- was trägt,
- was nur Rauschen ist,
- wo Geometrieantwort besser oder schlechter wird,
- ob eine Mehrkanal-Lesart unterstützt wird.

---

## 6. Ablaufreihenfolge

Der Runner soll in dieser Reihenfolge arbeiten:

1. Config laden
2. Inputs laden
3. Inputs normalisieren
4. `A0` konstruieren
5. `theta0` konstruieren
6. Baseline-Projektion rechnen
7. über `coupling_mode` und `lambda` iterieren
8. Kopplung anwenden
9. Geometrieprojektion rechnen
10. Diagnostiken berechnen
11. Resultate gegen Baseline vergleichen
12. Dateien schreiben
13. Readout erzeugen

---

## 7. Konfigurationsschema

Beispielstruktur:

```yaml
run_id: bridge_mechanics_run_a
dataset_id: k0
export_class: negative
regime: macro

inputs:
  matrices_path: data/k0_negative_matrices.npz
  graph_path: data/k0_negative_graph.json
  pair_units_path: null

parameters:
  tau: 0.025
  coarse_grain_strength: 1.0
  adapter_mode: adjacency_plus_threshold
  score_field: G
  a_theta_coupling: standard
  coupling_modes:
    - additive
    - multiplicative
    - dual_channel
  lambda_values:
    - 0.0
    - 0.05
    - 0.10
    - 0.20
  theta_transform: identity
  normalization_mode: standard

output:
  base_dir: results/bridge_mechanics
  write_state_json: true
  write_readout_md: true
  write_claims_json: true
  write_scan_csv: true
```

---

## 8. Pflicht-Dateioutputs

Pro Run sollen mindestens folgende Dateien erzeugt werden:

- `bridge_mechanics_state.json`
- `bridge_mechanics_readout.md`
- `bridge_mechanics_claims.json`
- `bridge_mechanics_coupling_scan.csv`

Optional:

- `bridge_mechanics_summary.json`
- `bridge_mechanics_geometry_probe.json`
- `bridge_mechanics_debug.json`

---

## 9. Minimale JSON-Struktur

### 9.1 `bridge_mechanics_state.json`

Soll mindestens enthalten:

```json
{
  "run_id": "bridge_mechanics_run_a",
  "dataset_id": "k0",
  "export_class": "negative",
  "regime": "macro",
  "baseline": {
    "A0_summary": {},
    "theta0_summary": {},
    "phi_geom_summary": {},
    "d_eff_summary": {}
  },
  "coupling_results": []
}
```

Jedes Element in `coupling_results` soll mindestens enthalten:

- `coupling_mode`
- `lambda`
- `A_eff_summary`
- optional `A_bind_summary`
- optional `B_info_summary`
- `phi_geom_summary`
- `d_eff_summary`
- `diagnostics`

### 9.2 `bridge_mechanics_claims.json`

Soll mindestens Felder enthalten:

- `claim_m1_status`
- `claim_m2_status`
- `claim_m3_status`
- `claim_m4_status`
- `claim_m5_status`
- `overall_status`
- `notes`

### 9.3 `bridge_mechanics_coupling_scan.csv`

Mindestens Spalten:

- `run_id`
- `dataset_id`
- `export_class`
- `regime`
- `coupling_mode`
- `lambda`
- `phase_influence_score`
- `structure_stability_score`
- `binding_channel_score`
- `information_channel_score`
- `geometry_readability_score`
- `delta_vs_baseline`
- `claim_label`

---

## 10. Readout-Template

`bridge_mechanics_readout.md` soll kurz und streng strukturiert sein:

1. **Run-Kontext**
2. **Baseline**
3. **Beste Kopplungsform**
4. **Schwächste Kopplungsform**
5. **Exportklassen-Lesart**
6. **Regime-Lesart**
7. **Kanaltrennung**
8. **Geometry response**
9. **Claim-Status**
10. **Bottom line**

Der Readout soll nicht paper-prosig werden, sondern klar sagen:

- was robust ist,
- was nur signalhaft ist,
- was offen bleibt.

---

## 11. Minimaler Run-Plan

### Run A
- `dataset_id = k0`
- `export_class in {negative, abs, positive}`
- `regime = macro`
- `coupling_modes = {additive, multiplicative, dual_channel}`

### Run B
- `dataset_id = theta_0.03`
- `export_class in {negative, abs, positive}`
- `regime = macro`
- `coupling_modes = {additive, multiplicative, dual_channel}`

### Run C
- gleiche Datensätze wie A/B
- `regime = coherent`

### Run D
- `dataset_id = n1a_alpha`
- nur beste Kopplungsform aus A–C
- Sensitivitätsprüfung

---

## 12. Entscheidungslogik

### Unterstützt
Wenn mindestens eine Kopplung:

- kontrolliert und nichttrivial wirkt,
- gegenüber Baseline nicht schlechter ist,
- `negative/abs` günstiger behandelt als `positive`,
- und eine sinnvolle Kanal- oder Regimeantwort zeigt.

### Teilweise unterstützt
Wenn Effekte vorhanden, aber instabil, selektiv oder stark datensatzabhängig bleiben.

### Nicht unterstützt
Wenn:

- alle Kopplungen nur Rauschen erzeugen,
- `theta` praktisch irrelevant oder destruktiv bleibt,
- keine sinnvolle Mechanikantwort lesbar wird.

---

## 13. Technische Minimalanforderungen

Der Runner soll im ersten Wurf:

- robust gegen fehlende optionale Inputs sein
- bei `nan`/`inf` sauber abbrechen oder markieren
- Summary-Statistiken statt voller Roharrays in JSON schreiben
- CSV-Scan für einfachen Vergleich erzeugen
- Readout auch bei `failed` oder `inconclusive` sauber schreiben

Optional später:

- Plot-Outputs
- Batch-Läufe
- Vergleich gegen Referenzkopplungen
- alternative Neighborhood-Definitionen

---

## 14. Bottom line

`bridge_mechanics_runner_spec_v1` macht aus dem Mechanikblock einen launchbaren Maschinenraum-Runner.

Die operative Leitformel lautet:

> Der Runner soll nicht bloß zeigen, dass eine Brücke beschrieben werden kann, sondern welche minimale Kopplungsmechanik zwischen `theta` und `A` in den vorhandenen Datensätzen tatsächlich tragfähig ist.
