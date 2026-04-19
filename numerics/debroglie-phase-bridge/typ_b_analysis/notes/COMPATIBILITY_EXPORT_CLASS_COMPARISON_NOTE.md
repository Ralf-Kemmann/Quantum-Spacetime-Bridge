# COMPATIBILITY_EXPORT_CLASS_COMPARISON_NOTE

## Comparative note across NPZ-derived export classes: negative, abs, positive

**Date:** 2026-04-08  
**Status:** internal comparison note

---

## 1. Purpose
This note compares the current compatibility outcomes across the three NPZ-derived export classes:

- **negative**
- **abs**
- **positive**

Its purpose is to move from isolated run reading to a first structured export-class comparison.

This is a comparison note, not a final theory note.

---

## 2. Comparison frame
All three export classes were treated through the same general workflow:

1. convert NPZ matrix artifacts into local export JSON
2. map the export into the compatibility runner
3. test launchability under the current local-neighbor rule
4. read A1 and B1 under the current proxy logic
5. compare outcomes

For the negative export, the reformed A1 anti-stabilization rule was already applied and validated.
The abs export was then run under the same reformed rule.
The positive export was checked for launchability under the current neighborhood definition.

So the comparison is methodologically aligned.

---

## 3. Negative export
### Launchability
- **launchable**

### Result state
- **A1:** materially active
- **B1:** materially active
- **global outcome:** Outcome C
- **promotion state:** both candidates promoted

### Reading
The reformed negative-export run restored A1 without weakening B1.

A concise reading is:

> **negative export = dual-candidate compatible under the reformed rule**

So the negative export is the strongest current compatibility case.

---

## 4. Abs export
### Launchability
- **launchable**

### Result state
- **A1:** weak / ambiguous
- **B1:** materially active
- **global outcome:** Outcome C
- **promotion state:** one candidate promoted
- **lead candidate:** B1

### Reading
The abs export remains compatible enough to launch and to reach Outcome C,
but it does not support A1 at the same strength as the negative export.

A concise reading is:

> **abs export = fragility-dominant compatibility case**

So the abs export is an intermediate case.

---

## 5. Positive export
### Launchability
- **not launchable under current local-neighbor rule**

### Structural reason
The NPZ-derived positive export currently contains only:

- `p0_2`
- `p1_3`

and both pair-units have:

- `immediate_neighbors = []`

So no focal unit can provide a nontrivial immediate local shell.

### Reading
The positive export is therefore not currently evaluable by the present compatibility runner.

A concise reading is:

> **positive export = no-local-shell case under current neighborhood definition**

So the positive export is currently outside the runner’s launchable domain.

---

## 6. Compact comparison table

| Export class | Launchable | A1 | B1 | Outcome | Current reading |
|---|---|---|---|---|---|
| negative | yes | materially active | materially active | Outcome C | dual-candidate compatible |
| abs | yes | weak / ambiguous | materially active | Outcome C | fragility-dominant |
| positive | no | not evaluated | not evaluated | no run | no-local-shell |

This is the current compact comparison picture.

---

## 7. Main comparative pattern
The three export classes do not behave uniformly.

Instead they show a structured gradient:

- **negative** = strongest compatibility structure
- **abs** = partially compatible, but B1-led
- **positive** = structurally not launchable under current neighborhood rule

That means the current framework is not acting like a trivial all-pass system.

A concise summary is:

> **The compatibility layer is export-class sensitive.**

This is the main comparative pattern.

---

## 8. Why this matters theoretically
This matters because a meaningful compatibility layer should not simply:

- accept everything
- or reject everything

Instead, it should show selective structural response.

The present comparison does exactly that:

- one class supports both candidates
- one class supports mainly fragility-side structure
- one class currently does not instantiate a local shell

So the framework is already producing differentiated structure, not merely generic positivity.

That is an encouraging sign for the theory’s operational side.

---

## 9. What this comparison does not yet prove
This comparison still does **not** prove:

- that the current export conversion is final
- that the present neighborhood rule is optimal
- that A1/B1 roles are fully stabilized
- or that the observed gradient is already universal

This is still:

- a first structured comparison
- under one current export construction and one current compatibility runner

That limitation must remain explicit.

---

## 10. Most defensible current reading
The most defensible current reading is:

> **The current compatibility framework carries real structural signal. Under the present export construction, the negative class is the strongest compatibility case, the abs class remains compatible but B1-dominant, and the positive class is not currently launchable because it does not generate a local shell.**

A shorter version is:

> **negative strongest, abs intermediate, positive non-launchable.**

This is the best current comparison sentence.

---

## 11. Immediate next step
The next correct step after this comparison is:

> **decide whether the positive class should remain a documented no-local-shell result under the current rule, or whether a separate later test of an alternative neighborhood definition should be opened as a new methodological branch**

That is now the real decision point.

---

## 12. Bottom line
The current export-class comparison yields:

- **negative:** launchable, A1 active, B1 active
- **abs:** launchable, A1 weak, B1 active
- **positive:** not launchable under current local-neighbor rule

So the present compatibility layer already shows a nontrivial structural ranking across export classes.

This is the current comparison status of the compatibility framework.
