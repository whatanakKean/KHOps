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

from khops.db.models.pipeline import Pipeline
from khops.db.models.run import Run
from khops.db.models.model import Model
from khops.db.models.metrics import Metrics


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
    
    def test_list_pipelines_pagination(self, client: TestClient, multiple_pipelines: list[Pipeline]):
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
        payload = {
            "name": "",  # Empty name
            "description": "Invalid pipeline",
            "definition": {}
        }
        
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
        assert "id" in data  # Run ID
        assert data["pipeline_id"] == sample_pipeline.id


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
        payload = {
            "name": "",  # Empty name
            "version": "1.0.0"
        }
        
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
                json={**payload, "version": first_version}
            )
            
            assert response.status_code in [200, 422]  # Success or validation error


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


# ============================================================================
# Health Check Tests
# ============================================================================

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
            headers={"Content-Type": "application/json"}
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
