"""Observability routes for metrics, drift, and alerts."""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from khops.server.dependencies import get_db
from khops.server.services.metrics_service import MetricsService
from khops.observability.metrics import summarize_metrics
from khops.observability.drift import detect_drift
from khops.observability.alerts import generate_alerts, send_alert_notification, batch_send_alerts
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/observability/summary")
async def observability_summary(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Return a summary of collected metrics and telemetry."""
    try:
        service = MetricsService(db)
        metrics, total = await service.list_metrics(skip=skip, limit=limit)
        return {
            "metric_count": total,
            "summary": summarize_metrics(metrics),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/observability/drift")
async def observability_drift(
    threshold: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
):
    """Return estimated drift signals based on model metrics."""
    try:
        service = MetricsService(db)
        metrics, _ = await service.list_metrics(skip=0, limit=1000)
        return detect_drift(metrics, threshold=threshold)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/observability/alerts")
async def observability_alerts(
    severity: Optional[str] = Query(None, description="Optional alert severity filter"),
    send_notifications: bool = Query(False, description="Whether to send alert notifications"),
    db: Session = Depends(get_db),
):
    """Return current alert conditions derived from metrics and optionally send notifications."""
    try:
        service = MetricsService(db)
        metrics, _ = await service.list_metrics(skip=0, limit=1000)
        alerts = generate_alerts(metrics, severity=severity)

        # Send notifications if requested
        if send_notifications and alerts:
            summary = batch_send_alerts(alerts)
            return {
                "alerts": alerts,
                "notification_summary": summary,
            }

        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/observability/alerts/send")
async def send_alerts(
    alert_severities: Optional[List[str]] = Query(None, description="Alert severity filter"),
    channels: Optional[List[str]] = Query(None, description="Notification channels"),
    db: Session = Depends(get_db),
):
    """Manually trigger alert notifications for current alert conditions."""
    try:
        service = MetricsService(db)
        metrics, _ = await service.list_metrics(skip=0, limit=1000)

        # Generate alerts
        all_alerts = generate_alerts(metrics)

        # Filter by severity if specified
        if alert_severities:
            alerts = [a for a in all_alerts if a.get("severity") in alert_severities]
        else:
            alerts = all_alerts

        # Send notifications
        if alerts:
            summary = batch_send_alerts(alerts, channels=channels)
            logger.info(f"Manual alert send triggered: {summary}")
            return {
                "message": f"Sent {summary['sent']} alerts, {summary['failed']} failed",
                "alerts_sent": summary["sent"],
                "alerts_failed": summary["failed"],
                "total_alerts": len(alerts),
            }
        else:
            return {
                "message": "No alerts matching criteria",
                "alerts_sent": 0,
                "alerts_failed": 0,
                "total_alerts": 0,
            }
    except Exception as e:
        logger.error(f"Error sending alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
