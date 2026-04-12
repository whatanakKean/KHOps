"""Pipeline execution service for background runs."""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from khops.db.session import SessionLocal
from khops.pipelines.executor import PipelineExecutionError, PipelineExecutor
from khops.pipelines.models import NodeType, PipelineConfig
from khops.pipelines.parser import PipelineParser
from khops.server.schemas.model import ModelCreate
from khops.server.schemas.run import RunUpdate
from khops.server.services.model_service import ModelService
from khops.server.services.run_service import RunService

logger = logging.getLogger(__name__)


class PipelineExecutionService:
    """Background execution manager for pipeline runs."""

    @staticmethod
    def execute_pipeline_background(
        pipeline_definition: dict,
        pipeline_id: int,
        run_id: int,
        project_id: Optional[int] = None,
    ) -> None:
        db: Session = SessionLocal()
        run_service = RunService(db)

        try:
            asyncio.run(
                run_service.update(
                    run_id,
                    RunUpdate(
                        status="running",
                        logs="Pipeline execution started.",
                        start_time=datetime.utcnow(),
                    ),
                )
            )

            config_data = (
                pipeline_definition.copy() if isinstance(pipeline_definition, dict) else {}
            )
            config_data.setdefault("name", f"pipeline_{run_id}")
            config_data.setdefault("version", "1.0")
            config_data.setdefault("description", "Executed pipeline")
            config = PipelineParser.parse_dict(config_data)
            executor = PipelineExecutor(config, run_id=run_id)
            result = executor.execute()

            registered_models = PipelineExecutionService._register_trained_models(
                config,
                executor,
                db,
                pipeline_id=pipeline_id,
                run_id=run_id,
                project_id=project_id,
            )
            if registered_models:
                result_meta = result.get("meta", {})
                result_meta["registered_models"] = registered_models
                result["meta"] = result_meta
                registration_logs = "\n".join(
                    f"Registered model {item['name']}@{item['version']} stage={item['stage']} id={item['id']}"
                    for item in registered_models
                )
                result_logs = f"{result['logs']}\n{registration_logs}"
            else:
                result_logs = result["logs"]

            asyncio.run(
                run_service.update(
                    run_id,
                    RunUpdate(
                        status="success",
                        logs=result_logs,
                        meta=result.get("meta"),
                        end_time=datetime.utcnow(),
                    ),
                )
            )
        except Exception as exc:
            error_message = f"Pipeline execution failed: {exc}"
            asyncio.run(
                run_service.update(
                    run_id,
                    RunUpdate(
                        status="failed",
                        logs=error_message,
                        meta={"error": str(exc)},
                        end_time=datetime.utcnow(),
                    ),
                )
            )
        finally:
            db.close()

    @staticmethod
    def _register_trained_models(
        config: PipelineConfig,
        executor: PipelineExecutor,
        db: Session,
        pipeline_id: int,
        run_id: int,
        project_id: Optional[int] = None,
    ) -> list[dict]:
        """Persist trained models found in a completed pipeline execution."""
        registered_models: list[dict] = []
        model_service = ModelService(db)

        for node in config.nodes:
            if node.type != NodeType.TRAINING:
                continue

            output = executor.context.get(node.id, {}) or {}
            if not output.get("trained") or not output.get("model_path"):
                continue

            model_name = str(node.params.get("model_name") or config.name)
            version = str(
                node.params.get("model_version") or node.params.get("version") or config.version
            )
            stage = str(node.params.get("stage", "dev"))
            path = str(output["model_path"])
            framework = node.params.get("framework", "sklearn")
            metadata = node.params.get("metadata")
            tags = node.params.get("tags")
            metrics = output.get("metrics") or {}

            payload = ModelCreate(
                name=model_name,
                version=version,
                stage=stage,
                project_id=project_id,
                pipeline_id=pipeline_id,
                run_id=run_id,
                path=path,
                framework=framework,
                metrics=metrics,
                metadata=metadata,
                tags=tags,
            )

            try:
                model = asyncio.run(model_service.create(payload))
                registered_models.append(
                    {
                        "id": model.id,
                        "name": model.name,
                        "version": model.version,
                        "stage": model.stage,
                        "path": model.path,
                        "metrics": model.metrics,
                    }
                )
            except Exception as exc:
                logger.warning(f"Failed to register trained model for node {node.id}: {exc}")

        return registered_models
