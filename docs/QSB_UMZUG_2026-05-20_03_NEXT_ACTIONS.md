# QSB-ST — Geplante nächste Aktionen nach dem Umzug

## Aktueller Haltepunkt

Status:

```text
COMP01D_wave_identity_fingerprint_observables_concept_documented
```

Letzter Commit:

```text
c36e169 Add QSB-ST COMP01D wave identity fingerprint observables concept
```

Repo sauber:

```text
## main...origin/main
```

## Unmittelbar nächster sinnvoller Block

Empfohlen:

```text
QSB-ST-COMP01-D1 wave identity fingerprint minimal design plan
```

Ziel:

Nicht direkt einen großen Scanner bauen.

Stattdessen einen Minimal-Design-Plan erstellen für drei Fingerprintfamilien:

```text
1. spectral shift / delta_k
2. phase drift / phase_gradient_delta
3. local linear fingerprint / slope-intercept
```

## Warum D1?

COMP01-C3 zeigte:

```text
C2-Kandidaten nicht bestätigt unter Kernel-Level label_shuffle Smoke-Test.
```

Daraus folgt:

```text
Nicht mehr tiefer in dieselben Kandidaten bohren.
Nicht sofort tau/delay/D(A,B)/S_rel2.
Zuerst prüfen, wie Wellen ohne Zeitanker unterscheidbar sind.
```

## D1-Plan: gewünschte Inhalte

Dateiname vermutlich:

```text
docs/QSB_ST_COMP01D1_WAVE_IDENTITY_FINGERPRINT_MINIMAL_DESIGN_PLAN.md
```

Pflichtsections:

```text
# QSB-ST-COMP01-D1 Wave Identity Fingerprint Minimal Design Plan

## 1. Purpose
## 2. Current status anchor
## 3. Motivation after COMP01-D concept
## 4. Minimal fingerprint families
## 5. Spectral shift / delta_k design
## 6. Phase drift / phase_gradient_delta design
## 7. Local linear slope-intercept design
## 8. Same-wave and near-identical-wave controls
## 9. Required null/control families
## 10. Proposed output files
## 11. Continuous field list
## 12. Minimal computation rules
## 13. Decision logic
## 14. Interpretation rules
## 15. What this block must not do
## 16. Claim Boundary
## 17. Current status label
```

## D1-Minimalobservablen

### 1. spectral shift / delta_k

Mögliche Felder:

```text
delta_k
relative_k_shift
k_ratio
spectral_identity_distance
```

Grenze:

Keine kosmologische Rotverschiebung.

### 2. phase drift / phase_gradient_delta

Mögliche Felder:

```text
relative_phase_drift
phase_gradient_delta
phase_curvature_delta
phase_unwrap_warning
```

Grenze:

Kein Delay, keine Zeit, kein tau.

### 3. local linear fingerprint / slope-intercept

Aus:

```text
psi_i(x)=A_i cos(k_i x)+B_i sin(k_i x)
```

lokal:

```text
y ≈ B_i k_i x + A_i
```

Mögliche Felder:

```text
intercept_similarity
slope_similarity
delta_intercept_ij
delta_slope_ij
slope_intercept_balance
local_linear_response_overlap
```

Grenze:

Lokale Tangente, kein globales Wellenmodell.

## D1-Control-Priorität

Pflicht:

```text
same-wave duplicate sanity check
near-identical-wave decoy control
label_shuffle
kernel-level label_shuffle
```

Optional später:

```text
phase_randomized control
amplitude_preserved_phase_randomized control
distribution_matched control
spectrum_matched control
noise perturbation
```

## Alternative nächster Block

Falls Ralf zuerst verstehen will, warum C2/C3 divergieren:

```text
QSB-ST-COMP01-C3A failure-mode analysis of C2/C3 divergence
```

Nova-Empfehlung:

```text
D1 zuerst, wenn der neue Wellenfingerprint-Gedanke im Vordergrund steht.
C3A zuerst, wenn die methodische Ursachenanalyse der alten Kandidaten wichtiger ist.
```
