# QSB-BRIDGE-DATA-02A Result Note

## 1. Purpose

QSB-BRIDGE-DATA-02A creates a synthetic/reference-style sp2 contrast scaffold for benzene versus C60.

The block is designed to test controlled contrast data before any later real DATA-02 work. It is not real-data validation, physical validation, or molecular validation.

## 2. Expected Outputs

The DATA-02A implementation is configured to produce:

```text
data/QSB-BRIDGE-DATA-02A/benzene_nodes.csv
data/QSB-BRIDGE-DATA-02A/benzene_edges.csv
data/QSB-BRIDGE-DATA-02A/c60_nodes.csv
data/QSB-BRIDGE-DATA-02A/c60_edges.csv
data/QSB-BRIDGE-DATA-02A/c60_faces.csv
data/QSB-BRIDGE-DATA-02A/sp2_contrast_manifest.json
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/summary.json
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/readout.md
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/sp2_family_summary.csv
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/bond_class_summary.csv
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/face_environment_summary.csv
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/proxy_risk_summary.csv
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/resolved_config.json
```

## 3. Required C60 Validation

The C60 scaffold must pass:

```text
node_count = 60
edge_count = 90
all node degrees = 3
face_count = 32
pentagon_count = 12
hexagon_count = 20
Euler check: V - E + F = 2
bond_class_counts:
  6_6 = 30
  5_6 = 60
```

If the exact C60 scaffold cannot be generated and validated, the run must report:

```text
stop_go_outcome: requires_exact_c60_scaffold_before_use
```

## 4. Required Carry-Forward From 05C

DATA-02A must carry forward the QSB-BRIDGE-NUM-05C warning:

```text
local-neighborhood sensitivity under small additive magnitude noise at 0.02
```

## 5. Future Result Discussion Requirement

A separate DATA-02A result discussion should be created only after reading the DATA-02A outputs.

That future discussion must include a human-readable Bauchbild. It should explain DATA-02A as a controlled contrast bench: benzene is the small planar ring reference, C60 is the curved cage reference, and the scaffold checks whether labels, controls, and proxy risks are clean before any real-data interpretation is attempted.

## 6. Claim Boundary

DATA-02A is synthetic/reference-style scaffold data only.

It does not establish real-data validation, physical validation, molecular validation, spacetime emergence, physical metric recovery, causal structure, de-Broglie confirmation, or real quantum dynamics.
