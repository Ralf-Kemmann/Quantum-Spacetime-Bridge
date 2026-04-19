from __future__ import annotations

from pathlib import Path
from typing import Type, TypeVar, Any
import json

import pandas as pd
import yaml
from pydantic import BaseModel

from src.m39x3g_a.models import (
    RunConfig,
    InputManifestRowModel,
    DiagnosticRowModel,
    ResamplingRowModel,
    SummaryModel,
    validate_run_id_consistency,
    validate_feature_space_consistency,
)


T = TypeVar("T", bound=BaseModel)


def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"YAML file does not contain a mapping: {path}")
    return data


def load_run_config(path: str | Path) -> RunConfig:
    raw = load_yaml(path)
    return RunConfig.model_validate(raw)


def load_csv_as_models(path: str | Path, model_cls: Type[T]) -> list[T]:
    path = Path(path)
    df = pd.read_csv(path)
    records = df.to_dict(orient="records")
    return [model_cls.model_validate(record) for record in records]


def load_input_manifest(path: str | Path) -> list[InputManifestRowModel]:
    return load_csv_as_models(path, InputManifestRowModel)


def load_diagnostics_csv(path: str | Path) -> list[DiagnosticRowModel]:
    return load_csv_as_models(path, DiagnosticRowModel)


def load_resampling_csv(path: str | Path) -> list[ResamplingRowModel]:
    return load_csv_as_models(path, ResamplingRowModel)


def write_summary_json(summary: SummaryModel, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(summary.model_dump(mode="json"), f, indent=2, ensure_ascii=False)


def load_summary_json(path: str | Path) -> SummaryModel:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return SummaryModel.model_validate(raw)


def validate_manifest_against_config(
    manifest_rows: list[InputManifestRowModel],
    config: RunConfig,
) -> None:
    validate_feature_space_consistency(manifest_rows, config)
    validate_run_id_consistency(manifest_rows=manifest_rows)

    enabled_control_ids = {cf.id for cf in config.enabled_control_families}

    for row in manifest_rows:
        if row.run_id != config.run_id:
            raise ValueError(
                f"Manifest row run_id '{row.run_id}' does not match config.run_id '{config.run_id}'"
            )

        if row.source_type == "control" and row.is_enabled:
            if row.control_family not in enabled_control_ids:
                raise ValueError(
                    f"Enabled control row uses control_family '{row.control_family}', "
                    f"which is not enabled in config"
                )


def resolve_repo_path(config: RunConfig, relative_path: str | Path) -> Path:
    return Path(relative_path)


def load_config_and_manifest(
    config_path: str | Path,
) -> tuple[RunConfig, list[InputManifestRowModel]]:
    config = load_run_config(config_path)
    manifest = load_input_manifest(config.data.input_manifest_path)
    validate_manifest_against_config(manifest, config)
    return config, manifest