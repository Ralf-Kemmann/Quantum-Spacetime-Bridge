# QSB-ST / Gravitation und RaumZeit — Projektstand zum Umzug

## 1. Projektidentität

Projektfamilie:

```text
QSB / Quantum-Spacetime Bridge
Gravitation und RaumZeit
QSB-ST
de Broglie / Wellen-basierte relationale Struktur
```

Aktueller Teilpfad:

```text
COMP01 / COMP01-B/C/C2/C3/D
```

Der aktuelle Pfad untersucht diagnostische Observablen für:

- psi(i)-psi(j)-Kompatibilität,
- komponentenaufgelöste Mustervergleiche,
- identity-sensitive Kontrollen gegen label_shuffle,
- Wellen-Identitätsfingerprints ohne vorausgesetzten Zeitanker.

## 2. Repo und aktueller Git-Anker

Lokaler Repo-Pfad:

```text
/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

GitHub:

```text
https://github.com/Ralf-Kemmann/Quantum-Spacetime-Bridge
```

Letzter bestätigter Commit:

```text
c36e169 Add QSB-ST COMP01D wave identity fingerprint observables concept
```

Letzter bestätigter Status:

```text
## main...origin/main
```

Aktuelles Statuslabel:

```text
COMP01D_wave_identity_fingerprint_observables_concept_documented
```

## 3. Wissenschaftlicher Stand

### LIC01 / tau-epsilon

LIC01 / tau-epsilon wurde methodisch sauber durchgearbeitet, aber nicht als Spezifitätsnachweis bestätigt.

Status:

```text
specificity_established = false
```

Interpretation:

- tau wird aktuell nicht als primitive Zeit, universeller Taktgeber oder proper time geführt.
- tau könnte später höchstens als abgeleitete Antwortlatenz im Korrelationsnetz erscheinen.
- Der aktuelle COMP01-D-Gedanke verschiebt den Fokus stärker weg von tau/delay.

### COMP01 Minimal Scanner

COMP01 begann als Suche nach psi(i)-psi(j)-Kompatibilitätswerten.

Status:

```text
COMP01_minimal_scanner_result_documented_candidates_observed_specificity_not_established
```

Befund:

- Kandidatenbewegung vorhanden.
- Keine Spezifität.
- label_shuffle blieb kritisch.

### COMP01-B Component-Resolved Compatibility

Status:

```text
COMP01B_component_resolved_compatibility_result_documented_candidates_observed_specificity_not_established
```

Wichtige Sicherungsnote:

```text
docs/QSB_ST_COMP01B_REAL_IMAG_PROXY_DEFINITION_NOTE.md
```

Kernregel:

```text
real_imag_proxy = diagnostischer Komponenten-Split
nicht = physikalische cos/sin-Ableitung
nicht = physikalische Wellenfunktion
```

### Mathematischer Anker

Dokumentiert in:

```text
docs/QSB_ST_PSI_ADDITION_CURVE_ANALYSIS_LOCAL_LINEAR_FORM.md
```

Arbeitsform:

```text
psi_i(x)=A_i cos(k_i x)+B_i sin(k_i x)
```

Lokale Tangente bei x0=0:

```text
y ≈ B_i k_i x + A_i
```

Interpretation:

- A_i als lokaler Offset / Intercept.
- B_i k_i als lokale Steigung / initiale Response.
- Lokale Tangenten-/Diagnoseform, kein globaler Ersatz für psi(x).

### Komplexe Notation — aktuelle Entscheidung

Künftige bevorzugte formale Schreibweise:

```text
psi_i(x)=A_i^C cos(k_i x)+B_i^C sin(k_i x)
```

mit:

```text
A_i^C = A_i^R + i A_i^I
B_i^C = B_i^R + i B_i^I
```

Begründung:

- Roter Faden zur reellen Gleichung bleibt sichtbar.
- cos-/sin-Kanäle bleiben anschaulich.
- A/B-Komponenten bleiben anschlussfähig.
- Komplexe Phase, Interferenz und Overlap werden möglich.
- Keine unnötige Euler-Übersetzungsstufe als Projektnotation.

Exponentialform nur als mathematisch äquivalenter Hintergrund.

### COMP01-C Identity-Sensitive Component Contrast

Status:

```text
COMP01C_identity_sensitive_component_contrast_result_documented_candidates_observed_specificity_not_established
```

Befund:

- structured_local_phase_response vs label_shuffle
- pairwise_delta / rank_correlation / top_quartile_overlap
- Kandidatenbewegung bei:

```text
sin_sin_overlap
component_resolved_relative_phase_similarity
```

Aber:

```text
specificity_established = false
```

### COMP01-C2 Candidate Metric Inspection

Status:

```text
COMP01C2_candidate_metric_inspection_result_documented_candidates_stable_specificity_not_established
```

Befund:

Die beiden COMP01-C-Kandidaten blieben über 20 deterministic value-permutation label_shuffle Controls stabil:

```text
sin_sin_overlap
component_resolved_relative_phase_similarity
```

Wichtige Werte:

```text
sin_sin_overlap:
  candidate_signal_count = 20
  seed_count = 20
  candidate_signal_fraction = 1
  mean_rank_correlation = 0.00303938356164
  mean_top_quartile_overlap = 0.240625
  decision_status = strong_identity_sensitive_candidate_for_followup

