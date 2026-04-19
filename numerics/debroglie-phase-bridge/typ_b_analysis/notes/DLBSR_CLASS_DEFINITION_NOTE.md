# DLBSR_CLASS_DEFINITION_NOTE

## Concrete first-pass definition of DLBSR-class

**Date:** 2026-04-07  
**Status:** internal proxy-definition note

---

## 1. Purpose
This note gives the first concrete definition of:

> **DLBSR-class = Downstream Local Bridge-Support Response class**

Its purpose is to make the first compatibility pass operationally sharper by fixing what the downstream outcome proxy should mean in class form.

This note does **not** claim that DLBSR-class is already the final or universally correct downstream target.

It only fixes the first-pass working definition.

---

## 2. Why DLBSR-class is needed
The first compatibility pass now already has:

- Candidate A = local support coherence
- Candidate B = early removal fragility
- overlap-only baseline
- later-stabilization boundary
- and the decision to use DLBSR in class form for the first pass

What was still missing was one explicit question:

> **What exactly counts as a local downstream bridge-support-positive versus bridge-support-negative outcome?**

This note answers that question.

---

## 3. Working conceptual definition
The intended meaning of DLBSR-class is:

> **DLBSR-class labels whether a local or mesoscopic structure has reached a later support-positive bridge-response state strongly enough to count as downstream bridge-support present, rather than only weakly implied or absent.**

A shorter version is:

> **DLBSR-class says whether later local bridge-support has actually become positively readable at a narrow support-response level.**

That is the intended meaning.

---

## 4. Why class form is the right first-pass choice
DLBSR-class is used in the first pass because it keeps the target:

- narrow
- interpretable
- less narratively inflatable
- easier to compare against Candidate A and B
- and simpler than a continuous score or margin

The first pass is a triage block.
A class target is therefore better than a rich scalar target at this stage.

---

## 5. Recommended first-pass form
### Preferred first-pass implementation
Use **binary DLBSR-class**:

- **DLBSR-positive**
- **DLBSR-negative**

This is the cleanest first-pass start.

### Optional later refinement
A ternary form may later be introduced:
- positive
- borderline
- negative

But for the first pass, the binary form is preferred unless there is a strong reason not to.

---

## 6. Structural role of DLBSR-class
DLBSR-class is intended to sit:

- later than Candidate A and Candidate B
- later than overlap-only
- downstream of early supportability candidates
- but still earlier and narrower than broad morphology/readability claims

Working role in the chain:

`overlap -> compatibility candidate -> later local bridge-support response (DLBSR-class) -> broader stabilization / readability development`

This keeps DLBSR-class close to the mechanism gap without jumping too far downstream.

---

## 7. Concrete first-pass class meaning

## 7.1 DLBSR-positive
A local or mesoscopic structure is classified as **DLBSR-positive** if:

- it shows a downstream bridge-support response strong enough to count as local support actually materializing,
- and that response is not merely a tiny fluctuation or weak descriptive hint,
- and the response sits at the support side rather than at full morphology/readability scale.

In plain language:
- later local support has become positively present.

---

## 7.2 DLBSR-negative
A local or mesoscopic structure is classified as **DLBSR-negative** if:

- it does not show a downstream bridge-support response strong enough to count as local support-positive,
- or the response remains too weak, too absent, or too unformed to count as later local bridge-support present.

In plain language:
- later local support has not materially formed.

---

## 8. What DLBSR-class should be based on
DLBSR-class should be based on one narrow later support-related criterion, such as:

- a later local support response exceeding a defined minimal support threshold
- a later local support-success classification
- a later support-positive status assigned from one narrow bridge-support indicator

The exact implementation criterion still needs to be selected explicitly in the run design, but it must remain:

- local or mesoscopic
- later than the candidates
- narrower than full readability
- distinct from raw rigidity labeling

This is essential.

---

## 9. What DLBSR-class must not be based on
DLBSR-class must **not** be defined from:

- full morphology/readability success
- large ontological interpretation
- a vague “interesting structure” judgment
- a direct reuse of Candidate A or Candidate B
- or a raw copy of the later-stabilization boundary itself

In particular:
- DLBSR-class must not simply be “rigidity high = positive”
without further narrowing, because then the target and the upper boundary collapse into one another.

That must be avoided.

---

## 10. Minimal implementation rule
A safe first-pass implementation rule is:

> **Assign DLBSR-positive if a narrow later local bridge-support indicator crosses a pre-declared minimal support-positive criterion; otherwise assign DLBSR-negative.**

This is intentionally plain.
The important part is:
- pre-declared
- narrow
- later than the candidates
- and not broadened during the pass

That is the correct first-pass rule shape.

---

## 11. Why DLBSR-class is distinct from the later-stabilization boundary
The distinction should remain explicit.

### Later-stabilization boundary
Used as:
- anti-tautology ceiling
- “too late / too much like already-achieved persistence” check

Current preferred proxy:
- `simple_rigidity_surrogate`

### DLBSR-class
Used as:
- downstream outcome target
- “did later local bridge-support actually materialize enough to count as support-positive?” check

So the difference is:

- **boundary** = limit above which a candidate is too late
- **DLBSR-class** = target outcome the candidate is supposed to relate to

These roles must remain separate.

---

## 12. Why DLBSR-class is distinct from overlap-only
DLBSR-class must also remain distinct from the lower baseline.

### Overlap-only baseline
Means:
- relation is present
- overlap is descriptively there

### DLBSR-class
Means:
- later local bridge-support has actually materialized enough to count as support-positive or support-negative

So the difference is:

- **overlap** = descriptive presence
- **DLBSR-class** = later support-response outcome

That distinction must stay clear.

---

## 13. Main risks of DLBSR-class

### Risk 1 — Too close to rigidity
If DLBSR-class is defined too directly from a rigidity-like signal, then the upper boundary and downstream target collapse together.

### Risk 2 — Too broad
If DLBSR-class includes late morphology or readability logic, the first pass becomes too inflated.

### Risk 3 — Too weak
If DLBSR-positive is assigned too easily, the class loses discriminative force.

### Risk 4 — Threshold arbitrariness
If the support-positive criterion is chosen loosely or post hoc, the class becomes unstable.

These risks must be controlled explicitly.

---

## 14. Recommended first-pass discipline
For the first pass, DLBSR-class should be:

- binary
- pre-declared
- fixed before candidate comparison
- identical for Candidate A and Candidate B
- explicitly stated in the result record
- and not redefined mid-pass

This is mandatory.

---

## 15. Safe summary sentence
A useful internal sentence is:

> DLBSR-class should mark whether later local bridge-support has become positively present at a narrow support-response level, without expanding into full readability and without collapsing into the rigidity-side boundary.

A shorter version is:

> **DLBSR-class = later local bridge-support: yes or no.**

Both are good current steering lines.

---

## 16. Bottom line
The concrete first-pass definition of DLBSR-class is:

- **binary**
- **later than Candidate A and Candidate B**
- **narrowly support-response based**
- **distinct from overlap-only**
- **distinct from the later-stabilization boundary**

Its two values are:

- **DLBSR-positive** = later local bridge-support response materially present
- **DLBSR-negative** = later local bridge-support response not materially present

That is the current working definition of DLBSR-class for the first compatibility pass.
