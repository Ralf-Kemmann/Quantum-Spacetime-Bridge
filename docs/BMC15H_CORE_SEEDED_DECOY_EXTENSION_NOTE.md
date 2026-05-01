# BMC-15h — Core-Seeded Decoy Extension Note

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMC15H_CORE_SEEDED_DECOY_EXTENSION_NOTE.md`  
Status: Extension note for the next BMC-15h diagnostic run

---

## 1. Purpose

BMC-15h-v1 established that the corrected feature-structured null family is a genuine node-family-preserving control. The result was construction-dependent:

- the real graph exceeded degree-/weight-preserving rewires throughout;
- the real graph exceeded feature-structured shuffles mainly under selective local construction rules;
- broad envelope constructions were partially reproduced by feature-structured nulls.

The next diagnostic step is the `core_seeded_decoy` family.

Its purpose is to test whether a BMC-15-like compact reference core can be deliberately and cheaply inserted into otherwise controlled null graphs.

Internal working question:

```text
Kann man den Klunker absichtlich billig nachbauen?
```

More formal question:

```text
Can compact reference-core containment be reproduced by seeding a small
high-weight local core into otherwise controlled null objects, or does the
canonical real graph still remain distinguishable under selective local
construction rules?
```

---

## 2. Relation to previous BMC-15h runs

### BMC-15h-v0

The initial run completed technically, but `feature_structured_shuffle` degraded to an unrestricted node-shuffle fallback because the metadata family column was misconfigured.

Interpretation status:

```text
pipeline smoke test plus partial null diagnostic
```

### BMC-15h-v1

The metadata mapping was corrected:

```yaml
columns:
  node_id: "node_id"
  family: "node_family"

null_families:
  feature_structured_shuffle:
    family_column: "node_family"
```

This removed the metadata/fallback warnings and enabled a genuine feature-structured shuffle.

Interpretation status:

```text
construction-dependent local-core specificity indication
```

### BMC-15h-v2 target

Enable `core_seeded_decoy` as a deliberately adversarial null family.

Interpretation status to be determined:

```text
cheap-core reproducibility diagnostic
```

---

## 3. Null family definition

The core-seeded decoy family should create null graph objects that preserve broad graph context while deliberately planting a compact high-weight local seed.

Recommended config activation:

```yaml
null_families:
  core_seeded_decoy:
    enabled: true
    repeats: 50
    seed_edge_count: 6
    seed_weight_quantile: 0.90
    preserve_global_edge_count: true
```

Conceptual meaning:

| field name | type | description |
|---|---:|---|
| `enabled` | boolean | Whether the core-seeded decoy family is included in the run. |
| `repeats` | integer | Number of decoy samples generated. |
| `seed_edge_count` | integer | Number of edges deliberately used to form the artificial local seed. |
| `seed_weight_quantile` | float | Quantile threshold for choosing high-weight seed candidates. |
| `preserve_global_edge_count` | boolean | Whether the final decoy graph keeps the same global edge count as the canonical object. |

---

## 4. Expected output impact

With the new null family enabled, the output files should remain the same type as in BMC-15h-v1:

```text
runs/BMC-15h/structured_specificity_extension_open/
  bmc15h_core_metrics.csv
  bmc15h_envelope_metrics.csv
  bmc15h_real_vs_null_summary.csv
  bmc15h_null_family_inventory.csv
  bmc15h_run_manifest.json
  bmc15h_warnings.json
  bmc15h_config_resolved.yaml
```

Expected inventory change:

```text
degree_weight_preserving_rewire: 50 null objects
feature_structured_shuffle:       50 null objects
core_seeded_decoy:                50 null objects
```

If the real object is still included as one canonical object, then the evaluated object count should become:

```text
1 real object + 150 null objects = 151 objects
```

With 18 construction variants, the approximate row count expectation is:

```text
core metrics:      18 × 151 = 2718 rows
envelope metrics:  18 × 151 = 2718 rows
```

The real-vs-null summary should add one further null-family block.

If the runner computes 54 comparison rows per null family, then the expected summary row count becomes:

```text
3 null families × 54 rows = 162 rows
```

These numbers are expectations, not acceptance requirements. The run manifest should be treated as the source of truth.

---

## 5. Befund target

The core-seeded decoy is intentionally adversarial.

A strong result would not be that the real graph always wins. A more informative result is whether the real graph remains distinguishable specifically under selective local construction rules, while broad envelope rules may again be easier to reproduce.

Possible result patterns:

### Pattern A — Decoy cheaply reproduces the real core

```text
core_seeded_decoy produces high core containment across selective and broad
construction rules, with high empirical exceedance fractions.
```

Interpretation:

```text
The current core-containment readout is cheap under seeded local construction.
The BMC-15h core metric is then less specific than indicated by rewire and
feature-structured shuffle controls alone.
```

### Pattern B — Decoy reproduces only broad envelopes

```text
core_seeded_decoy reproduces broad threshold / high-k envelope containment but
does not reproduce selective local construction behavior.
```

Interpretation:

```text
This reinforces the BMC-15h-v1 distinction between selective-local specificity
and broad-envelope non-specificity.
```

### Pattern C — Real graph still exceeds seeded decoys under most rules

```text
The real graph remains above core-seeded decoys even though the decoys contain
an intentionally planted local seed.
```

Interpretation:

```text
This would strengthen the construction-qualified local-core specificity
indication. It would still not prove physical geometry, but it would show that
the tested core behavior is not trivially reproduced by planting a compact
high-weight seed.
```

---

## 6. Interpretation discipline

The core-seeded decoy test is a methodological adversarial control, not a physical proof.

Allowed language:

```text
cheap-core reproducibility diagnostic
adversarial structured null
construction-qualified local-core specificity indication
selective-local robustness
broad-envelope non-specificity
```

Disallowed language:

```text
core specificity is proven
physical geometry is recovered
the core is physically real
the decoy test proves emergent spacetime
feature-structured nulls are defeated
```

---

## 7. Recommended run command

After enabling `core_seeded_decoy` in the config:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

python scripts/run_bmc15h_structured_specificity_extension.py \
  --config data/bmc15h_structured_specificity_extension_config.yaml
```

