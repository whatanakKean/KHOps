export interface MonitoringMetric {
  id: string;
  title: string;
  value: string;
  detail: string;
  icon: string;
  trendClass: string;
}

export interface FeatureDrift {
  id: string;
  name: string;
  statusLabel: string;
  statusClass: string;
  bars: number[];
}

export interface LabelDistributionItem {
  id: string;
  label: string;
  value: string;
  change: string;
  changeClass: string;
}

export interface AlertItem {
  id: string;
  level: 'critical' | 'warning' | 'info';
  title: string;
  description: string;
  timestamp: string;
  primaryClass: string;
  actionText: string;
}

export interface LatencyBar {
  id: string;
  height: string;
  variant: 'primary' | 'error';
}

export interface EventLog {
  id: string;
  severity: 'info' | 'warn';
  timestamp: string;
  message: string;
}
