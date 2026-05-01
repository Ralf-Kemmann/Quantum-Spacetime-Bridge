# BMS-IE01 — Isoelectronic Matter-Information Test Specification

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_IE01_ISOELECTRONIC_MATTER_INFORMATION_TEST_SPEC.md`  
Status: Specification only; no numerical run completed in this note.

---

## 1. Purpose

This specification defines a small iso-electronic diagnostic block for the de Broglie matter-signature / bridge-information line of the project.

The central question is:

```text
Does a bridge-readable matter signature collapse under equal or similar electron occupation,
or do nuclear charge, mass scale, and coupling scale remain distinguishable as relational
structure information?
```

The test is meant as a controlled complement to the earlier isotope and carbon-structure tests.

This note does not claim physical spacetime emergence, chemical identity recognition, metric recovery, causal structure, or a continuum limit.

---

## 2. Relation to earlier matter-signature tests

The current project already contains matter-signature test families for:

```text
generic de Broglie matter signatures
isotopic variants
carbon isotope / carbon-structure variants
strontium isotope variants
quantum-chemical / shell / valence extensions
van-der-Waals extensions
```

The iso-electronic block adds an orthogonal control axis.

### 2.1 Isotope tests

Isotope tests keep the chemical element identity approximately fixed while changing neutron number and mass.

Working question:

```text
If the electron structure remains similar but mass changes, does the bridge-readable
signature respond to the changed matter-wave scale?
```

Internal image:

```text
same chemical name, different matter-wave clock
```

### 2.2 Carbon structure tests

Carbon tests keep the element fixed while changing structural organization.

Working question:

```text
If the same element forms different local structures, does the bridge-readable signature
preserve structural information rather than only mass information?
```

Internal image:

```text
same building material, different architecture
```

### 2.3 Iso-electronic tests

Iso-electronic tests keep electron count or shell occupation fixed or similar while changing nuclear charge, mass scale, ionic charge state, and coupling scale.

Working question:

```text
If the electronic occupation is held constant or nearly constant, does the bridge-readable
signature still distinguish the different nuclear/coupling centers?
```

Internal image:

```text
same electron mask, different nucleus behind it
```

---

## 3. Scientific framing

The iso-electronic test should be interpreted as a matter-information diagnostic.

Allowed language:

```text
iso-electronic control family
matter-information diagnostic
bridge-readable scale information
electron-count-controlled comparison
coupling-scale diagnostic
construction-qualified signal
```

Disallowed language without much stronger evidence:

```text
the bridge recognizes ions
spacetime stores chemistry
physical geometry is proven
isoelectronic specificity is proven
metric structure is recovered
causal structure is recovered
Lorentzian structure is recovered
```

Safe one-sentence description:

```text
Iso-electronic systems are used as controlled comparison families to test whether
bridge-readable matter signatures are exhausted by electron-count similarity or remain
sensitive to mass-, charge-, and coupling-scale differences.
```

---

## 4. Candidate iso-electronic families

The first implementation should use small, transparent families rather than large chemistry-heavy sets.

### 4.1 Helium-like family

Candidate systems:

```text
He
Li+
Be2+
B3+          optional extension
```

All members are two-electron systems in the idealized atomic/ionic sense.

Advantages:

```text
small family
clear electron count
simple conceptual interpretation
strong nuclear-charge gradient
```

Limitations:

```text
ionization state must be represented explicitly
highly charged ions are idealized comparison objects
environmental stability is not modeled unless explicitly added
```

Recommended first-pass status:

```text
primary first-pass family
```

### 4.2 Neon-like family

Candidate systems:

```text
N3-
O2-
F-
Ne
Na+
Mg2+
Al3+         optional extension
```

All members are formally ten-electron systems.

Advantages:

```text
classic iso-electronic sequence
larger nuclear-charge and mass range
neutral atom included as central anchor
```

Limitations:

```text
high negative/positive charge states require careful model annotation
ionic radius and environment may dominate in realistic settings
```

Recommended first-pass status:

```text
secondary family after helium-like smoke test
```

### 4.3 Argon-like family

Candidate systems:

```text
Cl-
Ar
K+
Ca2+
```

Advantages:

```text
chemically familiar iso-electronic family
moderate charge states
```

Limitations:

```text
larger atoms introduce more shell/radius/model choices
```

Recommended first-pass status:

```text
optional follow-up family
```

---

## 5. Minimal first-pass family recommendation

For BMS-IE01-v0, use the helium-like family:

```text
He
Li+
Be2+
```

Optional fourth member:

```text
B3+
```

The first-pass question is:

```text
Do He, Li+, and Be2+ collapse to nearly identical bridge-readable signatures under equal
electron count, or does increasing nuclear charge and mass produce a distinguishable
monotonic or structured signature change?
```

---

## 6. Conceptual variables

The runner should not pretend to perform ab initio chemistry unless that model is explicitly implemented.

The minimal diagnostic variables are:

```text
electron_count
nuclear_charge_Z
mass_u
ionic_charge
temperature_K
speed_model
debroglie_wavelength
kinetic_energy
frequency_proxy
coupling_proxy
length_scale_proxy
signature_score
```

Optional later variables:

```text
ionic_radius_pm
effective_nuclear_charge_proxy
ionization_energy_eV
polarizability_proxy
shell_label
environment_label
```

---

## 7. Input schema draft

Recommended input file:

```text
data/bms_ie01_isoelectronic_species.csv
```

Recommended fields:

| field name | type | description |
|---|---:|---|
| `species_id` | string | Stable machine-readable species identifier, e.g. `He`, `Li_plus`, `Be_2plus`. |
| `family_id` | string | Iso-electronic family label, e.g. `helium_like`, `neon_like`. |
| `display_label` | string | Human-readable species label, e.g. `Li+`. |
| `element_symbol` | string | Chemical element symbol. |
| `nuclear_charge_Z` | integer | Proton number / nuclear charge. |
| `mass_u` | float | Atomic or ionic mass proxy in unified atomic mass units. |
| `electron_count` | integer | Number of bound electrons in the idealized species. |
| `ionic_charge` | integer | Net charge state; positive for cations, negative for anions. |
| `shell_label` | string | Optional shell configuration family label, e.g. `1s2`, `Ne_like`. |
| `include_in_v0` | boolean | Whether this species is included in the first smoke-test run. |
| `notes` | string | Methodological notes, assumptions, caveats. |

---

## 8. Config schema draft

Recommended config file:

```text
data/bms_ie01_isoelectronic_config.yaml
```

Recommended fields:

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory under `runs/`. |
| `run.random_seed` | integer | Seed for any stochastic controls. |
| `inputs.species_table` | string | Path to iso-electronic species table. |
| `conditions.temperature_K` | float | Temperature used for thermal velocity / kinetic scale proxy. |
| `conditions.pressure_mbar` | float | Optional pressure context; may be unused in ion-only v0. |
| `conditions.volume_m3` | float | Optional volume context; may be unused in ion-only v0. |
| `model.speed_model` | string | Velocity model, e.g. `rms`, `mean`, `fixed_reference`. |
| `model.frequency_mode` | string | Frequency proxy mode, e.g. `kinetic_energy_based`, `omega_from_v_over_lambda`. |
| `model.coupling_proxy_mode` | string | Charge/coupling proxy mode, e.g. `Z_only_proxy`, `Z_over_radius_proxy`. |
| `model.normalize_within_family` | boolean | Whether scores are normalized per iso-electronic family. |
| `outputs.scan_csv` | string | Main per-species scan output. |
| `outputs.family_summary_csv` | string | Per-family summary table. |
| `outputs.pairwise_csv` | string | Pairwise signature-distance output. |
| `outputs.claims_json` | string | Machine-readable conservative claim labels. |
| `outputs.readout_md` | string | Human-readable result note. |
| `outputs.state_json` | string | Run manifest / method state. |

---

## 9. Output schema draft

Recommended output directory:

```text
runs/BMS-IE01/isoelectronic_matter_information_open/
```

Recommended output files:

```text
bms_ie01_isoelectronic_scan.csv
bms_ie01_family_summary.csv
bms_ie01_pairwise_signature_distances.csv
bms_ie01_claims.json
bms_ie01_readout.md
bms_ie01_state.json
bms_ie01_warnings.json
```

### 9.1 `bms_ie01_isoelectronic_scan.csv`

| field name | type | description |
|---|---:|---|
| `run_id` | string | Run identifier. |
| `family_id` | string | Iso-electronic family label. |
| `species_id` | string | Species identifier. |
| `display_label` | string | Human-readable species label. |
| `nuclear_charge_Z` | integer | Proton number. |
| `mass_u` | float | Mass proxy in unified atomic mass units. |
| `electron_count` | integer | Electron count. |
| `ionic_charge` | integer | Ion charge state. |
| `temperature_K` | float | Temperature used for kinetic proxy. |
| `speed_model` | string | Velocity model used. |
| `frequency_mode` | string | Frequency proxy mode used. |
| `debroglie_wavelength_m` | float | Computed de Broglie wavelength proxy. |
| `kinetic_energy_J` | float | Computed kinetic-energy proxy. |
| `frequency_proxy_Hz` | float | Frequency proxy. |
| `mass_scale_score` | float | Normalized mass-scale contribution. |
| `charge_coupling_score` | float | Normalized charge/coupling contribution. |
| `length_scale_score` | float | Normalized length/de Broglie scale contribution. |
| `signature_score` | float | Combined bridge-readable matter-signature proxy. |
| `warning_flags` | string | Semicolon-separated warnings for this species. |

### 9.2 `bms_ie01_family_summary.csv`

| field name | type | description |
|---|---:|---|
| `run_id` | string | Run identifier. |
| `family_id` | string | Iso-electronic family label. |
| `n_species` | integer | Number of species included in the family. |
| `electron_count_mode` | integer | Shared electron count for the family. |
| `min_Z` | integer | Minimum nuclear charge. |
| `max_Z` | integer | Maximum nuclear charge. |
| `min_mass_u` | float | Minimum mass proxy. |
| `max_mass_u` | float | Maximum mass proxy. |
| `signature_range` | float | Max minus min signature score. |
| `signature_cv` | float | Coefficient of variation of signature score. |
| `monotonic_vs_Z` | boolean | Whether signature score is monotonic with Z. |
| `monotonic_vs_mass` | boolean | Whether signature score is monotonic with mass. |
| `collapse_index` | float | Small value indicates near-collapse under iso-electronic control. |
| `decision_label` | string | Conservative readout label. |

### 9.3 `bms_ie01_pairwise_signature_distances.csv`

| field name | type | description |
|---|---:|---|
| `run_id` | string | Run identifier. |
| `family_id` | string | Iso-electronic family label. |
| `species_i` | string | First species identifier. |
| `species_j` | string | Second species identifier. |
| `delta_Z` | integer | Difference in nuclear charge. |
| `delta_mass_u` | float | Difference in mass proxy. |
| `delta_ionic_charge` | integer | Difference in ionic charge. |
| `signature_distance` | float | Distance between species in signature-feature space. |
| `mass_component_distance` | float | Mass-related contribution to distance. |
| `charge_component_distance` | float | Charge/coupling-related contribution to distance. |
| `length_component_distance` | float | Length/de Broglie contribution to distance. |

---

## 10. Decision labels

Recommended conservative labels:

```text
isoelectronic_collapse_supported
isoelectronic_noncollapse_supported
mixed_family_dependent_result
mass_scale_dominant_result
charge_coupling_sensitive_result
inconclusive_due_to_scope_or_warnings
```

Interpretation examples:

```text
Collapse:
  The tested iso-electronic family shows near-collapse of the bridge-readable signature
  under equal electron count in the current proxy model.

