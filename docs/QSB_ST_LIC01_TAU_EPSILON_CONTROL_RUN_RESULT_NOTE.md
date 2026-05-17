# QSB-ST-LIC01 Tau/Epsilon Control Run Result Note

**Block:** QSB-ST-LIC01-E / LIC01_tau_epsilon_control_runner_extension  
**Run:** `tau_epsilon_phase_response_open`  
**Previous status:** `LIC01_tau_epsilon_controls_planned_not_implemented`  
**Status after run:** `LIC01_tau_epsilon_controls_implemented_and_run_checked`  
**Date:** 2026-05-17  
**Document type:** Result note / synthetic control-run documentation  
**Claim level:** Synthetic diagnostic control result only; no physical time, Lorentz metric, spacetime, or validation claim.

---

## 1. Purpose

This note documents the first control extension of the QSB-ST-LIC01 tau/epsilon phase-response runner.

The previous minimal run established that the synthetic pipeline can compute:

```text
rho_tau(A,B)
tau_rel_candidate(A,B)
```

from a controlled local phase perturbation of a synthetic reference kernel.

LIC01-E extends this by adding a first control suite. The purpose is not to prove physical significance, but to test whether the current response diagnostic is distinguishable from trivial, random, phase-randomized, or label-shuffled alternatives.

---

## 2. Files involved

### 2.1 Planning document

```text
docs/QSB_ST_LIC01_TAU_EPSILON_CONTROL_EXTENSION_PLAN.md
```

### 2.2 Modified runner

```text
scripts/run_qsb_st_lic01_tau_epsilon_phase_response.py
```

### 2.3 Config

```text
data/qsb_st_lic01_tau_epsilon_phase_response_config.yaml
```

### 2.4 Output directory

```text
runs/QSB-ST-LIC01/tau_epsilon_phase_response_open/
```

### 2.5 New/updated output files

```text
summary.json
readout.md
config_resolved.json
tau_epsilon_pairwise_response.csv
tau_epsilon_response_sweep.csv
tau_rel_candidate_matrix.csv
control_pairwise_response.csv
control_summary.csv
```

The `runs/` directory is treated as machine output and may remain untracked unless explicitly added later.

---

## 3. Control families implemented

The runner now implements the following five control families:

```text
structured_local_phase_response
global_phase_shift
random_phase
amplitude_preserved_phase_randomized
label_shuffle
```

### 3.1 `structured_local_phase_response`

This is the structured reference condition and corresponds to the original local source-centered phase perturbation.

### 3.2 `global_phase_shift`

This applies a global phase factor and tests whether the diagnostic is overly sensitive to uniform phase changes.

### 3.3 `random_phase`

This applies reproducible random phase perturbations and tests whether the response field is distinguishable from seeded phase noise.

### 3.4 `amplitude_preserved_phase_randomized`

This preserves amplitudes while perturbing/randomizing phase organization, testing whether the diagnostic depends on phase organization rather than amplitude alone.

### 3.5 `label_shuffle`

This applies a reproducible label/identity shuffle and tests whether source-target identity is meaningful in the small synthetic system.

---

## 4. Run and acceptance summary

Codex reported the following acceptance result:

```text
Compile: bestanden
Runner: bestanden
Minimalwerte erhalten:
  synthetic_node_count=8
  pair_count=64
  sweep_row_count=576
  tau_rel_constructed=true
  S_rel2_constructed=false

summary.json Kontrollfelder: OK
control_pairwise_response.csv: 320 Rows
control_summary.csv: 5 Rows
Kontrollfamilien: alle 5 erwartet
readout.md enthält ## Control Readout
git diff --check: bestanden
```

The expected row counts are internally consistent:

```text
5 control families × 64 source-target pairs = 320 control_pairwise_response rows
5 control families = 5 control_summary rows
```

The repository status after implementation and acceptance showed only the runner as modified:

```text
## main...origin/main
 M scripts/run_qsb_st_lic01_tau_epsilon_phase_response.py
```

---

## 5. Summary control fields

The acceptance log reported the following new `summary.json` control fields:

```text
controls_implemented:
  structured_local_phase_response
  global_phase_shift
  random_phase
  amplitude_preserved_phase_randomized
  label_shuffle

control_family_count: 5
control_pairwise_response_file: control_pairwise_response.csv
control_summary_file: control_summary.csv
structured_reference_family: structured_local_phase_response
```

Control status labels:

```text
structured_local_phase_response: structured_reference
global_phase_shift: control_close_to_structured_warning
random_phase: control_close_to_structured_warning
amplitude_preserved_phase_randomized: control_close_to_structured_warning
label_shuffle: control_close_to_structured_warning
```

