"""CLI commands for project management."""

import asyncio
import json
from pathlib import Path

import click
from rich.console import Console

from khops.db.session import SessionLocal
from khops.server.schemas.project import ProjectCreate
from khops.server.services.model_service import ModelService
from khops.server.services.project_service import ProjectService

console = Console()
PROJECT_STATE_FILE = Path(".khops_project")


def _write_project_state(data: dict[str, str]) -> None:
    PROJECT_STATE_FILE.write_text(json.dumps(data, indent=2))


def _read_project_state() -> dict[str, str] | None:
    if not PROJECT_STATE_FILE.exists():
        return None
    try:
        return json.loads(PROJECT_STATE_FILE.read_text())
    except Exception:
        return None


def _clear_project_state() -> None:
    if PROJECT_STATE_FILE.exists():
        PROJECT_STATE_FILE.unlink()


@click.group()
def projects_cli():
    """Project workspace commands."""
    pass


@projects_cli.command("create")
@click.argument("name")
@click.option("--description", default=None, help="Project description")
def create_project(name, description):
    """Create a new project."""
    session = SessionLocal()
    try:
        service = ProjectService(session)
        project = asyncio.run(service.create(ProjectCreate(name=name, description=description)))
        console.print(f"✅ Created project {project.name} (id={project.id})", style="bold green")
        _write_project_state({"project_id": project.id, "project_name": project.name})
        console.print(f"📌 Selected project {project.name} by default", style="dim")
    except Exception as exc:
        console.print(f"❌ Error creating project: {exc}", style="bold red")
    finally:
        session.close()


@projects_cli.command("list")
@click.option("--limit", default=20, type=int, help="Maximum number of projects to list")
def list_projects(limit):
    """List available projects."""
    session = SessionLocal()
    try:
        service = ProjectService(session)
        projects, total = asyncio.run(service.list_projects(skip=0, limit=limit))
        console.print("📁 Projects", style="bold blue")
        for project in projects:
            console.print(
                f"  {project.id} - {project.name}: {project.description or 'No description'}"
            )
        console.print(f"\nTotal: {total}")
    finally:
        session.close()


@projects_cli.command("select")
@click.argument("identifier")
def select_project(identifier):
    """Select the active project by id or name."""
    session = SessionLocal()
    try:
        service = ProjectService(session)
        project = None
        if identifier.isdigit():
            project = asyncio.run(service.get(int(identifier)))
        if not project:
            project = asyncio.run(service.get_by_name(identifier))

        if not project:
            console.print("❌ Project not found", style="bold red")
            return

        _write_project_state({"project_id": project.id, "project_name": project.name})
        console.print(f"✅ Selected project {project.name} (id={project.id})", style="bold green")
    finally:
        session.close()


@projects_cli.command("current")
def current_project():
    """Show the current selected project."""
    state = _read_project_state()
    if not state:
        console.print("No active project selected.", style="dim yellow")
        return
    console.print("📌 Current project", style="bold blue")
    console.print(f"  id: {state.get('project_id')}\n  name: {state.get('project_name')}")


@projects_cli.command("clear")
def clear_project():
    """Clear the active project selection."""
    if PROJECT_STATE_FILE.exists():
        _clear_project_state()
        console.print("✅ Project selection cleared.", style="bold green")
    else:
        console.print("No active project selection to clear.", style="dim yellow")
