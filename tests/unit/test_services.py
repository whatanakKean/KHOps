"""
Unit tests for KHOps service layer.

Tests cover:
- Pipeline service (CRUD + list)
- Run service (CRUD + by_pipeline queries)
- Model service (CRUD + versioning + promotion)
- Metrics service (CRUD + by_run queries)
"""

import pytest
from sqlalchemy.orm import Session

# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio

from khops.db.models.metrics import Metrics
from khops.db.models.model import Model
from khops.db.models.pipeline import Pipeline
from khops.db.models.run import Run
from khops.server.schemas.metrics import MetricsCreate
from khops.server.schemas.model import ModelCreate, ModelUpdate
from khops.server.schemas.pipeline import PipelineCreate, PipelineUpdate
from khops.server.schemas.project import ProjectCreate
from khops.server.schemas.run import RunCreate, RunUpdate
from khops.server.services.metrics_service import MetricsService
from khops.server.services.model_service import ModelService
from khops.server.services.pipeline_service import PipelineService
from khops.server.services.project_service import ProjectService
from khops.server.services.run_service import RunService

# ============================================================================
# Pipeline Service Tests
# ============================================================================


class TestPipelineService:
    """Test PipelineService CRUD operations."""

    @pytest.fixture
    def service(self, test_db: Session) -> PipelineService:
        """Create pipeline service instance."""
        return PipelineService(test_db)

    async def test_create_pipeline(self, service: PipelineService):
        """Test pipeline creation."""
        payload = PipelineCreate(
            name="test_pipeline", description="Test pipeline", definition={"nodes": [], "edges": []}
        )

        pipeline = await service.create(payload)

        assert pipeline.id is not None
        assert pipeline.name == "test_pipeline"
        assert pipeline.description == "Test pipeline"

    async def test_get_pipeline(self, service: PipelineService, sample_pipeline: Pipeline):
        """Test getting a pipeline by ID."""
        pipeline = await service.get(sample_pipeline.id)

        assert pipeline is not None
        assert pipeline.id == sample_pipeline.id
        assert pipeline.name == sample_pipeline.name

    async def test_get_pipeline_not_found(self, service: PipelineService):
        """Test getting non-existent pipeline."""
        pipeline = await service.get(9999)

        assert pipeline is None

    async def test_get_all_pipelines(
        self, service: PipelineService, multiple_pipelines: list[Pipeline]
    ):
        """Test listing all pipelines."""
        pipelines = await service.get_all()

        assert len(pipelines) >= 5
        assert all(isinstance(p, Pipeline) for p in pipelines)

    async def test_get_all_with_pagination(
        self, service: PipelineService, multiple_pipelines: list[Pipeline]
    ):
        """Test pagination."""
        pipelines = await service.get_all(skip=0, limit=2)

        assert len(pipelines) <= 2

    async def test_update_pipeline(self, service: PipelineService, sample_pipeline: Pipeline):
        """Test updating a pipeline."""
        update = PipelineUpdate(description="Updated description")

        updated = await service.update(sample_pipeline.id, update)

        assert updated.description == "Updated description"

    async def test_delete_pipeline(self, service: PipelineService, sample_pipeline: Pipeline):
        """Test deleting a pipeline."""
        pipeline_id = sample_pipeline.id

        await service.delete(pipeline_id)

        deleted = await service.get(pipeline_id)
        assert deleted is None

    async def test_get_by_name(self, service: PipelineService, sample_pipeline: Pipeline):
        """Test getting pipeline by name."""
        pipeline = await service.get_by_name("sample_pipeline")

        assert pipeline is not None
        assert pipeline.name == "sample_pipeline"

    async def test_list_pipelines(
        self, service: PipelineService, multiple_pipelines: list[Pipeline]
    ):
        """Test list_pipelines with aggregation."""
        pipelines, total = await service.list_pipelines(skip=0, limit=10)

        assert total >= 5
        assert len(pipelines) >= 1


class TestProjectService:
    """Test ProjectService CRUD operations."""

    @pytest.fixture
    def service(self, test_db: Session) -> ProjectService:
        return ProjectService(test_db)

    async def test_create_project(self, service: ProjectService):
        payload = ProjectCreate(name="project_alpha", description="Alpha test project")
        project = await service.create(payload)

        assert project.id is not None
        assert project.name == "project_alpha"

    async def test_get_project_by_name(self, service: ProjectService):
        payload = ProjectCreate(name="project_beta", description="Beta project")
        project = await service.create(payload)

        fetched = await service.get_by_name("project_beta")

        assert fetched is not None
        assert fetched.id == project.id


