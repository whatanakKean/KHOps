"""KHOps CLI - Command Line Interface"""

import asyncio
import json
import pickle
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import click
import pandas as pd
import requests
from rich.console import Console
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from khops.cli.models import models_cli
from khops.cli.monitor import monitor_cli
from khops.cli.pipeline import pipeline_cli
from khops.cli.projects import _read_project_state, projects_cli
from khops.core.config import settings
from khops.core.logging import setup_logging
from khops.db.session import SessionLocal
from khops.pipelines.executor import PipelineExecutor
from khops.pipelines.parser import PipelineParser
from khops.server.schemas.model import ModelCreate
from khops.server.services.model_service import ModelService

console = Console()

# Setup logging
setup_logging()


def _build_model(algorithm: str, y: pd.Series):
    algorithm = algorithm.lower()
    regression_algorithms = {
        "linear_regression",
        "linear",
        "random_forest_regressor",
        "rf_reg",
        "rf",
    }
    classification_algorithms = {
        "logistic_regression",
        "logistic",
        "random_forest",
        "rf",
        "decision_tree",
        "dt",
    }

    if algorithm in classification_algorithms:
        return (
            RandomForestClassifier(random_state=42)
            if algorithm in {"random_forest", "rf"}
            else LogisticRegression(max_iter=500)
        )
    if algorithm in regression_algorithms:
        return (
            RandomForestRegressor(random_state=42)
            if algorithm in {"random_forest_regressor", "rf_reg"}
            else LinearRegression()
        )

    return None


def _compute_metrics(y_true: pd.Series, y_pred: Any) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    is_classification = y_true.dtype == object or y_true.nunique() <= 10

    if is_classification:
        metrics["accuracy"] = float(accuracy_score(y_true, y_pred))
        metrics["precision"] = float(
            precision_score(y_true, y_pred, average="macro", zero_division=0)
        )
        metrics["recall"] = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    else:
        metrics["mse"] = float(mean_squared_error(y_true, y_pred))
        metrics["r2"] = float(r2_score(y_true, y_pred))

    return metrics


def _get_best_metric(metrics: dict[str, Any]) -> float:
    if "accuracy" in metrics:
        return metrics["accuracy"]
    if "f1" in metrics:
        return metrics["f1"]
    if "r2" in metrics:
        return metrics["r2"]
    if "mse" in metrics:
        return -metrics["mse"]
    return 0.0


@click.group()
@click.version_option(version="0.1.0", prog_name="khops")
def cli():
    """
    🚀 KHOps - High-Performance MLOps Platform

    Streamline the entire machine learning lifecycle from development to deployment.
    """
    pass


@cli.command()
@click.option(
    "--host",
    default=settings.SERVER_HOST,
    help="Server host address",
    show_default=True,
)
@click.option(
    "--port",
    default=settings.SERVER_PORT,
    type=int,
    help="Server port",
    show_default=True,
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload on code changes",
)
def server(host: str, port: int, reload: bool):
    """Start the KHOps API Server"""
    import uvicorn

    console.print(f"🚀 Starting KHOps Server at http://{host}:{port}", style="bold green")
    console.print(f"📚 API Docs: http://{host}:{port}/docs", style="dim")

    uvicorn.run(
        "khops.server.app:app",
        host=host,
        port=port,
        reload=reload,
    )


@cli.command()
@click.option(
    "--host",
    default=settings.MODEL_SERVER_HOST,
    help="Model server host address",
    show_default=True,
)
@click.option(
    "--port",
    default=settings.MODEL_SERVER_PORT,
    type=int,
    help="Model server port",
    show_default=True,
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload on code changes",
)
def model_server(host: str, port: int, reload: bool):
    """Start the dedicated model serving API"""
    import uvicorn

    console.print(f"🚀 Starting KHOps Model Server at http://{host}:{port}", style="bold green")
    console.print(f"📚 Model API Docs: http://{host}:{port}/docs", style="dim")

    uvicorn.run(
        "khops.server.serving_app:app",
        host=host,
        port=port,
        reload=reload,
    )


@cli.command()
@click.argument("pipeline_path", type=click.Path(exists=True))
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose output",
)
def run(pipeline_path: str, verbose: bool):
    """
    Execute a pipeline from a YAML configuration file

    Example:
        khops run examples/pipelines/sample_pipeline.yaml
    """
    console.print(f"⚙️  Executing pipeline: {pipeline_path}", style="bold blue")

    try:
        pipeline_config = PipelineParser.parse_yaml_file(pipeline_path)
        executor = PipelineExecutor(pipeline_config)
        result = executor.execute()

        if verbose:
            console.print("\n".join(result.logs.splitlines()), style="dim")

        console.print("✅ Pipeline execution finished.", style="bold green")
        console.print(f"Pipeline: {pipeline_config.name} v{pipeline_config.version}")
        console.print(f"Status: {result.status}")
        console.print(f"Nodes executed: {len(result.context)}")

        if result.meta:
            console.print(f"Summary: {result.meta}", style="yellow")

    except Exception as exc:
        console.print(f"❌ Pipeline execution failed: {exc}", style="bold red")
        raise click.Abort()


