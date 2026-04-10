"""
Pytest configuration and fixtures for KHOps tests.

This module provides:
- Database fixtures (in-memory SQLite for fast testing)
- FastAPI test client
- Sample data factories
- Mock configurations
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from typing import Generator

from khops.server.app import app
from khops.db.base import Base
from khops.server.dependencies import get_db
from khops.db.models.pipeline import Pipeline
from khops.db.models.run import Run
from khops.db.models.model import Model
from khops.db.models.metrics import Metrics


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create an in-memory SQLite database for testing.
    
    This fixture:
    - Creates a fresh database for each test
    - Creates all tables
    - Provides a session
    - Rolls back after each test
    
    Yields:
        Session: SQLAlchemy session connected to test database
    """
    # Create in-memory SQLite engine
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    # Create session
    db = TestingSessionLocal()
    
    yield db
    
    # Cleanup
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> TestClient:
    """
    Create a FastAPI test client with test database.
    
    This fixture:
    - Overrides get_db dependency with test database
    - Provides TestClient for making HTTP requests
    - Ensures isolation between tests
    
    Args:
        test_db: Test database session
    
    Returns:
        TestClient: FastAPI test client
    """
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    # Cleanup overrides
    app.dependency_overrides.clear()


# ============================================================================
# Sample Data Factories
# ============================================================================

@pytest.fixture
def sample_pipeline(test_db: Session) -> Pipeline:
    """
    Create a sample pipeline for testing.
    
    Returns:
        Pipeline: Test pipeline instance
    """
    pipeline = Pipeline(
        name="sample_pipeline",
        description="Sample pipeline for testing",
        definition={
            "nodes": [
                {"id": "data_load", "type": "data"},
                {"id": "model_train", "type": "training"}
            ],
            "edges": [
                {"from": "data_load", "to": "model_train"}
            ]
        }
    )
    test_db.add(pipeline)
    test_db.commit()
    test_db.refresh(pipeline)
    return pipeline


@pytest.fixture
def sample_run(test_db: Session, sample_pipeline: Pipeline) -> Run:
    """
    Create a sample run for testing.
    
    Args:
        test_db: Test database session
        sample_pipeline: Sample pipeline
    
    Returns:
        Run: Test run instance
    """
    run = Run(
        pipeline_id=sample_pipeline.id,
        status="completed",
        logs="Test execution logs",
        meta={"duration": 10.5, "nodes_executed": 2}
    )
    test_db.add(run)
    test_db.commit()
    test_db.refresh(run)
    return run


@pytest.fixture
def sample_model(test_db: Session) -> Model:
    """
    Create a sample model for testing.
    
    Args:
        test_db: Test database session
    
    Returns:
        Model: Test model instance
    """
    model = Model(
        name="sample_model",
        version="1.0.0",
        stage="dev",
        path="s3://models/sample_model/1.0.0",
        metrics={"accuracy": 0.95, "f1_score": 0.92}
    )
    test_db.add(model)
    test_db.commit()
    test_db.refresh(model)
    return model


@pytest.fixture
def sample_metrics(test_db: Session, sample_run: Run) -> Metrics:
    """
    Create sample metrics for testing.
    
    Args:
        test_db: Test database session
        sample_run: Sample run
    
    Returns:
        Metrics: Test metrics instance
    """
    metrics = Metrics(
        name="accuracy",
        value=0.95,
        run_id=sample_run.id,
        tags={"dataset": "test", "model": "sample"}
    )
    test_db.add(metrics)
    test_db.commit()
    test_db.refresh(metrics)
    return metrics


@pytest.fixture
def multiple_pipelines(test_db: Session) -> list[Pipeline]:
    """
    Create multiple pipelines for testing pagination and filtering.
    
    Args:
        test_db: Test database session
    
    Returns:
        list[Pipeline]: List of test pipelines
    """
    pipelines = []
    for i in range(5):
        pipeline = Pipeline(
            name=f"pipeline_{i}",
            description=f"Pipeline {i} for testing",
            definition={"nodes": [], "edges": []}
        )
        test_db.add(pipeline)
        pipelines.append(pipeline)
    test_db.commit()
    return pipelines


@pytest.fixture
def multiple_runs(test_db: Session, sample_pipeline: Pipeline) -> list[Run]:
    """
    Create multiple runs for testing pagination.
    
    Args:
        test_db: Test database session
        sample_pipeline: Sample pipeline
    
    Returns:
        list[Run]: List of test runs
    """
    runs = []
    statuses = ["completed", "failed", "running", "completed", "pending"]
    for i, status in enumerate(statuses):
        run = Run(
            pipeline_id=sample_pipeline.id,
            status=status,
            logs=f"Logs for run {i}",
            meta={"attempt": i}
        )
        test_db.add(run)
        runs.append(run)
    test_db.commit()
    return runs


@pytest.fixture
def multiple_models(test_db: Session) -> list[Model]:
    """
    Create multiple model versions for testing.
    
    Args:
        test_db: Test database session
    
    Returns:
        list[Model]: List of test models
    """
    models = []
    versions = ["1.0.0", "1.1.0", "2.0.0", "2.1.0", "2.2.0"]
    stages = ["dev", "staging", "production", "dev", "staging"]
    
    for version, stage in zip(versions, stages):
        model = Model(
            name="versioned_model",
            version=version,
            stage=stage,
            path=f"s3://models/versioned_model/{version}",
            metrics={"accuracy": 0.9 + float(version.split(".")[0]) * 0.02}
        )
        test_db.add(model)
        models.append(model)
    test_db.commit()
    return models


@pytest.fixture
def multiple_metrics(test_db: Session, sample_run: Run) -> list[Metrics]:
    """
    Create multiple metrics for testing.
    
    Args:
        test_db: Test database session
        sample_run: Sample run
    
    Returns:
        list[Metrics]: List of test metrics
    """
    metrics_list = []
    metric_names = ["accuracy", "precision", "recall", "f1_score", "auc"]
    
    for name in metric_names:
        metrics = Metrics(
            name=name,
            value=0.85 + (metric_names.index(name) * 0.02),
            run_id=sample_run.id,
            tags={"model": "test"}
        )
        test_db.add(metrics)
        metrics_list.append(metrics)
    test_db.commit()
    return metrics_list


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def api_headers() -> dict:
    """
    Provide common API headers for testing.
    
    Returns:
        dict: HTTP headers
    """
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


@pytest.fixture
def valid_pipeline_payload() -> dict:
    """
    Provide a valid pipeline creation payload.
    
    Returns:
        dict: API request payload
    """
    return {
        "name": "integration_test_pipeline",
        "description": "Pipeline for integration testing",
        "definition": {
            "nodes": [
                {"id": "load", "type": "data"},
                {"id": "train", "type": "training"}
            ],
            "edges": [{"from": "load", "to": "train"}]
        }
    }


@pytest.fixture
def valid_model_payload() -> dict:
    """
    Provide a valid model creation payload.
    
    Returns:
        dict: API request payload
    """
    return {
        "name": "integration_test_model",
        "version": "3.0.0",
        "stage": "dev",
        "path": "s3://models/test/3.0.0",
        "metrics": {"accuracy": 0.96, "f1_score": 0.93}
    }


@pytest.fixture
def valid_metrics_payload() -> dict:
    """
    Provide a valid metrics creation payload.
    
    Returns:
        dict: API request payload
    """
    return {
        "name": "custom_metric",
        "value": 0.88,
        "tags": {"dataset": "validation"}
    }
