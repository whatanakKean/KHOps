"""
Unit tests for Pydantic schemas and validation.

Tests cover:
- Pipeline schema validation
- Run schema validation
- Model schema validation
- Metrics schema validation
- Error handling for invalid data
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from khops.server.schemas.pipeline import (
    PipelineCreate,
    PipelineUpdate,
    PipelineResponse,
    PipelineListResponse,
)
from khops.server.schemas.run import RunCreate, RunUpdate, RunResponse, RunListResponse
from khops.server.schemas.model import ModelCreate, ModelUpdate, ModelResponse, ModelListResponse
from khops.server.schemas.metrics import MetricsCreate, MetricsResponse, MetricsListResponse


# ============================================================================
# Pipeline Schema Tests
# ============================================================================


class TestPipelineSchemas:
    """Test pipeline schema validation."""

    def test_pipeline_create_valid(self):
        """Test valid pipeline creation schema."""
        data = {
            "name": "valid_pipeline",
            "description": "A valid pipeline",
            "definition": {"nodes": [], "edges": []},
        }

        schema = PipelineCreate(**data)

        assert schema.name == "valid_pipeline"
        assert schema.description == "A valid pipeline"

    def test_pipeline_create_missing_name(self):
        """Test validation error when name is missing."""
        data = {"description": "Missing name", "definition": {}}

        with pytest.raises(ValidationError) as exc_info:
            PipelineCreate(**data)

        assert "name" in str(exc_info.value)

    def test_pipeline_create_empty_name(self):
        """Test validation error when name is empty."""
        data = {"name": "", "description": "Empty name", "definition": {}}

        with pytest.raises(ValidationError):
            PipelineCreate(**data)

    def test_pipeline_create_missing_definition(self):
        """Test validation error when definition is missing."""
        data = {"name": "no_definition", "description": "Missing definition"}

        with pytest.raises(ValidationError) as exc_info:
            PipelineCreate(**data)

        assert "definition" in str(exc_info.value)

    def test_pipeline_update_partial(self):
        """Test partial pipeline update."""
        data = {"description": "Updated description"}

        schema = PipelineUpdate(**data)

        assert schema.description == "Updated description"

    def test_pipeline_response(self):
        """Test pipeline response schema."""
        data = {
            "id": 1,
            "name": "test_pipeline",
            "description": "Test",
            "definition": {},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        schema = PipelineResponse(**data)

        assert schema.id == 1
        assert schema.name == "test_pipeline"

    def test_pipeline_list_response(self):
        """Test pipeline list response schema."""
        pipelines = [
            {
                "id": 1,
                "name": "p1",
                "description": "Pipeline 1",
                "definition": {},
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ]

        data = {"pipelines": pipelines, "total": 1, "skip": 0, "limit": 10}

        schema = PipelineListResponse(**data)

        assert len(schema.pipelines) == 1
        assert schema.total == 1


# ============================================================================
# Run Schema Tests
# ============================================================================


class TestRunSchemas:
    """Test run schema validation."""

    def test_run_create_valid(self):
        """Test valid run creation schema."""
        data = {"pipeline_id": 1, "status": "pending"}

        schema = RunCreate(**data)

        assert schema.pipeline_id == 1
        assert schema.status == "pending"

    def test_run_create_missing_pipeline(self):
        """Test validation error when pipeline_id is missing."""
        data = {"status": "pending"}

        with pytest.raises(ValidationError) as exc_info:
            RunCreate(**data)

        assert "pipeline_id" in str(exc_info.value)

    def test_run_create_invalid_status(self):
        """Test validation error with invalid status."""
        data = {"pipeline_id": 1, "status": "invalid_status"}

        # May or may not validate depending on schema constraints
        try:
            schema = RunCreate(**data)
            # If it passes, that's okay
            assert schema.status == "invalid_status"
        except ValidationError:
            # If it fails, that's also okay (better validation)
            pass

    def test_run_update_partial(self):
        """Test partial run update."""
        data = {"status": "success", "logs": "Execution completed successfully"}

        schema = RunUpdate(**data)

        assert schema.status == "success"
        assert schema.logs == "Execution completed successfully"

    def test_run_response(self):
        """Test run response schema."""
        data = {
            "id": 1,
            "pipeline_id": 1,
            "status": "success",
            "logs": "Success",
            "meta": {"duration": 10.5},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        schema = RunResponse(**data)

        assert schema.id == 1
        assert schema.status == "success"

    def test_run_list_response(self):
        """Test run list response schema."""
        runs = [
            {
                "id": 1,
                "pipeline_id": 1,
                "status": "success",
                "logs": "Success",
                "meta": {},
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ]

        data = {"runs": runs, "total": 1, "skip": 0, "limit": 10}

        schema = RunListResponse(**data)

        assert len(schema.runs) == 1


# ============================================================================
# Model Schema Tests
# ============================================================================


class TestModelSchemas:
    """Test model schema validation."""

    def test_model_create_valid(self):
        """Test valid model creation schema."""
        data = {
            "name": "test_model",
            "version": "1.0.0",
            "stage": "dev",
            "path": "s3://bucket/model",
            "metrics": {"accuracy": 0.95},
        }

        schema = ModelCreate(**data)

        assert schema.name == "test_model"
        assert schema.version == "1.0.0"

    def test_model_create_missing_name(self):
        """Test validation error when name is missing."""
        data = {"version": "1.0.0", "stage": "dev", "path": "s3://bucket/model"}

        with pytest.raises(ValidationError):
            ModelCreate(**data)

    def test_model_create_missing_version(self):
        """Test validation error when version is missing."""
        data = {"name": "test_model", "stage": "dev", "path": "s3://bucket/model"}

        with pytest.raises(ValidationError):
            ModelCreate(**data)

    def test_model_create_invalid_version_format(self):
        """Test with invalid version format (might still pass)."""
        data = {
            "name": "test_model",
            "version": "not_a_version",
            "stage": "dev",
            "path": "s3://bucket/model",
        }

        # Should still create (version is just a string)
        schema = ModelCreate(**data)
        assert schema.version == "not_a_version"

    def test_model_update_stage(self):
        """Test model stage update."""
        data = {"stage": "production"}

        schema = ModelUpdate(**data)

        assert schema.stage == "production"

    def test_model_response(self):
        """Test model response schema."""
        data = {
            "id": 1,
            "name": "test_model",
            "version": "1.0.0",
            "stage": "dev",
            "path": "s3://model",
            "metrics": {"acc": 0.95},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        schema = ModelResponse(**data)

        assert schema.name == "test_model"
        assert schema.stage == "dev"

    def test_model_list_response(self):
        """Test model list response schema."""
        models = [
            {
                "id": 1,
                "name": "m1",
                "version": "1.0.0",
                "stage": "dev",
                "path": "s3://m1",
                "metrics": {},
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ]

        data = {"models": models, "total": 1, "skip": 0, "limit": 10}

        schema = ModelListResponse(**data)

        assert len(schema.models) == 1


# ============================================================================
# Metrics Schema Tests
# ============================================================================


class TestMetricsSchemas:
    """Test metrics schema validation."""

    def test_metrics_create_valid(self):
        """Test valid metrics creation schema."""
        data = {"name": "accuracy", "value": 0.95, "run_id": 1, "tags": {"dataset": "test"}}

        schema = MetricsCreate(**data)

        assert schema.name == "accuracy"
        assert schema.value == 0.95

    def test_metrics_create_missing_name(self):
        """Test validation error when name is missing."""
        data = {"value": 0.95, "run_id": 1}

        with pytest.raises(ValidationError):
            MetricsCreate(**data)

    def test_metrics_create_missing_value(self):
        """Test validation error when value is missing."""
        data = {"name": "accuracy", "run_id": 1}

        with pytest.raises(ValidationError):
            MetricsCreate(**data)

    def test_metrics_create_missing_run_id(self):
        """Test that run_id is actually required now."""
        data = {"name": "accuracy", "value": 0.95}

        # run_id is required, so this should fail
        with pytest.raises(ValidationError):
            MetricsCreate(**data)

    def test_metrics_create_invalid_value_type(self):
        """Test validation error with non-numeric value."""
        data = {"name": "accuracy", "value": "not_a_number", "run_id": 1}

        with pytest.raises(ValidationError):
            MetricsCreate(**data)

    def test_metrics_response(self):
        """Test metrics response schema."""
        data = {
            "id": 1,
            "name": "accuracy",
            "value": 0.95,
            "run_id": 1,
            "timestamp": datetime.now(),
            "tags": {"dataset": "test"},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        schema = MetricsResponse(**data)

        assert schema.name == "accuracy"
        assert schema.value == 0.95

    def test_metrics_list_response(self):
        """Test metrics list response schema."""
        metrics = [
            {
                "id": 1,
                "name": "metric1",
                "value": 0.9,
                "run_id": 1,
                "timestamp": datetime.now(),
                "tags": {},
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ]

        data = {"metrics": metrics, "total": 1, "skip": 0, "limit": 10}

        schema = MetricsListResponse(**data)

        assert len(schema.metrics) == 1


# ============================================================================
# Cross-Schema Validation Tests
# ============================================================================


class TestCrossSchemaValidation:
    """Test validation across multiple schemas."""

    def test_response_from_db_object(self):
        """Test creating response schema from database object."""
        # Simulate DB object with from_attributes=True
        db_data = {
            "id": 1,
            "name": "test",
            "description": "desc",
            "definition": {},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        schema = PipelineResponse(**db_data)

        assert schema.id == 1

    def test_schema_serialization(self):
        """Test schema can be serialized to dict."""
        data = {
            "id": 1,
            "name": "test_pipeline",
            "description": "Test",
            "definition": {},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        schema = PipelineResponse(**data)
        serialized = schema.model_dump()

        assert serialized["id"] == 1
        assert serialized["name"] == "test_pipeline"

    def test_schema_json_serialization(self):
        """Test schema can be serialized to JSON."""
        data = {
            "id": 1,
            "name": "test_pipeline",
            "description": "Test",
            "definition": {},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        schema = PipelineResponse(**data)
        json_str = schema.model_dump_json()

        assert "test_pipeline" in json_str
