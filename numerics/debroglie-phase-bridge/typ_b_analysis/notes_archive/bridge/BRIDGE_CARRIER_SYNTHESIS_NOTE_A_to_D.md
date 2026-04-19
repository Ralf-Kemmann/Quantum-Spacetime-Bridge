# BRIDGE_CARRIER_SYNTHESIS_NOTE  
## Internal synthesis after Blocks A–D  
### Current status of bridge-carrier isolation and reduced H2 transfer reading

## 1. Purpose of this note
This note consolidates the current internal results from the first bridge-carrier isolation sequence:

- **Block A**: leave-one-out core reduction  
- **Block B**: minimal-set identification  
- **Block C**: single-feature and triple-feature tests  
- **Block D**: reduced H2 / transfer mirror

The purpose is not to overstate conclusions, but to separate:

- what appears to carry the bridge **internally**,
- what appears to matter for **reduced transfer**,
- and which variables currently look more like **secondary or stabilizing quantities** than primary internal carriers.

## 2. Starting point
The bridge-carrier isolation program was opened because the project had already reached a stage where the central question was no longer merely whether a structured bridge signal exists, but rather:

> **Which quantities actually carry that bridge physically, which only support it, and which mainly belong to the diagnostic/reporting layer?**

The first core candidate set was:

- `distance_to_type_D`
- `spacing_cv`
- `simple_rigidity_surrogate`
- `grid_deviation_score`

The working expectation at the start was still relatively open. In particular, `distance_to_type_D` and `spacing_cv` were initially plausible as strong or near-primary bridge-carrier candidates, while `simple_rigidity_surrogate` and `grid_deviation_score` were also treated as likely important but not yet cleanly ranked.

## 3. Methodological clarification before interpretation
A decisive methodological distinction emerged early in the sequence:

### 3.1 Execution-level success vs physical interpretability
The first placeholder evaluator was useful as a workflow test, but not yet physically faithful enough to support robust carrier assignment. Its main value was to prove that:

- the I/O layer worked,
- the variant logic worked,
- degradation relative to `full` could be computed,
- and the result structure could be documented cleanly.

Only after replacement by the corridor-based original-reference evaluator did the sequence begin to produce physically interpretable internal carrier signals.

### 3.2 Internal carrier anatomy vs transfer anatomy
By Block D it became necessary to distinguish between two different questions:

1. **Which variables carry the bridge internally under current bridge-classification logic?**
2. **Which variables remain useful or necessary under reduced H2 proxy-mediated transfer?**

This distinction turned out to be essential. The same variable need not play the same role internally and under transport conditions.

## 4. Main results by block

## 4.1 Block A — Leave-one-out core reduction
Under the corridor-based replacement evaluator, the first structurally meaningful leave-one-out result was:

- removing `simple_rigidity_surrogate` caused a hard collapse of bridge support,
- removing `grid_deviation_score` also caused collapse,
- removing `distance_to_type_D` did **not** collapse the bridge,
- removing `spacing_cv` did **not** collapse the bridge.

This was the first clear sign that the bridge is not currently best read as being carried primarily by distance/corridor quantities alone. Instead, the decisive internal damage appeared when the rigidity and structural-deviation part of the representation was removed.

### Provisional reading after Block A
- `simple_rigidity_surrogate` → primary candidate  
- `grid_deviation_score` → primary candidate  
- `distance_to_type_D` → not necessary under current internal logic  
- `spacing_cv` → not necessary under current internal logic

This was already a major shift away from a purely distance-centered reading.

## 4.2 Block B — Minimal-set identification
Block B tested several 2-feature subsets.

### Supported 2-feature sets
- `simple_rigidity_surrogate + grid_deviation_score`
- `simple_rigidity_surrogate + distance_to_type_D`
- `simple_rigidity_surrogate + spacing_cv`

### Failing 2-feature sets
- `grid_deviation_score + distance_to_type_D`
- `grid_deviation_score + spacing_cv`

This sharpened the picture considerably. Every tested pair containing `simple_rigidity_surrogate` remained supported; every tested pair without it failed.