@cli.group()
def automl():
    """AutoML pipeline commands"""
    pass


@automl.command("run")
@click.argument("pipeline_path", type=click.Path(exists=True))
@click.option(
    "--algorithms",
    default="",
    help="Comma-separated list of algorithms for AutoML run",
)
def automl_run(pipeline_path: str, algorithms: str):
    """Run a simple AutoML workflow over pipeline definitions."""
    console.print(f"🤖 Starting AutoML run for: {pipeline_path}", style="bold blue")

    pipeline_config = PipelineParser.parse_yaml_file(pipeline_path)
    algorithms_list = [algo.strip() for algo in algorithms.split(",") if algo.strip()]
    if algorithms_list:
        best_score = float("-inf")
        best_result = None
        best_algorithm = None

        for algorithm in algorithms_list:
            console.print(f"Testing AutoML algorithm: {algorithm}")
            modified_config = pipeline_config.model_copy(deep=True)
            for node in modified_config.nodes:
                if node.type == "training":
                    node.params["algorithm"] = algorithm
            executor = PipelineExecutor(modified_config)
            result = executor.execute()
            metrics = result.get("meta", {}).get("metrics") or {}
            score = _get_best_metric(metrics)
            if score > best_score:
                best_score = score
                best_result = result
                best_algorithm = algorithm

        if best_result is None:
            console.print("⚠️  No valid AutoML candidates were found.", style="yellow")
            return

        console.print(
            f"✅ Best algorithm: {best_algorithm} with score {best_score}", style="bold green"
        )
        console.print(f"Status: {best_result.status}")
        if best_result.meta:
            console.print(f"Summary: {best_result.meta}", style="yellow")
    else:
        executor = PipelineExecutor(pipeline_config)
        result = executor.execute()
        console.print("✅ AutoML pipeline completed.", style="bold green")
        if result.meta:
            console.print(f"Summary: {result.meta}", style="yellow")


@cli.group()
def train():
    """Training and model creation commands"""
    pass


@train.command("start")
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--name", required=True, help="Model name")
@click.option("--version", default="1.0.0", help="Model version")
@click.option("--target", required=True, help="Target column name")
@click.option("--algorithm", default="random_forest", help="Algorithm to use")
@click.option(
    "--stage",
    default="dev",
    type=click.Choice(["dev", "staging", "production"]),
    help="Model stage",
)
@click.option("--save-path", default=None, help="Optional model artifact path")
def train_start(
    dataset_path: str,
    name: str,
    version: str,
    target: str,
    algorithm: str,
    stage: str,
    save_path: str | None,
):
    """Train a model from a dataset and register it."""
    console.print(f"🎯 Training model {name}@{version} using {algorithm}", style="bold blue")

    dataset_path = Path(dataset_path)
    if dataset_path.suffix.lower() == ".csv":
        df = pd.read_csv(dataset_path)
    elif dataset_path.suffix.lower() in {".json", ".ndjson"}:
        df = pd.read_json(dataset_path)
    else:
        console.print("❌ Unsupported dataset format. Use CSV or JSON.", style="bold red")
        raise click.Abort()

    if target not in df.columns:
        console.print(f"❌ Target column '{target}' not found in data.", style="bold red")
        raise click.Abort()

    X = df.drop(columns=[target])
    y = df[target]
    model = _build_model(algorithm, y)
    if model is None:
        console.print(f"❌ Unsupported algorithm: {algorithm}", style="bold red")
        raise click.Abort()

    model.fit(X, y)
    predictions = model.predict(X)
    metrics = _compute_metrics(y, predictions)

    selected_project = _read_project_state()
    if selected_project:
        console.print(
            f"📌 Using selected project: {selected_project.get('project_name')} (id={selected_project.get('project_id')})",
            style="dim",
        )

    model_dir = Path("models")
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = (
        Path(save_path)
        if save_path
        else model_dir / f"{name}_{version}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pkl"
    )
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    session = SessionLocal()
    try:
        service = ModelService(session)
        model_payload = ModelCreate(
            project_id=selected_project.get("project_id") if selected_project else None,
            name=name,
            version=version,
            stage=stage,
            path=str(model_path),
            metrics=metrics,
        )
        registered = asyncio.run(service.create(model_payload))
        console.print("✅ Model trained and registered successfully.", style="bold green")
        console.print(f"Model path: {registered.path}")
        console.print(f"Metrics: {registered.metrics}")
    finally:
        session.close()


