# debroglie_matter_signature_isotope_strontium_io_v1

## 1. Ziel

Diese I/O-Spezifikation definiert die Eingabe- und Ausgabeschicht für den ersten **Strontium-Isotopen-Block** der materialsensitiven Signaturarchitektur.

Der Block dient als methodisch stärkerer **Serien- und Staffeltest** über den bisherigen Minimal- und Generalisierungsfall hinaus.

Leitfrage:

> Wie muss die Daten- und Outputstruktur aufgebaut sein, damit eine gestufte Isotopenreihe von Strontium als geordneter Test der Wellen-/Massenskala bei konstanter elektronischer Struktur ausgewertet werden kann?

---

## 2. Ausgangslage

Die bisherigen Isotopenblöcke haben gezeigt:

- H/D/T liefert den ersten harten Minimalbefund der Achsentrennung
- `12C` / `13C` generalisiert diesen Befund auf eine chemisch zentrale Atomsorte
- in beiden Fällen bleibt die Strukturseite invariant, während die Wellenachse systematisch auf Massenvariation reagiert

Der Strontium-Block geht nun einen Schritt weiter:

- nicht nur ein Isotopenpaar
- sondern eine kleine **stabile Isotopenserie**
- damit eine echte Staffelprüfung über mehrere Massenschritte hinweg

---

## 3. Scope des ersten Strontium-Blocks

### 3.1 Minimaler stabiler Startsatz
- `84Sr`
- `86Sr`
- `87Sr`
- `88Sr`

### 3.2 Perspektivische spätere Erweiterungen
- zusätzliche seltenere oder speziell motivierte Sr-Isotope
- ggf. isotopennahe kernphysikalische Zusatzdeskriptoren

### 3.3 Nicht Ziel des ersten Wurfs
- Hyperfein- oder Kernspin-Dynamik
- Kernquadrupolkopplung
- isotope shifts im spektroskopischen Feinsinn
- kondensierte Sr-Systeme oder optische Gitterphysik

Der erste Strontium-Block bleibt bewusst **atomar, minimal und seriell**.

---

## 4. Input-Schicht

### 4.1 Pflicht-Inputs

`DebroglieMatterSignatureIsotopeStrontiumInput` enthält mindestens:

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

Für den ersten Strontium-Block:

- `84Sr`
- `86Sr`
- `87Sr`
- `88Sr`

mit:

- gleicher Elektronenanzahl
- gleicher Valenzlogik
- gleicher Closure-Logik
- gestufter isotopischer Masse

---

## 5. Interne Zustandsgrößen

### 5.1 Wellen-Grundgrößen
Für jedes Sr-Isotop mindestens:

- `mass_kg`
- `velocity`
- `momentum`
- `lambda_db`
- `energy`
- `number_density`

### 5.2 Struktur-Grundgrößen
Für jedes Sr-Isotop mindestens:

- `electron_count`
- `valence_electron_count`
- `shell_closure_score`

Im Minimalfall sollen diese Größen über die Serie invariant bleiben.

### 5.3 Optionale spätere Kern-Grundgrößen
Noch nicht Pflicht, aber perspektivisch denkbar:

- `nuclear_spin`
- `nuclear_quadrupole_moment`
- `isotope_shift_proxy`

---

## 6. Verarbeitungsschritte

### Schritt 1: Input Normalization
- Pflichtfelder prüfen
- Sr-Isotopendaten validieren
- Konsistenz der Elektronenstruktur über die Serie sicherstellen

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

### Schritt 7: Serien-Diagnostik berechnen
- Massenordnung
- Wellenordnung
- kombinierte Ordnung
- Delta relativ zur Massenordnung
- Strukturinvarianzdiagnostik
- Staffel-/Monotonieprüfung

### Schritt 8: Readout und Claims schreiben
- Ordnungen
- Deltas
- Invarianzflags
- Kommentar zum Serienverhalten

---

## 7. Output-Schicht

`DebroglieMatterSignatureIsotopeStrontiumOutput` enthält mindestens:

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
  - `matter_sensitive_delta_isotope_strontium`
  - `structure_invariance_check`
  - `series_consistency_flag`
  - `monotonic_wave_flag`
- `claim_readout`

---

## 8. Pflicht-Dateioutputs

Der Strontium-Runner oder die Strontium-Erweiterung schreibt mindestens:

- `debroglie_matter_signature_isotope_strontium_state.json`
- `debroglie_matter_signature_isotope_strontium_readout.md`
- `debroglie_matter_signature_isotope_strontium_scan.csv`
- `debroglie_matter_signature_isotope_strontium_claims.json`

Optional später:

- `debroglie_matter_signature_isotope_strontium_debug.json`
- `debroglie_matter_signature_isotope_strontium_series_report.json`

---

## 9. Pflicht-Diagnostiken

### 9.1 `structure_invariance_check`
Prüft, ob die strukturgetragenen Größen über die Sr-Serie konstant geblieben sind.

### 9.2 `series_consistency_flag`
Kennzeichnet, ob die Serie insgesamt dem erwarteten Muster folgt:
- Struktur konstant
- Welle staffelartig verschoben

### 9.3 `monotonic_wave_flag`
Prüft, ob die Wellenordnung über die gesamte Isotopenserie monoton mit der Massenskala reagiert.

### 9.4 `combined_shift_profile`
Beschreibt, ob die kombinierte Signatur kontrolliert staffelt oder an einzelnen Punkten unruhig springt.

---

## 10. Minimaler Erfolg

Die I/O-Spezifikation ist gelungen, wenn sie ermöglicht:

1. mehrere stabile Sr-Isotope sauber als Serie einzuspeisen
2. Strukturinvarianz explizit sichtbar zu machen
3. Serien- und Staffelverhalten der Wellenachse auszulesen
4. die Strontium-Serie als methodisch stärkeren Achsentrennungstest zu bewerten

---

## 11. Testbare Claims-Readiness

Die I/O-Schicht muss mindestens die Grundlage dafür liefern, folgende Fragen sauber zu testen:

- Reagiert die Wellen-Schicht über die gesamte Sr-Serie geordnet und monoton?
- Bleiben Valenz und Closure über die Serie konstant?
- Bleibt die kombinierte Signatur kontrolliert?
- Liefert Strontium einen echten Staffeltest statt nur eines Paarvergleichs?

---

## 12. Minimaler Run-Plan

### Strontium Run A
- `84Sr`, `86Sr`, `87Sr`, `88Sr`
- nur Wellen-Schicht

### Strontium Run B
- `84Sr`, `86Sr`, `87Sr`, `88Sr`
- Wellen-Schicht + `valence_electron_count`

### Strontium Run C
- `84Sr`, `86Sr`, `87Sr`, `88Sr`
- Wellen-Schicht + `valence_electron_count` + `shell_closure_score`

---

## 13. Bottom line

`debroglie_matter_signature_isotope_strontium_io_v1` definiert die I/O-Schicht für den ersten echten Serien- und Staffeltest des Isotopenprogramms.

Die operative Leitformel lautet:

> gleiche Strontium-Struktur, mehrere Massenschritte.

Oder knapper:

> Strontium prüft nicht nur, ob es trägt — sondern ob es in Serie trägt.
