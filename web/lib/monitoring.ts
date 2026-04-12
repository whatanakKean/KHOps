import type { AlertItem, EventLog, LabelDistributionItem, LatencyBar, FeatureDrift, MonitoringMetric } from '@/types/monitoring';

export const monitoringMetrics: MonitoringMetric[] = [
  {
    id: 'inference-volume',
    title: 'Inference Volume',
    value: '2.4M',
    detail: '+12.4% vs last period',
    icon: 'analytics',
    trendClass: 'text-primary'
  },
  {
    id: 'p95-latency',
    title: 'P95 Latency',
    value: '142ms',
    detail: '+8ms spike detected',
    icon: 'speed',
    trendClass: 'text-error'
  },
  {
    id: 'drift-status',
    title: 'Drift Status',
    value: 'Moderate',
    detail: 'Psi: 0.18 (Warning at 0.2)',
    icon: 'warning',
    trendClass: 'text-on-tertiary-container'
  },
  {
    id: 'data-quality',
    title: 'Data Quality',
    value: '99.8%',
    detail: '0.02% null rate in feature_X',
    icon: 'fact_check',
    trendClass: 'text-primary'
  }
];

export const featureDriftData: FeatureDrift[] = [
  {
    id: 'user-credit-score',
    name: 'user_credit_score',
    statusLabel: 'KS: 0.042 (Stable)',
    statusClass: 'text-on-surface-variant',
    bars: [80, 90, 75, 95, 70, 25]
  },
  {
    id: 'account-age-months',
    name: 'account_age_months',
    statusLabel: 'KS: 0.198 (Critical)',
    statusClass: 'text-error',
    bars: [120, 80, 40, 20, 45]
  }
];

export const labelDistribution: LabelDistributionItem[] = [
  { id: 'approved', label: 'Class: Approved', value: '78.2%', change: '↑ 2.1%', changeClass: 'text-primary' },
  { id: 'rejected', label: 'Class: Rejected', value: '14.5%', change: '↓ 1.4%', changeClass: 'text-error' },
  { id: 'review', label: 'Class: Review', value: '6.8%', change: '0.0%', changeClass: 'text-on-surface-variant' },
  { id: 'fraud', label: 'Class: Fraud', value: '0.5%', change: '↑ 0.2%', changeClass: 'text-error' }
];

export const alerts: AlertItem[] = [
  {
    id: 'alert-01',
    level: 'critical',
    title: 'Inference Latency Spike',
    description: 'p99 exceeded 450ms for consecutive 5 minute window.',
    timestamp: '12m ago',
    primaryClass: 'bg-error',
    actionText: 'Investigate'
  },
  {
    id: 'alert-02',
    level: 'warning',
    title: 'Feature Drift Detected',
    description: "'account_age_months' drift score > 0.15 threshold.",
    timestamp: '2h ago',
    primaryClass: 'bg-tertiary',
    actionText: 'Review'
  },
  {
    id: 'alert-03',
    level: 'info',
    title: 'Baseline Updated',
    description: 'System automatically updated drift baseline for new region.',
    timestamp: '5h ago',
    primaryClass: 'bg-primary',
    actionText: 'Details'
  }
];

export const latencyBars: LatencyBar[] = [
  { id: 'bar-01', height: '10%', variant: 'primary' },
  { id: 'bar-02', height: '15%', variant: 'primary' },
  { id: 'bar-03', height: '30%', variant: 'primary' },
  { id: 'bar-04', height: '50%', variant: 'primary' },
  { id: 'bar-05', height: '80%', variant: 'primary' },
  { id: 'bar-06', height: '95%', variant: 'primary' },
  { id: 'bar-07', height: '85%', variant: 'primary' },
  { id: 'bar-08', height: '60%', variant: 'primary' },
  { id: 'bar-09', height: '40%', variant: 'primary' },
  { id: 'bar-10', height: '25%', variant: 'primary' },
  { id: 'bar-11', height: '15%', variant: 'primary' },
  { id: 'bar-12', height: '8%', variant: 'primary' },
  { id: 'bar-13', height: '12%', variant: 'error' },
  { id: 'bar-14', height: '18%', variant: 'error' },
  { id: 'bar-15', height: '10%', variant: 'error' },
  { id: 'bar-16', height: '5%', variant: 'error' }
];

export const liveEventStream: EventLog[] = [
  { id: 'event-01', severity: 'info', timestamp: '14:02:41', message: 'Inference successful: req_id=f920... pred=0.982' },
  { id: 'event-02', severity: 'info', timestamp: '14:02:43', message: 'Payload validated: features=12 schema=v2.1' },
  { id: 'event-03', severity: 'warn', timestamp: '14:02:45', message: 'Response latency (342ms) exceeds soft threshold (300ms)' },
  { id: 'event-04', severity: 'info', timestamp: '14:02:48', message: 'Inference successful: req_id=e110... pred=0.012' },
  { id: 'event-05', severity: 'info', timestamp: '14:02:50', message: 'Metric sync complete. Push to Prometheus.' }
];