component_resolved_relative_phase_similarity:
  candidate_signal_count = 20
  seed_count = 20
  candidate_signal_fraction = 1
  mean_rank_correlation = 0.0243435549027
  mean_top_quartile_overlap = 0.240625
  decision_status = strong_identity_sensitive_candidate_for_followup
```

Aber:

- value-permutation label_shuffle ist nur eine harder-control approximation.
- Keine echte Kernel-Level-Neusimulation.
- Keine Spezifität.

### COMP01-C3 Real Kernel Resimulation Label-Shuffle

Status:

```text
COMP01C3_real_kernel_resimulation_label_shuffle_result_documented_candidates_not_confirmed_specificity_not_established
```

Echter Kernel-/Node-Level label_shuffle Smoke-Test:

```text
control_family:
  true_label_shuffle_kernel_resimulation

control_mode:
  kernel_node_label_permutation_fixed_structured_reference

seeds:
  2000–2019
```

Ergebnis:

```text
stable_candidate_metrics:
  none / empty list

failed_or_inconclusive_metrics:
  sin_sin_overlap
  component_resolved_relative_phase_similarity

label_shuffle_mimic_warning_metrics:
  none / empty list
```

Konkrete C3-Werte:

```text
sin_sin_overlap:
  candidate_signal_count_true_label_shuffle = 12
  seed_count_true_label_shuffle = 20
  candidate_signal_fraction_true_label_shuffle = 0.6
  mean_rank_correlation_true_label_shuffle = 0.344295815404
  mean_top_quartile_overlap_true_label_shuffle = 0.5625
  decision_status = inconclusive_control_result

component_resolved_relative_phase_similarity:
  candidate_signal_count_true_label_shuffle = 12
  seed_count_true_label_shuffle = 20
  candidate_signal_fraction_true_label_shuffle = 0.6
  mean_rank_correlation_true_label_shuffle = 0.331325743665
  mean_top_quartile_overlap_true_label_shuffle = 0.5625
  decision_status = inconclusive_control_result
```

Interpretation:

- C2-Kandidaten nicht bestätigt im ersten echten Kernel-Level label_shuffle Smoke-Test.
- Nicht als klare mimic warning entwertet.
- Aber nicht promotionsfähig.
- Wichtiger Bremsbefund gegen Overclaiming.

### COMP01-D Wave Identity Fingerprint Observables Concept

Status:

```text
COMP01D_wave_identity_fingerprint_observables_concept_documented
```

Aktueller Konzeptwechsel:

Nicht mehr primär:

```text
Wann entsteht Korrelation?
tau?
Delay?
wann-ähnliche Ordnung?
```

Sondern:

```text
Woran unterscheide ich scheinbar gleiche Wellen,
wenn noch kein Zeitanker existiert?
```

Leitsatz:

```text
Nicht die Uhr suchen, bevor klar ist, welche Welle welche ist.
```

Kandidatengruppen:

- spectral shift / delta_k
- relative_k_shift
- relative_phase_drift
- phase_gradient_delta
- phase_curvature_delta
- envelope_difference
- modulation_depth_delta
- sideband_structure_delta
- slope_similarity
- intercept_similarity
- local_linear_response_overlap
- complex_component_phase_delta
- complex_component_magnitude_delta
- cross_channel_leakage

Wichtig:

- spectral shift ist nur diagnostische Analogie, keine kosmologische Rotverschiebung.
- phase drift ist Strukturmarker, kein physikalischer Delay.
- wave identity fingerprints sind diagnostische Unterscheidbarkeitsobservablen, keine physikalischen Observablen per se.

## 4. Aktuelle Claim Boundary

Erlaubt:

```text
diagnostische Kandidatenbewegung
methodische Null-/Kontrollprüfung
Konzeptwechsel zu Wellen-Identitätsfingerprints
synthetische Diagnosehypothesen
```

Nicht erlaubt:

```text
Spezifität etabliert
tau-Modell
D(A,B)
S_rel2
Lorentz-Metrik
physikalische Zeit
proper time
universeller Taktgeber
physikalische Wellenfunktion
Bridge-Validierung
Big Bang-Erklärung
kosmologische Rotverschiebung
```
