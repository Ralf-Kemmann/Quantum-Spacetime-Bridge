# Kurzfassung — PBR State Spec 01

Der Planck-Bridge-Resonator wird in diesem Paket nicht als physikalisch existierende Entität eingeführt, sondern als formaler QSB-interner Interface-Kandidat.

## Minimalobjekt

```text
B_i = (H_i, Phi_i, M_i, gamma_i, sigma_i)
```

- `H_i`: komplexer innerer Zustandsraum
- `Phi_i`: Kandidatenzustand
- `M_i`: Moden-/Strukturoperator
- `gamma_i`: geometrie- oder feldartige Randbedingung
- `sigma_i`: Scale-Gate-Status

## Relationale Kopplung

Allgemein:

```text
K_ij(gamma) = <Phi_i, C_ij(gamma) Phi_j>
```

Minimal:

```text
K_ij = <Phi_i, Phi_j>
```

## Gram-Hypothese

Wenn `K_ij` als Gram-Skalarprodukt gelesen wird, muss die Matrix `K` hermitesch und positiv semidefinit sein.

```text
Gram-Hypothese => PSD-Gate
```

## Claim-Boundary

PSD-pass validiert QSB nicht. PSD-pass bedeutet nur: Die minimale Gram-Lesart ist formal nicht ausgeschlossen.

PSD-fail widerlegt QSB nicht. PSD-fail verwirft nur diese konkrete Minimalinterpretation.

## Nächster Schritt

```text
QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01
```

mit einer bestätigten Kandidatenmatrix, wahrscheinlich:

```text
runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv
```
