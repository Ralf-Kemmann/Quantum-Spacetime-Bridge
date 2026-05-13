# QSB-BRIDGE-DATA-02A Result Discussion

## 1. Purpose

This discussion note separates the QSB-BRIDGE-DATA-02A scaffold readout from its cautious interpretation.

It uses the existing DATA-02A artifacts only:

```text
docs/QSB_BRIDGE_DATA_02A_TESTDATA_SCAFFOLD_PLAN.md
docs/QSB_BRIDGE_DATA_02A_RESULT_NOTE.md
data/QSB-BRIDGE-DATA-02A/sp2_contrast_manifest.json
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/summary.json
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/readout.md
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/sp2_family_summary.csv
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/bond_class_summary.csv
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/face_environment_summary.csv
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/proxy_risk_summary.csv
```

No new numerical test is introduced here.

DATA-02A is synthetic/reference-style scaffold only. It is not real-data validation, physical validation, or molecular validation.

## 2. Befund

The DATA-02A run reports:

```text
stop_go_outcome: go_scaffold_generated_with_exact_c60_validation
external_data_downloaded: false
no_realdata_validation_claim: true
no_physical_validation_claim: true
no_molecular_validation_claim: true
```

The benzene scaffold validation reports:

```text
node_count = 6
edge_count = 6
all degrees = 2
degree_distribution = {2: 6}
passed = true
```

The C60 scaffold validation reports:

```text
node_count = 60
edge_count = 90
all degrees = 3
degree_distribution = {3: 60}
face_count = 32
pentagon_count = 12
hexagon_count = 20
Euler characteristic = 2
bond_class_counts:
  5_6 = 60
  6_6 = 30
passed = true
```

The scaffold therefore passes the exact structural checks required for DATA-02A. This is a scaffold validity result, not a molecular validation result.

The proxy risk summary marks:

```text
coordinate_distance_reference_kernel: reference/control only, high geometry-smuggling risk
graph_distance_reference_kernel: reference/control only, high geometry-smuggling risk
bond_class_weighted_proxy: synthetic contrast proxy only
local_environment_proxy: synthetic local label proxy only
spectral_graph_toy_proxy: toy graph diagnostic only
phase_loop_toy_proxy: toy loop/phase scaffold only
```

The 05C warning is carried forward:

```text
local-neighborhood sensitivity under small additive magnitude noise at 0.02
```

## 3. Human-readable Bauchbild / Intuition

DATA-02A builds a clean chemical training bench.

Benzene is the small flat sp2 resonator: six carbon nodes, six ring edges, and a simple planar aromatic scaffold. It is the small training tile where a later diagnostic can see whether it recognizes a uniform planar ring organization without pretending that this is independent evidence from measured molecular data.

C60 is the exact curved sp2 cage: sixty carbon nodes, ninety edges, twelve pentagons, twenty hexagons, and two bond environments. It is the larger curved training tile where a later diagnostic can see whether cage organization, face environment, and bond-class structure are handled cleanly.

The useful image is not a molecule proof. It is two calibrated training tiles on the bench:

```text
benzene = small flat ring tile
C60     = exact curved cage tile
```

The question is not:

```text
does QSB validate molecules?
```

The question is:

```text
can later diagnostics distinguish planar aromatic organization from curved
fullerene cage organization without pretending this is independent real-data
evidence?
```

That distinction matters. DATA-02A gives the project a clean bench, not a physical result.

## 4. Interpretation

DATA-02A is stronger than DATA-01 because it creates actual local scaffold tables. DATA-01 was a preflight over candidate source types, provenance requirements, and proxy risks. DATA-02A now adds concrete benzene and C60 scaffold tables that later scripts can read.

But the block remains synthetic/reference-style. The data are constructed as controlled scaffold material. They are not measured molecular data.

The exact C60 validation is important. Approximate or decorative fullerene data would be unusable because later diagnostics could react to construction mistakes rather than fullerene structure. Here, the reported C60 scaffold satisfies the required node, edge, degree, face, Euler, and bond-class checks.

Benzene and C60 form a chemically meaningful sp2 contrast pair at the scaffold level:

```text
benzene: planar aromatic ring organization
C60: curved fullerene cage organization
```

That contrast can support later method tests. It cannot itself support physical or molecular validation claims.

The random and shuffle control families are declared scaffold families in DATA-02A. If they are not instantiated as full graph controls in this block, that should remain explicit. A later DATA-02B could generate actual control instances for matched random sp2 controls, degree-preserving random controls, bond-class shuffles, and curvature-label shuffles.

## 5. Misstrauen / Self-deception risks

The scaffold data are constructed, not measured.

C60 exactness does not make DATA-02A real-data validation. It only means the reference scaffold is internally consistent enough to use as controlled test material.

Bond classes and local environment labels can encode the target distinction. If a later diagnostic succeeds mainly because the labels directly carry the benzene/C60 contrast, the result is label recognition, not independent structure recovery.

Coordinate-distance and graph-distance kernels remain circular if used as independent evidence. They are reference/control channels only. They can help check a pipeline, but they cannot prove that geometry was recovered from independent physical input.

Declared controls are not the same as fully executed null ensembles. A family name such as `degree_preserving_random_control` is only a scaffold declaration until actual control instances are generated and read out.

No vibrational, spectral, or quantum chemistry data are used yet. DATA-02A does not contain measured modes, spectral assignments, QC matrix outputs, or an independent real-source `K_ij`.

The 05C local-neighborhood sensitivity must remain visible. A later method could look acceptable in broad contrast while local neighborhoods or bond environments wobble under small magnitude perturbations.

## 6. Hypothese

The cautious working hypothesis after DATA-02A is:

```text
The benzene/C60 sp2 contrast scaffold may be useful as a method-level
training bench if later diagnostics can separate planar ring organization
from curved cage organization while keeping reference/control channels
labeled as circular or synthetic.
```

This is a method-level hypothesis. It is not molecular validation.

## 7. Offene Luecken

Open gaps after DATA-02A:

```text
No external data were downloaded.
No measured molecular data are used.
No vibrational modes are used.
No spectral data are used.
No quantum chemistry matrix outputs are used.
No DATA-02B control ensemble has been generated yet.
No independent K_ij proxy from real sources has been constructed.
No physical validation has been performed.
```

The main remaining gap is the difference between a clean scaffold bench and independent source data. DATA-02A solves the scaffold problem, not the real-data problem.

## 8. Consequences for next blocks

DATA-02B could instantiate controls and first diagnostics on the scaffold:

```text
matched random sp2 control
degree-preserving random control
bond-class shuffle
curvature-label shuffle
```

DATA-02B should remain scaffold-level, not real-data validation.

A separate later source-acquisition block is still needed for real normal-mode, spectral, or quantum chemistry data. That later block would need provenance, machine-readable fields, uncertainty notes, and explicit separation between reference geometry and `K_ij` input.

Any later `K_ij` proxy must label coordinate and graph channels as reference/control only. If those channels are used, the interpretation must say that they are circular or synthetic.

DATA-02B must report local-neighborhood sensitivity because of the 05C warning:

```text
local-neighborhood sensitivity under small additive magnitude noise at 0.02
```

## 9. Claim Boundary

DATA-02A provides no real-data validation.

It does not establish:

```text
physical validation
molecular validation
spacetime emergence
physical metric recovery
causal structure
de-Broglie confirmation
real quantum dynamics
```

DATA-02A supports only a synthetic/reference scaffold statement: a validated benzene/C60 sp2 contrast bench has been generated for later controlled method tests.
