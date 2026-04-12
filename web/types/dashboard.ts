export interface DashboardMetric {
  id: string;
  title: string;
  value: string;
  trendText: string;
  trendIcon: string;
  trendColor: string;
  icon: string;
  iconColor: string;
}

export interface ClusterStatus {
  id: string;
  name: string;
  tagline: string;
  load: string;
  status: string;
  iconColor: string;
  statusColor: string;
}

export interface Deployment {
  id: string;
  name: string;
  version: string;
  phase: string;
  badgeColor: string;
  timestamp: string;
  icon: string;
}

export interface UtilizationBar {
  label: string;
  primary: number;
  secondary: number;
  primaryColor: string;
  secondaryColor: string;
}

export interface UtilizationSeries {
  label: string;
  dotColor: string;
  bars: UtilizationBar[];
}

export interface DashboardData {
  metrics: DashboardMetric[];
  clusters: ClusterStatus[];
  deployments: Deployment[];
  utilization: UtilizationSeries[];
}
