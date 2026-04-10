"""Observability utilities for metrics aggregation."""

from typing import Dict, Any, List
from khops.db.models.metrics import Metrics


def summarize_metrics(metrics: List[Metrics]) -> Dict[str, Any]:
    """Create a simple summary of metrics for observability dashboards."""
    summary = {
        "total_metrics": len(metrics),
        "latest_values": {},
        "groups": {},
    }

    for metric in metrics:
        name = metric.name
        if name not in summary["latest_values"] or metric.timestamp:
            summary["latest_values"][name] = metric.value

        group = name.split(".")[0] if "." in name else "default"
        summary["groups"].setdefault(group, 0)
        summary["groups"][group] += 1

    return summary
