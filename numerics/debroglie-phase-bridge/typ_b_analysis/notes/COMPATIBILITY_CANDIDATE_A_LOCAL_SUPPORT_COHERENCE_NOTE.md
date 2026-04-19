# COMPATIBILITY_CANDIDATE_A_LOCAL_SUPPORT_COHERENCE_NOTE

## Candidate A: local support coherence as a first compatibility-layer candidate

**Date:** 2026-04-07  
**Status:** internal candidate note  
**Candidate ID:** CLC-A-01

---

## 1. Purpose
This note defines the first concrete Tier-1 compatibility candidate:

> **Local support coherence**

The purpose is not to claim that this candidate already solves the compatibility layer.

The purpose is narrower:

- to define one concrete early candidate,
- to place it clearly between overlap and stabilization,
- and to make it testable under the current first-pass compatibility framework.

This is a candidate-definition note, not a result note.

---

## 2. One-sentence meaning
This candidate is intended to capture whether a local overlap environment is not merely present, but already internally coherent enough to count as a plausible pre-stabilization supportability signal.

---

## 3. Why this candidate is worth testing first
Local support coherence is a strong Tier-1 candidate because it fits the current architecture unusually well.

The project already suggests:

- overlap alone is too weak
- stabilization is too late
- morphology/readability are later still

So the missing layer should plausibly be something like:

- not yet persistence
- but already more than mere overlap
- and locally structured enough to indicate whether a common mode could in principle be jointly supported

That is exactly the niche local support coherence tries to occupy.

---

## 4. Structural role in the mechanism chain
The intended role of Candidate A is:

- **after** overlap
- **before** stabilization
- **before** morphology / readability

Working mechanism position:

`generic overlap -> local support coherence -> later stabilization possibility -> later form / readability`

That does **not** mean Candidate A is already known to work.
It only means this is the role it is supposed to test.

---

## 5. Earliest computation point
### Intended earliest computation point
Candidate A should be computable from a local relational neighborhood before later bridge-support success is already known.

That means:
- before later stabilization-side outcomes are used
- before later morphology/readability measures are read in
- and ideally from local overlap-structured information alone plus local neighborhood context

### Timing judgment
**Target status:** clearly pre-stabilization

### Main timing danger
If the candidate requires:
- already-thresholded late graph structure
- or information that already presupposes stable bridge survival

then it has drifted too late and should be downgraded or rejected.

---

## 6. Required inputs
The candidate should ideally use only early local information such as:

- local overlap relations
- local sign consistency or inconsistency
- local phase-sector agreement, if available and meaningful
- local neighborhood support agreement
- simple pre-stabilization adjacency context

It should **not** require as input:
- later bridge-survival labels
- later rigidity values as defining ingredients
- morphology/readability outputs

That is essential for anti-tautology discipline.

---

## 7. Provisional candidate logic
The basic intended logic is:

> A local overlap relation should count as more compatible when its surrounding local neighborhood is not merely strong in magnitude, but internally more consistent, less conflicted, and more jointly supportable.

In other words:
- mere overlap magnitude says “something is there”
- local support coherence asks whether what is there is mutually aligned enough to plausibly support a common mode later

That is the conceptual difference.

---

## 8. Provisional procedural definition
A fully fixed formula is not yet claimed here.
But the candidate should be defined procedurally enough for first-pass work.

### Procedural sketch
For each local relation or local neighborhood unit:

1. identify the local overlap environment
2. characterize internal consistency across that environment
3. penalize obvious internal conflict or fragmentation
4. aggregate into one local support-coherence score

Possible ingredients:
- sign agreement fraction
- phase-sector consistency
- neighborhood-weighted relational agreement
- conflict penalty term
- local dispersion penalty

### Minimal formal template
A generic placeholder form could be:

`CLC = local agreement term - local conflict term`

or more explicitly:

`CLC = A_local - lambda * C_local`

where:
- `A_local` measures internally aligned local support
- `C_local` measures internal inconsistency / conflict
- `lambda` controls conflict penalty strength

This is only a working formal shell, not yet a final formula.

---

## 9. Why this is not just overlap
This section is mandatory.

Candidate A is **not** supposed to be just overlap because overlap alone says only:
- how much relation is present
or
- how strong a local relation looks in raw magnitude terms