### Provisional reading after Block B
`simple_rigidity_surrogate` emerged as the strongest minimal-set anchor.  
`grid_deviation_score` looked strongest in combination with rigidity, especially in the pair:

- `simple_rigidity_surrogate + grid_deviation_score`

This suggested that the bridge is internally not best represented as a mere distance corridor, but rather as a **rigidity-centered structured bridge**, with grid structure contributing strongly to the richer internal form of that bridge.

## 4.3 Block C — Single-feature and triple-feature tests
Block C produced the sharpest internal anatomical result so far.

### Single-feature tests
- `single_rigidity` → **supported**
- `single_distance` → failed
- `single_spacing` → failed
- `single_grid` → failed

This means that under the current internal evaluator:

> `simple_rigidity_surrogate` behaves as a **single-anchor carrier**.

No other single feature was sufficient.

### Triple-feature tests
- `triple_without_distance` → supported
- `triple_without_spacing` → supported
- `triple_without_rigidity` → failed
- `triple_without_grid` → failed

This was highly informative because it showed:

- the bridge remains intact without `distance_to_type_D`,
- the bridge remains intact without `spacing_cv`,
- the bridge does **not** remain intact without `simple_rigidity_surrogate`,
- the bridge does **not** remain intact without `grid_deviation_score`.

### Internal anatomical reading after Block C
A very clean provisional internal anatomy follows:

#### Primary internal anchor
- `simple_rigidity_surrogate`

#### Necessary internal co-carrier for fuller structure
- `grid_deviation_score`

#### Secondary / removable under current internal logic
- `distance_to_type_D`
- `spacing_cv`

This was the first point at which the bridge could be read, internally, as predominantly a **rigidity-centered structured bridge**, with grid deviation acting as a necessary co-carrier of the fuller internal bridge picture.

## 4.4 Block D — Reduced H2 / transfer mirror
Block D initially failed in a degenerate way because the wrong H2 input file had been selected: the first H2 file was a holdout candidate registry, not a feature matrix. That failure therefore had no physical meaning.

After correction, the proper H2 feature table confirmed a crucial fact already known conceptually from the relocation notes:

- H2 is **not** a direct 4-feature mirror,
- it is a **reduced 3-of-4 plus proxy** setting,
- `simple_rigidity_surrogate` is not directly available,
- only `rigidity_proxy_second_difference_curvature` is available,
- `rigidity_proxy_used = True`,
- `mapping_mode = reduced_3of4_plus_proxy`.

A proxy-substitution patch was then introduced so that H2 could at least be read as a reduced proxy-mediated transfer test.

### Main Block D result after proxy patch
No tested variant passed H2.  
However, the H2 side was no longer degenerate. Weak nonzero H2 signals appeared for:

- `full`
- `triple_without_spacing`

while

- `single_rigidity`
- `pair_rigidity_grid`
- `triple_without_distance`

remained effectively zero.

### Transfer reading after Block D
This is the key synthesis point:

> The internal carrier core does **not** reproduce as such under reduced H2 proxy transfer.

More precisely:

- the internally strongest anchor (`simple_rigidity_surrogate`) does **not** transfer as a direct reduced H2 anchor,
- the internally strong pair (`simple_rigidity_surrogate + grid_deviation_score`) also does **not** transfer as such,
- weak nonzero H2 signal appears only in variants that retain `distance_to_type_D`.

This suggests a distinction between:

- **internal carrier role**
- **transfer-stabilizing role**

## 5. Current provisional carrier anatomy

## 5.1 Internal bridge anatomy
Under the current corridor-based evaluator, the bridge is best read internally as:

### Internal primary anchor
- `simple_rigidity_surrogate`

### Internal necessary co-carrier
- `grid_deviation_score`

### Internal secondary / removable quantities
- `distance_to_type_D`
- `spacing_cv`

This means that the bridge is currently **not** best read as a purely distance-driven or spacing-driven corridor phenomenon. Instead, the strongest internal signal points to a structure dominated by:

