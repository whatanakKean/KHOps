"""Alert generation utilities for observability."""

from typing import Any, Dict, List, Optional
from khops.db.models.metrics import Metrics
from khops.core.config import settings
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_alerts(metrics: List[Metrics], severity: Optional[str] = None) -> List[Dict[str, Any]]:
    """Generate active alerts from metric values."""
    alerts: List[Dict[str, Any]] = []

    for metric in metrics:
        name = metric.name.lower()
        if "error_rate" in name and metric.value >= 0.05:
            alerts.append(
                {
                    "severity": "critical",
                    "metric": metric.name,
                    "value": metric.value,
                    "message": "High error rate detected.",
                    "timestamp": metric.timestamp.isoformat() if metric.timestamp else None,
                }
            )
        elif "latency" in name and metric.value >= 1000:
            alerts.append(
                {
                    "severity": "warning",
                    "metric": metric.name,
                    "value": metric.value,
                    "message": "High latency observed.",
                    "timestamp": metric.timestamp.isoformat() if metric.timestamp else None,
                }
            )
        elif "drift" in name and metric.value >= 0.5:
            alerts.append(
                {
                    "severity": "warning",
                    "metric": metric.name,
                    "value": metric.value,
                    "message": "Potential drift detected.",
                    "timestamp": metric.timestamp.isoformat() if metric.timestamp else None,
                }
            )

    if severity:
        result = [alert for alert in alerts if alert["severity"] == severity]
        return result

    return alerts


def send_alert_notification(alert: Dict[str, Any], channels: Optional[List[str]] = None) -> bool:
    """Send alert notification through configured channels (email, webhook, etc).

    Args:
        alert: Alert dictionary with severity, metric, value, message, timestamp
        channels: List of channels to send to (email, webhook). Defaults to configured channels.

    Returns:
        True if sending succeeded, False otherwise
    """
    if channels is None:
        channels = getattr(settings, "ALERT_CHANNELS", [])

    if not channels:
        logger.debug(
            f"No alert channels configured, skipping notification for {alert.get('metric')}"
        )
        return False

    success = True
    for channel in channels:
        try:
            if channel == "email":
                success &= _send_email_alert(alert)
            elif channel == "webhook":
                success &= _send_webhook_alert(alert)
            elif channel == "slack":
                success &= _send_slack_alert(alert)
            else:
                logger.warning(f"Unknown alert channel: {channel}")
        except Exception as e:
            logger.error(f"Error sending {channel} alert: {str(e)}")
            success = False

    return success


def _send_email_alert(alert: Dict[str, Any]) -> bool:
    """Send email alert notification."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        smtp_server = getattr(settings, "SMTP_SERVER", None)
        smtp_port = getattr(settings, "SMTP_PORT", 587)
        smtp_user = getattr(settings, "SMTP_USER", None)
        smtp_password = getattr(settings, "SMTP_PASSWORD", None)
        alert_to_email = getattr(settings, "ALERT_EMAIL_TO", None)
        alert_from_email = getattr(settings, "ALERT_EMAIL_FROM", "khops@alerting.local")

        if not all([smtp_server, smtp_user, smtp_password, alert_to_email]):
            logger.warning("SMTP settings incomplete, skipping email alert")
            return False

        # Build email content
        subject = f"[{alert.get('severity', 'UNKNOWN').upper()}] KHOps Alert: {alert.get('metric')}"
        body = f"""
KHOps Alert Notification

Severity: {alert.get('severity', 'unknown').upper()}
Metric: {alert.get('metric')}
Value: {alert.get('value')}
Message: {alert.get('message')}
Timestamp: {alert.get('timestamp')}

---
This is an automated alert from KHOps Observability System.
"""

        msg = MIMEMultipart()
        msg["From"] = alert_from_email
        msg["To"] = alert_to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info(f"Email alert sent for metric: {alert.get('metric')}")
        return True
    except Exception as e:
        logger.error(f"Error sending email alert: {str(e)}")
        return False


def _send_webhook_alert(alert: Dict[str, Any]) -> bool:
    """Send webhook alert notification."""
    try:
        import requests

        webhook_url = getattr(settings, "ALERT_WEBHOOK_URL", None)
        if not webhook_url:
            logger.warning("Webhook URL not configured, skipping webhook alert")
            return False

        payload = {
            "severity": alert.get("severity"),
            "metric": alert.get("metric"),
            "value": alert.get("value"),
            "message": alert.get("message"),
            "timestamp": alert.get("timestamp"),
            "source": "khops-alerting",
        }

        response = requests.post(
            webhook_url, json=payload, timeout=10, headers={"Content-Type": "application/json"}
        )

        if response.status_code >= 400:
            logger.warning(f"Webhook alert failed: {response.status_code} {response.text}")
            return False

        logger.info(f"Webhook alert sent for metric: {alert.get('metric')}")
        return True
    except Exception as e:
        logger.error(f"Error sending webhook alert: {str(e)}")
        return False


def _send_slack_alert(alert: Dict[str, Any]) -> bool:
    """Send Slack alert notification."""
    try:
        import requests

        slack_webhook = getattr(settings, "SLACK_WEBHOOK_URL", None)
        if not slack_webhook:
            logger.warning("Slack webhook not configured, skipping Slack alert")
            return False

        # Color based on severity
        color_map = {"critical": "danger", "warning": "warning", "info": "good"}
        color = color_map.get(alert.get("severity", "info"), "good")

        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": f"KHOps Alert: {alert.get('metric')}",
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert.get("severity", "unknown"),
                            "short": True,
                        },
                        {"title": "Value", "value": str(alert.get("value")), "short": True},
                        {"title": "Message", "value": alert.get("message"), "short": False},
                        {
                            "title": "Timestamp",
                            "value": alert.get("timestamp", "unknown"),
                            "short": True,
                        },
                    ],
                }
            ]
        }

        response = requests.post(
            slack_webhook,
            json=payload,
            timeout=10,
        )

        if response.status_code >= 400:
            logger.warning(f"Slack alert failed: {response.status_code}")
            return False

        logger.info(f"Slack alert sent for metric: {alert.get('metric')}")
        return True
    except Exception as e:
        logger.error(f"Error sending Slack alert: {str(e)}")
        return False


def batch_send_alerts(
    alerts: List[Dict[str, Any]], channels: Optional[List[str]] = None
) -> Dict[str, int]:
    """Send multiple alerts and return summary.

    Args:
        alerts: List of alert dictionaries
        channels: List of channels to send to

    Returns:
        Dictionary with counts: {sent, failed}
    """
    sent = 0
    failed = 0

    for alert in alerts:
        if send_alert_notification(alert, channels):
            sent += 1
        else:
            failed += 1

    logger.info(f"Alert batch summary: {sent} sent, {failed} failed")
    return {"sent": sent, "failed": failed}
