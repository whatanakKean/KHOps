import type { ClusterStatus, DashboardData } from '@/types/dashboard';
import type { PipelineListResponse } from '@/types/pipeline';

const DEFAULT_BROWSER_API_BASE = '/api/v1';
const DEFAULT_SERVER_API_BASE = 'http://127.0.0.1:8000/api/v1';
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? (typeof window === 'undefined' ? DEFAULT_SERVER_API_BASE : DEFAULT_BROWSER_API_BASE);

async function fetcher<T>(path: string, init?: RequestInit): Promise<T> {
  const normalizedBase = API_BASE.endsWith('/') ? API_BASE.slice(0, -1) : API_BASE;
  const url = `${normalizedBase}${path}`;

  let response: Response;
  try {
    response = await fetch(url, {
      ...init,
      cache: 'no-store',
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers || {}),
      },
    });
  } catch (error) {
    throw new Error(`API request failed: ${url} - ${String(error)}`);
  }

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`API request failed: ${url} ${response.status} ${response.statusText} ${body}`);
  }

  return response.json() as Promise<T>;
}

export async function getPipelineList(skip = 0, limit = 50) {
  return fetcher<PipelineListResponse>(`/pipelines?skip=${skip}&limit=${limit}`);
}

export async function getObservabilitySummary(skip = 0, limit = 1000) {
  return fetcher<{ metric_count: number; summary: { total_metrics: number; latest_values: Record<string, unknown>; groups: Record<string, number> } }>(`/observability/summary?skip=${skip}&limit=${limit}`);
}

export async function getObservabilityDrift(threshold = 0.5) {
  return fetcher<{ drift_count: number; threshold: number; signals: Array<Record<string, unknown>> }>(`/observability/drift?threshold=${threshold}`);
}

export async function getObservabilityAlerts() {
  return fetcher<{ alerts: Array<Record<string, unknown>> }>(`/observability/alerts`);
}

function formatMetricValue(latest: Record<string, unknown>, keys: string[], defaultValue: string) {
  for (const key of keys) {
    if (latest[key] !== undefined && latest[key] !== null) {
      return String(latest[key]);
    }
  }
  return defaultValue;
}

export async function getDashboardData(): Promise<DashboardData> {
  const [pipelines, summaryResponse] = await Promise.all([getPipelineList(), getObservabilitySummary()]);

  const latest = summaryResponse.summary?.latest_values ?? {};
  const activePipelines = String(pipelines.total ?? 0);
  const meanAccuracy = formatMetricValue(latest, ['model.accuracy', 'accuracy', 'metrics.accuracy'], 'N/A');
  const avgLatency = formatMetricValue(latest, ['latency.p95', 'response.latency', 'average.latency', 'latency'], 'N/A');
  const computeCost = formatMetricValue(latest, ['compute.cost', 'cost', 'resource.cost'], '$0');

  const metrics = [
    {
      id: 'active-pipelines',
      title: 'Active Pipelines',
      value: activePipelines,
      trendText: `${pipelines.total ?? 0} pipelines available`,
      trendIcon: '▲',
      trendColor: 'text-primary',
      icon: '•',
      iconColor: 'text-primary',
    },
    {
      id: 'mean-accuracy',
      title: 'Mean Accuracy',
      value: meanAccuracy,
      trendText: 'Latest observed model score',
      trendIcon: '✔',
      trendColor: 'text-tertiary',
      icon: '•',
      iconColor: 'text-tertiary',
    },
    {
      id: 'avg-latency',
      title: 'Avg Latency',
      value: avgLatency,
      trendText: 'From observability telemetry',
      trendIcon: '–',
      trendColor: 'text-outline',
      icon: '•',
      iconColor: 'text-primary',
    },
    {
      id: 'compute-cost',
      title: 'Compute Cost',
      value: computeCost,
      trendText: 'Derived from runtime metrics',
      trendIcon: '▲',
      trendColor: 'text-error',
      icon: '•',
      iconColor: 'text-error',
    },
  ];

  const clusters: ClusterStatus[] = [
    {
      id: 'core-01',
      name: 'Core Cluster',
      tagline: 'Production Alpha',
      load: '88% Load',
      status: 'Healthy',
      iconColor: 'text-primary',
      statusColor: 'text-primary',
    },
    {
      id: 'edge-02',
      name: 'Edge Cluster',
      tagline: 'Staging Beta',
      load: '32% Load',
      status: 'Processing',
      iconColor: 'text-tertiary',
      statusColor: 'text-tertiary',
    },
  ];

  const deployments = [
    {
      id: 'deploy-01',
      name: 'BERT-Semantic-Optimizer',
      version: 'v2.4.12-rc',
      phase: 'CANARY',
      badgeColor: 'bg-tertiary/10 text-on-tertiary-container',
      timestamp: '2 mins ago',
      icon: '🚀',
    },
    {
      id: 'deploy-02',
      name: 'Vision-Transformer-Edge',
      version: 'v1.9.0-stable',
      phase: 'PRODUCTION',
      badgeColor: 'bg-primary/10 text-on-primary-container',
      timestamp: '45 mins ago',
      icon: '🚀',
    },
    {
      id: 'deploy-03',
      name: 'RNN-Forecasting-Old',
      version: 'v0.8.2-legacy',
      phase: 'Decommissioned',
      badgeColor: 'bg-surface-container-highest text-outline uppercase',
      timestamp: '3 hours ago',
      icon: '⏳',
    },
  ];

  const utilization = [
    {
      label: 'GPU',
      dotColor: 'bg-primary',
      bars: [
        { label: 'Mon', primary: 60, secondary: 20, primaryColor: 'bg-primary/20', secondaryColor: 'bg-tertiary/20' },
        { label: 'Tue', primary: 45, secondary: 35, primaryColor: 'bg-primary/40', secondaryColor: 'bg-tertiary/30' },
        { label: 'Wed', primary: 75, secondary: 15, primaryColor: 'bg-primary/30', secondaryColor: 'bg-tertiary/20' },
        { label: 'Thu', primary: 50, secondary: 40, primaryColor: 'bg-primary/60', secondaryColor: 'bg-tertiary/20' },
        { label: 'Fri', primary: 90, secondary: 5, primaryColor: 'bg-primary/80', secondaryColor: 'bg-tertiary/50' },
        { label: 'Sat', primary: 65, secondary: 25, primaryColor: 'bg-primary', secondaryColor: 'bg-tertiary' },
        { label: 'Sun', primary: 40, secondary: 30, primaryColor: 'bg-primary/20', secondaryColor: 'bg-tertiary/20' },
      ],
    },
  ];

  return {
    metrics,
    clusters,
    deployments,
    utilization,
  };
}
