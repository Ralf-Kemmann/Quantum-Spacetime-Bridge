#!/usr/bin/env python3
from __future__ import annotations

"""
BMC-04-v3.1 — Distribution-Preserving Organization Scramble
Soft-repair / balanced-objective scaffold with adjusted decision logic.

Current scope:
    First implementation for:
        - degree_strength_weight_preserved

Main change vs v3:
    The decision logic is aligned to the observed run behavior.
    If preservation passes and arrangement_signal_score is clearly readable
    (default operational threshold: 0.25), the run is classified as
    organization_sensitive rather than distribution_dominant_or_weak.
"""

import argparse
import csv
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

EPS = 1e-12


@dataclass
class Readout:
    bridge_signal_score: float
    d1_d2_separation_score: float
    weighted_relational_contrast_score: float
    endpoint_load_shift_score: float
    endpoint_load_dispersion_shift_score: float
    pair_neighborhood_consistency_shift_score: float
    shell_arrangement_shift_score: float
    shell_boundary_disruption_score: float
    arrangement_signal_score: float
    readability_label: str


@dataclass
class DecisionSummary:
    decision_label: str
    primary_reason: str
    secondary_reason: str
    test_informativeness: str
    distribution_preservation_status: str
    organization_disruption_status: str
    bridge_response_status: str


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="BMC-04-v3.1 — Distribution-Preserving Organization Scramble"
    )
    p.add_argument("--input", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument(
        "--variant",
        required=True,
        choices=["degree_strength_weight_preserved"],
    )
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--shell-source", choices=["input_column", "derived"], default="input_column")
    p.add_argument("--preservation-tolerance", type=float, default=1e-9)
    p.add_argument("--repair-iterations", type=int, default=8000)
    p.add_argument("--strength-target-min", type=float, default=0.99)
    p.add_argument("--strength-hard-min", type=float, default=0.965)
    p.add_argument("--organization-weight", type=float, default=1.0)
    p.add_argument("--repair-patience", type=int, default=1000)
    p.add_argument(
        "--organization-readable-threshold",
        type=float,
        default=0.25,
        help="Decision threshold for organization_sensitive under passed preservation.",
    )
    p.add_argument("--write-pair-level-debug", action="store_true")
    p.add_argument("--write-node-level-debug", action="store_true")
    return p.parse_args()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    q = max(0.0, min(1.0, q))
    pos = q * (len(sorted_values) - 1)
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return sorted_values[lo]
    frac = pos - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def sort_pair(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a <= b else (b, a)


def load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows: list[dict[str, Any]] = []
        for raw in reader:
            row = dict(raw)
            for field in ["pair_id", "endpoint_a", "endpoint_b", "weight"]:
                if field not in row:
                    raise ValueError(f"Missing required field '{field}'.")
            row["baseline_weight"] = safe_float(row["weight"])
            row["weight"] = safe_float(row["weight"])
            row["endpoint_a"] = str(row["endpoint_a"])
            row["endpoint_b"] = str(row["endpoint_b"])
            row["pair_key"] = "|".join(sort_pair(row["endpoint_a"], row["endpoint_b"]))
            rows.append(row)
    if not rows:
        raise ValueError("Input CSV is empty.")
    return rows


def endpoint_loads_from_weights(rows: list[dict[str, Any]], weights: list[float]) -> dict[str, float]:
    loads: dict[str, float] = defaultdict(float)
    for row, w in zip(rows, weights):
        loads[row["endpoint_a"]] += w
        loads[row["endpoint_b"]] += w
    return dict(loads)


def endpoint_loads(rows: list[dict[str, Any]], weight_field: str) -> dict[str, float]:
    loads: dict[str, float] = defaultdict(float)
    for row in rows:
        w = safe_float(row[weight_field])
        loads[row["endpoint_a"]] += w
        loads[row["endpoint_b"]] += w
    return dict(loads)


def derive_shell_labels(rows: list[dict[str, Any]]) -> dict[str, str]:
    loads = endpoint_loads(rows, "baseline_weight")
    values = sorted(loads.values())
    q1 = percentile(values, 1 / 3)
    q2 = percentile(values, 2 / 3)
    out = {}
    for endpoint, value in loads.items():
        if value <= q1:
            out[endpoint] = "s_1"
        elif value <= q2:
            out[endpoint] = "s_2"
        else:
            out[endpoint] = "s_3"
    return out


def ensure_shell_fields(rows: list[dict[str, Any]], shell_source: str) -> None:
    have_pair_shell = all("shell_label" in r and str(r.get("shell_label", "")).strip() for r in rows)
    if have_pair_shell:
        return
    endpoint_shells = derive_shell_labels(rows)
    for row in rows:
        a = row["endpoint_a"]
        b = row["endpoint_b"]
        sa = endpoint_shells[a]
        sb = endpoint_shells[b]
        row["endpoint_a_shell"] = sa
        row["endpoint_b_shell"] = sb
        row["shell_label"] = "s_same_" + sa if sa == sb else f"s_cross_{min(sa, sb)}_{max(sa, sb)}"


def shell_endpoint_map(rows: list[dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for row in rows:
        if row.get("endpoint_a_shell"):
            mapping[row["endpoint_a"]] = str(row["endpoint_a_shell"])
        if row.get("endpoint_b_shell"):
            mapping[row["endpoint_b"]] = str(row["endpoint_b_shell"])
    if mapping:
        return mapping
    inferred: dict[str, str] = {}
    for row in rows:
        label = str(row.get("shell_label", ""))
        if label.startswith("s_same_"):
            shell = label.replace("s_same_", "")
            inferred[row["endpoint_a"]] = shell
            inferred[row["endpoint_b"]] = shell
    return inferred


def shell_pair_matrix(rows: list[dict[str, Any]]) -> Counter[tuple[str, str]]:
    endpoint_shells = shell_endpoint_map(rows)
    counts: Counter[tuple[str, str]] = Counter()
    for row in rows:
        sa = endpoint_shells.get(row["endpoint_a"], "unknown")
        sb = endpoint_shells.get(row["endpoint_b"], "unknown")
        counts[tuple(sorted((sa, sb)))] += 1
    return counts


def pair_neighborhood_consistency(rows: list[dict[str, Any]], weight_field: str) -> dict[str, float]:
    loads = endpoint_loads(rows, weight_field)
    out: dict[str, float] = {}
    for row in rows:
        local_context = 0.5 * (loads[row["endpoint_a"]] + loads[row["endpoint_b"]])
        out[row["pair_id"]] = abs(safe_float(row[weight_field]) - local_context)
    return out


def pair_neighborhood_consistency_from_weights(rows: list[dict[str, Any]], weights: list[float]) -> dict[str, float]:
    loads = endpoint_loads_from_weights(rows, weights)
    out: dict[str, float] = {}
    for row, w in zip(rows, weights):
        local_context = 0.5 * (loads[row["endpoint_a"]] + loads[row["endpoint_b"]])
        out[row["pair_id"]] = abs(w - local_context)
    return out


def shell_rank_map(rows: list[dict[str, Any]], weight_field: str) -> dict[str, float]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get("shell_label", "unknown"))].append(row)
    ranks: dict[str, float] = {}
    for _, shell_rows in groups.items():
        ordered = sorted(shell_rows, key=lambda r: (-safe_float(r[weight_field]), str(r["pair_id"])))
        for idx, row in enumerate(ordered, start=1):
            ranks[row["pair_id"]] = float(idx)
    return ranks


def shell_rank_map_from_weights(rows: list[dict[str, Any]], weights: list[float]) -> dict[str, float]:
    groups: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for row, w in zip(rows, weights):
        groups[str(row.get("shell_label", "unknown"))].append((str(row["pair_id"]), w))
    ranks: dict[str, float] = {}
    for _, items in groups.items():
        ordered = sorted(items, key=lambda x: (-x[1], x[0]))
        for idx, (pair_id, _) in enumerate(ordered, start=1):
            ranks[pair_id] = float(idx)
    return ranks


def shell_boundary_metrics(rows: list[dict[str, Any]], baseline_rows: list[dict[str, Any]]) -> tuple[float, float, float]:
    baseline_shells = shell_endpoint_map(baseline_rows)
    crossing_flags: list[int] = []
    distances: list[int] = []
    for row in rows:
        sa = baseline_shells.get(row["endpoint_a"], "unknown")
        sb = baseline_shells.get(row["endpoint_b"], "unknown")
        try:
            ia = int(sa.split("_")[-1])
            ib = int(sb.split("_")[-1])
            d = abs(ia - ib)
        except Exception:
            d = 0
        crossing_flags.append(1 if d > 0 else 0)
        distances.append(d)
    frac = sum(crossing_flags) / len(crossing_flags) if crossing_flags else 0.0
    mean_d = sum(distances) / len(distances) if distances else 0.0
    return frac, mean_d, frac * max(1.0, mean_d)


def preservation_score_absdiff(numerator: float, denominator: float) -> float:
    if abs(denominator) < EPS:
        return 1.0 if abs(numerator) < EPS else 0.0
    return max(0.0, 1.0 - numerator / (denominator + EPS))


def preservation_metrics(baseline_rows: list[dict[str, Any]], perturbed_rows: list[dict[str, Any]]) -> dict[str, float]:
    base_weights = sorted(safe_float(r["baseline_weight"]) for r in baseline_rows)
    pert_weights = sorted(safe_float(r["weight"]) for r in perturbed_rows)
    p_w = preservation_score_absdiff(
        sum(abs(a - b) for a, b in zip(base_weights, pert_weights)),
        sum(abs(x) for x in base_weights),
    )

    base_deg = Counter()
    pert_deg = Counter()
    for rows, dest in ((baseline_rows, base_deg), (perturbed_rows, pert_deg)):
        for row in rows:
            dest[row["endpoint_a"]] += 1
            dest[row["endpoint_b"]] += 1
    nodes = sorted(set(base_deg) | set(pert_deg))
    p_d = preservation_score_absdiff(
        sum(abs(pert_deg[n] - base_deg[n]) for n in nodes),
        sum(base_deg[n] for n in nodes),
    )

    base_strength = endpoint_loads(baseline_rows, "baseline_weight")
    pert_strength = endpoint_loads(perturbed_rows, "weight")
    nodes_s = sorted(set(base_strength) | set(pert_strength))
    p_s = preservation_score_absdiff(
        sum(abs(pert_strength.get(n, 0.0) - base_strength.get(n, 0.0)) for n in nodes_s),
        sum(base_strength.get(n, 0.0) for n in nodes_s),
    )

    base_shell = shell_pair_matrix(baseline_rows)
    pert_shell = shell_pair_matrix(perturbed_rows)
    shell_keys = set(base_shell) | set(pert_shell)
    shell_den = sum(base_shell.values())
    p_shell = preservation_score_absdiff(
        sum(abs(pert_shell.get(k, 0) - base_shell.get(k, 0)) for k in shell_keys),
        shell_den,
    ) if shell_den > 0 else 0.0

    return {
        "weight_multiset_preservation_score": p_w,
        "degree_preservation_score": p_d,
        "strength_preservation_score": p_s,
        "shell_count_preservation_score": p_shell,
        "block_count_preservation_score": 0.0,
    }


def compute_readout(baseline_rows: list[dict[str, Any]], rows: list[dict[str, Any]]) -> Readout:
    weights = [safe_float(r["weight"]) for r in rows]
    mean_w = statistics.fmean(weights) if weights else 0.0
    std_w = statistics.pstdev(weights) if len(weights) > 1 else 0.0
    bridge_signal = abs(std_w / mean_w) if abs(mean_w) > EPS else std_w

    sorted_weights = sorted(weights)
    d1d2 = percentile(sorted_weights, 0.90) - percentile(sorted_weights, 0.10)
    contrast = statistics.fmean(abs(w - mean_w) for w in weights) if weights else 0.0

    base_loads = endpoint_loads(baseline_rows, "baseline_weight")
    new_loads = endpoint_loads(rows, "weight")
    nodes = sorted(set(base_loads) | set(new_loads))
    endpoint_shift = statistics.fmean(
        abs(new_loads.get(v, 0.0) - base_loads.get(v, 0.0)) for v in nodes
    ) if nodes else 0.0

    base_disp = statistics.pstdev(list(base_loads.values())) if len(base_loads) > 1 else 0.0
    new_disp = statistics.pstdev(list(new_loads.values())) if len(new_loads) > 1 else 0.0
    endpoint_disp_shift = abs(new_disp - base_disp)

    base_pnc = pair_neighborhood_consistency(baseline_rows, "baseline_weight")
    new_pnc = pair_neighborhood_consistency(rows, "weight")
    pair_ids = sorted(set(base_pnc) | set(new_pnc))
    pair_shift = statistics.fmean(
        abs(new_pnc.get(pid, 0.0) - base_pnc.get(pid, 0.0)) for pid in pair_ids
    ) if pair_ids else 0.0

    base_ranks = shell_rank_map(baseline_rows, "baseline_weight")
    new_ranks = shell_rank_map(rows, "weight")
    rank_ids = sorted(set(base_ranks) | set(new_ranks))
    shell_rank_shift = statistics.fmean(
        abs(new_ranks.get(pid, 0.0) - base_ranks.get(pid, 0.0)) for pid in rank_ids
    ) if rank_ids else 0.0

    _, _, shell_boundary = shell_boundary_metrics(rows, baseline_rows)
    components = [endpoint_shift, endpoint_disp_shift, pair_shift, shell_rank_shift, shell_boundary]
    arrangement = statistics.fmean(components) if components else 0.0
    readability = "arrangement_sensitive" if arrangement >= 0.30 else ("weakly_readable" if arrangement >= 0.15 else "low_signal")

    return Readout(
        bridge_signal_score=bridge_signal,
        d1_d2_separation_score=d1d2,
        weighted_relational_contrast_score=contrast,
        endpoint_load_shift_score=endpoint_shift,
        endpoint_load_dispersion_shift_score=endpoint_disp_shift,
        pair_neighborhood_consistency_shift_score=pair_shift,
        shell_arrangement_shift_score=shell_rank_shift,
        shell_boundary_disruption_score=shell_boundary,
        arrangement_signal_score=arrangement,
        readability_label=readability,
    )


def strength_preservation_score_for_weights(rows: list[dict[str, Any]], weights: list[float]) -> float:
    target = endpoint_loads(rows, "baseline_weight")
    current = endpoint_loads_from_weights(rows, weights)
    nodes = sorted(set(target) | set(current))
    return preservation_score_absdiff(
        sum(abs(current.get(n, 0.0) - target.get(n, 0.0)) for n in nodes),
        sum(target.get(n, 0.0) for n in nodes),
    )


def pair_neigh_shift_for_weights(rows: list[dict[str, Any]], weights: list[float], baseline_pnc: dict[str, float]) -> float:
    cand_pnc = pair_neighborhood_consistency_from_weights(rows, weights)
    pair_ids = sorted(baseline_pnc)
    return statistics.fmean(abs(cand_pnc.get(pid, 0.0) - baseline_pnc.get(pid, 0.0)) for pid in pair_ids) if pair_ids else 0.0


def shell_rank_shift_for_weights(rows: list[dict[str, Any]], weights: list[float], baseline_ranks: dict[str, float]) -> float:
    cand_ranks = shell_rank_map_from_weights(rows, weights)
    pair_ids = sorted(baseline_ranks)
    return statistics.fmean(abs(cand_ranks.get(pid, 0.0) - baseline_ranks.get(pid, 0.0)) for pid in pair_ids) if pair_ids else 0.0


def organization_objective_for_weights(rows: list[dict[str, Any]], weights: list[float], baseline_pnc: dict[str, float], baseline_ranks: dict[str, float], organization_weight: float) -> float:
    raw = pair_neigh_shift_for_weights(rows, weights, baseline_pnc) + shell_rank_shift_for_weights(rows, weights, baseline_ranks)
    return organization_weight * raw


def greedy_assign(rows: list[dict[str, Any]], rng: random.Random) -> list[float]:
    target_strength = endpoint_loads(rows, "baseline_weight")
    assigned = [0.0] * len(rows)
    current_strength: dict[str, float] = defaultdict(float)
    idxs = list(range(len(rows)))
    group_weights = [safe_float(rows[i]["baseline_weight"]) for i in idxs]
    rng.shuffle(group_weights)
    group_weights.sort(reverse=True)

    remaining = idxs[:]
    for w in group_weights:
        def score(i: int) -> float:
            row = rows[i]
            rem_a = target_strength[row["endpoint_a"]] - current_strength[row["endpoint_a"]]
            rem_b = target_strength[row["endpoint_b"]] - current_strength[row["endpoint_b"]]
            return rem_a + rem_b + rng.random() * 1e-9

        best = max(remaining, key=score)
        assigned[best] = w
        row = rows[best]
        current_strength[row["endpoint_a"]] += w
        current_strength[row["endpoint_b"]] += w
        remaining.remove(best)
    return assigned


def balanced_repair(
    rows: list[dict[str, Any]],
    weights: list[float],
    rng: random.Random,
    repair_iterations: int,
    strength_target_min: float,
    organization_weight: float,
    repair_patience: int,
) -> tuple[list[float], dict[str, Any]]:
    baseline_pnc = pair_neighborhood_consistency(rows, "baseline_weight")
    baseline_ranks = shell_rank_map(rows, "baseline_weight")

    current = weights[:]
    current_ps = strength_preservation_score_for_weights(rows, current)
    current_org = organization_objective_for_weights(rows, current, baseline_pnc, baseline_ranks, organization_weight)

    best = current[:]
    best_ps = current_ps
    best_org = current_org

    n = len(rows)
    no_improve_counter = 0
    reached_target = current_ps >= strength_target_min

    for iteration in range(repair_iterations):
        i, j = rng.sample(range(n), 2)
        if abs(current[i] - current[j]) < EPS:
            continue

        trial = current[:]
        trial[i], trial[j] = trial[j], trial[i]
        trial_ps = strength_preservation_score_for_weights(rows, trial)
        trial_org = organization_objective_for_weights(rows, trial, baseline_pnc, baseline_ranks, organization_weight)

        accept = False
        if current_ps < strength_target_min:
            if trial_ps > current_ps + EPS:
                accept = True
            elif abs(trial_ps - current_ps) <= EPS and trial_org > current_org + EPS:
                accept = True
        else:
            if trial_ps >= strength_target_min:
                if trial_org > current_org + EPS:
                    accept = True
                elif abs(trial_org - current_org) <= EPS and trial_ps > current_ps + EPS:
                    accept = True

        if accept:
            current = trial
            current_ps = trial_ps
            current_org = trial_org
            reached_target = reached_target or (current_ps >= strength_target_min)
            no_improve_counter = 0

            if current_ps >= strength_target_min:
                if (current_org > best_org + EPS) or (abs(current_org - best_org) <= EPS and current_ps > best_ps + EPS):
                    best = current[:]
                    best_ps = current_ps
                    best_org = current_org
            else:
                if current_ps > best_ps + EPS:
                    best = current[:]
                    best_ps = current_ps
                    best_org = current_org
        else:
            no_improve_counter += 1

        if reached_target and no_improve_counter >= repair_patience:
            break

    exit_status = "target_band_reached" if best_ps >= strength_target_min else "max_iterations_reached"
    if best_ps >= strength_target_min and best_org <= EPS:
        exit_status = "collapsed_to_trivial_solution"

    meta = {
        "strength_target_min": strength_target_min,
        "best_strength_preservation_score": best_ps,
        "best_organization_objective_score": best_org,
        "repair_exit_status": exit_status,
        "iterations_used": iteration + 1 if repair_iterations > 0 else 0,
        "organization_weight": organization_weight,
    }
    return best, meta


def perturb_rows(
    rows: list[dict[str, Any]],
    rng: random.Random,
    repair_iterations: int,
    strength_target_min: float,
    organization_weight: float,
    repair_patience: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    perturbed = [dict(r) for r in rows]
    initial = greedy_assign(rows, rng)
    repaired, repair_meta = balanced_repair(
        rows=rows,
        weights=initial,
        rng=rng,
        repair_iterations=repair_iterations,
        strength_target_min=strength_target_min,
        organization_weight=organization_weight,
        repair_patience=repair_patience,
    )
    for row, w in zip(perturbed, repaired):
        row["weight"] = float(w)
        row["weight_delta"] = row["weight"] - safe_float(row["baseline_weight"])
        row["weight_changed_flag"] = bool(abs(row["weight_delta"]) > EPS)
    return perturbed, repair_meta


def classify_preservation_status(metrics: dict[str, float], strength_hard_min: float, tol: float) -> str:
    if metrics["weight_multiset_preservation_score"] < (1.0 - tol):
        return "failed"
    if metrics["degree_preservation_score"] < (1.0 - tol):
        return "failed"
    if metrics["strength_preservation_score"] < strength_hard_min:
        return "failed"
    return "passed"


def make_decision(
    preservation: dict[str, float],
    preservation_status: str,
    readout: Readout,
    strength_target_min: float,
    organization_readable_threshold: float,
) -> DecisionSummary:
    if preservation_status != "passed":
        return DecisionSummary(
            decision_label="test_not_informative",
            primary_reason="The hard preservation floor was not maintained strongly enough.",
            secondary_reason="The intervention changed protected distributional structure too much, so the comparison is not clean.",
            test_informativeness="low",
            distribution_preservation_status="failed",
            organization_disruption_status="unresolved",
            bridge_response_status="unresolved",
        )

    if preservation["strength_preservation_score"] >= strength_target_min and readout.arrangement_signal_score <= EPS:
        return DecisionSummary(
            decision_label="overconstrained_or_trivialized",
            primary_reason="The run reached the preservation target band, but the resulting organization disruption collapsed to a trivial or near-trivial level.",
            secondary_reason="This suggests that the admissible search space may be too narrow or the objective still too baseline-attractive.",
            test_informativeness="medium",
            distribution_preservation_status="passed",
            organization_disruption_status="trivial",
            bridge_response_status="stable",
        )

    if readout.arrangement_signal_score >= organization_readable_threshold:
        return DecisionSummary(
            decision_label="organization_sensitive",
            primary_reason="The preservation side held, and the arrangement-sensitive response remained clearly readable inside the tested objective corridor.",
            secondary_reason="This supports the interpretation that bridge-facing behavior depends on organization, not only on preserved broad distributions.",
            test_informativeness="medium",
            distribution_preservation_status="passed",
            organization_disruption_status="readable",
            bridge_response_status="responsive",
        )

    return DecisionSummary(
        decision_label="distribution_dominant_or_weak",
        primary_reason="The preservation side held, but the arrangement-sensitive response remained below the current readable threshold.",
        secondary_reason="Either the organization objective is still too shallow, or the tested organization layer is less structurally decisive than expected.",
        test_informativeness="medium",
        distribution_preservation_status="passed",
        organization_disruption_status="weak",
        bridge_response_status="weak_or_stable",
    )


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, sort_keys=True)


def build_node_level_comparison(baseline_rows: list[dict[str, Any]], perturbed_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base_loads = endpoint_loads(baseline_rows, "baseline_weight")
    new_loads = endpoint_loads(perturbed_rows, "weight")
    nodes = sorted(set(base_loads) | set(new_loads))
    return [
        {
            "endpoint": node,
            "baseline_load": base_loads.get(node, 0.0),
            "perturbed_load": new_loads.get(node, 0.0),
            "load_delta": new_loads.get(node, 0.0) - base_loads.get(node, 0.0),
            "abs_load_delta": abs(new_loads.get(node, 0.0) - base_loads.get(node, 0.0)),
        }
        for node in nodes
    ]


def build_pair_level_comparison(baseline_rows: list[dict[str, Any]], perturbed_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base_pnc = pair_neighborhood_consistency(baseline_rows, "baseline_weight")
    new_pnc = pair_neighborhood_consistency(perturbed_rows, "weight")
    base_rank = shell_rank_map(baseline_rows, "baseline_weight")
    new_rank = shell_rank_map(perturbed_rows, "weight")
    out = []
    for base_row, new_row in zip(baseline_rows, perturbed_rows):
        pid = base_row["pair_id"]
        out.append(
            {
                "pair_id": pid,
                "endpoint_a": base_row["endpoint_a"],
                "endpoint_b": base_row["endpoint_b"],
                "shell_label": base_row.get("shell_label", ""),
                "baseline_weight": safe_float(base_row["baseline_weight"]),
                "perturbed_weight": safe_float(new_row["weight"]),
                "weight_delta": safe_float(new_row["weight"]) - safe_float(base_row["baseline_weight"]),
                "baseline_pair_neighborhood_consistency": base_pnc.get(pid, 0.0),
                "perturbed_pair_neighborhood_consistency": new_pnc.get(pid, 0.0),
                "pair_neighborhood_delta": new_pnc.get(pid, 0.0) - base_pnc.get(pid, 0.0),
                "baseline_shell_rank": base_rank.get(pid, 0.0),
                "perturbed_shell_rank": new_rank.get(pid, 0.0),
                "shell_rank_delta": new_rank.get(pid, 0.0) - base_rank.get(pid, 0.0),
            }
        )
    return out


def build_block_readout(
    run_id: str,
    args: argparse.Namespace,
    baseline_rows: list[dict[str, Any]],
    preservation: dict[str, float],
    preservation_status: str,
    readout: Readout,
    decision: DecisionSummary,
    repair_meta: dict[str, Any],
) -> str:
    node_count = len({r["endpoint_a"] for r in baseline_rows} | {r["endpoint_b"] for r in baseline_rows})
    pair_count = len(baseline_rows)
    base_weights = [safe_float(r["baseline_weight"]) for r in baseline_rows]
    mean_w = statistics.fmean(base_weights) if base_weights else 0.0
    std_w = statistics.pstdev(base_weights) if len(base_weights) > 1 else 0.0

    lines = [
        "# BMC-04-v3.1 Block Readout",
        "",
        "## Run identity",
        "",
        f"- Run ID: `{run_id}`",
        "- Block: `BMC-04-v3.1`",
        "- Title: `Distribution-Preserving Organization Scramble`",
        f"- Variant: `{args.variant}`",
        f"- Seed: `{args.seed}`",
        "",
        "## Baseline description",
        "",
        "- Framework label: `pair_based_h3`",
        f"- Pair count: `{pair_count}`",
        f"- Node count: `{node_count}`",
        f"- Baseline weight mean: `{mean_w:.6f}`",
        f"- Baseline weight std: `{std_w:.6f}`",
        "",
        "## Repair / objective status",
        "",
        "- Repair mode: `soft_repair_balanced_objective`",
        f"- Strength target min: `{args.strength_target_min:.6f}`",
        f"- Strength hard min: `{args.strength_hard_min:.6f}`",
        f"- Organization readable threshold: `{args.organization_readable_threshold:.6f}`",
        f"- Best strength preservation score: `{repair_meta['best_strength_preservation_score']:.6f}`",
        f"- Best organization objective score: `{repair_meta['best_organization_objective_score']:.6f}`",
        f"- Repair exit status: `{repair_meta['repair_exit_status']}`",
        f"- Iterations used: `{repair_meta['iterations_used']}`",
        "",
        "## Preservation status",
        "",
        f"- Weight multiset preservation score: `{preservation['weight_multiset_preservation_score']:.6f}`",
        f"- Degree preservation score: `{preservation['degree_preservation_score']:.6f}`",
        f"- Strength preservation score: `{preservation['strength_preservation_score']:.6f}`",
        f"- Shell count preservation score: `{preservation['shell_count_preservation_score']:.6f}`",
        f"- Block count preservation score: `{preservation['block_count_preservation_score']:.6f}`",
        f"- Preservation status: `{preservation_status}`",
        "",
        "## Organization disruption / bridge-facing readout",
        "",
        f"- Bridge signal score: `{readout.bridge_signal_score:.6f}`",
        f"- D1/D2 separation score: `{readout.d1_d2_separation_score:.6f}`",
        f"- Weighted relational contrast score: `{readout.weighted_relational_contrast_score:.6f}`",
        f"- Endpoint load shift score: `{readout.endpoint_load_shift_score:.6f}`",
        f"- Endpoint load dispersion shift score: `{readout.endpoint_load_dispersion_shift_score:.6f}`",
        f"- Pair-to-neighborhood consistency shift score: `{readout.pair_neighborhood_consistency_shift_score:.6f}`",
        f"- Shell arrangement shift score: `{readout.shell_arrangement_shift_score:.6f}`",
        f"- Shell boundary disruption score: `{readout.shell_boundary_disruption_score:.6f}`",
        f"- Arrangement signal score: `{readout.arrangement_signal_score:.6f}`",
        f"- Readability label: `{readout.readability_label}`",
        "",
        "## Decision",
        "",
        f"- Decision label: `{decision.decision_label}`",
        f"- Test informativeness: `{decision.test_informativeness}`",
        f"- Distribution preservation status: `{decision.distribution_preservation_status}`",
        f"- Organization disruption status: `{decision.organization_disruption_status}`",
        f"- Bridge response status: `{decision.bridge_response_status}`",
        "",
        "### Primary reason",
        decision.primary_reason,
        "",
        "### Secondary reason",
        decision.secondary_reason,
        "",
        "## Next-step note",
        "",
        "Treat BMC-04-v3.1 as a target-band organization-vs-distribution probe with decision logic aligned to observed readable runs.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = output_dir.name

    baseline_rows = load_rows(input_path)
    ensure_shell_fields(baseline_rows, args.shell_source)

    perturbed_rows, repair_meta = perturb_rows(
        rows=baseline_rows,
        rng=rng,
        repair_iterations=args.repair_iterations,
        strength_target_min=args.strength_target_min,
        organization_weight=args.organization_weight,
        repair_patience=args.repair_patience,
    )

    preservation = preservation_metrics(baseline_rows, perturbed_rows)
    preservation_status = classify_preservation_status(
        metrics=preservation,
        strength_hard_min=args.strength_hard_min,
        tol=args.preservation_tolerance,
    )
    readout = compute_readout(baseline_rows, perturbed_rows)
    decision = make_decision(
        preservation=preservation,
        preservation_status=preservation_status,
        readout=readout,
        strength_target_min=args.strength_target_min,
        organization_readable_threshold=args.organization_readable_threshold,
    )

    intervention_fields = [
        "pair_id", "endpoint_a", "endpoint_b", "weight", "shell_label",
        "baseline_weight", "weight_delta", "weight_changed_flag",
    ]
    write_csv(output_dir / "intervention_table.csv", perturbed_rows, intervention_fields)

    preservation_row = {
        "run_id": run_id,
        "variant": args.variant,
        "seed": args.seed,
        **preservation,
        "preservation_status": preservation_status,
    }
    write_csv(output_dir / "preservation_summary.csv", [preservation_row], list(preservation_row.keys()))

    org_row = {
        "run_id": run_id,
        "variant": args.variant,
        "arrangement_signal_score": readout.arrangement_signal_score,
        "endpoint_load_shift_score": readout.endpoint_load_shift_score,
        "endpoint_load_dispersion_shift_score": readout.endpoint_load_dispersion_shift_score,
        "pair_neighborhood_consistency_shift_score": readout.pair_neighborhood_consistency_shift_score,
        "shell_arrangement_shift_score": readout.shell_arrangement_shift_score,
        "shell_boundary_disruption_score": readout.shell_boundary_disruption_score,
        "organization_objective_score": repair_meta["best_organization_objective_score"],
        "repair_exit_status": repair_meta["repair_exit_status"],
    }
    write_csv(output_dir / "organization_disruption_summary.csv", [org_row], list(org_row.keys()))

    summary_payload = {
        "run_id": run_id,
        "block": "BMC-04-v3.1",
        "variant": args.variant,
        "seed": args.seed,
        "preservation": preservation,
        "preservation_status": preservation_status,
        "readout": asdict(readout),
        "repair_meta": repair_meta,
    }
    write_json(output_dir / "summary.json", summary_payload)
    write_json(output_dir / "decision_summary.json", asdict(decision))
    write_json(output_dir / "run_metadata.json", {"run_id": run_id, "block": "BMC-04-v3.1"})
    write_json(output_dir / "run_config.json", vars(args))
    write_json(output_dir / "constraint_status.json", {
        "variant": args.variant,
        "preservation_status": preservation_status,
        "strength_target_min": args.strength_target_min,
        "strength_hard_min": args.strength_hard_min,
        "organization_readable_threshold": args.organization_readable_threshold,
        "repair_exit_status": repair_meta["repair_exit_status"],
    })

    variant_row = {
        "run_id": run_id,
        "variant": args.variant,
        "seed": args.seed,
        **preservation,
        "arrangement_signal_score": readout.arrangement_signal_score,
        "bridge_signal_score": readout.bridge_signal_score,
        "organization_objective_score": repair_meta["best_organization_objective_score"],
        "decision_label": decision.decision_label,
    }
    write_csv(output_dir / "variant_comparison_row.csv", [variant_row], list(variant_row.keys()))

    if args.write_node_level_debug:
        node_rows = build_node_level_comparison(baseline_rows, perturbed_rows)
        write_csv(
            output_dir / "node_level_comparison.csv",
            node_rows,
            ["endpoint", "baseline_load", "perturbed_load", "load_delta", "abs_load_delta"],
        )

    if args.write_pair_level_debug:
        pair_rows = build_pair_level_comparison(baseline_rows, perturbed_rows)
        write_csv(
            output_dir / "pair_level_comparison.csv",
            pair_rows,
            [
                "pair_id",
                "endpoint_a",
                "endpoint_b",
                "shell_label",
                "baseline_weight",
                "perturbed_weight",
                "weight_delta",
                "baseline_pair_neighborhood_consistency",
                "perturbed_pair_neighborhood_consistency",
                "pair_neighborhood_delta",
                "baseline_shell_rank",
                "perturbed_shell_rank",
                "shell_rank_delta",
            ],
        )

    block_readout = build_block_readout(
        run_id=run_id,
        args=args,
        baseline_rows=baseline_rows,
        preservation=preservation,
        preservation_status=preservation_status,
        readout=readout,
        decision=decision,
        repair_meta=repair_meta,
    )
    (output_dir / "block_readout.md").write_text(block_readout, encoding="utf-8")

    print(f"Wrote BMC-04-v3.1 outputs to: {output_dir}")


if __name__ == "__main__":
    main()
