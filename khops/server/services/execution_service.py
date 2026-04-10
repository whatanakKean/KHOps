"""Pipeline execution service for background runs."""

import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from khops.db.session import SessionLocal
from khops.pipelines.parser import PipelineParser
from khops.pipelines.executor import PipelineExecutor, PipelineExecutionError
from khops.server.schemas.run import RunUpdate
from khops.server.services.run_service import RunService


class PipelineExecutionService:
    """Background execution manager for pipeline runs."""

    @staticmethod
    def execute_pipeline_background(pipeline_definition: dict, run_id: int) -> None:
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
            executor = PipelineExecutor(config)
            result = executor.execute()

            asyncio.run(
                run_service.update(
                    run_id,
                    RunUpdate(
                        status="success",
                        logs=result["logs"],
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
