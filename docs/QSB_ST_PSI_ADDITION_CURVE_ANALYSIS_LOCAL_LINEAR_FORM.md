# QSB-ST ψ-Addition Curve Analysis and Local Linear Form

## 1. Purpose

This note discusses the project-internal psi addition form

```text
ψ(x) = A cos(kx) + B sin(kx)
```

and shows how it can be represented locally in a linear form

```text
y ≈ m x + b
```

The function is not globally linear in general. A form `y = mx + b` is meaningful only as a local tangent approximation or as a secant approximation over an interval.

No implementation, data output, or physical claim is introduced here.

## 2. Starting equation

Starting equation:

```text
ψ(x) = A cos(kx) + B sin(kx)
```

Parameters:

- `A`: cosine / in-phase coefficient
- `B`: sine / quadrature coefficient
- `k`: wave number / spatial frequency
- `x`: local coordinate or diagnostic coordinate

In this note, these parameters are mathematical/project-internal diagnostic quantities unless separately derived in another context.

## 3. Amplitude-phase transformation

Define the amplitude

```text
R = sqrt(A² + B²)
```

If `(A, B) != (0, 0)`, one possible amplitude-phase form is:

```text
ψ(x) = R cos(kx - φ)
```

with

```text
cos φ = A / R
sin φ = B / R
φ = atan2(B, A)
```

Check:

```text
R cos(kx - φ)
= R[cos(kx) cos φ + sin(kx) sin φ]
= A cos(kx) + B sin(kx)
```

If `A = B = 0`, then `R = 0` and `ψ(x)` is the zero function.

## 4. Basic curve discussion

For general `A`, `B`, and nonzero `k`, `ψ(x)` is a sinusoidal curve with amplitude `R`.

Important special cases:

- If `A = B = 0`, the function is identically zero.
- If `k = 0`, then `ψ(x) = A`, because `cos(0) = 1` and `sin(0) = 0`.
- If `A = 0`, the curve is a pure sine component: `ψ(x) = B sin(kx)`.
- If `B = 0`, the curve is a pure cosine component: `ψ(x) = A cos(kx)`.

The curve is globally linear only in degenerate constant cases. Otherwise, a line can only approximate it locally or connect two selected points as a secant.

## 5. First derivative

Starting from

```text
ψ(x) = A cos(kx) + B sin(kx)
```

the first derivative is

```text
ψ'(x) = -A k sin(kx) + B k cos(kx)
```

This derivative gives the local slope of the curve.

## 6. Second derivative

The second derivative is

```text
ψ''(x) = -A k² cos(kx) - B k² sin(kx)
```

Since

```text
ψ(x) = A cos(kx) + B sin(kx)
```

it follows that

```text
ψ''(x) = -k² ψ(x)
```

This is the standard harmonic relation for this sinusoidal form.

## 7. Extrema

Extrema occur where

```text
ψ'(x) = 0
```

Using the first derivative:

```text
-A k sin(kx) + B k cos(kx) = 0
```

For `k != 0`, this is equivalent to:

```text
-A sin(kx) + B cos(kx) = 0
```

If `A != 0` and `cos(kx) != 0`, this can be written as:

```text
tan(kx) = B / A
```

In amplitude-phase form,

```text
ψ(x) = R cos(kx - φ)
```

Maxima occur at

```text
kx - φ = 2πn
```

with value

```text
max = +R
```

Minima occur at

```text
kx - φ = π + 2πn
```

with value

```text
min = -R
```

where `n` is an integer.

## 8. Inflection points

Inflection points occur where

```text
ψ''(x) = 0
```

Because

```text
ψ''(x) = -k² ψ(x)
```

for `k != 0`, this gives

```text
ψ(x) = 0
```

In amplitude-phase form:

```text
R cos(kx - φ) = 0
```

For `R != 0`, the inflection points satisfy

```text
cos(kx - φ) = 0
kx - φ = π/2 + nπ
```

where `n` is an integer.

## 9. Periodicity and zeros

For `k != 0`, the period is

```text
T = 2π / |k|
```

If `k = 0`, then

```text
ψ(x) = A
```

so the function is constant.

Zeros occur where

```text
ψ(x) = 0
```

In amplitude-phase form:

```text
R cos(kx - φ) = 0
```

For `R != 0`, the zeros satisfy

```text
kx - φ = π/2 + nπ
```

where `n` is an integer.

## 10. Local tangent form y = mx + b

`ψ(x)` is not a straight line in general. A form `y = mx + b` is valid as a local tangent approximation at a point `x0`.

Set

```text
m = ψ'(x0)
b = ψ(x0) - m x0
```

Then the tangent line is

```text
y_tangent(x) = m x + b
```

Using the explicit formulas:

```text
m = -A k sin(k x0) + B k cos(k x0)
```

and

```text
b = A cos(k x0) + B sin(k x0) - x0[-A k sin(k x0) + B k cos(k x0)]
```

Therefore

```text
y ≈ [-A k sin(k x0) + B k cos(k x0)] x
    + [A cos(k x0) + B sin(k x0) - x0(-A k sin(k x0) + B k cos(k x0))]
```

Special case `x0 = 0`:

```text
ψ(0) = A
ψ'(0) = Bk
```

Therefore

```text
m = Bk
b = A
```

The local tangent at `x0 = 0` is

```text
y ≈ Bk x + A
```

This is the simplest local `y = mx + b` representation.

## 11. Secant form over an interval

A linear form may also be defined as a secant over an interval `[x1, x2]`.

For `x1 != x2`:

```text
m_sec = [ψ(x2) - ψ(x1)] / (x2 - x1)
b_sec = ψ(x1) - m_sec x1
```

Then

```text
y_sec(x) = m_sec x + b_sec
```

This secant line connects two selected points on the curve. It is not a global replacement for `ψ(x)`.

## 12. Interpretation for COMP01 / QSB-ST

This curve discussion is mathematical preparation for the internal psi working form.

The decomposition

```text
ψ_i(x) = A_i cos(k_i x) + B_i sin(k_i x)
```

makes visible:

- `A_i` as cosine-like / in-phase coefficient
- `B_i` as sine-like / quadrature coefficient
- `k_i` as wave number / structural frequency
- `R_i` as total amplitude
- `φ_i` as phase position

For COMP01-B and COMP01-C, this is relevant because:

- cosine and sine components can be tested separately,
- same-channel overlaps can be considered separately from cross-channel overlaps,
- the local linear form can be read as a tangent/response approximation,
- `y = mx + b` is not a global form of the oscillation, but a local linear approximation.

## 13. Claim Boundary

- ψ is a diagnostic pattern object here, not automatically a physical wavefunction.
- The local y=mx+b form is a tangent or secant approximation, not a global replacement for ψ(x).
- A, B, k are diagnostic parameters in this project context unless separately derived physically.
- tau is not physical time.
- No D(A,B) is attached.
- No S_rel2 is constructed.
- No Lorentzian metric is derived.
- No physical Bridge is validated.
- This is mathematical/project-internal diagnostic work only.

## 14. Current status label

`PSI_addition_curve_analysis_local_linear_form_documented`
