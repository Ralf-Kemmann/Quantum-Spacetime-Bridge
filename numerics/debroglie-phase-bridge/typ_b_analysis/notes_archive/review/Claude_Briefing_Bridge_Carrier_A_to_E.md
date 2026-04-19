# Claude Briefing Note
## Bridge-carrier isolation status after Blocks A–E

Please read the following as an **internal project synthesis note**, not as an external claim draft.

## 1. Project context
The project investigates whether spacetime geometry may be understood as an **emergent relational structure** rather than as a predefined background stage. The central bridge question is whether stable relational / interference-based order can act as a bridge between spectral structure and emergent geometric order. A key physical candidate for that bridge is **de Broglie interference**.

The project had already reached the stage where the main question was no longer merely whether some bridge-like signal exists, but rather:

> **Which quantities actually carry that bridge physically, which only support it, and which belong mainly to the diagnostic/reporting layer?**

The first core candidate set for isolation was:

- `distance_to_type_D`
- `spacing_cv`
- `simple_rigidity_surrogate`
- `grid_deviation_score`

## 2. Important methodological point
A placeholder evaluator was first used only to validate the workflow, but the physically interpretable results began only after replacement by a more project-near **corridor-based original-reference evaluator**. So the relevant carrier reading below refers to that later evaluator, not to the initial placeholder pass.

## 3. Main results from Blocks A–C
### Block A — leave-one-out
Under the corridor-based evaluator:
- removing `simple_rigidity_surrogate` caused collapse
- removing `grid_deviation_score` also caused collapse
- removing `distance_to_type_D` did not collapse the bridge
- removing `spacing_cv` did not collapse the bridge

### Block B — minimal pairs
Supported 2-feature sets:
- `simple_rigidity_surrogate + grid_deviation_score`
- `simple_rigidity_surrogate + distance_to_type_D`
- `simple_rigidity_surrogate + spacing_cv`

Failing 2-feature sets:
- `grid_deviation_score + distance_to_type_D`
- `grid_deviation_score + spacing_cv`

### Block C — singles and triples
Single-feature results:
- `simple_rigidity_surrogate` alone = supported
- `distance_to_type_D` alone = failed
- `spacing_cv` alone = failed
- `grid_deviation_score` alone = failed

Triple-feature results:
- without `distance_to_type_D` = supported
- without `spacing_cv` = supported
- without `simple_rigidity_surrogate` = failed
- without `grid_deviation_score` = failed

## 4. Internal carrier anatomy after A–C
The strongest current internal reading is:

- `simple_rigidity_surrogate` = **internal anchor / primary carrier**
- `grid_deviation_score` = **necessary internal co-carrier** for the fuller bridge picture
- `distance_to_type_D` = **secondary / removable internally**
- `spacing_cv` = **secondary / removable internally**

So the bridge is currently **not** best read as primarily distance-driven or spacing-driven. It is better read as a **rigidity-centered structured bridge**, with grid structure carrying the fuller internal form.

## 5. Blocks D–E: reduced H2 / transfer side
A first H2 mirror initially failed for technical reasons because the wrong H2 file had been selected. After correction, the proper H2 feature table showed that H2 is **not** a direct 4-feature mirror, but a **reduced 3-of-4 plus proxy** setting:

- `distance_to_type_D` direct
- `spacing_cv` direct
- `grid_deviation_score` direct/extracted
- `simple_rigidity_surrogate` **not directly available**
- proxy available: `rigidity_proxy_second_difference_curvature`
- `rigidity_proxy_used = True`
- `mapping_mode = reduced_3of4_plus_proxy`

After adding proxy-rigidity substitution, H2 became readable, but no tested variant passed H2.

### Key reduced-H2 result after D–E
The strongest weak residual H2 signal appears for:
- **proxy-rigidity plus grid**

A narrower Block E discrimination test was specifically used to test whether `distance_to_type_D` is a genuine reduced-H2 transfer stabilizer.

That test did **not** support the distance-stabilizer idea. In particular:
- `proxy_rigidity_plus_distance` did not improve over `proxy_rigidity_only`
- `proxy_rigidity_plus_grid_plus_distance` did not improve over `proxy_rigidity_plus_grid`

So the earlier suspicion that `distance_to_type_D` might stabilize H2 transfer is currently **not supported**.

## 6. Best current synthesis after A–E
The cleanest current reading is:

> **Internally**, the bridge is best read as a rigidity-centered structure, with `simple_rigidity_surrogate` as the anchor and `grid_deviation_score` as the necessary co-carrier for the fuller bridge picture.  
> **Under reduced H2 proxy-mediated transfer**, this internal core does not reproduce fully. The strongest weak residual H2 signal is associated with **proxy-rigidity plus grid**, while `distance_to_type_D` is **not supported** as a genuine transfer stabilizer.

## 7. End role matrix
### Core
- `simple_rigidity_surrogate`
- `grid_deviation_score`

### Secondary
- `distance_to_type_D`
- `spacing_cv`

### Diagnostic/open
- `dominant_marker`
- `observed_irregularity_level`

The last two are **not** currently part of the isolated core model and should not be promoted into the bridge core without new evidence.

## 8. What I want from you
Please do **not** flatter this result and do **not** smooth over weak points.

I want you to do three things:

1. **Stress-test the logic**
   - Is the move from A/B/C to the role assignment actually justified?
   - Is the distinction between internal carrier anatomy and reduced transfer anatomy conceptually clean?

2. **Attack the weak points**
   - Could the corridor-based evaluator still be biasing the carrier picture too strongly toward rigidity/grid?
   - Could the H2 proxy result be too evaluator-dependent to justify even the weak “proxy-rigidity plus grid” retention reading?

3. **Tell me what would count as a real next discriminating test**
   - not a vague wish list
   - but the sharpest next test that could either strengthen or seriously damage the current internal reading

## 9. Tone / project rules
Please keep the tone:
- critical
- precise
- non-flattering
- methodologically serious
- willing to say “this is still too weak” if that is your conclusion

Do **not** rewrite this into a marketing summary. Treat it as a serious internal research note.
