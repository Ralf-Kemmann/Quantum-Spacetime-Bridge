# debroglie_matter_signature_isotope_io_v1

## 1. Ziel

Diese I/O-Spezifikation definiert die Eingabe- und Ausgabeschicht für den ersten Isotopen-Block der materialsensitiven Signaturarchitektur.

Der Block soll einen methodisch besonders sauberen Trennschnitt zwischen
- **Wellen-/Massenskala**
- **innerer elektronischer Struktur**

ermöglichen.

Leitfrage:

> Wie muss die Daten- und Outputstruktur aufgebaut sein, damit isotopische Massenvariation bei weitgehend gleicher Elektronenstruktur sauber gegen strukturgetragene Deskriptoren getestet werden kann?

---

## 2. Ausgangslage

Die bisherigen Blöcke haben gezeigt:

- die reine Wellen-Schicht erzeugt robuste, aber stark massen- bzw. längenskalengetragene Ordnung
- Ionisierungsenergie wirkt als atomnahe Stärkeachse
- Valenzelektronenzahl wirkt als atomnahe Strukturachse
- shell_closure verfeinert die Strukturachse

Mit Isotopen kann nun gezielt geprüft werden, ob
- die **Wellenachse** auf Massenvariation reagiert
- die **Strukturachse** bei gleicher Elektronenorganisation stabil bleibt

---

## 3. Scope des ersten Isotopen-Blocks

### 3.1 Minimaler Startfall
- protium (`1H`)
- deuterium (`2H`)
- tritium (`3H`)

### 3.2 Spätere Erweiterungen
- `12C` / `13C`
- `14N` / `15N`
- ggf. weitere isotopische Paare

### 3.3 Nicht Ziel des ersten Wurfs
- hyperfeine Spektroskopie
- isotopenabhängige Feinkorrekturen der Ionisierungsenergie
- Kernspin- oder Quadrupolkopplung

Der erste Block bleibt bewusst minimal.

---

## 4. Input-Schicht

### 4.1 Pflicht-Inputs

`DebroglieMatterSignatureIsotopeInput` enthält mindestens:

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
  - optional:
    - `valence_electron_count`
    - `shell_closure_score`
    - `ionization_energy_ev` (falls später gewünscht)
- `surrogates`
  - aktive Wellen-Surrogate
  - aktive Struktur-Surrogate
  - Kombinationsmodus
  - Gewichte

### 4.2 Minimaler Default-Input für Run ISO-A/B/C

Für den Wasserstoffblock:

- `1H`
- `2H`
- `3H`

mit:

- gleicher Elektronenanzahl
- gleicher Valenzlogik
- gleicher Closure-Logik
- unterschiedlicher isotopischer Masse

---

## 5. Interne Zustandsgrößen

### 5.1 Wellen-Grundgrößen
Für jedes Isotop mindestens:

- `mass_kg`
- `velocity`
- `momentum`
- `lambda_db`
- `energy`
- `number_density`

### 5.2 Struktur-Grundgrößen
Für jedes Isotop mindestens:

- `electron_count`
- `valence_electron_count`
- `shell_closure_score`

Wichtig:
Diese Größen sollen im Minimalfall zwischen Isotopen eines Elements identisch bleiben.

### 5.3 Optionale spätere Kern-Grundgrößen
Noch nicht Pflicht, aber perspektivisch denkbar:

- `nuclear_spin`
- `nuclear_quadrupole_moment`
- `isotope_shift_proxy`

---

## 6. Verarbeitungsschritte

### Schritt 1: Input Normalization
- Pflichtfelder prüfen
- Isotopendaten validieren
- sicherstellen, dass die Elektronenstruktur im getesteten Isotopenblock konsistent gehalten wird

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
- optional weitere QC-Strukturgrößen

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
- Invarianzdiagnostik der Strukturgrößen

### Schritt 8: Readout und Claims schreiben
- Ordnungen
- Deltas
- Kommentar zur Trennung von Wellen- und Strukturanteil

---

## 7. Output-Schicht

`DebroglieMatterSignatureIsotopeOutput` enthält mindestens:

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
  - `matter_sensitive_delta_isotope`
  - `structure_invariance_check`
- `claim_readout`

---

## 8. Pflicht-Dateioutputs

Der erste Isotopen-Runner schreibt mindestens:

- `debroglie_matter_signature_isotope_state.json`
- `debroglie_matter_signature_isotope_readout.md`
- `debroglie_matter_signature_isotope_scan.csv`
- `debroglie_matter_signature_isotope_claims.json`

Optional später:

- `debroglie_matter_signature_isotope_debug.json`
- `debroglie_matter_signature_isotope_invariance_report.json`

---

## 9. Pflicht-Diagnostiken

### 9.1 `structure_invariance_check`
Prüft, ob die strukturgetragenen Größen im Isotopenblock tatsächlich konstant geblieben sind.

### 9.2 `wave_shift_magnitude`
Misst, wie stark sich die Wellen-Surrogate infolge der Massenänderung verschieben.

### 9.3 `combined_shift_magnitude`
Misst, ob die kombinierte Signatur kontrolliert reagiert und nicht chaotisch umspringt.

### 9.4 `isotope_consistency_flag`
Kennzeichnet, ob die beobachteten Änderungen dem erwarteten Muster entsprechen:
- Welle verschiebt sich
- Struktur bleibt stabil

---

## 10. Minimaler Erfolg

Die I/O-Spezifikation ist gelungen, wenn sie ermöglicht:

1. isotopische Massenvariation sauber einzuspeisen
2. Elektronenstruktur explizit als invariant zu markieren
3. Wellen- und Strukturbeitrag getrennt auszugeben
4. den Isotopen-Test als echten Achsentrennungstest auszulesen

---

## 11. Testbare Claims-Readiness

Die I/O-Schicht muss die Grundlage dafür liefern, mindestens folgende Fragen sauber zu testen:

- Reagiert die Wellen-Schicht systematisch auf isotopische Masse?
- Bleiben Strukturgrößen im Minimalfall invariant?
- Verschiebt sich die kombinierte Signatur kontrolliert statt willkürlich?
- Ist damit die Trennung von Wellen- und Strukturachse methodisch gestützt?

---

## 12. Minimaler Run-Plan

### Run ISO-A
- `1H`, `2H`, `3H`
- nur Wellen-Schicht

### Run ISO-B
- `1H`, `2H`, `3H`
- Wellen-Schicht + `valence_electron_count`

### Run ISO-C
- `1H`, `2H`, `3H`
- Wellen-Schicht + `valence_electron_count` + `shell_closure_score`

### Run ISO-D optional
- C- und N-Isotopenpaare als Generalisierung

---

## 13. Bottom line

`debroglie_matter_signature_isotope_io_v1` definiert die I/O-Schicht für einen methodisch besonders sauberen Prüfblock:

> gleiche Elektronenstruktur, andere Massenskala.

Oder knapper:

> Isotope sind der I/O-sauberste Test, um Welle und Struktur gegeneinander auszulesen.