# ============================================================================
# Run Service Tests
# ============================================================================


class TestRunService:
    """Test RunService CRUD operations."""

    @pytest.fixture
    def service(self, test_db: Session) -> RunService:
        """Create run service instance."""
        return RunService(test_db)

    async def test_create_run(self, service: RunService, sample_pipeline: Pipeline):
        """Test run creation."""
        payload = RunCreate(pipeline_id=sample_pipeline.id, status="pending")

        run = await service.create(payload)

        assert run.id is not None
        assert run.pipeline_id == sample_pipeline.id
        assert run.status == "pending"

    async def test_get_run(self, service: RunService, sample_run: Run):
        """Test getting a run by ID."""
        run = await service.get(sample_run.id)

        assert run is not None
        assert run.id == sample_run.id

    async def test_update_run(self, service: RunService, sample_run: Run):
        """Test updating a run."""
        update = RunUpdate(status="failed", logs="Updated logs")

        updated = await service.update(sample_run.id, update)

        assert updated.status == "failed"
        assert updated.logs == "Updated logs"

    async def test_delete_run(self, service: RunService, sample_run: Run):
        """Test deleting a run."""
        run_id = sample_run.id

        await service.delete(run_id)

        deleted = await service.get(run_id)
        assert deleted is None

    async def test_get_by_pipeline(
        self, service: RunService, sample_run: Run, sample_pipeline: Pipeline
    ):
        """Test getting runs by pipeline."""
        runs = await service.get_by_pipeline(sample_pipeline.id)

        assert len(runs) > 0
        assert all(r.pipeline_id == sample_pipeline.id for r in runs)

    async def test_list_runs(self, service: RunService, multiple_runs: list[Run]):
        """Test list_runs with pagination."""
        runs, total = await service.list_runs(skip=0, limit=10)

        assert total >= 1
        assert len(runs) >= 1


# ============================================================================
# Model Service Tests
# ============================================================================


class TestModelService:
    """Test ModelService CRUD and special operations."""

    @pytest.fixture
    def service(self, test_db: Session) -> ModelService:
        """Create model service instance."""
        return ModelService(test_db)

    async def test_create_model(self, service: ModelService):
        """Test model creation."""
        payload = ModelCreate(
            name="test_model",
            version="1.0.0",
            stage="dev",
            path="s3://models/test/1.0.0",
            metrics={"accuracy": 0.95},
        )

        model = await service.create(payload)

        assert model.id is not None
        assert model.name == "test_model"
        assert model.version == "1.0.0"

    async def test_get_model(self, service: ModelService, sample_model: Model):
        """Test getting a model by ID."""
        model = await service.get(sample_model.id)

        assert model is not None
        assert model.id == sample_model.id

    async def test_update_model(self, service: ModelService, sample_model: Model):
        """Test updating a model."""
        update = ModelUpdate(stage="production")

        updated = await service.update(sample_model.id, update)

        assert updated.stage == "production"

    async def test_update_model_metadata_maps_to_meta(
        self, service: ModelService, sample_model: Model
    ):
        """Test that metadata updates are mapped to the meta field."""
        update = ModelUpdate(metadata={"source": "unit_test", "format": "pickle"})

        updated = await service.update(sample_model.id, update)

        assert updated.meta == {"source": "unit_test", "format": "pickle"}
        assert getattr(updated, "metadata", None) is None

    async def test_delete_model(self, service: ModelService, sample_model: Model):
        """Test deleting a model."""
        model_id = sample_model.id

        await service.delete(model_id)

        deleted = await service.get(model_id)
        assert deleted is None

    async def test_get_by_name(self, service: ModelService, sample_model: Model):
        """Test getting latest model version by name."""
        model = await service.get_by_name("sample_model")

        assert model is not None
        assert model.name == "sample_model"

    async def test_get_versions(self, service: ModelService, multiple_models: list[Model]):
        """Test getting all versions of a model."""
        versions = await service.get_versions("versioned_model")

        assert len(versions) > 0
        assert all(m.name == "versioned_model" for m in versions)

    async def test_promote_model(self, service: ModelService, multiple_models: list[Model]):
        """Test promoting a model to a new stage."""
        # Get a model in dev stage
        initial = await service.get_by_name("versioned_model")
        assert initial.stage in ["dev", "staging", "production"]

        # Promote it
        promoted = await service.promote("versioned_model", initial.version, "staging")

        assert promoted.stage == "staging"
        assert promoted.api_port == 8002

    async def test_create_model_sets_api_port(self, service: ModelService):
        """Test model creation sets the proper API port for the stage."""
        payload = ModelCreate(
            name="api_port_model",
            version="1.0.0",
            stage="staging",
            path="s3://models/api_port_model/1.0.0",
            metrics={"accuracy": 0.96},
        )

        model = await service.create(payload)

        assert model.api_port == 8002
        assert model.stage == "staging"

    async def test_promote_model_updates_api_port(
        self, service: ModelService, multiple_models: list[Model]
    ):
        """Test promoting a model updates its API port to the target stage."""
        initial = await service.get_by_name("versioned_model")
        promoted = await service.promote("versioned_model", initial.version, "production")

        assert promoted.stage == "production"
        assert promoted.api_port == 8003


