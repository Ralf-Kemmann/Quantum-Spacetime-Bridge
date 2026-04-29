#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import random
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required for this script.") from exc


FEATURE_COLUMNS = [
    "feature_mode_frequency",
    "feature_length_scale",
    "feature_shape_factor",
    "feature_spectral_index",
]


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def read_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("Feature table is empty.")
    return rows


def safe_float(value: str, context: str) -> float:
    try:
        x = float(value)
    except Exception as exc:
        raise ValueError(f"Cannot parse float in {context}: {value}") from exc
    if math.isnan(x) or math.isinf(x):
        raise ValueError(f"Non-finite float in {context}: {value}")
    return x


def row_feature_vector(row: dict) -> list[float]:
    mode_freq = safe_float(row["feature_mode_frequency"], "feature_mode_frequency")
    length_scale = safe_float(row["feature_length_scale"], "feature_length_scale")
    l_major = safe_float(row["L_major_raw"], "L_major_raw")
    l_minor = safe_float(row["L_minor_raw"], "L_minor_raw")
    m_ref = safe_float(row["m_ref_raw"], "m_ref_raw")

    if l_major <= 0 or l_minor <= 0:
        raise ValueError("L_major_raw and L_minor_raw must be positive.")

    shape_factor = max(l_major, l_minor) / min(l_major, l_minor)
    spectral_index = m_ref

    return [mode_freq, length_scale, shape_factor, spectral_index]


def feature_matrix(rows: list[dict]) -> list[list[float]]:
    return [row_feature_vector(row) for row in rows]


def mean_vector(matrix: list[list[float]]) -> list[float]:
    n = len(matrix)
    d = len(matrix[0])
    means = [0.0] * d
    for row in matrix:
        for j, x in enumerate(row):
            means[j] += x
    return [x / n for x in means]


def covariance_matrix(matrix: list[list[float]], means: list[float]) -> list[list[float]]:
    n = len(matrix)
    d = len(matrix[0])
    if n < 2:
        raise ValueError("Need at least two rows for covariance estimation.")
    cov = [[0.0 for _ in range(d)] for _ in range(d)]
    for row in matrix:
        centered = [row[j] - means[j] for j in range(d)]
        for i in range(d):
            for j in range(d):
                cov[i][j] += centered[i] * centered[j]
    scale = 1.0 / (n - 1)
    for i in range(d):
        for j in range(d):
            cov[i][j] *= scale
    return cov


def cholesky_decomposition(matrix: list[list[float]], jitter: float = 1e-10) -> list[list[float]]:
    n = len(matrix)
    a = [row[:] for row in matrix]
    for i in range(n):
        a[i][i] += jitter
    l = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(l[i][k] * l[j][k] for k in range(j))
            if i == j:
                val = a[i][i] - s
                if val <= 0.0:
                    raise ValueError("Covariance matrix is not positive definite enough for Cholesky.")
                l[i][j] = math.sqrt(val)
            else:
                l[i][j] = (a[i][j] - s) / l[j][j]
    return l


def sample_multivariate_gaussian(means: list[float], chol: list[list[float]], rng: random.Random) -> list[float]:
    d = len(means)
    z = [rng.gauss(0.0, 1.0) for _ in range(d)]
    x = [0.0] * d
    for i in range(d):
        x[i] = means[i] + sum(chol[i][k] * z[k] for k in range(i + 1))
    return x


def safe_positive(value: float, floor: float = 1e-9) -> float:
    if math.isnan(value) or math.isinf(value):
        return floor
    return value if value > floor else floor


def write_rows(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build BMC-11 covariance-preserving nullmodel from BMC-08c-style feature table."
    )
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_yaml(Path(args.config))
    input_path = Path(cfg["input"]["feature_table_csv"])
    output_path = Path(cfg["output"]["feature_table_csv"])
    seeds = list(cfg["params"]["seeds"])

    template_rows = read_rows(input_path)
    matrix = feature_matrix(template_rows)
    means = mean_vector(matrix)
    cov = covariance_matrix(matrix, means)
    chol = cholesky_decomposition(cov)

    out_rows: list[dict] = []
    for seed in seeds:
        rng = random.Random(int(seed))
        for row in template_rows:
            sampled = sample_multivariate_gaussian(means, chol, rng)

            mode_freq, length_scale, shape_factor, spectral_index = sampled
            length_scale = safe_positive(length_scale)
            shape_factor = safe_positive(shape_factor)
            spectral_index = safe_positive(spectral_index)

            new_row = dict(row)
            new_row["feature_mode_frequency"] = f"{mode_freq:.12g}"
            new_row["feature_length_scale"] = f"{length_scale:.12g}"

            # Rohfelder so anpassen, dass die abgeleiteten Größen konsistent bleiben
            new_row["L_major_raw"] = f"{shape_factor:.12g}"
            new_row["L_minor_raw"] = "1"
            new_row["m_ref_raw"] = f"{spectral_index:.12g}"

            new_row["origin_tag"] = f"BMC11_cov_null_seed_{seed}"
            new_row["comment"] = "Covariance-preserving multivariate Gaussian nullmodel row"
            new_row["nullmodel_seed"] = str(seed)
            out_rows.append(new_row)

    fieldnames = list(template_rows[0].keys())
    if "nullmodel_seed" not in fieldnames:
        fieldnames.append("nullmodel_seed")

    write_rows(output_path, out_rows, fieldnames)
    print(f"Wrote: {output_path}")
    print(f"Row count: {len(out_rows)}")
    print(f"Seeds: {seeds}")


if __name__ == "__main__":
    main()
