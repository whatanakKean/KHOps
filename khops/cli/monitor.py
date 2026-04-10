"""CLI commands for monitoring and observability."""

import click
from rich.console import Console
from rich.table import Table
from khops.db.session import SessionLocal
from khops.server.services.metrics_service import MetricsService
from khops.observability.drift import detect_drift
from khops.observability.alerts import generate_alerts

console = Console()


def get_metrics_service():
    """Get metrics service with database session."""
    return MetricsService(SessionLocal())


@click.group()
def monitor_cli():
    """System monitoring and observability commands."""
    pass


@monitor_cli.command("status")
@click.option("--limit", default=20, type=int, help="Number of recent metrics")
def monitor_status(limit):
    """Show current system status and metrics."""
    console.print("📊 KHOps System Status", style="bold blue")

    service = get_metrics_service()
    try:
        metrics, total = asyncio.run(service.list_metrics(skip=0, limit=limit))

        table = Table(title="Recent Metrics")
        table.add_column("Name", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_column("Timestamp", style="green")

        for metric in metrics:
            table.add_row(
                metric.name,
                str(metric.value),
                metric.timestamp.isoformat() if metric.timestamp else "N/A",
            )

        console.print(table)
        console.print(f"\nTotal metrics collected: {total}")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
    finally:
        service.db.close()


@monitor_cli.command("drift")
@click.option("--threshold", default=0.5, type=float, help="Drift detection threshold")
def monitor_drift(threshold):
    """Detect and report model drift."""
    console.print(f"🔍 Model Drift Detection (threshold: {threshold})", style="bold blue")

    service = get_metrics_service()
    try:
        metrics, _ = asyncio.run(service.list_metrics(skip=0, limit=1000))
        drift_info = detect_drift(metrics, threshold=threshold)

        if drift_info["drift_count"] > 0:
            console.print(
                f"⚠️  Drift detected in {drift_info['drift_count']} metrics", style="yellow"
            )
            for signal in drift_info["signals"]:
                if signal["drift_detected"]:
                    console.print(f"  • {signal['metric']}: {signal['value']:.4f}")
        else:
            console.print("✅ No drift detected", style="bold green")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
    finally:
        service.db.close()


@monitor_cli.command("alerts")
@click.option(
    "--severity",
    default=None,
    type=click.Choice(["critical", "warning", "info"]),
    help="Filter by severity",
)
def monitor_alerts(severity):
    """Show active alerts and warnings."""
    console.print("🚨 System Alerts", style="bold blue")

    service = get_metrics_service()
    try:
        metrics, _ = asyncio.run(service.list_metrics(skip=0, limit=1000))
        alerts = generate_alerts(metrics, severity=severity)

        if not alerts:
            console.print("✅ No alerts", style="bold green")
        else:
            for alert in alerts:
                style = "bold red" if alert["severity"] == "critical" else "yellow"
                console.print(f"[{alert['severity'].upper()}] {alert['message']}", style=style)
                console.print(f"       {alert['metric']}: {alert['value']}", style="dim")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
    finally:
        service.db.close()


@monitor_cli.command("logs")
@click.option("--limit", default=50, type=int, help="Number of log lines to show")
@click.option("--follow", is_flag=True, help="Follow mode (not yet implemented)")
def monitor_logs(limit, follow):
    """View application logs."""
    console.print("📋 Application Logs", style="bold blue")
    if follow:
        console.print("[*] Follow mode not yet implemented", style="dim yellow")
    else:
        console.print(f"[*] Last {limit} log entries would be shown here", style="dim yellow")


import asyncio
