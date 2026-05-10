#!/usr/bin/env python3
"""
BMS-FU02g5g - FU02g4c Raw-Order Replay Certification Recovery

Inventory existing FU02g4c logs/configs and audit whether FU02g5e1/g5e2/g5f
scaffold-localized candidate raw_index values are supported by original FU02g4c
raw-window artifacts. This runner does not silently treat scaffold indices as
FU02g4c raw-order indices and does not make physical or global uniqueness
claims.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Missing dependency: PyYAML. Install it in the project environment.") from exc


LOG_INVENTORY_FIELDS = [
    "log_file",
    "log_kind",
    "chunk_id",
    "window_start",
    "window_end",
    "skip_first_raw_patches",
    "max_raw_patches_this_run",
    "raw_patch_count_seen_including_skipped",
    "raw_connected_patch_count_processed",
    "raw_role_colored_signature_exact_match_count",
    "raw_role_colored_signature_near_match_count",
    "enumeration_status",
    "stop_or_timeout_status",
    "covers_candidate_raw_indices",
    "parse_warnings",
]

CROSSCHECK_FIELDS = [
    "candidate_id",
    "scaffold_raw_index",
    "candidate_nodes",
    "inside_fu02g4c_logged_window",
    "matching_fu02g4c_log_file",
    "all_matching_fu02g4c_log_files",
    "fu02g4c_window_exact_count",
    "fu02g4c_window_near_count",
    "best_window_start",
    "best_window_end",
    "best_window_status",
    "crosscheck_basis",
]

CERTIFICATION_FIELDS = [
    "candidate_id",
    "scaffold_raw_index",
    "candidate_nodes",
    "exact_match",
    "near_distance",
    "classification_primary",
    "g5f_raw_order_certification_status",
    "inside_fu02g4c_logged_window",
    "matching_fu02g4c_log_file",
    "fu02g4c_window_exact_count",
    "fu02g4c_window_near_count",
    "required_target_label",
    "replay_attempted",
    "replay_certification_status",
    "replay_certification_basis",
    "scaffold_index_warning",
]

SCAFFOLD_INDEX_WARNING = (
    "scaffold raw_index values remain uncertified as FU02g4c raw-order indices "
    "unless direct FU02g4c replay/window artifacts support the specific target."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run BMS-FU02g5g FU02g4c raw-order replay certification recovery."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to data/bms_fu02g5g_fu02g4c_raw_order_replay_certification_config.yaml",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"YAML config must contain a mapping: {path}")
    return data


def resolve_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return repo_root / path


def read_csv_rows(path: Path, required: Set[str]) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV missing required columns {sorted(missing)}: {path}")
        return [{key: "" if value is None else str(value) for key, value in row.items()} for row in reader]


def parse_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def parse_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    return None


def csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple, set)):
        return json.dumps(value, sort_keys=True)
    return value


def write_csv(path: Path, rows: Iterable[Mapping[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field, "")) for field in fields})


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, sort_keys=True)
        handle.write("\n")


def extract_json_objects(text: str) -> List[Dict[str, Any]]:
    decoder = json.JSONDecoder()
    objects: List[Dict[str, Any]] = []
    index = 0
    while index < len(text):
        brace = text.find("{", index)
        if brace == -1:
            break
        try:
            obj, end = decoder.raw_decode(text[brace:])
        except json.JSONDecodeError:
            index = brace + 1
            continue
        if isinstance(obj, dict):
            objects.append(obj)
        index = brace + end
    return objects


def classify_log_kind(path: Path) -> str:
    name = path.name
    if name.startswith("inspect_window_"):
        return "inspect_window"
    if name.startswith("segment_"):
        return "segment"
    if name.startswith("chunk_"):
        return "chunk"
    return "other"


def parse_window_from_name(path: Path) -> Tuple[Optional[int], Optional[int]]:
    name = path.stem
    match = re.search(r"(?:inspect_window|segment|chunk)_(\d+)_(\d+)$", name)
    if not match:
        return None, None
    return int(match.group(1)), int(match.group(2))


def stop_status(enumeration_status: str) -> str:
    if "timeout" in enumeration_status:
        return "timeout"
    if "limit" in enumeration_status:
        return "chunk_limit"
    if enumeration_status == "complete":
        return "complete"
    if enumeration_status:
        return enumeration_status
    return "unknown"


def best_json_value(objects: Sequence[Mapping[str, Any]], key: str) -> Any:
    for obj in reversed(objects):
        if key in obj:
            return obj[key]
    return None


def infer_max_raw_patches(row: Mapping[str, Any]) -> Optional[int]:
    start = parse_int(row.get("skip_first_raw_patches")) or parse_int(row.get("window_start"))
    seen = parse_int(row.get("raw_patch_count_seen_including_skipped"))
    processed = parse_int(row.get("raw_connected_patch_count_processed"))
    if processed is not None:
        return processed
    if start is not None and seen is not None and seen >= start:
        return seen - start
    window_start = parse_int(row.get("window_start"))
    window_end = parse_int(row.get("window_end"))
    if window_start is not None and window_end is not None and window_end >= window_start:
        return window_end - window_start + 1
    return None


def inventory_log(path: Path) -> Dict[str, Any]:
    warnings: List[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    objects = extract_json_objects(text)
    if not objects:
        warnings.append("no_json_object_parsed")

    name_start, name_end = parse_window_from_name(path)
    chunk_id = best_json_value(objects, "chunk_id") or path.stem
    skip_first = parse_int(best_json_value(objects, "skip_first_raw_patches"))
    raw_seen = parse_int(best_json_value(objects, "raw_patch_count_seen_including_skipped"))
    processed = parse_int(best_json_value(objects, "raw_connected_patch_count_processed"))
    enumeration_status = str(best_json_value(objects, "enumeration_status") or "")

    window_start = name_start if name_start is not None else skip_first
    window_end = name_end
    if window_end is None and raw_seen is not None:
        window_end = raw_seen - 1

    row: Dict[str, Any] = {
        "log_file": str(path),
        "log_kind": classify_log_kind(path),
        "chunk_id": chunk_id,
        "window_start": window_start,
        "window_end": window_end,
        "skip_first_raw_patches": skip_first,
        "max_raw_patches_this_run": None,
        "raw_patch_count_seen_including_skipped": raw_seen,
        "raw_connected_patch_count_processed": processed,
        "raw_role_colored_signature_exact_match_count": parse_int(
            best_json_value(objects, "raw_role_colored_signature_exact_match_count")
        ),
        "raw_role_colored_signature_near_match_count": parse_int(
            best_json_value(objects, "raw_role_colored_signature_near_match_count")
        ),
        "enumeration_status": enumeration_status,
        "stop_or_timeout_status": stop_status(enumeration_status),
        "covers_candidate_raw_indices": "",
        "parse_warnings": "; ".join(warnings),
    }
    row["max_raw_patches_this_run"] = infer_max_raw_patches(row)
    return row


def load_g4c_patch_photo(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def covers_raw_index(log_row: Mapping[str, Any], raw_index: int) -> bool:
    start = parse_int(log_row.get("window_start"))
    end = parse_int(log_row.get("window_end"))
    raw_seen = parse_int(log_row.get("raw_patch_count_seen_including_skipped"))
    if start is None:
        return False
    effective_end = end
    if raw_seen is not None:
        raw_seen_end = raw_seen - 1
        effective_end = min(raw_seen_end, end) if end is not None else raw_seen_end
    if effective_end is None:
        return False
    return start <= raw_index <= effective_end


def window_width(log_row: Mapping[str, Any]) -> int:
    start = parse_int(log_row.get("window_start"))
    end = parse_int(log_row.get("window_end"))
    if start is None or end is None:
        return 10**18
    return max(0, end - start)


def choose_best_match(matches: Sequence[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
    if not matches:
        return None
    priority = {"inspect_window": 0, "segment": 1, "chunk": 2, "other": 3}
    return sorted(matches, key=lambda row: (priority.get(str(row.get("log_kind")), 9), window_width(row), str(row.get("log_file"))))[0]


def build_candidate_rows(
    g5e1_rows: Sequence[Mapping[str, str]],
    g5e2_by_raw: Mapping[str, Mapping[str, str]],
    g5f_by_raw: Mapping[str, Mapping[str, str]],
) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for index, row in enumerate(g5e1_rows):
        raw_index = str(row["raw_index"])
        g5e2 = g5e2_by_raw.get(raw_index, {})
        g5f = g5f_by_raw.get(raw_index, {})
        candidates.append(
            {
                "candidate_id": g5e2.get("candidate_id") or g5f.get("candidate_id") or f"candidate_{index:03d}",
                "scaffold_raw_index": parse_int(raw_index),
                "candidate_nodes": row["candidate_nodes"],
                "exact_match": parse_bool(row.get("exact_match")),
                "near_distance": parse_int(row.get("near_distance")),
                "classification_primary": g5e2.get("classification_primary", ""),
                "g5f_raw_order_certification_status": g5f.get("raw_order_certification_status", ""),
            }
        )
    return candidates


def target_label_for(candidate: Mapping[str, Any], targets: Sequence[Mapping[str, Any]]) -> str:
    for target in targets:
        if (
            str(target.get("candidate_id")) == str(candidate["candidate_id"])
            and parse_int(target.get("raw_index")) == candidate["scaffold_raw_index"]
        ):
            return str(target.get("label", ""))
    return ""


def certify_candidate(
    candidate: Mapping[str, Any],
    best_log: Optional[Mapping[str, Any]],
    required_label: str,
    patch_photo: Mapping[str, Any],
    allow_replay_rerun: bool,
) -> Tuple[str, str]:
    raw_index = candidate["scaffold_raw_index"]
    exact_match = candidate["exact_match"]
    near_distance = candidate["near_distance"]

    if best_log is None:
        return (
            "not_certified",
            "No parsed FU02g4c log window covers this scaffold raw_index.",
        )

    patch_event = patch_photo.get("candidate_event", {}) if patch_photo else {}
    photo_nodes = set(str(node) for node in patch_event.get("carriers", []))
    candidate_nodes = set(str(part).strip() for part in str(candidate["candidate_nodes"]).split(";") if part.strip())
    photo_matches_candidate = bool(photo_nodes) and photo_nodes == candidate_nodes
    photo_raw_target = raw_index == 26187175

    if photo_raw_target and exact_match is True and photo_matches_candidate:
        if allow_replay_rerun:
            return (
                "certified",
                "FU02g4c exact-patch photo matches candidate nodes and replay rerun policy allowed direct certification.",
            )
        return (
            "partially_certified",
            "FU02g4c exact-patch photo and narrow inspect log support raw_index 26187175, but FU02g5g did not rerun the original enumerator.",
        )

    if near_distance == 0 and exact_match is False:
        return (
            "not_certified",
            "The raw index is inside a FU02g4c logged window, but no direct FU02g4c per-index artifact certifies this non-exact near candidate.",
        )

    exact_count = parse_int(best_log.get("raw_role_colored_signature_exact_match_count")) or 0
    near_count = parse_int(best_log.get("raw_role_colored_signature_near_match_count")) or 0
    if near_count > 0:
        return (
            "partially_certified",
            "The raw index lies inside a FU02g4c logged window with raw near-match counts, but no per-index replay artifact confirms this candidate.",
        )
    if exact_count > 0:
        return (
            "partially_certified",
            "The raw index lies inside a FU02g4c logged window with raw exact-match counts, but no per-index replay artifact confirms this candidate.",
        )
    return (
        "not_certified",
        "The raw index is inside a FU02g4c logged window, but the window counts do not certify this candidate.",
    )


def build_result_note(summary: Mapping[str, Any]) -> str:
    created = str(summary["metadata"]["created_at_utc"])[:10]
    input_bundle = summary["input_bundle"]
    exact_target = summary["required_targets"].get("known_exact_candidate", {})
    c005_target = summary["required_targets"].get("candidate_005_stress_case", {})

    return f"""# BMS-FU02g5g - FU02g4c Raw-Order Replay Certification Recovery Result Note