Non-collapse:
  The tested iso-electronic family does not collapse under equal electron count;
  nuclear charge, mass, or coupling-scale proxies remain distinguishable in the
  bridge-readable signature.

Mixed:
  The result depends on family, proxy mode, or normalization setting and should be
  treated as a model-sensitivity diagnostic.
```

---

## 11. Minimal runner design

Suggested file:

```text
scripts/run_bms_ie01_isoelectronic_matter_information.py
```

Suggested command:

```bash
python scripts/run_bms_ie01_isoelectronic_matter_information.py \
  --config data/bms_ie01_isoelectronic_config.yaml
```

The runner should:

```text
load species table
validate iso-electronic families
compute mass/de Broglie/energy/frequency proxies
compute charge/coupling proxy
normalize within family
compute combined signature score
compute pairwise signature distances
write scan, family summary, claims, readout, state, warnings
```

The first version should avoid hidden chemistry assumptions. Any chemical or quantum-chemical quantity not explicitly supplied in the input table must be omitted or represented as a clearly labelled proxy.

---

## 12. Acceptance criteria for BMS-IE01-v0

A first acceptable run should satisfy:

```text
at least one iso-electronic family
at least three species in the primary family
explicit electron_count field
explicit nuclear_charge_Z field
explicit mass_u field
explicit ionic_charge field
no hidden external chemistry lookup
all formulas documented in runner or companion field list
scan CSV written
family summary written
pairwise signature-distance table written
claim labels written
warnings written
```

The initial family should be:

```text
helium_like: He, Li+, Be2+
```

---

## 13. Recommended comparison to isotope results

After BMS-IE01-v0 is run, compare the readout to the isotope family:

```text
Isotope tests:
  fixed Z, changed mass

