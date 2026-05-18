# QSB-ST-LIC01 Tau/Epsilon Specificity Contrast Result Note

**Block:** QSB-ST-LIC01-F / LIC01_tau_epsilon_specificity_contrast  
**Run:** `tau_epsilon_phase_response_open`  
**Previous status:** `LIC01_tau_epsilon_specificity_refinement_planned_not_implemented`  
**Status after run:** `LIC01_tau_epsilon_specificity_contrast_implemented_and_run_checked`  
**Date:** 2026-05-18  
**Document type:** Result note / synthetic specificity-contrast documentation  
**Claim level:** Synthetic diagnostic specificity assessment only; no physical time, Lorentz metric, spacetime, or validation claim.

---

## 1. Purpose

This note documents the LIC01-F specificity contrast layer for the QSB-ST-LIC01 tau/epsilon diagnostic.

The previous LIC01-E control run established that the runner can compare a structured local phase-response condition against a first suite of controls. It also produced a warning-level result: several controls remained close to the structured reference.

LIC01-F adds a dedicated specificity contrast layer. Its purpose is to make that warning more explicit and quantitatively inspectable by comparing the structured reference against the non-reference controls using raw `rho_tau` contrast fields, pairwise deltas, pattern correlation, and rank separation.

The goal is not to claim physical meaning. The goal is to answer the narrower methodological question:

> Does the current `rho_tau(A,B)` / `tau_rel_candidate(A,B)` construction show diagnostic specificity against the tested synthetic controls?

Current answer:

```text
specificity_established: false
```

---

## 2. Repo status anchor

The local status before this documentation step was clean and synchronized:

```text
## main...origin/main
```

The visible recent commits included:

```text
2ca8e01 Add QSB-ST LIC01 tau epsilon specificity contrast layer
eb55083 Add QSB-ST LIC01 tau epsilon specificity refinement plan
385ca0b Add QSB-ST LIC01 tau epsilon control run result note
c2139a0 Extend QSB-ST LIC01 tau epsilon runner with controls
8759fbf Add QSB-ST LIC01 tau epsilon control extension plan
7b80af2 Add QSB-ST LIC01 tau epsilon minimal run result note
387e937 Add QSB-ST LIC01 tau epsilon phase-response runner
a4614a8 Add QSB-ST LIC01 tau epsilon config scaffold
aaa0f78 Add QSB de Broglie relativity bridge notes
20884e8 Add QSB-ST LIC01 tau-rel phase-response design
```

This establishes that the specificity contrast layer was already committed before this result note was drafted.

---

## 3. Files involved

### 3.1 Planning document

```text
docs/QSB_ST_LIC01_TAU_EPSILON_SPECIFICITY_REFINEMENT_PLAN.md
```

### 3.2 Runner

```text
scripts/run_qsb_st_lic01_tau_epsilon_phase_response.py
```

### 3.3 Config

```text
data/qsb_st_lic01_tau_epsilon_phase_response_config.yaml
```

### 3.4 Output directory

```text
runs/QSB-ST-LIC01/tau_epsilon_phase_response_open/
```

### 3.5 Output files after LIC01-F

Existing minimal outputs:

```text
summary.json
readout.md
config_resolved.json
tau_epsilon_pairwise_response.csv
tau_epsilon_response_sweep.csv
tau_rel_candidate_matrix.csv
```

Control outputs:

```text
control_pairwise_response.csv
control_summary.csv
```

Specificity contrast outputs:

```text
specificity_contrast_summary.csv
specificity_pairwise_contrast.csv
```

The `runs/` directory is treated as local machine output and may remain untracked unless explicitly added later.

---

## 4. Specificity contrast implementation

The LIC01-F layer compares:

```text
reference:
  structured_local_phase_response
```

against the non-reference controls:

```text
global_phase_shift
random_phase
amplitude_preserved_phase_randomized
label_shuffle
```

The new contrast layer reports:

```text
rho_tau_reference
rho_tau_control
rho_tau_delta
rho_tau_ratio
tau_rel_reference
tau_rel_control
tau_rel_delta
pairwise_pattern_correlation
rank_separation_score
specificity_status
warning
```

The important methodological improvement is that raw `rho_tau` contrast is reported before treating `tau_rel_candidate` as a readable candidate field.

This avoids overinterpreting normalized `tau_rel_candidate` values as evidence of specificity.

---

## 5. Acceptance summary

The LIC01-F acceptance log showed that the runner still executed correctly and that existing outputs were preserved.

Minimal-run values remained:

```text
nodes: 8
pair_count: 64
sweep_row_count: 576
rho_tau_min: 0.139720252494
rho_tau_max: 1.41170547988
tau_rel_candidate_min: 0
tau_rel_candidate_max: 1
```

New specificity summary fields were present:

```text
specificity_contrast_summary_file: specificity_contrast_summary.csv
specificity_pairwise_contrast_file: specificity_pairwise_contrast.csv
specificity_reference_family: structured_local_phase_response
specificity_control_families:
  global_phase_shift
  random_phase
  amplitude_preserved_phase_randomized
  label_shuffle
specificity_established: False
```

New specificity outputs parsed successfully:

```text
specificity_contrast_summary.csv: 4 rows
specificity_pairwise_contrast.csv: 256 rows
```

Existing output regression check passed.

The `readout.md` contained:

```text
## Specificity Readout
```

The claim-risk grep returned only boundary and warning contexts. `git diff --check` passed.

---

## 6. Specificity status labels

The acceptance output reported the following specificity status labels:

```text
global_phase_shift: control_exceeds_reference_warning
random_phase: control_exceeds_reference_warning
amplitude_preserved_phase_randomized: control_exceeds_reference_warning
label_shuffle: small_kernel_ambiguity_warning
```

