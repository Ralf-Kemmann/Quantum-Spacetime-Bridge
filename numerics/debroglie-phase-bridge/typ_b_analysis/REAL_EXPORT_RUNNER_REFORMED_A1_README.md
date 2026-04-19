# Real Export Compatibility Runner — Reformed A1 Ceiling

This version updates the A1 anti-stabilization rule from:

```text
late_stage iff a1_score >= a1_stabilization_ceiling
```

to:

```text
late_stage iff (a1_score >= a1_stabilization_ceiling) AND (neighbor_count >= a1_neighbor_min)
```

Recommended first project setting after the negative-export diagnostics:
- `a1_neighbor_min = 3`

This preserves the original A1 role logic while preventing tiny immediate shells
from being auto-classified as late-stage solely because their local coherence is perfect.
