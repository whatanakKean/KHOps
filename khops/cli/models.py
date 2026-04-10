"""CLI commands for model management: promote, demote, rollback, retire."""

import click
import asyncio
from rich.console import Console
from khops.db.session import SessionLocal
from khops.server.services.model_service import ModelService
from khops.server.services.model_promotion_service import ModelPromotionService

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
@click.option("--limit", default=10, type=int, help="Number of models to list")
def list_models(stage, limit):
    """List registered models."""
    console.print("📦 Registered Models", style="bold blue")
    service = get_model_service()
    # Simple listing - in production would use async
    models = service.db.query(service.model).limit(limit).all()
    if stage:
        models = [m for m in models if m.stage == stage]

    for model in models:
        console.print(f"  {model.name}@{model.version} [{model.stage}]")
    console.print(f"\nTotal: {len(models)} models")


@models_cli.command("promote")
@click.argument("name")
@click.option("--version", required=True, help="Model version")
@click.option(
    "--stage",
    required=True,
    type=click.Choice(["dev", "staging", "production"]),
    help="Target stage",
)
@click.option("--reason", default=None, help="Promotion reason")
def promote_model(name, version, stage, reason):
    """Promote a model to a new stage."""
    console.print(f"🚀 Promoting {name}@{version} to {stage}", style="bold blue")
    service = get_model_service()
    try:
        promoted = asyncio.run(service.promote(name, version, stage, reason=reason))
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
