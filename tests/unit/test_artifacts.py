import json
from pathlib import Path

import pandas as pd

from khops.core.config import settings
from khops.utils import artifacts
from khops.utils.artifacts import (
    build_experiment_metadata,
    build_model_artifact_metadata,
    get_data_artifact_dir,
    get_model_artifact_dir,
    save_data_profile,
    save_json_artifact,
)


def test_artifact_directories_are_project_scoped(tmp_path):
    settings.STORAGE_PATH = str(tmp_path / "artifacts")
    model_dir = get_model_artifact_dir("sample_model", "1.0")
    assert model_dir.exists()
    assert "sample_model" in model_dir.as_posix()

    data_dir = get_data_artifact_dir("sample_dataset")
    assert data_dir.exists()
    assert "sample_dataset" in data_dir.as_posix()


def test_save_data_profile_creates_profile_file(tmp_path):
    settings.STORAGE_PATH = str(tmp_path / "artifacts")
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    output_dir = tmp_path / "profiles"
    result = save_data_profile(df, output_dir, filename="test_profile")

    assert result["csv"].exists()
    assert result["json"].exists()
    assert result["html"] is None


def test_save_data_profile_with_ydata_html_generation(tmp_path, monkeypatch):
    settings.STORAGE_PATH = str(tmp_path / "artifacts")
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    output_dir = tmp_path / "profiles"

    monkeypatch.setattr(artifacts, "YDATA_PROFILE_AVAILABLE", True)

    class DummyProfile:
        def __init__(self, df, title, explorative):
            pass

        def to_file(self, path: Path):
            path.write_text("<html><body>dummy profile</body></html>")

        def to_json(self):
            return json.dumps({"dummy": "profile"})

    monkeypatch.setattr(artifacts, "ProfileReport", DummyProfile, raising=False)

    result = save_data_profile(df, output_dir, filename="test_profile")

    assert result["html"] is not None
    assert result["html"].exists()
    assert result["html"].suffix == ".html"
    assert result["csv"].exists()
    assert result["json"].exists()
    assert json.loads(result["json"].read_text()) == {"dummy": "profile"}


def test_save_json_artifact_writes_json(tmp_path):
    payload = {"model": "sample", "accuracy": 0.95}
    output_path = tmp_path / "artifact_metadata.json"
    returned_path = save_json_artifact(payload, output_path)

    assert returned_path == output_path
    assert output_path.exists()
    loaded = json.loads(output_path.read_text())
    assert loaded == payload


def test_build_model_artifact_metadata_includes_hashes(tmp_path):
    model_file = tmp_path / "model.pkl"
    model_file.write_text("dummy model")

    data_profile_file = tmp_path / "profile.json"
    data_profile_file.write_text(json.dumps({"rows": 1}))

    metadata = build_model_artifact_metadata(
        model_path=model_file,
        data_profile_path=data_profile_file,
        extra={"test_key": "value"},
    )

    assert metadata["model_path"] == str(model_file)
    assert metadata["artifact_dir"] == str(model_file.parent)
    assert metadata["model_hash"] != ""
    assert metadata["data_profile_hash"] != ""
    assert metadata["test_key"] == "value"


def test_build_experiment_metadata_contains_expected_fields():
    definition = {"name": "sample", "version": "1.0", "nodes": []}
    metrics = {"accuracy": 0.99}
    lineage = [{"node_id": "train", "model_path": "/tmp/model.pkl"}]
    parameters = {"learning_rate": 0.01}

    experiment_meta = build_experiment_metadata(
        pipeline_name="sample_pipeline",
        pipeline_version="1.0",
        pipeline_definition=definition,
        metrics=metrics,
        artifact_lineage=lineage,
        parameters=parameters,
    )

    assert experiment_meta["pipeline_name"] == "sample_pipeline"
    assert experiment_meta["pipeline_version"] == "1.0"
    assert experiment_meta["pipeline_definition"] == definition
    assert experiment_meta["metrics"] == metrics
    assert experiment_meta["artifact_lineage"] == lineage
    assert experiment_meta["parameters"] == parameters
    assert "recorded_at" in experiment_meta
