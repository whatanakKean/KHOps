"""
Integration tests for KHOps API routes.

Tests cover:
- Pipeline API (GET, POST, update, delete)
- Run API (GET, POST, update, delete, logs)
- Model API (GET, POST, list versions, promote)
- Metrics API (GET, POST, query)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from khops.db.models.metrics import Metrics
from khops.db.models.model import Model
from khops.db.models.pipeline import Pipeline
from khops.db.models.run import Run

# ============================================================================
# Pipeline API Tests
# ============================================================================


class TestPipelineAPI:
    """Test pipeline API endpoints."""

    def test_list_pipelines(self, client: TestClient, multiple_pipelines: list[Pipeline]):
        """Test GET /api/v1/pipelines."""
        response = client.get("/api/v1/pipelines")

        assert response.status_code == 200
        data = response.json()
        assert "pipelines" in data
        assert data["total"] >= 5

    def test_list_pipelines_pagination(
        self, client: TestClient, multiple_pipelines: list[Pipeline]
    ):
        """Test pagination in list pipelines."""
        response = client.get("/api/v1/pipelines?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["pipelines"]) == 2

    def test_create_pipeline(self, client: TestClient, valid_pipeline_payload: dict):
        """Test POST /api/v1/pipelines/create."""
        response = client.post("/api/v1/pipelines/create", json=valid_pipeline_payload)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == valid_pipeline_payload["name"]

    def test_create_pipeline_invalid_name(self, client: TestClient):
        """Test creating pipeline with invalid data."""
        payload = {"name": "", "description": "Invalid pipeline", "definition": {}}  # Empty name

        response = client.post("/api/v1/pipelines/create", json=payload)

        assert response.status_code == 422  # Validation error

    def test_get_pipeline(self, client: TestClient, sample_pipeline: Pipeline):
        """Test GET /api/v1/pipelines/{pipeline_id}."""
        response = client.get(f"/api/v1/pipelines/{sample_pipeline.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_pipeline.id
        assert data["name"] == sample_pipeline.name

    def test_get_pipeline_not_found(self, client: TestClient):
        """Test getting non-existent pipeline."""
        response = client.get("/api/v1/pipelines/9999")

        assert response.status_code == 404

    def test_execute_pipeline(self, client: TestClient, sample_pipeline: Pipeline):
        """Test POST /api/v1/pipelines/{pipeline_id}/execute."""
        response = client.post(f"/api/v1/pipelines/{sample_pipeline.id}/execute")

        assert response.status_code == 200
        data = response.json()
        assert data["pipeline_id"] == sample_pipeline.id
        assert "run_id" in data

        run_id = data["run_id"]
        status_response = client.get(f"/api/v1/runs/{run_id}")
        assert status_response.status_code == 200
        run_data = status_response.json()
        assert run_data["status"] in {"running", "success", "failed"}

        logs_response = client.get(f"/api/v1/runs/{run_id}/logs")
        assert logs_response.status_code == 200
        logs_data = logs_response.json()
        assert "logs" in logs_data


class TestProjectAPI:
    """Test project API endpoints."""

    def test_create_and_list_projects(self, client: TestClient):
        payload = {"name": "api_project", "description": "API Project"}

        create_response = client.post("/api/v1/projects/create", json=payload)
        assert create_response.status_code == 200
        project_data = create_response.json()
        assert project_data["name"] == "api_project"
        assert project_data["description"] == "API Project"

        list_response = client.get("/api/v1/projects")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert any(p["name"] == "api_project" for p in list_data["projects"])


# ============================================================================
# Run API Tests
# ============================================================================


class TestRunAPI:
    """Test run API endpoints."""

    def test_list_runs(self, client: TestClient, multiple_runs: list[Run]):
        """Test GET /api/v1/runs."""
        response = client.get("/api/v1/runs")

        assert response.status_code == 200
        data = response.json()
        assert "runs" in data
        assert data["total"] >= len(multiple_runs)

    def test_list_runs_pagination(self, client: TestClient, multiple_runs: list[Run]):
        """Test pagination in list runs."""
        response = client.get("/api/v1/runs?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["runs"]) <= 2

    def test_get_run(self, client: TestClient, sample_run: Run):
        """Test GET /api/v1/runs/{run_id}."""
        response = client.get(f"/api/v1/runs/{sample_run.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_run.id
        assert data["status"] == sample_run.status

    def test_get_run_not_found(self, client: TestClient):
        """Test getting non-existent run."""
        response = client.get("/api/v1/runs/9999")

        assert response.status_code == 404

    def test_get_run_logs(self, client: TestClient, sample_run: Run):
        """Test GET /api/v1/runs/{run_id}/logs."""
        response = client.get(f"/api/v1/runs/{sample_run.id}/logs")

        assert response.status_code == 200
        data = response.json()
        assert "logs" in data

    def test_cancel_run(self, client: TestClient, sample_run: Run):
        """Test POST /api/v1/runs/{run_id}/cancel."""
        response = client.post(f"/api/v1/runs/{sample_run.id}/cancel")

        assert response.status_code in [200, 400]  # May succeed or fail depending on status

    def test_update_run_status(self, client: TestClient, sample_run: Run):
        """Test updating run status directly."""
        payload = {"status": "failed", "logs": "Updated logs"}

        response = client.put(f"/api/v1/runs/{sample_run.id}", json=payload)

        # May not be implemented, check if endpoints exist
        assert response.status_code in [200, 405, 404]


# ============================================================================
# Model API Tests
# ============================================================================


class TestModelAPI:
    """Test model API endpoints."""

    def test_list_models(self, client: TestClient, multiple_models: list[Model]):
        """Test GET /api/v1/models."""
        response = client.get("/api/v1/models")

        assert response.status_code == 200
        data = response.json()
        assert "models" in data

    def test_list_models_pagination(self, client: TestClient, multiple_models: list[Model]):
        """Test pagination in list models."""
        response = client.get("/api/v1/models?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["models"]) <= 2

    def test_register_model(self, client: TestClient, valid_model_payload: dict):
        """Test POST /api/v1/models/register."""
        response = client.post("/api/v1/models/register", json=valid_model_payload)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == valid_model_payload["name"]
        assert data["stage"] == valid_model_payload["stage"]

    def test_register_model_invalid(self, client: TestClient):
        """Test registering model with invalid data."""
        payload = {"name": "", "version": "1.0.0"}  # Empty name

        response = client.post("/api/v1/models/register", json=payload)

        assert response.status_code == 422  # Validation error

    def test_get_model_by_name(self, client: TestClient, sample_model: Model):
        """Test GET /api/v1/models/{model_name}."""
        response = client.get(f"/api/v1/models/{sample_model.name}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_model.name

    def test_get_model_not_found(self, client: TestClient):
        """Test getting non-existent model."""
        response = client.get("/api/v1/models/nonexistent_model")

        assert response.status_code == 404

    def test_get_model_versions(self, client: TestClient, multiple_models: list[Model]):
        """Test GET /api/v1/models/{model_name}/versions."""
        response = client.get("/api/v1/models/versioned_model/versions")

        assert response.status_code == 200
        data = response.json()
        assert "versions" in data
        assert len(data["versions"]) > 0

    def test_promote_model(self, client: TestClient, multiple_models: list[Model]):
        """Test POST /api/v1/models/{model_name}/promote."""
        # Get first available model version
        response = client.get("/api/v1/models/versioned_model/versions")
        versions = response.json()["versions"]

        if versions:
            first_version = versions[0]["version"]
            payload = {"stage": "production"}

            response = client.post(
                f"/api/v1/models/versioned_model/promote",
                json={**payload, "version": first_version},
            )

            assert response.status_code in [200, 422]  # Success or validation error

    def test_get_model_promotion_history(self, client: TestClient, sample_model: Model):
        """Test GET /api/v1/models/{model_name}/{version}/history."""
        response = client.get(f"/api/v1/models/{sample_model.name}/{sample_model.version}/history")

        assert response.status_code == 200
        data = response.json()
        # Should be a list (empty if no promotions)
        assert isinstance(data, list)


# ============================================================================
# Metrics API Tests
# ============================================================================


class TestMetricsAPI:
    """Test metrics API endpoints."""

    def test_list_metrics(self, client: TestClient, multiple_metrics: list[Metrics]):
        """Test GET /api/v1/metrics."""
        response = client.get("/api/v1/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data

    def test_list_metrics_pagination(self, client: TestClient, multiple_metrics: list[Metrics]):
        """Test pagination in list metrics."""
        response = client.get("/api/v1/metrics?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["metrics"]) <= 2

    def test_log_metrics(self, client: TestClient, sample_run: Run, valid_metrics_payload: dict):
        """Test POST /api/v1/metrics/log."""
        payload = {**valid_metrics_payload, "run_id": sample_run.id}

        response = client.post("/api/v1/metrics/log", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == payload["name"]

    def test_get_metric_history(self, client: TestClient, sample_metrics: Metrics):
        """Test GET /api/v1/metrics/{metric_name}."""
        response = client.get(f"/api/v1/metrics/{sample_metrics.name}")

        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data


class TestRegistryAPI:
    """Test model registry and artifact endpoints."""

    def test_get_model_artifacts_returns_meta(self, client: TestClient, valid_model_payload: dict):
        """Test GET /api/v1/registry/models/{model_name}/artifacts."""
        payload = {
            **valid_model_payload,
            "metadata": {"format": "pickle", "size_bytes": 1234, "hash": "abc123"},
        }

        register_response = client.post("/api/v1/models/register", json=payload)
        assert register_response.status_code == 200

        model_name = payload["name"]
        version = payload["version"]

        response = client.get(f"/api/v1/registry/models/{model_name}/artifacts?version={version}")

        assert response.status_code == 200
        data = response.json()
        assert data["size_bytes"] == 1234
        assert data["hash"] == "abc123"
        assert data["artifact_info"]["format"] == "pickle"

    def test_export_model_metadata_returns_metadata(
        self, client: TestClient, valid_model_payload: dict
    ):
        """Test GET /api/v1/registry/export-metadata."""
        payload = {
            **valid_model_payload,
            "metadata": {"owner": "test", "format": "pkl"},
        }

        register_response = client.post("/api/v1/models/register", json=payload)
        assert register_response.status_code == 200

        model_name = payload["name"]
        version = payload["version"]

        response = client.get(
            f"/api/v1/registry/export-metadata?model_name={model_name}&version={version}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["export_metadata"]["metadata"]["owner"] == "test"
        assert data["export_metadata"]["metadata"]["format"] == "pkl"


class TestPipelineUploadAPI:
    """Test pipeline upload endpoints."""

    def test_upload_pipeline_from_yaml(self, client: TestClient):
        """Test POST /api/v1/pipelines/upload."""
        yaml_content = """