Iso-electronic tests:
  fixed electron count, changed Z and mass

Carbon structure tests:
  fixed element, changed topology / structural context
```

Three-axis matter-information matrix:

| axis | controlled feature | varied feature | question |
|---|---|---|---|
| isotope | element / electron structure | mass / neutron number | Is mass-wave information readable? |
| iso-electronic | electron count / shell occupation | nuclear charge / mass / coupling scale | Is the signature exhausted by electron-count similarity? |
| carbon structure | element | topology / structural organization | Is structural information preserved? |

---

## 14. Project-internal interpretation image

```text
Isotope:
  same name on the vial, different matter-wave clock

Carbon:
  same building material, different architecture

Iso-electronic:
  same electron mask, different nucleus behind it
```

Compact internal summary:

```text
BMS-IE01 tests whether the bridge reads only the electron mask,
or whether the different nucleus behind the same mask still leaves
a distinguishable relational trace.
```

---

## 15. Recommended next step

Create the minimal input table and config:

```text
data/bms_ie01_isoelectronic_species.csv
data/bms_ie01_isoelectronic_config.yaml
```

Then create the first runner:

```text
scripts/run_bms_ie01_isoelectronic_matter_information.py
```

and companion field-list note:

```text
docs/BMS_IE01_RUNNER_FIELD_LIST.md
```

Do not interpret BMS-IE01 as a physical-geometry result. It is a matter-information control block within the broader bridge-signature program.
