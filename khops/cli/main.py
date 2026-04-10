"""KHOps CLI - Command Line Interface"""

import sys
import click
from pathlib import Path
from rich.console import Console
from khops.core.logging import setup_logging

console = Console()

# Setup logging
setup_logging()


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
    default="0.0.0.0",
    help="Server host address",
    show_default=True,
)
@click.option(
    "--port",
    default=8000,
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
    console.print("📚 API Docs: http://localhost:8000/docs", style="dim")
    
    uvicorn.run(
        "khops.server.app:app",
        host=host,
        port=port,
        reload=reload,
    )


@cli.command()
@click.argument("pipeline_path", type=click.Path(exists=True))
@click.option(
    "-v", "--verbose",
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
    console.print("[*] Feature coming soon!", style="dim yellow")


@cli.command()
@click.argument("model_path", type=click.Path(exists=True))
@click.option(
    "-n", "--name",
    required=True,
    help="Model name in registry",
)
@click.option(
    "-v", "--version",
    default="1.0.0",
    help="Model version",
    show_default=True,
)
def register(model_path: str, name: str, version: str):
    """Register a trained model in the model registry"""
    console.print(f"📦 Registering model: {name}@v{version}", style="bold blue")
    console.print(f"   Path: {model_path}", style="dim")
    console.print("[*] Feature coming soon!", style="dim yellow")


@cli.group()
def config():
    """Manage KHOps configuration"""
    pass


@config.command()
def show():
    """Display current configuration"""
    console.print("⚙️  KHOps Configuration", style="bold blue")
    console.print("[*] Configuration management coming soon!", style="dim yellow")


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
    # Create example directories
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


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n❌ Interrupted by user", style="bold red")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Error: {str(e)}", style="bold red")
        sys.exit(1)
