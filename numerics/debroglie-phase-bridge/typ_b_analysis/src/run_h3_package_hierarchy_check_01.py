#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from reporting import write_csv, write_json


def now_utc_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Config root must be a mapping: {path}")
    return data


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_md(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run H3 package hierarchy check 01.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    return parser.parse_args()


def load_matrix_from_npz(path: Path, preferred_fields: list[str]) -> tuple[str, np.ndarray]:
    if not path.exists():
        raise FileNotFoundError(f"NPZ file not found: {path}")

    with np.load(path, allow_pickle=True) as data:
        available = list(data.files)
        for field in preferred_fields:
            if field in data:
                arr = np.asarray(data[field], dtype=float)
                if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
                    raise ValueError(f"Field {field} in {path} is not a square matrix.")
                return field, arr

    raise ValueError(
        f"No preferred matrix found in {path}. Preferred={preferred_fields}, available={available}"
    )


def upper_triangle_values(M: np.ndarray) -> np.ndarray:
    idx = np.triu_indices_from(M, k=1)
    return M[idx]


def signed_power(M: np.ndarray, alpha: float) -> np.ndarray:
    return np.sign(M) * (np.abs(M) ** alpha)


def safe_corr(x: np.ndarray, y: np.ndarray) -> float:
    if x.size == 0 or y.size == 0:
        return 0.0
    if float(np.std(x)) <= 1.0e-15 or float(np.std(y)) <= 1.0e-15:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def mean_abs_diff(x: np.ndarray, y: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    return float(np.mean(np.abs(x - y)))


def baseline_clarity_score(x: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    return float(np.std(x) / max(np.mean(np.abs(x)), 1.0e-12))


def contrast_gain(base_vals: np.ndarray, aux_vals: np.ndarray) -> float:
    base_std = float(np.std(base_vals))
    aux_std = float(np.std(aux_vals))
    if base_std <= 1.0e-15:
        return 0.0
    return float((aux_std - base_std) / base_std)


def structural_preservation(base_vals: np.ndarray, aux_vals: np.ndarray) -> float:
    corr = safe_corr(base_vals, aux_vals)
    mad = mean_abs_diff(base_vals, aux_vals)
    penalty = min(1.0, mad)
    score = 0.7 * max(corr, 0.0) + 0.3 * max(0.0, 1.0 - penalty)
    return float(max(0.0, min(1.0, score)))


def interpretive_value_reference(sp: float, cg: float) -> str:
    if sp >= 0.85 and cg >= 0.05:
        return "secondary_helpful"
    if sp >= 0.75 and cg >= 0.00:
        return "secondary_mildly_helpful"
    return "secondary_not_helpful"


def interpretive_value_support(sp: float, cg: float, base_clarity: float, aux_clarity: float) -> str:
    clarity_delta = aux_clarity - base_clarity
    if sp >= 0.80 and cg >= 0.00 and clarity_delta <= 0.10:
        return "secondary_tolerable_but_not_needed"
    if sp >= 0.70 and clarity_delta <= 0.20:
        return "secondary_restricted"
    return "secondary_not_recommended"


def edge_risk_gain_reading(sp: float, cg: float) -> str:
    if cg > 0.03 and sp < 0.75:
        return "risk_gt_gain"
    if cg <= 0.03:
        return "little_gain"
    return "unclear"


def evaluate_package(
    role: str,
    matrix: np.ndarray,
    alpha_baseline: float,
    alpha_aux: float,
    open_aux: bool,
    probe_edge_aux: bool,
) -> dict[str, Any]:
    baseline = signed_power(matrix, alpha_baseline)
    base_vals = upper_triangle_values(baseline)
    base_clarity = baseline_clarity_score(base_vals)

    row: dict[str, Any] = {
        "package_role": role,
        "baseline_mode": f"G_eq_B_pow_{alpha_baseline}".replace(".", "p"),
        "auxiliary_mode": f"G_eq_B_pow_{alpha_aux}".replace(".", "p"),
        "baseline_readout_status": "computed",
        "auxiliary_status": None,
        "structural_preservation": None,
        "contrast_gain": None,
        "interpretive_value": None,
        "hierarchy_decision": None,
        "opening_status": None,
        "final_package_judgment": None,
        "baseline_clarity_score": round(base_clarity, 6),
        "auxiliary_clarity_score": None,
        "risk_gain_reading": None,
    }

    if role == "edge" and not open_aux and not probe_edge_aux:
        row["auxiliary_status"] = "blocked_by_rule"
        row["opening_status"] = "not_opened_by_default"
        row["hierarchy_decision"] = "baseline_only"
        row["final_package_judgment"] = "not_opened_by_default"
        row["interpretive_value"] = "not_evaluated"
        return row

    auxiliary = signed_power(matrix, alpha_aux)
    aux_vals = upper_triangle_values(auxiliary)
    aux_clarity = baseline_clarity_score(aux_vals)

    sp = structural_preservation(base_vals, aux_vals)
    cg = contrast_gain(base_vals, aux_vals)

    row["auxiliary_status"] = "computed"
    row["structural_preservation"] = round(sp, 6)
    row["contrast_gain"] = round(cg, 6)
    row["auxiliary_clarity_score"] = round(aux_clarity, 6)

    if role == "reference":
        iv = interpretive_value_reference(sp, cg)
        row["interpretive_value"] = iv
        row["opening_status"] = "opened"
        row["hierarchy_decision"] = "baseline_first_auxiliary_secondary"
        row["final_package_judgment"] = iv

    elif role == "support":
        iv = interpretive_value_support(sp, cg, base_clarity, aux_clarity)
        row["interpretive_value"] = iv
        row["opening_status"] = "opened_restricted"
        row["hierarchy_decision"] = "baseline_clearly_primary"
        row["final_package_judgment"] = iv

    elif role == "edge":
        rg = edge_risk_gain_reading(sp, cg)
        row["risk_gain_reading"] = rg
        row["opening_status"] = "probe_only" if probe_edge_aux else "opened"
        row["hierarchy_decision"] = "baseline_only_preferred"
        row["interpretive_value"] = "risk_gt_gain" if rg == "risk_gt_gain" else "not_helpful"
        row["final_package_judgment"] = "not_opened_by_default" if rg in {"risk_gt_gain", "little_gain"} else "unclear"

    else:
        raise ValueError(f"Unknown package role: {role}")

    return row


def build_block_readout(
    run_id: str,
    rows: list[dict[str, Any]],
    global_status: str,
    reference_vs_support_delta: str,
    edge_non_opening_confirmed: bool,
) -> str:
    lines = [
        f"# {run_id}",
        "",
        "## Ziel",
        "Numerischer Erdungs-Run der H3-Paketlogik: Reference hilfreich, Support begrenzt, Edge nicht geöffnet.",
        "",
        "## Paketurteile",
    ]
    for row in rows:
        lines.append(
            f"- {row['package_role']}: judgment=`{row['final_package_judgment']}`, "
            f"opening_status=`{row['opening_status']}`, "
            f"structural_preservation=`{row['structural_preservation']}`, "
            f"contrast_gain=`{row['contrast_gain']}`"
        )

    lines += [
        "",
        "## Globalurteil",
        f"- global_h3_hierarchy_status: `{global_status}`",
        f"- reference_vs_support_delta: `{reference_vs_support_delta}`",
        f"- edge_non_opening_confirmed: `{edge_non_opening_confirmed}`",
        "",
        "## Kurzlesart",
        "- Reference: auxiliary darf kleinen echten Zusatznutzen liefern, bleibt aber sekundär.",
        "- Support: auxiliary bleibt verträglich, ist aber klar enger begrenzt und nicht nötig.",
        "- Edge: auxiliary wird nicht standardmäßig geöffnet; baseline-first bleibt maßgeblich.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    cfg_path = Path(args.config).resolve()
    cfg = load_yaml(cfg_path)

    run_id = str(cfg["run_id"])
    output_dir = Path(cfg["output_dir"]).resolve()
    ensure_dir(output_dir)

    baseline_alpha = float(cfg["response_modes"]["baseline"]["alpha"])
    aux_alpha = float(cfg["response_modes"]["auxiliary"]["alpha"])
    preferred_fields = list(cfg["inputs"]["preferred_matrix_fields"])

    edge_default_opening = bool(cfg["policy"]["edge_default_opening"])
    edge_probe_if_blocked = bool(cfg["policy"].get("edge_probe_if_blocked", False))

    package_inputs = cfg["package_inputs"]
    rows: list[dict[str, Any]] = []

    for role in ["reference", "support", "edge"]:
        role_cfg = package_inputs[role]
        npz_path = Path(role_cfg["npz"]).resolve()
        field_name, matrix = load_matrix_from_npz(npz_path, preferred_fields)

        open_aux = role != "edge" or edge_default_opening
        row = evaluate_package(
            role=role,
            matrix=matrix,
            alpha_baseline=baseline_alpha,
            alpha_aux=aux_alpha,
            open_aux=open_aux,
            probe_edge_aux=edge_probe_if_blocked,
        )
        row["source_npz"] = str(npz_path)
        row["source_matrix_field"] = field_name
        rows.append(row)

    ref_j = next(r["final_package_judgment"] for r in rows if r["package_role"] == "reference")
    sup_j = next(r["final_package_judgment"] for r in rows if r["package_role"] == "support")
    edge_j = next(r["final_package_judgment"] for r in rows if r["package_role"] == "edge")

    if ref_j in {"secondary_helpful", "secondary_mildly_helpful"} and sup_j in {
        "secondary_tolerable_but_not_needed",
        "secondary_restricted",
    } and edge_j == "not_opened_by_default":
        global_status = "graded_package_role_hierarchy_supported"
    else:
        global_status = "graded_package_role_hierarchy_not_cleanly_supported"

    reference_vs_support_delta = f"{ref_j} -> {sup_j}"
    edge_non_opening_confirmed = edge_j == "not_opened_by_default"

    summary = {
        "run_id": run_id,
        "created_at_utc": now_utc_iso(),
        "global_h3_hierarchy_status": global_status,
        "reference_vs_support_delta": reference_vs_support_delta,
        "edge_non_opening_confirmed": edge_non_opening_confirmed,
        "expected_logic": cfg.get("expected_logic", {}),
        "summary_text": (
            "Reference helpful, support limited, edge not opened."
            if global_status == "graded_package_role_hierarchy_supported"
            else "H3 hierarchy only partially supported or not cleanly reproduced."
        ),
        "package_rows": rows,
    }

    write_json(output_dir / "summary.json", summary)
    write_csv(output_dir / "package_table.csv", rows)
    write_md(
        output_dir / "block_readout.md",
        build_block_readout(
            run_id=run_id,
            rows=rows,
            global_status=global_status,
            reference_vs_support_delta=reference_vs_support_delta,
            edge_non_opening_confirmed=edge_non_opening_confirmed,
        ),
    )

    print(json.dumps({
        "run_id": run_id,
        "global_h3_hierarchy_status": global_status,
        "reference_vs_support_delta": reference_vs_support_delta,
        "edge_non_opening_confirmed": edge_non_opening_confirmed,
        "output_dir": str(output_dir),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
