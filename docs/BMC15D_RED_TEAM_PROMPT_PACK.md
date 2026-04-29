# BMC-15d Red-Team Prompt Pack

## Purpose

This file contains copy-ready prompts for external or parallel AI red-team review.

The aim is not to obtain praise.  
The aim is to expose weak interpretations, overclaims, missing controls, and better wording.

---

## Shared context for all red-team prompts

```text
Project: Quantum-Spacetime-Bridge / Gravitation und RaumZeit

Current status:
We are after BMC-15b geometry-proxy null comparison and a label/readout refinement patch.

Core robustness status:
Across the BMC-14 series, 0 / 3300 tested null replicates reconstructed the observed compact 6-edge N=81 core completely.
Maximum partial recovery was 3 / 6.

BMC-15a:
Observed geometry-proxy diagnostics found zero direct triangle defects, low to moderately low embedding stress,
stable sparse-scaffold shell-growth proxies for larger envelopes, and a core that is too small/fragmented
for standalone geometry interpretation.

BMC-15b:
The observed N81 baseline and selected envelopes were compared against null graph objects.

Null families:
- global_covariance_gaussian
- family_covariance_gaussian
- weight_rank_edge_rewire
- degree_preserving_edge_rewire
- degree_weightclass_edge_rewire
- gaussian_copula_feature_null

Main result:
The observed geometry-proxy values are generally more favorable than graph-rewire nulls,
especially for normalized embedding stress and negative eigenvalue burden.

Important limitation:
Feature-/family-/correlation-structured nulls often generate geometry-proxy values in the observed range.

Interpretation boundary:
This is geometry-proxy evidence only.
It does not establish physical spacetime emergence, physical metric reconstruction, causal structure,
continuum geometry, or uniqueness against all possible null explanations.
```

---

## Prompt 1 — General skeptical reviewer

```text
Please act as a skeptical but fair theoretical-physics/methodology reviewer.

I have a project result with the following status:

- A compact observed N=81 relational core was not fully reconstructed by 3300 tested null replicates.
- Geometry-proxy diagnostics on observed core/envelope graph objects show low embedding stress and other geometry-like proxy behavior.
- In a null comparison, observed graph objects outperform graph-rewire nulls in embedding compatibility.
- However, feature-/family-/correlation-structured nulls often produce geometry-proxy values in the observed range.

Please red-team the interpretation.

Specifically:
1. What claims are supported?
2. What claims are not supported?
3. What alternative explanations remain?
4. Where is overclaiming most likely?
5. What wording would be defensible in a paper?
6. What additional controls would you request before accepting stronger claims?

Please keep the distinction between core identity robustness and geometry-proxy behavior explicit.
Do not treat geometry-proxy diagnostics as physical spacetime evidence.
```

---

## Prompt 2 — Null-model specialist

```text
Please act as a null-model and graph-statistics specialist.

We tested geometry-proxy behavior of observed relational graph objects against:
- graph-rewire nulls
- degree-preserving edge rewires
- degree/weight-class edge rewires
- global covariance Gaussian feature nulls
- family covariance Gaussian feature nulls
- Gaussian copula feature nulls

The observed case is more embedding-compatible than graph-rewire nulls,
but often null-typical under feature-/family-/correlation-structured nulls.

Please evaluate:
1. Whether the null-family split is meaningful.
2. Whether graph-rewire separation is still useful if feature-structured nulls are often typical.
3. Whether feature-structured typicality should be interpreted as failure, confounding, or mechanistic clue.
4. Which additional null models would be most informative.
5. Whether the current result supports "informative but not uniquely specific" as a fair interpretation.
```

---

## Prompt 3 — Harsh anti-overclaim reviewer

```text
Please act as a harsh anti-overclaim reviewer.

Given this result:
- robust observed 6-edge N=81 core identity across tested nulls
- geometry-like proxy consistency at the envelope level
- strong separation from graph-rewire nulls
- mixed/null-typical behavior against feature-/family-/correlation nulls

Attack the strongest possible overclaim risks.

Please identify:
1. Sentences that must not appear in the manuscript.
2. Terms that are dangerous or misleading.
3. Places where "geometry" may accidentally sound like physical geometry.
4. Whether "embedding-compatible" is safe wording.
5. How to phrase the result so a skeptical reader does not feel manipulated.
```

---

## Prompt 4 — Constructive next-test planner

```text
Please act as a constructive methodology planner.

Current result:
The observed geometry-proxy behavior is more favorable than graph-rewire nulls,
but often typical under feature-/family-/correlation structured nulls.

Please propose the next three test blocks.

For each block provide:
- purpose
- input data needed
- minimal runner logic
- main metrics
- expected diagnostic value
- what result would strengthen the claim
- what result would weaken the claim

Please prefer tests that distinguish:
1. feature/family contribution
2. pipeline-generic core-in-envelope morphology
3. true observed core identity specificity
4. envelope construction sensitivity
```

---

## Prompt 5 — Louis-style collegial European reviewer

```text
Please act as a collegial European theoretical-physics reviewer:
critical, careful, not hostile, and sensitive to wording.

The project is exploratory and methodologically defensive.
It uses geometry-proxy diagnostics on relational graph objects,
not claims of physical spacetime reconstruction.

Please help refine the interpretation of this mixed result:
- observed core identity robust against tested nulls
- observed geometry proxies stronger than graph-rewire controls
- feature-/family-/correlation nulls often produce similar proxy values

Please give:
1. A calm reviewer-style assessment.
2. A defensible paragraph for a working paper.
3. A warning paragraph about what not to claim.
4. A recommendation for the next internal note before visualization.
```

---

## Prompt 6 — Visualization gatekeeper

```text
Please act as a visualization gatekeeper for a scientific project.

We want to eventually create a visual showing:
- a stable relational core
- method-dependent envelopes
- geometry-like proxy consistency

But the current result is mixed:
- graph-rewire nulls are clearly less geometry-like
- feature/family/correlation nulls are often similar to observed values

Please decide what a figure is allowed to suggest and what it must not suggest.

Please provide:
1. Safe visual metaphors.
2. Unsafe visual metaphors.
3. Required caption warnings.
4. A publication-safe figure title.
5. A public-outreach-safe but non-overclaiming explanation.
```

---

## Integration instruction

After receiving red-team outputs, do not paste them unfiltered into the project.

Classify each critique as:

```text
accepted
partially accepted
rejected with reason
requires numerical follow-up
language-only correction
```

Then integrate only the defensible points into:

```text
docs/BMC15D_GEOMETRY_PROXY_RED_TEAM_INTEGRATION_NOTE.md
docs/BMC15_SERIES_GEOMETRY_PROXY_CONSOLIDATED_NOTE.md
```