Local support coherence instead asks:
- whether neighboring local relations tell a mutually compatible story

So the intended distinction is:

- overlap = presence
- local support coherence = structured local supportability

If Candidate A ends up collapsing into a smoothed overlap magnitude, it has failed.

---

## 10. Why this is not just stabilization
This section is equally mandatory.

Candidate A is **not** supposed to be stabilization because it should not require:
- already-achieved persistence
- later bridge survival
- or downstream rigidity-like behavior

Instead it should remain:
- a pre-stabilization plausibility signal
- not an already-achieved success signal

If Candidate A predicts later support only because it already encodes persistence, then it is not compatibility but disguised stabilization leakage.

---

## 11. Expected directional meaning
### Higher value means
Greater local joint supportability.
In the intended reading, a higher score means:
- local relations are more mutually aligned
- less internally conflicted
- and therefore more plausible as preconditions for later bridge-support behavior

### Lower value means
Weaker local supportability.
In the intended reading, a lower score means:
- locally fragmented
- more internally conflicted
- or less plausible as a compatibility-side precursor

If no interpretable direction survives implementation, the candidate weakens substantially.

---

## 12. Main risks
### Main tautology risk
The candidate may accidentally encode later stabilization if the local neighborhood definition is taken from already stabilized structure.

### Main overlap-redundancy risk
The candidate may collapse into a dressed-up overlap magnitude or local density measure.

### Main threshold/artifact risk
The candidate may appear meaningful only under one neighborhood definition or one threshold choice.

### Main interpretability risk
If conflict and agreement terms are too abstract or too arbitrary, the score may become numerically active but structurally unclear.

### Main current risk sentence
The main current risk of Candidate A is that it may look like a supportability signal while in practice behaving only as a smoothed overlap proxy or a weak late-stage stability shadow.

---

## 13. Baseline comparison plan
Candidate A should be compared explicitly against:

### Overlap-only baseline
A direct overlap magnitude or simple overlap-derived baseline.

### Later stabilization proxy
A clearly downstream persistence/support signal, most naturally:
- `simple_rigidity_surrogate`

### Optional trivial control proxy
A weak local-density or local-smoothed-overlap control.

### What would count as success
Candidate A should count as interesting only if it:
- beats overlap-only meaningfully
- remains computable earlier than rigidity-side outcomes
- and stays structurally interpretable

### What would count as failure
Candidate A fails if it:
- adds no value beyond overlap
- works only because it leaks later stabilization
- or is too unstable to interpret

---

## 14. First-pass downstream outcome proxy
Candidate A should be judged in the first pass against one narrow downstream bridge-support or stabilization-related outcome proxy.

The exact proxy still needs to be fixed in the first matrix block, but it should be:
- downstream enough to count as later outcome
- narrow enough to stay interpretable
- and not so broad that every weak trend looks meaningful

For now:
**First-pass outcome proxy: to be fixed jointly with Candidate B in the first matrix block.**

---

## 15. Initial expectation
### Pre-test expectation
**Plausible Tier-1 candidate**

Why:
- it is structurally well placed
- it is earlier than stabilization in spirit
- and it directly targets the missing supportability gap

Why caution remains:
- it has a serious redundancy risk with overlap-only
- and a serious leakage risk if local structure is defined too late

So this is a promising but risky first candidate.

---

## 16. Readiness decision
### Readiness label
**ready for exploratory definition refinement**

### Reason
Candidate A is conceptually precise enough to enter the next step, but not yet formula-fixed enough for a clean first-pass comparison run without one more refinement layer.

That refinement should now specify:
- exact local neighborhood definition
- exact agreement term
- exact conflict term
- and timing-safe computation point

---

## 17. Safe current summary sentence
Candidate A is currently the strongest first-pass coherence-side compatibility candidate, but it must still be sharpened enough that it clearly exceeds overlap-only without collapsing into smoothed density or hidden stabilization.

---

## 18. Bottom line
Candidate A — local support coherence — is currently a strong Tier-1 compatibility candidate because it sits naturally in the missing gap between overlap and stabilization.

Its promise is:
- early structured supportability

Its danger is:
- redundancy with overlap
- or leakage from later stability

So the next correct move is not broad promotion, but one step of precise definition refinement before first-pass comparison.
