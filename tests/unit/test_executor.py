import pytest

from khops.pipelines.parser import PipelineParser
from khops.pipelines.executor import PipelineExecutor


def test_pipeline_executor_completes_with_minimal_pipeline():
    yaml_content = """
name: sample_pipeline
version: "1.0"
description: Minimal execution pipeline
nodes:
  - id: data_load
    type: data
    params:
      source: "./nonexistent.csv"
  - id: model_train
    type: training
    params:
      algorithm: "random_forest"
      target: "label"
edges:
  - from: data_load
    to: model_train
"""

    pipeline_config = PipelineParser.parse_yaml_string(yaml_content)
    executor = PipelineExecutor(pipeline_config)
    result = executor.execute()

    assert result["status"] == "success"
    assert "Pipeline execution completed" in result["logs"]
    assert result["meta"]["pipeline_name"] == "sample_pipeline"
    assert result["meta"]["nodes_executed"] == 2
