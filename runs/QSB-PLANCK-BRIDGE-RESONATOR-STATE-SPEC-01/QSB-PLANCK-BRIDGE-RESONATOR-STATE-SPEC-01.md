# QSB Planck-Bridge-Resonator State Specification 01

**Work package:** `QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01`  
**Object:** Planck-Bridge-Resonator minimal formal candidate  
**Claim status:** `formal_state_spec_candidate`  
**Physical claim release:** `blocked_no_physics_claim`  
**Review status:** `requires_human_formal_review`

---

## 1. Purpose

This document defines a Planck-Bridge-Resonator (PBR) as a minimal formal candidate object inside QSB.

It does **not** claim that PBRs exist physically. It does **not** claim that spacetime consists of PBRs. It does **not** claim validation of QSB.

The purpose is narrower and testable:

```text
Can the PBR vocabulary be reduced to a minimal mathematical candidate
with explicit admissibility gates?
```

The first proposed admissibility gate is the Gram/PSD gate.

---

## 2. Local candidate object

For an index set

```text
I = {1, 2, ..., N}
```

we define a local PBR candidate as:

```text
B_i = (H_i, Phi_i, M_i, gamma_i, sigma_i)
```

where:

| Symbol | Meaning | Status |
|---|---|---|
| `H_i` | complex internal state space | formal assumption |
| `Phi_i in H_i` | local candidate state | formal assumption |
| `M_i` | mode / structure operator on `H_i` | formal assumption |
| `gamma_i` | geometric or field-like boundary condition | external parameter / test context |
| `sigma_i` | scale-gate status | registered gate status |

The object `B_i` is local. A coupling `K_ij` is relational and belongs to the pair `(B_i, B_j)`, not to one candidate alone.

```text
B_i = local candidate
K_ij = relation between candidates
G_B = network built from admitted relations
```

---

## 3. Phase-bearing condition

A global absolute phase is not treated as a physical observable. QSB uses an operational definition:

```text
A candidate is phase-bearing only if relative phase information can be formed
and enters a registered coupling, transition or stability rule.
```

In the minimal Gram reading, define:

```text
K_ij = <Phi_i, Phi_j>
```

If `K_ij` is complex and nonzero, write:

```text
K_ij = |K_ij| exp(i Delta_phi_ij)
Delta_phi_ij = arg(K_ij)
```

Then `Delta_phi_ij` is a pairwise relative phase candidate, not an absolute ontological phase.

### Gauge caution

Under a local phase convention:

```text
Phi_i -> exp(i alpha_i) Phi_i
```

one obtains:

```text
K_ij -> exp(i(alpha_j - alpha_i)) K_ij
```

Therefore pairwise phase candidates require either a registered comparison convention or gauge-robust derived quantities, such as loop phase candidates:

```text
Omega_ijk = arg(K_ij K_jk K_ki)
```

---

## 4. Moded condition

A candidate is called moded only if the state admits a decomposition with respect to a registered operator.

Let:

```text
M_i : H_i -> H_i
```

be a mode / structure operator. In the finite-dimensional minimal setting, take `M_i` to be self-adjoint where appropriate.

Eigenmode relation:

```text
M_i e_i^(n) = mu_i^(n) e_i^(n)
```

State decomposition:

```text
Phi_i = sum_n c_i^(n) e_i^(n)
```

with complex coefficients:

```text
c_i^(n) = |c_i^(n)| exp(i theta_i^(n))
```

Thus `moded` refers to spectral decomposition under a registered operator, not to an unverified physical Planck oscillator.

---

## 5. Coupling-capable condition

A candidate is coupling-capable only if at least one registered relational quantity exists and affects a model decision.

General form:

```text
K_ij(gamma) = <Phi_i, C_ij(gamma) Phi_j>
```

where `C_ij(gamma)` is a registered comparison or coupling operator.

Minimal Gram form:

```text
K_ij = <Phi_i, Phi_j>
```

A relation can then enter a decision rule, for example:

```text
edge(i, j) = 1 if S(K_ij) >= theta
```

where `S` is a registered strength/stability functional and `theta` is a registered threshold.

A coupling is QSB-relevant only if it changes a model decision. Otherwise it remains decorative notation.

---

## 6. Gram hypothesis

The minimal Gram hypothesis states:

```text
K_ij = <Phi_i, Phi_j>
```

for candidate states in a common complex Hilbert space or compatible comparison space.

Then the candidate coupling matrix

```text
K = (K_ij)
```

must be Hermitian:

```text
K = K^dagger
```

and positive semidefinite:

```text
x^dagger K x >= 0
```

for all complex vectors `x`.

Therefore:

```text
Gram hypothesis => PSD admissibility gate
```

---

## 7. PSD admissibility gate

A candidate matrix `K` passes the PSD gate if:

1. `K` is square.
2. `K` is Hermitian / symmetric within tolerance.
3. Diagonal entries are nonnegative within tolerance.
4. Eigenvalues satisfy `lambda_min >= -epsilon`.
5. Negative eigenvalue count and negative eigenvalue mass are documented.

Recommended fields:

```text
matrix_id
matrix_source
n
is_square
is_hermitian
max_hermitian_deviation
min_diagonal
lambda_min
lambda_max
negative_eigenvalue_count
negative_eigenvalue_mass
psd_pass
tolerance
admissibility_result
```

### Interpretation

```text
PSD-pass does not validate QSB.
PSD-pass means only that the minimal Gram interpretation is not formally excluded.
```

```text
PSD-fail does not refute QSB.
PSD-fail rejects or forces modification of this specific minimal Gram interpretation.
```

---

## 8. Network level

A single `B_i` is not spacetime.

Given a set of candidates:

```text
R_N = {B_1, ..., B_N}
```

and admitted relations `K_ij`, one may construct a weighted candidate graph:

```text
G_B = (V, E, W)
```

where:

```text
V = {B_i}
E = stable admitted relations
W_ij = S(K_ij)
```

Any spacetime-like interpretation must be evaluated at the network level and remains blocked until further gates and controls are passed.

---

## 9. External suggestion triage

An external Grok-style model sketch introduced LQG spin labels, CDT-like simplicial language, metric emergence formulas and Einstein-Hilbert limit wording. This state spec does not adopt those elements as core definition.

The only abstract idea retained is:

```text
phase- and mode-dependent relational coupling
```

implemented in QSB-compatible notation as:

```text
K_ij(gamma) = <Phi_i, C_ij(gamma) Phi_j>
```

Discarded for this core state spec:

- LQG spin labels as PBR fields.
- LQG area spectrum as PBR definition.
- CDT simplices as PBR definition.
- unreviewed metric expectation formulas.
- Einstein-Hilbert limit claims.
- reuse of reserved QSB symbols `beta_B` and `Xi_CS` for unrelated amplitudes or coherence measures.

---

## 10. Claim boundary

Allowed:

```text
B_i is a formal QSB-internal interface candidate.
```

Allowed:

```text
The minimal Gram interpretation of K_ij implies Hermitian and PSD admissibility conditions.
```

Blocked:

```text
PBRs physically exist.
```

Blocked:

```text
Spacetime consists of PBRs.
```

Blocked:

```text
PSD-pass validates QSB as a physical theory.
```

Blocked:

```text
PSD-fail refutes QSB as a whole.
```

---

## 11. Next work package

The natural next work package is:

```text
QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01
```

which should apply the PSD gate to a concrete candidate matrix, for example:

```text
runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv
```

if this file is confirmed as the intended matrix source.
