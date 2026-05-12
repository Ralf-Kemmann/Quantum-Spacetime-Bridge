# Deep Research Prompt — QSB Bridge Physics after 04A

Conduct a focused deep research scan for real datasets, methodological comparison systems, and literature-context relevant to the Quantum–Spacetime Bridge (QSB) project after the completed block **QSB-BRIDGE-NUM-04A Phase-Sensitive Toy Diagnostic**.

## Project context

The QSB project studies whether wave-based relational input structures can support geometrically readable organization through controlled graph, geometry, magnitude, and phase diagnostics.

Do **not** evaluate QSB as a proven theory of spacetime. Treat it as a methodological research framework requiring external datasets, stress tests, null models, and comparison cases.

The current internal bridge picture is:

1. Wave-based / de-Broglie-like motivation
2. Complex relational input `K_ij = A_ij exp(i phi_ij)`
3. Magnitude-only distance-like construction, e.g. `D_ij = -l0 log(|K_ij| + epsilon)`
4. Graph/geometry/proxy diagnostics from `|K_ij|`
5. Separate phase-sensitive / interference-like diagnostics from `phi_ij`
6. Conservative claim boundary: geometry proxy remains proxy; no physical spacetime metric, no causal structure, no de-Broglie confirmation, no physical emergence claim.

## New 04A calculation anchor

A new deterministic toy diagnostic was completed in block **QSB-BRIDGE-NUM-04A**.

Core setup:

- `n_nodes = 12`
- `l0 = 2.0`
- `tau = 0.35`
- fixed magnitude matrix `A_ij` across all variants
- only phase matrix `phi_ij` varied
- five phase variants:
  - `phase_zero`
  - `phase_linear_gradient`
  - `phase_random_low`
  - `phase_random_high`
  - `phase_vortex_like`

Core results:

- `magnitude_invariance_passed = True`
- `all_hermitian_checks_passed = True`
- `phase_sensitive_diagnostics_changed = True`
- `max_distance_diff_across_phase_variants = 0.0`
- `max_graph_jaccard_loss = 0.0`

Interpretation:

- With `|K_ij|` fixed, magnitude-only distance-like diagnostics and threshold graph structure remain invariant.
- Phase-sensitive toy diagnostics change across phase patterns.
- This supports only a methodological separation between magnitude-based geometry-readability proxies and phase-sensitive interference-like diagnostics.
- It does **not** establish physical emergence, metric recovery, causal structure, real quantum dynamics, or de-Broglie confirmation.

Use this 04A result as a search lens: find real or semi-real data situations where magnitude/graph structure and phase/spectral/mode structure can be separated, compared, or stress-tested.

## Research goals

Find immediately useful external datasets and methodological comparison systems for the next QSB bridge-physics blocks.

Focus especially on systems that provide at least two or more of the following:

- graph / bonding / adjacency structure
- weighted graph or interaction strength
- 3D molecular or crystal coordinates
- vibrational modes, phonon spectra, normal modes, or eigenvectors
- phase-like, mode-like, or complex-valued relational information
- symmetry / automorphism / group-theoretic information
- multiple comparable variants or polymorphs
- downloadable machine-readable data
- clear license/access pathway

## Priority domains

### 1. Carbon systems

Search for usable data on:

- C60 / Buckminsterfullerene
- other fullerenes
- graphene
- nanotubes
- graphite
- diamond
- amorphous carbon if useful
- carbon allotrope comparison datasets

Assess whether each source provides graph structure, coordinates, spectra, vibrational modes, phonons, symmetry data, or machine-readable files.

### 2. Molecular systems

Find molecules or molecule families useful for testing graph-to-geometry and graph-to-spectrum relationships:

- same or similar bonding graph with different conformers
- different molecules with similar distance/graph features but different spectra
- highly symmetric molecules with known normal modes
- molecules with public SDF/MOL/XYZ coordinates and vibrational data
- cases where phase/mode information adds distinctions not visible in graph magnitude alone