Warning check:

```bash
python - <<'PY'
import json
from pathlib import Path

root = Path("runs/BMC-15h/structured_specificity_extension_open")
warnings = json.loads((root / "bmc15h_warnings.json").read_text(encoding="utf-8"))

print("warnings:", len(warnings))
for w in warnings:
    print(w["severity"], "-", w["message"])
PY
```

Summary readout:

```bash
python - <<'PY'
from pathlib import Path
import csv
from collections import Counter, defaultdict

root = Path("runs/BMC-15h/structured_specificity_extension_open")
summary = root / "bmc15h_real_vs_null_summary.csv"

rows = list(csv.DictReader(summary.open(newline="", encoding="utf-8")))

print("rows:", len(rows))

print("\nInterpretation labels:")
for k, v in Counter(r["interpretation_label"] for r in rows).items():
    print(" ", k + ":", v)

print("\nBy null family:")
byfam = defaultdict(Counter)
for r in rows:
    byfam[r["null_family"]][r["interpretation_label"]] += 1

for fam, c in byfam.items():
    print("\n" + fam)
    for k, v in c.items():
        print(" ", k + ":", v)

core_rows = [
    r for r in rows
    if "core" in r["metric_name"]
]

def f(x):
    try:
        return float(x)
    except Exception:
        return float("nan")

print("\nCore-related strongest real-minus-null cases:")
for r in sorted(core_rows, key=lambda r: f(r["real_minus_null_mean"]), reverse=True)[:20]:
    print(
        r["null_family"],
        r["metric_name"],
        r["construction_family"],
        r["construction_variant"],
        "real=", r["real_value"],
        "null_mean=", r["null_mean"],
        "delta=", r["real_minus_null_mean"],
        "exceed=", r["empirical_exceedance_fraction"],
        "label=", r["interpretation_label"],
    )

print("\nStrongest null-reproduction cases:")
for r in sorted(core_rows, key=lambda r: f(r["empirical_exceedance_fraction"]), reverse=True)[:20]:
    print(
        r["null_family"],
        r["metric_name"],
        r["construction_family"],
        r["construction_variant"],
        "real=", r["real_value"],
        "null_mean=", r["null_mean"],
        "delta=", r["real_minus_null_mean"],
        "exceed=", r["empirical_exceedance_fraction"],
        "label=", r["interpretation_label"],
    )
PY
```

---

## 8. Recommended config patch

Patch the existing config in place:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

python - <<'PY'
from pathlib import Path

cfg = Path("data/bmc15h_structured_specificity_extension_config.yaml")
text = cfg.read_text(encoding="utf-8")

text = text.replace(
    "core_seeded_decoy:\n    enabled: false",
    "core_seeded_decoy:\n    enabled: true",
)

cfg.write_text(text, encoding="utf-8")
print("patched:", cfg)
PY
```

Verify:

```bash
grep -A8 'core_seeded_decoy:' data/bmc15h_structured_specificity_extension_config.yaml
```

Expected:

```yaml
core_seeded_decoy:
  enabled: true
  repeats: 50
  seed_edge_count: 6
  seed_weight_quantile: 0.90
  preserve_global_edge_count: true
```

---

## 9. Suggested result-note target after run

After the run, create:

```text
docs/BMC15H_CORE_SEEDED_DECOY_RESULT_NOTE.md
```

The result note should again separate:

```text
Befund
Interpretation
Hypothesis
Open gap
Claim boundary
```

Recommended summary sentence template:

```text
BMC-15h-v2 tests whether the compact BMC-15 reference-core proxy can be
deliberately reproduced by core-seeded decoys. The result should be interpreted
as a cheap-core reproducibility diagnostic, not as a physical-geometry proof.
```

---

## 10. Minimal commit plan

Before running:

```bash
git add \
  data/bmc15h_structured_specificity_extension_config.yaml \
  docs/BMC15H_CORE_SEEDED_DECOY_EXTENSION_NOTE.md

git status --short

git commit -m "Enable BMC-15h core-seeded decoy diagnostic"

git push
```

After running and writing the result note, commit the result note separately:

```bash
git add docs/BMC15H_CORE_SEEDED_DECOY_RESULT_NOTE.md

git status --short

git commit -m "Add BMC-15h core-seeded decoy result note"

git push
```

Run outputs should only be committed deliberately after checking file size and repository policy.
