# QSB-ST-LIC01 Tau/Epsilon Observable Normalization Audit Plan

## Purpose

This document defines the audit plan for LIC01-G after the warning that some controls are close to, or above, the structured reference.

The goal is not to rescue the current score. The goal is to determine whether the warning is caused by an implementation issue, a normalization artifact, a tau/epsilon choice, an observable definition problem, a rho_tau construction issue, or a real diagnostic boundary where the current controls mimic the structured reference too well.

This is a plan document only. It creates no new numerical result and makes no physical validation claim.

## Current status

LIC01-G is treated as unresolved until the control/reference overlap is audited.

Current interpretation boundary:

- controls near the structured reference are not nuisance rows
- controls above the structured reference are warning rows
- the diagnostic cannot be used for stronger claims until the warning mechanism is isolated
- any later result must report whether the warning survives after observable, normalization, tau, epsilon, and rho_tau checks

## Known warning result

Known warning:

```text
Some controls are close to, or above, the structured reference.
```

This warning can mean several different things:

- the observable is not discriminative for LIC01-G
- normalization compresses structured and control cases into the same range
- tau or epsilon creates artificial stability or artificial edges
- rho_tau is too permissive or too insensitive
- a global phase convention hides relevant differences
- a small-kernel regime makes rank/order comparisons unstable
- the controls are genuinely strong mimics under the current diagnostic

No single interpretation is accepted without an audit.

## Audit hypotheses

The audit should test the following hypotheses separately:

- H1: The observable is dominated by summary magnitude, degree, or density terms that controls can match.
- H2: The normalization maps different raw distributions to similar normalized scores.
- H3: The chosen tau creates a threshold region where controls and structured reference have similar graph support.
- H4: Epsilon clipping or flooring changes weak entries enough to affect distances, ratios, or rank order.
- H5: rho_tau is insensitive to the distinction LIC01-G is intended to measure.
- H6: A global phase convention or phase alignment step removes a difference that should be retained for this diagnostic.
- H7: The relevant kernel is too small, sparse, or near-degenerate for stable discrimination.
- H8: The warning is a legitimate negative result for the current diagnostic.

## Observable audit

For every structured reference and control row, record the observable before any final normalization or aggregate scoring.

Required checks:

- list the exact observable formula used in LIC01-G
- identify all inputs used by the observable
- mark whether each input is magnitude-derived, phase-derived, topology-derived, label-derived, or externally supplied
- report raw observable values for structured reference and controls
- report per-component observable values if the observable is composite
- check whether controls exceed the structured reference before normalization
- check whether the observable is invariant under relabeling when invariance is expected
- check whether the observable changes under relabeling when the diagnostic expects label sensitivity

Pass condition for this section is not that the structured reference wins. Pass condition is that the raw observable behavior is visible and explainable.

## Normalization audit

The normalization audit should determine whether score overlap is introduced or amplified by scaling.

Required checks:

- record raw min, max, mean, median, standard deviation, and quantiles before normalization
- record the normalization formula and all constants
- identify whether normalization is per-run, per-family, per-reference, global, or fixed by configuration
- compare raw ranking against normalized ranking
- report rank flips caused by normalization
- report whether outliers set the scale
- rerun the score table with at least one alternative normalization only as a diagnostic comparison

The alternative normalization is not automatically a replacement. It is only a probe to see whether the warning is normalization-dependent.

## rho_tau audit

The rho_tau audit should isolate threshold sensitivity.

Required checks:

- define rho_tau explicitly
- record the configured tau value
- sweep tau across a documented range around the configured value
- report structured/control ordering across the sweep
- report edge/support counts across tau if rho_tau depends on thresholded support
- identify tau regions where the structured reference separates from controls
- identify tau regions where controls match or exceed the structured reference
- check whether the configured tau sits in an unstable or near-crossing region

If the conclusion depends on a narrow tau window, the result must be marked parameter-sensitive.

## global phase issue

The audit should check whether any global phase handling changes the warning.

Required checks:

- state whether LIC01-G uses complex-valued K, phase-derived terms, or phase alignment
- state whether a global phase is fixed, minimized over, averaged out, or ignored
- compare diagnostics before and after any phase alignment step where applicable
- distinguish gauge-like phase changes from loop/closure-sensitive phase structure where applicable
- report whether controls exploit a phase convention rather than the intended structure

If LIC01-G is magnitude-only, this section should explicitly say that global phase cannot affect the magnitude-only readout except through implementation mistakes or unintended complex-to-real reductions.

## small-kernel issue

The audit should check whether the warning comes from small, sparse, or near-degenerate kernels.

Required checks:

- record kernel size, nonzero count, density, and effective support
- record the distribution of magnitudes before epsilon handling
- record the number of entries affected by epsilon
- check rank/order stability under small perturbations
- check whether nearest-neighbor or support decisions are tied or near-tied
- compare results for any available larger or less-degenerate kernel variant

If small-kernel instability is present, LIC01-G should not be described as robust.

## proposed next diagnostics

Proposed diagnostics:

- raw observable table for structured reference and every control
- normalized score table with rank-change columns
- tau sweep table for rho_tau
- epsilon sensitivity table
- support/edge-count table before and after thresholding
- rank-stability table under small perturbations
- phase-handling comparison table if phase terms exist
- structured-minus-control delta table with the minimum delta highlighted
- warning-row report listing every control within a predefined margin of the structured reference

Recommended output should separate machine-readable artifacts from human-readable notes.

## Acceptance checks

The audit is accepted only if it provides:

- exact formulas for observable, normalization, rho_tau, tau, and epsilon handling
- raw and normalized values for structured reference and controls
- explicit identification of controls near or above the structured reference
- tau sensitivity results
- epsilon sensitivity results
- phase-handling statement
- small-kernel stability statement
- a clear conclusion choosing one or more audited warning mechanisms
- a claim boundary that keeps the result at diagnostic-method level

Passing the audit does not require the structured reference to outperform controls. If controls remain close to or above the structured reference after audit, that must be reported as a boundary or negative diagnostic result.

## Claim Boundary

This audit plan does not show that LIC01-G is correct, robust, physical, or validated.

It does not establish:

- physical validation
- molecular validation
- spacetime emergence
- physical metric recovery
- causal structure
- de-Broglie confirmation
- real quantum dynamics
- independent observable recovery

The only allowed outcome is a method-level audit of why controls are close to, or above, the structured reference under the current LIC01-G diagnostic.
