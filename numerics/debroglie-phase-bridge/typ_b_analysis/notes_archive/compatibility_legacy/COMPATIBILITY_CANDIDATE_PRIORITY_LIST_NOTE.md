# COMPATIBILITY_CANDIDATE_PRIORITY_LIST_NOTE

## Priority list for first-pass compatibility candidate families

**Date:** 2026-04-06  
**Status:** internal priority / candidate triage note

---

## 1. Purpose
This note translates the current compatibility-layer work into a practical first-pass candidate ranking.

Its purpose is not to prove that any candidate is already correct.
Its purpose is narrower:

> **to decide which compatibility candidate families should be tested first, which should be treated as secondary, and which should currently be deferred.**

This is needed because the project now has:
- a minimal compatibility pilot frame
- an evaluation standard for candidates
- but not yet a practical candidate triage order

This note provides that order.

---

## 2. Why a priority list is needed
The compatibility layer is currently the largest open mechanism gap in the `typ_b_analysis` block.

That makes it both:
- the highest-leverage target,
- and the most dangerous place for idea inflation.

Without a priority structure, the next phase could easily fragment into:
- too many attractive signals,
- too much concept-driven optimism,
- and too little focused testing.

A candidate priority list is therefore a discipline device.

---

## 3. Priority logic
Candidates are ranked here using four questions:

1. Can the candidate plausibly be computed early enough?
2. Does it have a realistic chance of outperforming overlap-only?
3. Is it less likely to collapse into later stabilization or morphology?
4. Is the candidate interpretable enough to justify real testing effort?

Candidates that score better on these four points should be tested earlier.

---

## 4. Tier 1 — Highest priority candidates

## 4.1 Pre-stabilization local coherence
This is the current highest-priority candidate family.

### Why it is Tier 1
It sits most naturally between:
- generic overlap
and
- later stabilization

Possible directions include:
- local sign consistency
- local phase-sector consistency
- neighborhood agreement
- structured local support coherence

### Why it fits the current architecture
This family speaks directly to the project’s strongest open question:
- whether some overlaps are already more jointly supportable before stabilization has visibly emerged

### Main risk
It may still collapse into:
- overlap descriptors that add little,
or
- hidden stability signals that are too late

### Current priority judgement
**Tier 1**
because it is:
- early enough in spirit
- structurally meaningful
- and close to the missing mechanism gap itself

---

## 4.2 Removal sensitivity near the bridge-support layer
This is the second Tier-1 candidate family.

### Why it is Tier 1
It directly asks:
- which overlap relations are truly carrying later supportability?

If done carefully enough, this can expose:
- not merely present overlap,
but
- structurally important overlap

### Why it fits the current architecture
This family has strong practical value because it aligns well with the project’s existing style:
- leave-one-out logic
- damage testing
- carrier thinning
- role discrimination

### Main risk
If performed too late in the pipeline, it stops being compatibility and turns into:
- a disguised stabilization analysis

So its timing and insertion point are critical.

### Current priority judgement
**Tier 1**
because it is:
- close to existing project methodology
- likely to produce interpretable signals quickly
- and useful even if it does not fully solve compatibility

---

## 5. Tier 2 — Secondary but worthwhile candidates

## 5.1 Sign / sector contrast signals
This is a serious candidate family, but not first.

### Why it is interesting
Earlier project work already suggested that sign structure can matter strongly.
Possible directions include:
- positive/negative sector contrast
- structured sign imbalance
- sector-alignment vs sector-conflict measures

### Why it is not Tier 1
This family is more vulnerable to:
- model sensitivity
- interpretive overreading
- and accidental artifact generation

It may be very useful, but it is less clean as a first move than local coherence or removal sensitivity.

### Main risk
Sector structure can look deep even when it is:
- family-specific
- threshold-sensitive
- or only indirectly relevant

### Current priority judgement
**Tier 2**
because it is:
- promising,
- but not the cleanest first candidate family

---

## 5.2 Structured asymmetry candidates
This family includes signals based on local asymmetry, directional imbalance, or non-uniform relational support environments.