- rigidity / coherence-like organization
- plus structural deformation / grid deviation

## 5.2 Reduced transfer anatomy
Under reduced H2 proxy-mediated transfer, the picture changes.

### Reduced H2 result
- no variant passes H2,
- the internal core is therefore **not directly transportable** under the current H2 mirror.

### But H2 is not empty
The reduced H2 mirror is not fully null after proxy substitution. Weak residual signal appears when `distance_to_type_D` is retained.

### Provisional transfer reading
This suggests that:

- `distance_to_type_D` may be less important as an **internal carrier**
- but may still matter as a **transfer stabilizer** or **projection anchor** under reduced proxy-mediated transport conditions.

This is a meaningful distinction. A variable need not be the main internal carrier in order to matter for how reduced or incomplete representations preserve bridge-related structure across contexts.

## 6. Current best synthetic reading
The most defensible current synthesis is therefore:

> The bridge currently appears to have a split anatomy. Internally, it is dominated by a rigidity-centered carrier core, with grid structure acting as a necessary co-carrier for the fuller bridge picture. Under reduced H2 proxy-mediated transfer, this internal core does not reproduce directly. Instead, the only weak residual H2 signal appears in variants that retain `distance_to_type_D`, suggesting that the project should distinguish between internal carriers and transfer-stabilizing quantities.

This is stronger than the earlier diffuse bridge picture because it provides a first concrete anatomical separation between:

- what seems to **carry** the bridge internally,
- and what may help **transport** bridge structure under incomplete mapping.

## 7. What this does **not** yet justify
Several overclaims must still be avoided.

The current results do **not** justify the claim that:

- `simple_rigidity_surrogate` is the final definitive physical carrier in a full project-level sense,
- `grid_deviation_score` has been proven as the unique co-carrier under all evaluators,
- `distance_to_type_D` is physically unimportant,
- the H2 transfer line has been refuted,
- or the reduced H2 proxy result can already replace the official inherited H2 reading.

The present status remains internal, evaluator-dependent, and still methodologically bounded.

## 8. What **has** been gained
Even under those restrictions, something substantial has been gained.

### 8.1 Conceptual gain
The bridge is no longer just “multi-component somehow.”  
It now has a first plausible internal anatomy:

- anchor,
- co-carrier,
- secondary quantities,
- and possible transfer stabilizer.

### 8.2 Methodological gain
The project now has a structured sequence showing that:
- a naïve placeholder evaluator is insufficient,
- a more project-near evaluator changes the carrier picture,
- the carrier picture remains stable across A/B/C internally,
- and transfer must be read separately from internal carrier logic.

### 8.3 Interpretive gain
The bridge may need to be described not as one undifferentiated mechanism, but as a layered structure with at least two planes:

- **internal bridge constitution**
- **reduced transfer retention**

That is a significant refinement of the project’s physical reading.

## 9. Immediate consequence for next work
The next step should not be to flatten these results into one summary label.  
Instead, the immediate consequence is:

### 9.1 Preserve the distinction
Keep separate:
- internal carrier role
- transfer-stabilizing role
- diagnostic/reporting layer

### 9.2 Open the next narrow question
The next focused question is:

> Is `distance_to_type_D` genuinely acting as a reduced transfer stabilizer, and if so, under which reduced-H2 combinations does that stabilization become visible?

This would motivate the next narrow transfer-focused block rather than another broad internal sweep.

## 10. Bottom line
The current bridge-carrier isolation sequence supports the following internal conclusion:

> **Internally**, the bridge is currently best read as a rigidity-centered structure, with `simple_rigidity_surrogate` acting as a single-anchor carrier and `grid_deviation_score` acting as a necessary co-carrier for the fuller bridge picture.  
> **Under reduced H2 proxy-mediated transfer**, this internal core does not reproduce directly. The only weak residual H2 signal appears in variants retaining `distance_to_type_D`, which suggests that the project should distinguish between internal carriers and transfer-stabilizing quantities.

That is the cleanest current synthesis after Blocks A–D.
