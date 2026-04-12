"""CLI commands for model management: promote, demote, rollback, retire."""

import asyncio

import click
from rich.console import Console

from khops.db.session import SessionLocal
from khops.server.services.model_promotion_service import ModelPromotionService
from khops.server.services.model_service import ModelService

console = Console()


def get_model_service():
    """Get model service with database session."""
    return ModelService(SessionLocal())


@click.group()
def models_cli():
    """Model registry management commands."""
    pass


@models_cli.command("list")
@click.option("--stage", default=None, help="Filter by stage (dev, staging, production)")
@click.option("--project-id", type=int, help="Filter by project ID")
@click.option("--pipeline-id", type=int, help="Filter by pipeline ID")
@click.option("--limit", default=10, type=int, help="Number of models to list")
def list_models(stage, project_id, pipeline_id, limit):
    """List registered models."""
    console.print("📦 Registered Models", style="bold blue")
    service = get_model_service()
    try:
        models, total = asyncio.run(
            service.list_models(skip=0, limit=limit, project_id=project_id, pipeline_id=pipeline_id)
        )

        for model in models:
            if stage and model.stage != stage:
                continue
            pipeline_info = f" (pipeline: {model.pipeline_id})" if model.pipeline_id else ""
            console.print(f"  {model.name}@{model.version} [{model.stage}]{pipeline_info}")
        console.print(f"\nTotal: {total} models")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
    finally:
        service.db.close()


@models_cli.command("promote")
@click.argument("name")
@click.option("--version", required=True, help="Model version")
@click.option(
    "--stage",
    required=True,
    type=click.Choice(["dev", "staging", "production"]),
    help="Target stage",
)
@click.option("--pipeline-id", type=int, help="Pipeline ID for pipeline-scoped promotion")
@click.option("--project-id", type=int, help="Project ID for project-scoped promotion")
@click.option("--reason", default=None, help="Promotion reason")
def promote_model(name, version, stage, pipeline_id, project_id, reason):
    """Promote a model to a new stage."""
    console.print(f"🚀 Promoting {name}@{version} to {stage}", style="bold blue")
    service = get_model_service()
    try:
        promoted = asyncio.run(
            service.promote(
                name, version, stage, pipeline_id=pipeline_id, project_id=project_id, reason=reason
            )
        )
        if promoted:
            console.print(f"✅ Successfully promoted to {stage}", style="bold green")
        else:
            console.print("❌ Model version not found", style="bold red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
    finally:
        service.db.close()


@models_cli.command("demote")
@click.argument("name")
@click.option("--version", required=True, help="Model version")
@click.option("--stage", required=True, type=click.Choice(["dev", "staging"]), help="Target stage")
def demote_model(name, version, stage):
    """Demote a model to a lower stage."""
    console.print(f"⬇️  Demoting {name}@{version} to {stage}", style="bold blue")
    service = get_model_service()
    try:
        demoted = asyncio.run(service.promote(name, version, stage, reason="Demoted by user"))
        if demoted:
            console.print(f"✅ Successfully demoted to {stage}", style="bold green")
        else:
            console.print("❌ Model version not found", style="bold red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
    finally:
        service.db.close()


@models_cli.command("history")
@click.argument("name")
@click.option("--version", required=True, help="Model version")
def get_history(name, version):
    """Get promotion history for a model version."""
    console.print(f"📜 Promotion History for {name}@{version}", style="bold blue")
    service = get_model_service()
    try:
        model = (
            service.db.query(service.model)
            .filter(
                service.model.name == name,
                service.model.version == version,
            )
            .first()
        )

        if not model:
            console.print("❌ Model version not found", style="bold red")
            return

        promotions = model.promotions if hasattr(model, "promotions") else []
        if not promotions:
            console.print("No promotion history", style="dim yellow")
        else:
            for promo in promotions:
                console.print(f"  {promo.from_stage} → {promo.to_stage} ({promo.promoted_at})")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
    finally:
        service.db.close()