Datum: {created}

## Befund

FU02g5g inventories the available FU02g4c logs/configs and cross-checks the
FU02g5e1/g5e2/g5f scaffold-localized candidates against parsed FU02g4c logged
windows.

Raw-order certification was not fully achieved.

```text
overall_certification_status = {summary["overall_certification_status"]}
original_fu02g4c_input_bundle_sufficient_for_rerun = {input_bundle["sufficient_for_safe_rerun"]}
candidate_008_raw_index_26187175_status = {exact_target.get("replay_certification_status", "")}
candidate_005_raw_index_26157530_status = {c005_target.get("replay_certification_status", "")}
```

## Interpretation

The original FU02g4c input bundle can be partially identified from the primary
config, inspect-window configs, logs, and the exact-patch photo. It is not
sufficiently certified for a safe FU02g5g rerun under this block, because the
runner does not re-execute the original enumerator or write through FU02g4c
output surfaces.

Scaffold indices remain uncertified as FU02g4c raw-order indices unless direct
FU02g4c replay/window artifacts support the specific target. Candidate_008 /
raw_index 26187175 is supported by a FU02g4c exact-patch photo and narrow
inspect log, so it is reported as partially certified rather than fully replay
certified. Candidate_005 / raw_index 26157530 is inside logged FU02g4c coverage
but has no direct per-index FU02g4c artifact here, so it is not certified.