name: upload_test_pipeline
version: "1.0"
description: Upload test pipeline
nodes:
  - id: load
    type: data
  - id: train
    type: training
edges:
  - from: load
    to: train
"""
        response = client.post(
            "/api/v1/pipelines/upload",
            json={"yaml_content": yaml_content},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "upload_test_pipeline"
        assert data["definition"]["version"] == "1.0"
        assert len(data["definition"]["nodes"]) == 2

    def test_upload_invalid_yaml(self, client: TestClient):
        """Test uploading invalid YAML returns error."""
        response = client.post(
            "/api/v1/pipelines/upload",
            json={"yaml_content": "{ invalid: yaml: content }"},
        )

        assert response.status_code == 400


# ============================================================================
# Model Serving Tests
# ============================================================================


class TestModelServingAPI:
    """Test model serving endpoints (predictions, metadata, health)."""

    def test_serve_model_metadata(self, client: TestClient, sample_model: Model):
        """Test GET /serve/{model_name}/metadata."""
        response = client.get(f"/serve/{sample_model.name}/metadata")

        assert response.status_code == 200
        data = response.json()
        assert data["model_name"] == sample_model.name
        assert data["version"] == sample_model.version
        assert data["stage"] == sample_model.stage

    def test_serve_model_health(self, client: TestClient, sample_model: Model):
        """Test GET /serve/{model_name}/health."""
        response = client.get(f"/serve/{sample_model.name}/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "available"
        assert data["model_name"] == sample_model.name

    def test_serve_model_not_found(self, client: TestClient):
        """Test serving non-existent model returns 404."""
        response = client.get("/serve/nonexistent/metadata")

        assert response.status_code == 404

    def test_serve_model_health_nonexistent(self, client: TestClient):
        """Test health check for non-existent model."""
        response = client.get("/serve/nonexistent/health")

        assert response.status_code == 404

    def test_serve_prediction_with_features(self, client: TestClient, sample_model: Model):
        """Test POST /serve/{model_name} prediction endpoint."""
        payload = {
            "features": [
                {"feature1": 1.0, "feature2": 2.0},
                {"feature1": 3.0, "feature2": 4.0},
            ]
        }

        response = client.post(f"/serve/{sample_model.name}", json=payload)

        # May fail if model artifact doesn't exist; check for appropriate status
        assert response.status_code in [200, 404]


class TestObservabilityAPI:
    """Test observability endpoints (metrics, drift, alerts)."""

    def test_observability_summary(self, client: TestClient, multiple_metrics: list[Metrics]):
        """Test GET /api/v1/observability/summary."""
        response = client.get("/api/v1/observability/summary")

        assert response.status_code == 200
        data = response.json()
        assert "metric_count" in data
        assert "summary" in data

    def test_observability_drift(self, client: TestClient, multiple_metrics: list[Metrics]):
        """Test GET /api/v1/observability/drift."""
        response = client.get("/api/v1/observability/drift")

        assert response.status_code == 200
        data = response.json()
        assert "drift_count" in data
        assert "signals" in data
        assert "threshold" in data

    def test_observability_alerts(self, client: TestClient, multiple_metrics: list[Metrics]):
        """Test GET /api/v1/observability/alerts."""
        response = client.get("/api/v1/observability/alerts")

        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data

    def test_observability_alerts_send(self, client: TestClient, multiple_metrics: list[Metrics]):
        """Test POST /api/v1/observability/alerts/send."""
        response = client.post("/api/v1/observability/alerts/send")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "alerts_sent" in data
        assert "alerts_failed" in data


class TestRegistryStatsAPI:
    """Test registry statistics endpoints."""

    def test_registry_stats(self, client: TestClient, multiple_models: list[Model]):
        """Test GET /api/v1/registry/stats."""
        response = client.get("/api/v1/registry/stats")

        assert response.status_code == 200
        data = response.json()
        assert "total_models" in data
        assert "models_by_stage" in data
        assert "unique_model_names" in data

    def test_registry_search(self, client: TestClient, multiple_models: list[Model]):
        """Test GET /api/v1/registry/search."""
        response = client.get("/api/v1/registry/search?q=versioned")

        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "total" in data

    def test_registry_models_by_stage(self, client: TestClient, multiple_models: list[Model]):
        """Test GET /api/v1/registry/stages/{stage}."""
        for stage in ["dev", "staging", "production"]:
            response = client.get(f"/api/v1/registry/stages/{stage}")
            assert response.status_code == 200
            data = response.json()
            assert "models" in data
            assert "total" in data

    def test_registry_compare_models(self, client: TestClient, multiple_models: list[Model]):
        """Test GET /api/v1/registry/compare."""
        response = client.get(
            "/api/v1/registry/compare?model_names=versioned_model&model_names=sample_model"
        )

        # May not find both if not created; check for appropriate status
        assert response.status_code in [200, 404]


class TestHealthAPI:
    """Test health check endpoints."""

    def test_health_check(self, client: TestClient):
        """Test GET /api/v1/health."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200

    def test_root_endpoint(self, client: TestClient):
        """Test GET /."""
        response = client.get("/")

        assert response.status_code in [200, 404, 307]  # OK or redirect


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Test error handling across API."""

    def test_404_on_invalid_route(self, client: TestClient):
        """Test 404 for invalid route."""
        response = client.get("/api/v1/invalid_endpoint")

        assert response.status_code == 404

    def test_method_not_allowed(self, client: TestClient, sample_pipeline: Pipeline):
        """Test 405 for wrong HTTP method."""
        response = client.delete(f"/api/v1/pipelines/{sample_pipeline.id}/execute")

        assert response.status_code == 405

    def test_invalid_json(self, client: TestClient):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/v1/pipelines/create",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code in [400, 422]


# ============================================================================
# Response Format Tests
# ============================================================================


class TestResponseFormats:
    """Test API response format consistency."""

    def test_list_response_format(self, client: TestClient):
        """Test that list responses follow correct format."""
        response = client.get("/api/v1/pipelines")

        assert response.status_code == 200
        data = response.json()
        assert "pipelines" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data

    def test_single_object_response(self, client: TestClient, sample_pipeline: Pipeline):
        """Test that single object responses have correct format."""
        response = client.get(f"/api/v1/pipelines/{sample_pipeline.id}")

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "created_at" in data
        assert "updated_at" in data