Include sources such as PubChem, NIST CCCBDB, QM9, GEOM, MoleculeNet, OpenBabel-compatible datasets, or relevant supplementary datasets.

### 3. Crystal and materials systems

Find open crystallographic/materials data useful for graph/geometry/spectrum comparison:

- Materials Project
- NOMAD
- AFLOW
- OQMD
- Crystallography Open Database
- phonon databases
- carbon polymorphs and structurally related materials

Prioritize datasets with structure files plus computed phonons, band structures, density of states, neighbor graphs, or symmetry metadata.

### 4. Stress-test cases for QSB methodology

Search specifically for cases involving:

- same/similar graph but different geometry
- same/similar geometry but different spectra
- isospectral or near-isospectral graphs/molecules/manifolds
- cospectral graphs with different embeddings
- graph automorphism / orbit structure relevant to C60 or fullerene patches
- spectrum-preserving but geometry-changing transformations
- null models used in graph geometry, molecular graphs, materials networks, or spectral graph theory

These are especially valuable because they can challenge overinterpretation of geometry proxies.

## Required output format

Produce a structured report with these sections:

### A. Executive summary

Summarize the most promising real-data route for QSB after 04A in 5–10 bullet points.

### B. Dataset table

For each dataset/source, provide a table row with:

- name
- URL / citation source
- domain: carbon / molecule / crystal / graph / spectral
- available fields
- access method: API, download, SDF, CIF, XYZ, JSON, CSV, HDF5, etc.
- license or access restrictions
- whether it has graph structure
- whether it has coordinates
- whether it has vibrational / phonon / spectral data
- whether it has symmetry / automorphism-relevant data
- QSB relevance
- concrete first QSB test
- limitations / risks
- priority score from 1 to 5

### C. 04A-specific relevance

Identify sources where the 04A separation can be made more realistic:

- fixed or comparable magnitude/adjacency structure with varying phase/mode/spectral information
- fixed graph with multiple geometries or conformers
- same geometry class with different spectra
- mode/eigenvector information that could serve as phase-sensitive analogue
- datasets that allow magnitude-only vs phase/mode-sensitive diagnostic comparison

### D. Top 5 immediately usable datasets

Rank the top five by practical usability for a next QSB import block. For each, give:

- why it is usable now
- first import format
- first script idea
- expected fields
- minimal acceptance criteria

### E. Top 5 methodological ideas

List five concrete next tests inspired by the literature/data scan. Each idea should include:

- test name
- required input data
- diagnostic readout
- null/control family
- expected failure mode
- conservative interpretation boundary

### F. Recommended next QSB data-import block

Propose one concrete next block after 04A, with a name like:

`QSB-BRIDGE-DATA-01 Carbon Structure/Spectrum Import Preflight`

or a better name if justified.

Include:

- goal
- input sources
- files to create
- scripts to write
- first run output
- acceptance checks
- claim boundary

### G. Literature and terminology map

Map relevant external terminology to QSB terminology, for example:

- overlap / kernel / correlation matrix
- graph embedding / distance geometry
- spectral graph theory
- quantum graph / molecular graph
- normal modes / phonons / eigenvectors
- information geometry
- relational geometry
- phase retrieval / magnitude-phase separation

Highlight terms that may cause confusion or priority-risk, and terms that help connect QSB defensively to existing literature.

### H. Claim boundary

End with a conservative statement suitable for the QSB documentation:

- what real-data use can support
- what it cannot support
- how to avoid overclaiming
- how to phrase 04A + real-data follow-up defensively

## Important constraints

- Do not hype QSB.
- Do not claim spacetime emergence is shown.
- Do not claim a physical metric is recovered.
- Do not claim causal structure is derived.
- Do not claim de-Broglie physics is confirmed.
- Treat all outputs as candidate datasets, methods, and stress tests.
- Prefer primary sources, official documentation, data portals, peer-reviewed papers, and well-maintained open repositories.
- Include citations/links for all sources.
- Flag paywalled or license-restricted sources clearly.
- Distinguish experimental data, computed data, synthetic benchmark data, and purely mathematical graph examples.