@cli.group()
def models():
    """Model registry commands"""
    pass


@models.command("promote")
@click.argument("name")
@click.option("--version", required=True, help="Model version")
@click.option(
    "--stage",
    required=True,
    type=click.Choice(["dev", "staging", "production"]),
    help="Target promotion stage",
)
def promote(name: str, version: str, stage: str):
    """Promote a registered model to a new stage."""
    session = SessionLocal()
    try:
        service = ModelService(session)
        promoted = asyncio.run(service.promote(name, version, stage))
        if not promoted:
            console.print("❌ Model version not found.", style="bold red")
            raise click.Abort()
        console.print(f"✅ Promoted {name}@{version} to {stage}", style="bold green")
    finally:
        session.close()


@cli.group()
def api():
    """API generation and testing commands"""
    pass


@api.command("generate")
@click.option("--model", required=True, help="Model name")
@click.option("--version", default="latest", help="Model version to generate API for")
@click.option("--endpoint", default=None, help="Serving endpoint path")
def api_generate(model: str, version: str, endpoint: str | None):
    """Generate a simple serving API manifest for a registered model."""
    endpoint = endpoint or f"/api/v1/serve/{model}"
    api_dir = Path("models/api")
    api_dir.mkdir(parents=True, exist_ok=True)
    filename = api_dir / f"{model}_{version.replace('.', '_')}_api.json"
    manifest = {
        "model": model,
        "version": version,
        "endpoint": endpoint,
        "method": "POST",
        "body": {"features": [{"feature1": 1.0, "feature2": 2.0}]},
        "server": f"http://localhost:{settings.MODEL_SERVER_PORT}",
    }
    filename.write_text(json.dumps(manifest, indent=2))
    console.print(f"✅ API manifest written to {filename}", style="bold green")


@api.command("test")
@click.option("--model", required=True, help="Model name")
@click.option("--version", default=None, help="Model version")
@click.option("--stage", default=None, help="Model stage")
@click.option("--endpoint", default=None, help="Serving endpoint override")
@click.option("--input", default="{}", help="JSON string input payload")
def api_test(model: str, version: str | None, stage: str | None, endpoint: str | None, input: str):
    """Test the model serving endpoint."""
    endpoint = endpoint or f"http://localhost:{settings.MODEL_SERVER_PORT}/api/v1/serve/{model}"
    try:
        payload = json.loads(input)
        if isinstance(payload, dict):
            payload = {"features": [payload]}
    except json.JSONDecodeError:
        console.print("❌ Invalid JSON input.", style="bold red")
        raise click.Abort()

    params = {}
    if version:
        params["version"] = version
    if stage:
        params["stage"] = stage

    response = requests.post(endpoint, json=payload, params=params)
    if response.status_code != 200:
        console.print(
            f"❌ Request failed: {response.status_code} {response.text}", style="bold red"
        )
        raise click.Abort()

    console.print("✅ Prediction response:", style="bold green")
    console.print(json.dumps(response.json(), indent=2))


@cli.group()
def config():
    """Manage KHOps configuration"""
    pass


@config.command()
def show():
    """Display current configuration"""
    console.print("⚙️  KHOps Configuration", style="bold blue")
    console.print(json.dumps(settings.model_dump(), indent=2), style="dim")


@cli.group()
def logs():
    """View logs and monitoring data"""
    pass


@logs.command()
@click.option("-f", "--follow", is_flag=True, help="Follow log output")
def tail(follow: bool):
    """Tail application logs"""
    console.print("📋 Application Logs", style="bold blue")
    console.print("[*] Log viewing coming soon!", style="dim yellow")


@cli.command()
def status():
    """Check KHOps system status"""
    console.print("🔍 KHOps System Status", style="bold blue")
    console.print("[*] Status check coming soon!", style="dim yellow")


@cli.command()
def init():
    """Initialize a new KHOps project"""
    console.print("🎯 Initializing KHOps Project", style="bold blue")
    Path("pipelines").mkdir(exist_ok=True)
    Path("models").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    Path("scripts").mkdir(exist_ok=True)
    console.print("✅ Project initialized successfully!", style="bold green")
    console.print("\nExample files:")
    console.print("  📁 pipelines/    - Pipeline definitions")
    console.print("  📁 models/       - Trained models")
    console.print("  📁 data/         - Datasets and artifacts")
    console.print("  📁 scripts/      - Custom scripts")


# Add subcommand groups
cli.add_command(models_cli, name="models")
cli.add_command(monitor_cli, name="monitor")
cli.add_command(projects_cli, name="project")
cli.add_command(pipeline_cli, name="pipeline")


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n❌ Interrupted by user", style="bold red")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Error: {str(e)}", style="bold red")
        sys.exit(1)
