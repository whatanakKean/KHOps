"""CLI commands for pipeline management."""

import asyncio
from pathlib import Path

import click
import requests
from rich.console import Console

from khops.core.config import settings

console = Console()


@click.group()
def pipeline_cli():
    """Pipeline management commands."""
    pass


@pipeline_cli.command("list")
@click.option("--project-id", type=int, help="Filter by project ID")
@click.option("--limit", default=10, type=int, help="Number of pipelines to list")
def list_pipelines(project_id, limit):
    """List pipelines."""
    console.print("📋 Pipelines", style="bold blue")

    params = {"limit": limit}
    if project_id:
        params["project_id"] = project_id

    try:
        response = requests.get(
            f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/v1/pipelines", params=params
        )
        if response.status_code == 200:
            data = response.json()
            for pipeline in data["pipelines"]:
                console.print(f"  {pipeline['id']} - {pipeline['name']} v{pipeline['version']}")
            console.print(f"\nTotal: {data['total']}")
        else:
            console.print(f"❌ API Error: {response.status_code}", style="bold red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")


@pipeline_cli.command("create")
@click.argument("name")
@click.option("--description", default=None, help="Pipeline description")
@click.option("--yaml-file", type=click.Path(exists=True), help="YAML file to upload")
def create_pipeline(name, description, yaml_file):
    """Create a new pipeline."""
    console.print(f"📝 Creating pipeline: {name}", style="bold blue")

    if yaml_file:
        # Upload from YAML file
        try:
            with open(yaml_file, "r") as f:
                yaml_content = f.read()
            response = requests.post(
                f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/v1/pipelines/upload",
                json={"yaml_content": yaml_content},
            )
        except Exception as e:
            console.print(f"❌ Error reading file: {e}", style="bold red")
            return
    else:
        # Create basic pipeline
        pipeline_data = {
            "name": name,
            "description": description or "",
            "definition": {
                "name": name,
                "version": "1.0",
                "description": description or "",
                "nodes": [],
            },
        }
        response = requests.post(
            f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/v1/pipelines/create",
            json=pipeline_data,
        )

    if response.status_code == 200:
        pipeline = response.json()
        console.print(
            f"✅ Created pipeline {pipeline['name']} (id={pipeline['id']})", style="bold green"
        )
    else:
        console.print(f"❌ API Error: {response.status_code} - {response.text}", style="bold red")


@pipeline_cli.command("execute")
@click.argument("pipeline_id", type=int)
def execute_pipeline(pipeline_id):
    """Execute a pipeline."""
    console.print(f"⚙️  Executing pipeline ID: {pipeline_id}", style="bold blue")

    try:
        response = requests.post(
            f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/v1/pipelines/{pipeline_id}/execute"
        )
        if response.status_code == 200:
            data = response.json()
            console.print(f"✅ Pipeline execution started", style="bold green")
            console.print(f"  Run ID: {data['run_id']}")
        else:
            console.print(
                f"❌ API Error: {response.status_code} - {response.text}", style="bold red"
            )
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")


@pipeline_cli.command("versions")
@click.argument("pipeline_name")
@click.option("--project-id", type=int, help="Filter by project ID")
@click.option("--limit", default=10, type=int, help="Number of versions to list")
def get_pipeline_versions(pipeline_name, project_id, limit):
    """Get versions of a pipeline."""
    console.print(f"📋 Versions for pipeline: {pipeline_name}", style="bold blue")

    params = {"limit": limit}
    if project_id:
        params["project_id"] = project_id

    try:
        response = requests.get(
            f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/v1/pipelines/{pipeline_name}/versions",
            params=params,
        )
        if response.status_code == 200:
            versions = response.json()
            for version in versions:
                console.print(f"  {version['id']} - {version['name']} v{version['version']}")
        else:
            console.print(f"❌ API Error: {response.status_code}", style="bold red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
