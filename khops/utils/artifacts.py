"""Artifact management helpers."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from khops.core.config import settings

try:
    from ydata_profiling import ProfileReport

    YDATA_PROFILE_AVAILABLE = True
except ImportError:  # pragma: no cover
    YDATA_PROFILE_AVAILABLE = False


def get_project_name() -> str:
    """Use the current working directory name as the project identifier."""
    return Path.cwd().name or "project"


def get_artifacts_root(project_name: Optional[str] = None) -> Path:
    """Get the root artifacts folder for the current project."""
    project = project_name or get_project_name()
    return Path(settings.STORAGE_PATH).expanduser().resolve() / project


def get_model_artifact_dir(name: str, version: str, project_name: Optional[str] = None) -> Path:
    """Get a project-scoped directory for the model artifacts."""
    artifact_dir = get_artifacts_root(project_name) / "models" / name / version
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir


def get_data_artifact_dir(
    dataset_name: str = "dataset", project_name: Optional[str] = None
) -> Path:
    """Get a project-scoped directory for data artifacts."""
    artifact_dir = get_artifacts_root(project_name) / "data" / dataset_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir


def save_json_artifact(data: Dict[str, Any], path: Path) -> Path:
    """Save a JSON artifact to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    return path


def _compute_file_hash(path: Path, algorithm: str = "sha256") -> str:
    """Compute a file hash for artifact integrity and lineage tracking."""
    if not path.exists() or not path.is_file():
        return ""

    digest = hashlib.new(algorithm)
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(8192), b""):
            digest.update(chunk)

    return digest.hexdigest()


def build_experiment_metadata(
    pipeline_name: str,
    pipeline_version: str,
    pipeline_definition: Dict[str, Any],
    metrics: Dict[str, Any],
    artifact_lineage: Optional[list[Dict[str, Any]]] = None,
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build metadata describing an experiment run and its artifact lineage."""
    return {
        "pipeline_name": pipeline_name,
        "pipeline_version": pipeline_version,
        "pipeline_definition": pipeline_definition,
        "metrics": metrics,
        "artifact_lineage": artifact_lineage or [],
        "parameters": parameters or {},
        "recorded_at": datetime.utcnow().isoformat(),
    }


def _serialize_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _build_profile_summary(df: pd.DataFrame) -> Dict[str, Any]:
    describe = df.describe(include="all")
    summary: Dict[str, Any] = {
        "rows": int(len(df)),
        "columns": df.columns.tolist(),
        "dtypes": {str(col): str(dtype) for col, dtype in df.dtypes.items()},
        "describe": {},
    }

    for column, series in describe.items():
        summary["describe"][str(column)] = {
            str(index): _serialize_value(value) for index, value in series.items()
        }

    return summary


def save_data_profile(
    df: pd.DataFrame, artifact_dir: Path, filename: str = "data_profile"
) -> Dict[str, Optional[Path]]:
    """Save a dataset profile artifact, using ydata-profiling if available."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    html_path = artifact_dir / f"{filename}.html"
    csv_path = artifact_dir / f"{filename}.csv"
    json_path = artifact_dir / f"{filename}.json"

    # Always save a CSV summary for compatibility.
    df.describe(include="all").to_csv(csv_path)

    profile_data = _build_profile_summary(df)

    html_result = None
    if YDATA_PROFILE_AVAILABLE:
        profile = ProfileReport(df, title="KHOps Data Profile", explorative=True)
        profile.to_file(html_path)
        html_result = html_path
        try:
            json_text = profile.to_json()
            json_path.write_text(json_text)
        except Exception:
            save_json_artifact(profile_data, json_path)
    else:
        save_json_artifact(profile_data, json_path)

    return {
        "csv": csv_path,
        "json": json_path,
        "html": html_result,
    }


def build_model_artifact_metadata(
    model_path: Path,
    data_profile_path: Optional[Path] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build metadata for model artifacts."""
    metadata: Dict[str, Any] = {
        "model_path": str(model_path),
        "artifact_dir": str(model_path.parent),
    }

    if data_profile_path is not None:
        metadata["data_profile"] = str(data_profile_path)

    if model_path.exists():
        metadata["model_hash"] = _compute_file_hash(model_path)

    if data_profile_path is not None and Path(data_profile_path).exists():
        metadata["data_profile_hash"] = _compute_file_hash(Path(data_profile_path))

    if extra:
        metadata.update(extra)

    return metadata