### Why it is interesting
A compatibility layer might plausibly leave traces in how support is distributed unevenly before stabilization settles.

### Why it is not Tier 1
This family is more difficult to interpret cleanly and may easily drift into:
- descriptive irregularity
- or weak morphology proxies

### Main risk
Asymmetry can become a vague catch-all if not tightly defined.

### Current priority judgement
**Tier 2**
because it may be useful later, but should not currently outrank cleaner candidates.

---

## 6. Tier 3 — Deferred or low-priority candidates

## 6.1 Morphology-near candidates
Any candidate too close to:
- later form
- later readable structure
- or morphology-heavy measures

should currently be deferred.

### Reason
These candidates are too likely to collapse into:
- `grid_deviation_score`
- or other late-stage readable effects

That makes them weak compatibility candidates.

### Current priority judgement
**Tier 3**
because they are too late in the mechanism chain.

---

## 6.2 Stability-near candidates
Any candidate that looks too similar to:
- `simple_rigidity_surrogate`
- persistence-style bridge survival
- or already-achieved internal coherence

should currently be deferred or treated with extreme suspicion.

### Reason
These are precisely the tautology-risk zone.

### Current priority judgement
**Tier 3**
because they are most likely to rename stabilization rather than reveal compatibility.

---

## 6.3 Purely analogy-driven candidates
Candidates justified mainly because they sound chemically or philosophically elegant, but with no early operational pathway, should currently be deferred.

### Reason
The project has benefited from analogies, but compatibility testing now needs:
- operational leverage
more than
- conceptual beauty

### Current priority judgement
**Tier 3**
until they can be translated into early measurable form.

---

## 7. Summary table

| Candidate family | Priority | Why interesting | Main risk |
|---|---|---|---|
| Pre-stabilization local coherence | Tier 1 | Most natural early supportability signal | Could collapse into overlap or hidden stability |
| Removal sensitivity near bridge-support layer | Tier 1 | Strong fit to project’s existing leave-one-out style | Can become disguised stabilization analysis |
| Sign / sector contrast | Tier 2 | Earlier work suggests sign structure matters | Threshold/model sensitivity, overreading risk |
| Structured asymmetry | Tier 2 | May reveal uneven pre-support structure | Can drift into vague irregularity or morphology |
| Morphology-near candidates | Tier 3 | Easy to compute later | Too late, likely readability-side |
| Stability-near candidates | Tier 3 | Often numerically strong | Highest tautology risk |
| Pure analogy-driven candidates | Tier 3 | Conceptually attractive | Too weak operationally at present |

---

## 8. Recommended first-pass workflow
The current recommended order is:

### Step 1
Test one narrow local-coherence candidate family against overlap-only.

### Step 2
Test one removal-sensitivity candidate family, but only if the insertion point is early enough to remain mechanistically meaningful.

### Step 3
Only after that, examine one sign/sector contrast candidate family.

### Step 4
Hold morphology-near and stability-near candidates back unless they can be clearly redefined into earlier signals.

This is the preferred first-pass workflow.

---

## 9. What should not happen now
The following should currently be avoided:

- testing too many compatibility candidates at once
- starting with the most elegant-looking rather than the most structurally plausible candidates
- using morphology-side or rigidity-side candidates as “compatibility solutions”
- inflating a Tier-2 or Tier-3 signal into a major mechanism claim
- confusing candidate generation with mechanism closure

These are all bad next moves.

---

## 10. Short internal steering sentence
A useful short sentence is:

> **Test first what is earliest, structurally plausible, and least likely to rename stabilization.**

A second useful sentence is:

> **Tier 1 should sit between overlap and rigidity, not too close to either end.**

Both should remain guiding principles.

---

## 11. Bottom line
The compatibility layer should currently be approached with a narrow first-pass ranking.

### Test first
- pre-stabilization local coherence
- removal sensitivity near the bridge-support layer

### Test second
- sign / sector contrast
- structured asymmetry

### Hold back for now
- morphology-near candidates
- stability-near candidates
- purely analogy-driven candidates

That is the current best priority structure for compatibility candidate work.