Warnings reported:

```text
global_phase_shift:
  Control response is close to structured reference; diagnostic specificity is not established for this control.

random_phase:
  Control response is close to structured reference; diagnostic specificity is not established for this control.

amplitude_preserved_phase_randomized:
  Control response is close to structured reference; diagnostic specificity is not established for this control.

label_shuffle:
  Small synthetic systems can make label-shuffle controls ambiguous; interpret as a label/identity diagnostic only.
```

---

## 6. Befund

The LIC01-E runner extension is technically successful.

It adds a transparent first control suite and produces the expected control outputs:

```text
control_pairwise_response.csv
control_summary.csv
```

The control outputs parse successfully and contain the expected row counts.

The previous minimal output path remains intact:

```text
synthetic_node_count: 8
pair_count: 64
sweep_row_count: 576
tau_rel_constructed: true
S_rel2_constructed: false
```

The runner therefore now supports comparison of the structured local phase-response diagnostic against a first set of synthetic controls.

---

## 7. Interpretation

The control implementation is methodologically useful, but the first control result is cautionary.

Several controls are close to the structured reference. Therefore the current `rho_tau` / `tau_rel_candidate` construction does **not** yet show strong diagnostic specificity under the tested synthetic controls.

The technically correct interpretation is:

> LIC01-E establishes that control comparison is implemented and reproducible, but it does not establish that the current response diagnostic is specific to structured local phase response.

This warning is important. It suggests that the current observable, normalization, perturbation design, or synthetic reference kernel may still be too permissive or too insensitive to distinguish structured from unstructured/control perturbations.

---

## 8. Hypothese

A future refinement may improve specificity if it changes one or more of the following:

```text
response observable
normalization rule
control construction
synthetic kernel structure
phase-response score
source-target locality definition
threshold-free comparison statistic
```

The working hypothesis becomes:

> `tau_rel_candidate` may remain a useful relational-delay diagnostic only if later controls show that the response field is not merely a generic consequence of phase perturbation, normalization, or small-system symmetry.

At LIC01-E this remains open.

---

## 9. Offene Lücke

The following limitations remain:

1. **Specificity not established**  
   Multiple controls remain close to the structured reference.

2. **Global phase sensitivity warning**  
   The global phase control being close to structured reference may indicate that the observable is too sensitive to phase convention or aggregate phase movement.

3. **Random phase warning**  
   Random phase response being close to structured reference weakens any claim that the current diagnostic captures a uniquely structured response.

4. **Amplitude-preserved phase-randomized warning**  
   If amplitude-preserved randomized phase remains close to structured reference, phase-organization specificity is not yet demonstrated.

5. **Label-shuffle ambiguity**  
   In a small synthetic system, label shuffle can be ambiguous and should not be overinterpreted.

6. **No distance comparator**  
   `D(A,B)` is still not attached.

7. **No interval candidate**  
   `S_rel2_candidate` remains intentionally not constructed.

8. **No Lorentz-compatibility test**  
   The control suite does not test covariance, invariance, or behavior between inertial systems.

9. **No empirical relevance claim**  
   The run remains synthetic and does not use real physical or experimental data.

---

## 10. Claim Boundary

This run supports only the following bounded statement:

> Under the tested synthetic control families, the LIC01 tau/epsilon response diagnostic can be compared against global, random, phase-randomized, and label-shuffled controls. The first control suite is technically implemented and reproducible.

This run does **not** support the following claims:

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

The strongest current interpretation is:

```text
technically implemented: yes
control comparison available: yes
diagnostic specificity established: no
physical interpretation: no
```

---

## 11. Recommended next step

The next step should address the warning that several controls remain close to the structured reference.

Recommended next planning block:

```text
QSB-ST-LIC01-F tau/epsilon specificity refinement plan
```

Possible next file:

```text
docs/QSB_ST_LIC01_TAU_EPSILON_SPECIFICITY_REFINEMENT_PLAN.md
```

That plan should inspect and decide between at least three possible routes:

```text
1. revise the response observable,
2. revise the normalization / scoring,
3. add a structured-vs-control contrast statistic.
```

A useful next diagnostic may be a threshold-free contrast layer, for example:

```text
structured_control_mean_delta
structured_control_rank_separation
pairwise_pattern_correlation
source_target_locality_contrast
```

Only after the control specificity issue is understood should LIC01 proceed toward attaching `D(A,B)` or constructing `S_rel2_candidate`.

---

## 12. Current status label

After committing the control-runner extension and this result note, the recommended status label is:

```text
LIC01_tau_epsilon_controls_documented_specificity_open
```