Warnings reported:

```text
global_phase_shift:
  synthetic specificity remains conservative/open for this control

random_phase:
  synthetic specificity remains conservative/open for this control

amplitude_preserved_phase_randomized:
  synthetic specificity remains conservative/open for this control

label_shuffle:
  synthetic specificity remains conservative/open for this control;
  small synthetic systems can make label-shuffle specificity ambiguous
```

These labels are not implementation failures. They are the main scientific result of the LIC01-F contrast layer.

---

## 7. Befund

The LIC01-F specificity contrast layer is technically implemented and reproducible.

It adds two new output files:

```text
specificity_contrast_summary.csv
specificity_pairwise_contrast.csv
```

The output row counts match expectation:

```text
4 non-reference controls = 4 rows in specificity_contrast_summary.csv
4 controls × 64 source-target pairs = 256 rows in specificity_pairwise_contrast.csv
```

The existing minimal and control outputs were not broken by the extension.

Most importantly:

```text
specificity_established: false
```

Several controls are close to or exceed the structured local phase-response reference.

---

## 8. Interpretation

The specificity contrast layer makes the current limitation sharper.

Before LIC01-F, the project could say:

```text
The tau/epsilon diagnostic can be compared against controls.
```

After LIC01-F, the project must say:

```text
The tau/epsilon diagnostic is technically control-comparable, but the tested specificity contrast does not establish diagnostic specificity.
```

This means the current `rho_tau(A,B)` / `tau_rel_candidate(A,B)` construction is not yet selective enough to distinguish structured local phase response from several tested synthetic controls.

This is a scientifically useful negative or cautionary result.

It prevents the project from prematurely treating `tau_rel_candidate` as a robust relational-delay carrier.

---

## 9. Hypothese

The warning result may have several possible causes:

```text
1. The current response observable is too broad.
2. The normalization may wash out useful structure.
3. The rho_tau score may measure generic perturbation sensitivity.
4. The tau_rel transform may compress differences.
5. The 8-node synthetic kernel may be too small or too symmetric.
6. The control operators may preserve too much structure.
7. Global phase is not sufficiently removed by the current observable.
8. Source-target locality is not yet sharply defined.
```

A refined future diagnostic may need to separate:

```text
raw response strength
relative phase structure
global-phase-invariant response
source-target locality
pattern correlation
rank separation
kernel-family dependence
```

The working hypothesis becomes:

> `tau_rel_candidate` may remain useful only if a later observable or contrast statistic can show that structured local phase/correlation response separates from global, random, phase-randomized, and label-shuffled controls.

At LIC01-F, this remains unproven.

---

## 10. Offene Lücke

Open issues after LIC01-F:

1. **Diagnostic specificity remains open**  
   The tested contrast layer did not establish specificity.

2. **Controls may exceed the structured reference**  
   Several controls are not merely close; they are labeled as exceeding the structured reference.

3. **Global phase issue**  
   If global phase produces strong response, the observable may not be sufficiently relative-phase or gauge-like.

4. **Random phase issue**  
   If random phase exceeds or matches structured response, the diagnostic may be measuring generic phase sensitivity.

5. **Amplitude-preserved phase-randomized issue**  
   If randomized phase organization remains strong, phase organization specificity is not yet demonstrated.

6. **Small-kernel ambiguity**  
   The 8-node synthetic kernel may be too small, symmetric, or distributionally simple.

7. **No distance comparator**  
   `D(A,B)` is still not attached.

8. **No interval candidate**  
   `S_rel2_candidate` remains intentionally not constructed.

9. **No Lorentz-compatibility test**  
   No covariance, invariance, or inertial-frame behavior is established.

10. **No physical validation**  
   The run remains synthetic and does not use real physical or experimental data.

---

## 11. Claim Boundary

LIC01-F supports only the following bounded statement:

> The QSB-ST-LIC01 tau/epsilon runner now includes a reproducible specificity contrast layer that compares structured local phase-response against global, random, phase-randomized, and label-shuffled controls using raw response contrasts and pairwise comparison statistics.

LIC01-F does **not** support the following claims:

```text
tau_rel_candidate is physical time.
tau_rel_candidate is proper time.
QSB derives a Lorentzian metric.
QSB validates spacetime emergence.
QSB validates a physical Bridge.
QSB demonstrates real-data or experimental validity.
QSB proves diagnostic specificity.
QSB proves Lorentz behavior.
S_rel2 is physically meaningful in this run.
```

The strongest current statement is:

```text
specificity contrast layer implemented: yes
specificity established: no
physical interpretation: no
```

---

## 12. Recommended next step

The next step should not be `D(A,B)` attachment or `S_rel2_candidate` construction.

The next step should investigate why controls remain close to or exceed the structured reference.

Recommended next planning block:

```text
QSB-ST-LIC01-G tau/epsilon observable and normalization audit
```

Possible next file:

```text
docs/QSB_ST_LIC01_TAU_EPSILON_OBSERVABLE_NORMALIZATION_AUDIT_PLAN.md
```

Candidate audit questions:

```text
Is the row/column observable too broad?
Should global phase be divided out?
Should response be computed on relative phase differences?
Should rho_tau be replaced or supplemented by a pattern-specific statistic?
Should normalization be shared across families instead of family-local?
Should a less symmetric synthetic kernel family be introduced?
```

A reasonable LIC01-G path is:

```text
1. Do not change physical interpretation.
2. Audit observable definitions.
3. Audit normalization choices.
4. Add global-phase-invariant candidate observable.
5. Add small kernel-family sweep only after the observable issue is understood.
```

---

## 13. Current status label

After committing this result note, the recommended status label is:

```text
LIC01_tau_epsilon_specificity_contrast_documented_specificity_not_established
```
