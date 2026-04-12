"""Drift detection utilities for model observability."""

from typing import Any, Dict, List, Optional

from khops.db.models.metrics import Metrics


def detect_drift(metrics: List[Metrics], threshold: float = 0.5) -> Dict[str, Any]:
    """Detect drift signals from metrics using statistical methods."""
    drift_signals = []
    metric_values = {}

    for metric in metrics:
        name = metric.name.lower()
        if "drift" in name or "ks" in name or "distribution" in name:
            drift_signals.append(
                {
                    "metric": metric.name,
                    "value": metric.value,
                    "threshold": threshold,
                    "drift_detected": metric.value >= threshold,
                    "timestamp": metric.timestamp.isoformat() if metric.timestamp else None,
                }
            )

        # Collect values for statistical analysis
        base_name = metric.name.split(".")[0] if "." in metric.name else metric.name
        if base_name not in metric_values:
            metric_values[base_name] = []
        metric_values[base_name].append(metric.value)

    # Compute variance and trend statistics
    statistical_signals = []
    for name, values in metric_values.items():
        if len(values) > 5:
            variance = sum((x - sum(values) / len(values)) ** 2 for x in values) / len(values)
            if variance > threshold:
                statistical_signals.append(
                    {
                        "metric": name,
                        "variance": variance,
                        "type": "high_variance",
                        "drift_detected": True,
                    }
                )

    all_signals = drift_signals + statistical_signals
    return {
        "drift_count": sum(1 for s in all_signals if s.get("drift_detected")),
        "threshold": threshold,
        "signals": all_signals,
    }
