from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from khops.utils.artifacts import save_json_artifact


def save_experiment_metadata(
    run_id: str,
    pipeline_name: str,
    pipeline_version: str,
    metadata: Dict[str, Any],
    output_dir: Optional[Path] = None,
    filename: str = "experiment_metadata.json",
) -> Path:
    """Save experiment tracking metadata for a pipeline run."""
    directory = output_dir or Path("./data/artifacts")
    directory.mkdir(parents=True, exist_ok=True)

    payload = {
        "run_id": run_id,
        "pipeline_name": pipeline_name,
        "pipeline_version": pipeline_version,
        "metadata": metadata,
        "recorded_at": datetime.utcnow().isoformat(),
    }

    return save_json_artifact(payload, directory / filename)
