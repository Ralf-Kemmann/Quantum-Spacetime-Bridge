# debroglie_matter_signature_isotope_carbon_io_v1

## 1. Ziel

Diese I/O-Spezifikation definiert die Eingabe- und Ausgabeschicht für den ersten **Carbon-Isotopen-Block** der materialsensitiven Signaturarchitektur.

Der Block dient als erster Generalisierungstest über den erfolgreichen H/D/T-Minimalfall hinaus.

Leitfrage:

> Lässt sich die im Wasserstoff-Isotopenblock beobachtete Trennung von Wellen- und Strukturachse auch für ein chemisch deutlich reichhaltigeres, theoretisch-chemisch zentrales Element wie Kohlenstoff sauber reproduzieren?

---

## 2. Ausgangslage

Der H/D/T-Block hat gezeigt:

- isotopische Massenvariation verschiebt die Wellenachse systematisch
- Strukturdeskriptoren bleiben im Minimalfall invariant
- die kombinierte Signatur reagiert kontrolliert
- Wellen- und Strukturanteil sind damit im Minimalfall methodisch trennbar

Der Carbon-Block soll nun prüfen, ob diese Logik auch für ein Element mit:

- vier Valenzelektronen
- deutlich reichhaltigerer Bindungs- und Strukturchemie
- höherer theoretisch-chemischer Relevanz

bestehen bleibt.

---

## 3. Scope des ersten Carbon-Blocks

### 3.1 Minimaler Startfall
- `12C`
- `13C`

### 3.2 Optionale spätere Erweiterung
- `14C` nur mit expliziter Kennzeichnung und Vorsicht, da radioaktiv

### 3.3 Nicht Ziel des ersten Wurfs
- isotopensensitive Feinstrukturkorrekturen
- Hyperfein- oder Kernspinbeiträge
- molekulare oder allotrope Kohlenstoffformen
- sp2/sp3- oder Bandstruktur-Effekte

Der erste Carbon-Block bleibt bewusst **atomar und minimal**.

---

## 4. Input-Schicht

### 4.1 Pflicht-Inputs

`DebroglieMatterSignatureIsotopeCarbonInput` enthält mindestens:

- `run_id`
- `isotope_list`
- `conditions`
  - `temperature_C`
  - `pressure_mbar`
  - `volume_m3`
- `model_assumptions`
  - `species_mode`
  - `gas_model`
  - `velocity_model`
  - `frequency_mode`
  - `density_mode`
  - `isotope_mode`
- `isotope_data`
  - `label`
  - `element_symbol`
  - `mass_u`
  - `proton_number`
  - `neutron_number`
  - `electron_count`
  - `valence_electron_count`
  - `shell_closure_score`
- `surrogates`
  - aktive Wellen-Surrogate
  - aktive Struktur-Surrogate
  - Kombinationsmodus
  - Gewichte

### 4.2 Minimaler Default-Input

Für den ersten Carbon-Block:

- `12C`
- `13C`

mit:

- gleicher Elektronenanzahl
- gleicher Valenzlogik
- gleicher Closure-Logik
- unterschiedlicher isotopischer Masse

---

## 5. Interne Zustandsgrößen

### 5.1 Wellen-Grundgrößen
Für jedes C-Isotop mindestens:

- `mass_kg`
- `velocity`
- `momentum`
- `lambda_db`
- `energy`
- `number_density`

### 5.2 Struktur-Grundgrößen
Für jedes C-Isotop mindestens:

- `electron_count`
- `valence_electron_count`
- `shell_closure_score`

Im Minimalfall sollen diese Größen zwischen `12C` und `13C` invariant bleiben.

### 5.3 Optionale spätere Kern-Grundgrößen
Noch nicht Pflicht, aber perspektivisch denkbar:

- `nuclear_spin`
- `nuclear_quadrupole_moment`
- `isotope_shift_proxy`

---

## 6. Verarbeitungsschritte

### Schritt 1: Input Normalization
- Pflichtfelder prüfen
- C-Isotopendaten validieren
- Elektronenstrukturkonsistenz sicherstellen

### Schritt 2: Wellen-Grundgrößen berechnen
- thermische Geschwindigkeit
- Impuls
- de-Broglie-Wellenlänge
- Energie
- Teilchendichte

### Schritt 3: Wellen-Surrogate bilden
- `length_scale_score`
- `energy_score`
- `occupancy_score`
- `signature_score_wave`

