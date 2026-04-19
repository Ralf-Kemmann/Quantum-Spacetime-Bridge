# POSITIVE_EXPORT_NO_LOCAL_NEIGHBOR_NOTE

## Positive export is not launchable under the current local-neighbor rule

**Date:** 2026-04-08  
**Status:** internal diagnostic note

---

## 1. Purpose
This note records the structural reason why the NPZ-derived positive export is currently **not launchable** for the compatibility runner.

Its purpose is to separate clearly between:

- a runner error
and
- a real structural non-launch condition in the export itself

This is a diagnostic note, not a reform note.

---

## 2. Background
The compatibility runner was successfully connected to NPZ-derived local exports.

For the negative export, the converted local export yielded:

- a usable set of pair-units
- non-empty immediate-neighbor shells
- and therefore a launchable local compatibility context

The same process was then applied to the positive export.

The positive run, however, stopped with:

> **Focal unit must have at least one immediate adjacent unit.**

This note explains why that happened.

---

## 3. Positive export structure
The NPZ-derived positive export currently contains exactly:

- **2 pair-units**
  - `p0_2`
  - `p1_3`

Both units have:

- positive support sector
- nonzero support strength
- but **empty immediate-neighbor lists**

So the converted export is structurally extremely sparse.

---

## 4. Why the immediate-neighbor lists are empty
The current converter defines:

> **immediate neighbors = pair-units that share one endpoint**

For the two positive-export units:

- `p0_2` has endpoints `{0, 2}`
- `p1_3` has endpoints `{1, 3}`

These endpoint sets do **not** intersect.

Therefore:

- `p0_2` is not an immediate neighbor of `p1_3`
- `p1_3` is not an immediate neighbor of `p0_2`

So both units receive:

- `immediate_neighbors = []`

This is the direct structural reason.

---

## 5. Why the runner stops
The compatibility runner requires:

- one focal unit
- plus at least one immediate adjacent unit

This is not optional inside the current logic because:

- A1 needs a local shell for agreement/conflict reading
- B1 needs a local shell for perturbation-response reading
- and the compatibility frame assumes a nontrivial immediate local neighborhood

If the focal unit has no neighbors, the runner correctly refuses to proceed.

So the stop condition is methodologically correct.

---

## 6. This is not a runner bug
This point matters.

The positive-export failure is **not** currently evidence of:

- broken parsing
- broken mapping
- broken conversion
- or broken runner code

Instead, it is evidence that:

> **the current positive export does not instantiate a launchable local compatibility shell under the present neighborhood definition**

That distinction must remain explicit.

---

## 7. Methodical interpretation
The correct interpretation is:

- the negative export is locally launchable
- the positive export is currently **not** locally launchable
- and this difference is itself a meaningful structural result

A concise wording is:

> **The current positive export falls into a no-local-shell class under the present shared-endpoint neighborhood rule.**

That is the current best reading.

---

## 8. What is and is not concluded
### What is concluded
- the positive export contains only two pair-units
- those two pair-units do not share endpoints
- therefore the immediate-neighbor shell is empty
- therefore the compatibility runner cannot currently launch

### What is not concluded
- that the positive export is useless
- that compatibility is absent in principle
- that the positive export should be discarded
- or that no alternative neighborhood rule could later make it launchable

This note only fixes the result under the **current** local-shell definition.

---

## 9. Immediate next-step discipline
The correct next-step discipline is:

- do **not** artificially force the positive export into a launch
- do **not** silently relax the neighborhood rule inside the same result line
- do **not** treat the no-neighbor outcome as a software defect

Instead:

> **record the positive export as not launchable under the current rule, and only later test any alternative neighborhood definition as a separate methodological change**

That is the proper discipline.

---

## 10. Safe summary sentence
A useful internal sentence is:

> The NPZ-derived positive export is not currently launchable for compatibility because its two pair-units do not share endpoints and therefore generate no immediate local shell under the present neighborhood rule.

A shorter version is:

> **Positive export: no shared endpoints, no local shell, no launch.**

Both are good steering lines.

---

## 11. Bottom line
The NPZ-derived positive export is currently **not launchable** under the compatibility runner because:

- it contains only `p0_2` and `p1_3`
- both units have `immediate_neighbors = []`
- and the current compatibility logic requires at least one immediate adjacent unit

So the positive export should currently be classified as:

> **no-local-neighbor / no-local-shell under current neighborhood definition**

This is the present diagnostic status of the positive export.