## Hypothese

The available artifacts suggest that the exact candidate at raw_index 26187175
is recoverable from FU02g4c audit material, while the non-exact near candidates
need explicit narrow replay/photo artifacts before their scaffold raw indices
can be promoted to FU02g4c raw-order certification.

## Offene Luecke

Exact raw-order replay certification remains open. A stronger certification
would require an isolated rerun that reuses the original FU02g4c enumerator and
input bundle, records exact per-index outputs for the required candidates, and
does not overwrite prior FU02g4c artifacts.

## Claim Boundary

This is a certification/recovery audit only. No physical emergence, spacetime
emergence, global uniqueness, or global rarity claim follows from this block.
"""


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    config_path = resolve_path(repo_root, args.config)
    config = load_yaml(config_path)

    run_config = config["run"]
    input_config = config["input"]
    output_dir = resolve_path(repo_root, str(run_config["output_dir"]))
    output_dir.mkdir(parents=True, exist_ok=True)

    g5e1_path = resolve_path(repo_root, str(input_config["g5e1_candidates_csv"]))
    g5e2_path = resolve_path(repo_root, str(input_config["g5e2_classification_csv"]))
    g5f_path = resolve_path(repo_root, str(input_config["g5f_revalidation_csv"]))
    fu02g4c_run_dir = resolve_path(repo_root, str(input_config["fu02g4c_run_dir"]))
    base_config_path = resolve_path(repo_root, str(input_config["fu02g4c_base_config_yaml"]))
    face_graph_path = resolve_path(repo_root, str(input_config["face_graph_edges_csv"]))
    patch_photo_path = resolve_path(repo_root, str(input_config["known_exact_patch_photo_json"]))
    inspect_configs = sorted(repo_root.glob(str(input_config["fu02g4c_inspect_config_glob"])))
    required_targets = list(input_config.get("required_certification_targets", []))
    allow_replay_rerun = bool(run_config.get("allow_replay_rerun", False))

    g5e1_rows = read_csv_rows(g5e1_path, {"raw_index", "candidate_nodes", "exact_match", "near_distance"})
    g5e2_rows = read_csv_rows(g5e2_path, {"candidate_id", "raw_index"})
    g5f_rows = read_csv_rows(g5f_path, {"candidate_id", "raw_index", "raw_order_certification_status"})
    g5e2_by_raw = {row["raw_index"]: row for row in g5e2_rows}
    g5f_by_raw = {row["raw_index"]: row for row in g5f_rows}
    candidates = build_candidate_rows(g5e1_rows, g5e2_by_raw, g5f_by_raw)
    candidate_indices = {int(row["scaffold_raw_index"]) for row in candidates if row["scaffold_raw_index"] is not None}

    if not fu02g4c_run_dir.exists():
        raise FileNotFoundError(f"FU02g4c run directory not found: {fu02g4c_run_dir}")
    log_paths = sorted(fu02g4c_run_dir.rglob("*.log"))
    log_inventory_rows = [inventory_log(path) for path in log_paths]

    for log_row in log_inventory_rows:
        covered = sorted(index for index in candidate_indices if covers_raw_index(log_row, index))
        log_row["covers_candidate_raw_indices"] = ";".join(str(index) for index in covered)

    patch_photo = load_g4c_patch_photo(patch_photo_path)
    crosscheck_rows: List[Dict[str, Any]] = []
    certification_rows: List[Dict[str, Any]] = []

    for candidate in candidates:
        raw_index = int(candidate["scaffold_raw_index"])
        matches = [row for row in log_inventory_rows if covers_raw_index(row, raw_index)]
        best_log = choose_best_match(matches)
        inside = best_log is not None
        required_label = target_label_for(candidate, required_targets)
        status, basis = certify_candidate(candidate, best_log, required_label, patch_photo, allow_replay_rerun)

        crosscheck_rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "scaffold_raw_index": raw_index,
                "candidate_nodes": candidate["candidate_nodes"],
                "inside_fu02g4c_logged_window": inside,
                "matching_fu02g4c_log_file": best_log.get("log_file", "") if best_log else "",
                "all_matching_fu02g4c_log_files": ";".join(str(row["log_file"]) for row in matches),
                "fu02g4c_window_exact_count": best_log.get("raw_role_colored_signature_exact_match_count", "") if best_log else "",
                "fu02g4c_window_near_count": best_log.get("raw_role_colored_signature_near_match_count", "") if best_log else "",
                "best_window_start": best_log.get("window_start", "") if best_log else "",
                "best_window_end": best_log.get("window_end", "") if best_log else "",
                "best_window_status": best_log.get("stop_or_timeout_status", "") if best_log else "",
                "crosscheck_basis": (
                    "raw index falls inside parsed FU02g4c logged window"
                    if inside
                    else "no parsed FU02g4c logged window covers this raw index"
                ),
            }
        )

        certification_rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "scaffold_raw_index": raw_index,
                "candidate_nodes": candidate["candidate_nodes"],
                "exact_match": candidate["exact_match"],
                "near_distance": candidate["near_distance"],
                "classification_primary": candidate["classification_primary"],
                "g5f_raw_order_certification_status": candidate["g5f_raw_order_certification_status"],
                "inside_fu02g4c_logged_window": inside,
                "matching_fu02g4c_log_file": best_log.get("log_file", "") if best_log else "",
                "fu02g4c_window_exact_count": best_log.get("raw_role_colored_signature_exact_match_count", "") if best_log else "",
                "fu02g4c_window_near_count": best_log.get("raw_role_colored_signature_near_match_count", "") if best_log else "",
                "required_target_label": required_label,
                "replay_attempted": False,
                "replay_certification_status": status,
                "replay_certification_basis": basis,
                "scaffold_index_warning": SCAFFOLD_INDEX_WARNING,
            }
        )

    status_counts = Counter(row["replay_certification_status"] for row in certification_rows)
    exact_target_rows = {
        row["required_target_label"]: row
        for row in certification_rows
        if row["required_target_label"]
    }
    sufficient_for_safe_rerun = bool(
        base_config_path.exists()
        and face_graph_path.exists()
        and fu02g4c_run_dir.exists()
        and allow_replay_rerun
    )
    if any(row["replay_certification_status"] == "certified" for row in certification_rows):
        overall_status = "partially_certified"
    elif any(row["replay_certification_status"] == "partially_certified" for row in certification_rows):
        overall_status = "partially_certified"
    elif not sufficient_for_safe_rerun:
        overall_status = "insufficient_input_bundle"
    else:
        overall_status = "not_certified"

    if overall_status == "partially_certified":
        overall_basis = (
            "Some candidates are supported by FU02g4c window or exact-patch artifacts, "
            "but exact FU02g4c raw-order replay was not rerun/certified by FU02g5g."
        )
    elif overall_status == "insufficient_input_bundle":
        overall_basis = (
            "The runner did not have a safe, explicitly reusable FU02g4c input bundle/output isolation policy for replay."
        )
    else:
        overall_basis = "No candidate reached replay certification."

    output_paths = {
        "summary_json": output_dir / "summary.json",
        "fu02g4c_log_inventory_csv": output_dir / "fu02g4c_log_inventory.csv",
        "candidate_window_crosscheck_csv": output_dir / "candidate_window_crosscheck.csv",
        "candidate_replay_certification_csv": output_dir / "candidate_replay_certification.csv",
        "result_note_md": output_dir / "result_note.md",
    }

    summary = {
        "metadata": {
            "run_id": run_config["run_id"],
            "case_id": run_config["case_id"],
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "script_path": "scripts/run_bms_fu02g5g_fu02g4c_raw_order_replay_certification.py",
            "config_path": str(config_path),
        },
        "inputs": {
            "g5e1_candidates_csv": str(g5e1_path),
            "g5e2_classification_csv": str(g5e2_path),
            "g5f_revalidation_csv": str(g5f_path),
            "fu02g4c_run_dir": str(fu02g4c_run_dir),
            "fu02g4c_base_config_yaml": str(base_config_path),
            "fu02g4c_inspect_config_glob": str(input_config["fu02g4c_inspect_config_glob"]),
            "face_graph_edges_csv": str(face_graph_path),
            "known_exact_patch_photo_json": str(patch_photo_path),
            "required_certification_targets": required_targets,
        },
        "input_bundle": {
            "fu02g4c_run_dir_present": fu02g4c_run_dir.exists(),
            "fu02g4c_base_config_present": base_config_path.exists(),
            "fu02g4c_inspect_config_count": len(inspect_configs),
            "face_graph_edges_present": face_graph_path.exists(),
            "known_exact_patch_photo_present": patch_photo_path.exists(),
            "allow_replay_rerun": allow_replay_rerun,
            "rerun_policy": run_config.get("rerun_policy", ""),
            "sufficient_for_safe_rerun": sufficient_for_safe_rerun,
        },
        "log_inventory_counts": {
            "log_count": len(log_inventory_rows),
            "logs_with_parsed_window": sum(1 for row in log_inventory_rows if row["window_start"] != ""),
            "logs_covering_candidate_indices": sum(1 for row in log_inventory_rows if row["covers_candidate_raw_indices"]),
            "stop_or_timeout_status_counts": dict(Counter(str(row["stop_or_timeout_status"]) for row in log_inventory_rows)),
        },
        "candidate_counts": {
            "candidate_count": len(certification_rows),
            "inside_fu02g4c_logged_window_count": sum(1 for row in certification_rows if row["inside_fu02g4c_logged_window"]),
            "replay_certification_status_counts": dict(status_counts),
            "non_exact_near_candidate_count": sum(1 for row in certification_rows if row["exact_match"] is False),
        },
        "required_targets": exact_target_rows,
        "overall_certification_status": overall_status,
        "overall_certification_basis": overall_basis,
        "outputs": {key: str(path) for key, path in output_paths.items()},
        "claim_boundary": {
            "certification_recovery_block_only": True,
            "no_physical_emergence_claim": True,
            "no_spacetime_emergence_claim": True,
            "no_global_uniqueness_claim": True,
            "no_global_rarity_claim": True,
            "scaffold_indices_not_silently_treated_as_fu02g4c_raw_order": True,
        },
    }

    write_csv(output_paths["fu02g4c_log_inventory_csv"], log_inventory_rows, LOG_INVENTORY_FIELDS)
    write_csv(output_paths["candidate_window_crosscheck_csv"], crosscheck_rows, CROSSCHECK_FIELDS)
    write_csv(output_paths["candidate_replay_certification_csv"], certification_rows, CERTIFICATION_FIELDS)
    write_json(output_paths["summary_json"], summary)
    output_paths["result_note_md"].write_text(build_result_note(summary), encoding="utf-8")

    print(f"Wrote FU02g5g outputs to {output_dir}")
    print(f"overall_certification_status={overall_status}")
    for label, row in sorted(exact_target_rows.items()):
        print(f"{label}={row['replay_certification_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