### Schritt 4: Struktur-Surrogate laden
- `valence_electron_count`
- `shell_closure_score`

### Schritt 5: Struktur-Surrogate bilden
- `valence_score`
- `signature_score_structure`

### Schritt 6: Kombinierte Signatur bilden
- `signature_score_combined`

### Schritt 7: Vergleichsdiagnostik berechnen
- Massenordnung
- Wellenordnung
- kombinierte Ordnung
- Delta relativ zur Massenordnung
- Strukturinvarianzdiagnostik

### Schritt 8: Readout und Claims schreiben
- Ordnungen
- Deltas
- Invarianzflags
- Kommentar zur Generalisierung des H/D/T-Befunds

---

## 7. Output-Schicht

`DebroglieMatterSignatureIsotopeCarbonOutput` enthält mindestens:

- `run_id`
- `conditions`
- `model_assumptions`
- `isotope_results`
  - `label`
  - `element_symbol`
  - `mass_kg`
  - `lambda_db`
  - `energy`
  - `number_density`
  - `valence_electron_count`
  - `shell_closure_score`
  - `wave_surrogates`
  - `structure_surrogates`
  - `combined_surrogates`
- `comparisons`
  - `mass_only_ordering`
  - `wave_signature_ordering`
  - `combined_signature_ordering`
  - `matter_sensitive_delta_wave`
  - `matter_sensitive_delta_isotope_carbon`
  - `structure_invariance_check`
- `claim_readout`

---

## 8. Pflicht-Dateioutputs

Der Carbon-Runner oder die Carbon-Erweiterung schreibt mindestens:

- `debroglie_matter_signature_isotope_carbon_state.json`
- `debroglie_matter_signature_isotope_carbon_readout.md`
- `debroglie_matter_signature_isotope_carbon_scan.csv`
- `debroglie_matter_signature_isotope_carbon_claims.json`

Optional später:

- `debroglie_matter_signature_isotope_carbon_debug.json`
- `debroglie_matter_signature_isotope_carbon_invariance_report.json`

---

## 9. Pflicht-Diagnostiken

### 9.1 `structure_invariance_check`
Prüft, ob die strukturgetragenen Größen im Carbon-Block invariant geblieben sind.

### 9.2 `wave_shift_magnitude`
Misst die durch `12C` → `13C` ausgelöste Wellenverschiebung.

### 9.3 `combined_shift_magnitude`
Misst, ob die kombinierte Signatur kontrolliert und lesbar reagiert.

### 9.4 `carbon_generalization_flag`
Kennzeichnet, ob der H/D/T-Befund als Carbon-Generalisierung sauber trägt.

---

## 10. Minimaler Erfolg

Die I/O-Spezifikation ist gelungen, wenn sie ermöglicht:

1. `12C` und `13C` sauber als isotopisches Testpaar einzuspeisen
2. Strukturinvarianz explizit sichtbar zu machen
3. Wellen- und Strukturbeitrag getrennt auszugeben
4. die Carbon-Generalisation des H/D/T-Befunds methodisch sauber auszulesen

---

## 11. Testbare Claims-Readiness

Die I/O-Schicht muss mindestens die Grundlage dafür liefern, folgende Fragen sauber zu testen:

- Reagiert die Wellen-Schicht auch bei Kohlenstoff isotopensensitiv?
- Bleiben Valenz und Closure invariant?
- Reagiert die kombinierte Signatur kontrolliert?
- Ist der H/D/T-Befund damit über Wasserstoff hinaus generalisiert?

---

## 12. Minimaler Run-Plan

### Carbon Run A
- `12C`, `13C`
- nur Wellen-Schicht

### Carbon Run B
- `12C`, `13C`
- Wellen-Schicht + `valence_electron_count`

### Carbon Run C
- `12C`, `13C`
- Wellen-Schicht + `valence_electron_count` + `shell_closure_score`

---

## 13. Bottom line

`debroglie_matter_signature_isotope_carbon_io_v1` definiert die I/O-Schicht für den ersten inhaltlich ernsthaften Generalisierungstest des Isotopenblocks.

Die operative Leitformel lautet:

> gleiche Kohlenstoff-Struktur, andere Massenskala.

Oder knapper:

> Carbon prüft, ob der Wasserstoff-Befund auch bei einer zentralen Atomsorte trägt.