# ============================================================================
# Metrics Service Tests
# ============================================================================


class TestMetricsService:
    """Test MetricsService CRUD operations."""

    @pytest.fixture
    def service(self, test_db: Session) -> MetricsService:
        """Create metrics service instance."""
        return MetricsService(test_db)

    async def test_create_metrics(self, service: MetricsService, sample_run: Run):
        """Test metrics creation."""
        payload = MetricsCreate(
            name="test_metric", value=0.91, run_id=sample_run.id, tags={"type": "test"}
        )

        metrics = await service.create(payload)

        assert metrics.id is not None
        assert metrics.name == "test_metric"
        assert metrics.value == 0.91

    async def test_get_metrics(self, service: MetricsService, sample_metrics: Metrics):
        """Test getting metrics by ID."""
        metrics = await service.get(sample_metrics.id)

        assert metrics is not None
        assert metrics.id == sample_metrics.id

    async def test_get_by_run(
        self, service: MetricsService, sample_metrics: Metrics, sample_run: Run
    ):
        """Test getting metrics by run."""
        metrics = await service.get_by_run(sample_run.id)

        assert len(metrics) > 0
        assert all(m.run_id == sample_run.id for m in metrics)

    async def test_list_metrics(self, service: MetricsService, multiple_metrics: list[Metrics]):
        """Test list_metrics with pagination."""
        metrics, total = await service.list_metrics(skip=0, limit=10)

        assert total >= 1
        assert len(metrics) >= 1

    async def test_update_metrics(self, service: MetricsService, sample_metrics: Metrics):
        """Test updating metrics."""
        from khops.server.schemas.metrics import MetricsUpdate

        update = MetricsUpdate(value=0.99, tags={"updated": True})

        updated = await service.update(sample_metrics.id, update)

        assert updated.value == 0.99

    async def test_delete_metrics(self, service: MetricsService, sample_metrics: Metrics):
        """Test deleting metrics."""
        metrics_id = sample_metrics.id

        await service.delete(metrics_id)

        deleted = await service.get(metrics_id)
        assert deleted is None


# ============================================================================
# Service Integration Tests
# ============================================================================


class TestServiceIntegration:
    """Test services working together."""

    async def test_pipeline_run_relationship(
        self, test_db: Session, sample_pipeline: Pipeline, sample_run: Run
    ):
        """Test pipeline and run relationship."""
        pipeline_service = PipelineService(test_db)
        run_service = RunService(test_db)

        # Get pipeline and its runs
        pipeline = await pipeline_service.get(sample_pipeline.id)
        runs = await run_service.get_by_pipeline(pipeline.id)

        assert len(runs) > 0
        assert runs[0].pipeline_id == pipeline.id

    async def test_run_metrics_relationship(
        self, test_db: Session, sample_run: Run, sample_metrics: Metrics
    ):
        """Test run and metrics relationship."""
        run_service = RunService(test_db)
        metrics_service = MetricsService(test_db)

        # Get run and its metrics
        run = await run_service.get(sample_run.id)
        metrics = await metrics_service.get_by_run(run.id)

        assert len(metrics) > 0
        assert metrics[0].run_id == run.id
