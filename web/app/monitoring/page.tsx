import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import { SummaryCard } from '@/components/monitoring/SummaryCard';
import { FeatureDriftChart } from '@/components/monitoring/FeatureDriftChart';
import { LabelHistogram } from '@/components/monitoring/LabelHistogram';
import { AlertsPanel } from '@/components/monitoring/AlertsPanel';
import { LatencyHistogram } from '@/components/monitoring/LatencyHistogram';
import { LiveEventStream } from '@/components/monitoring/LiveEventStream';
import type { AlertItem, EventLog, LabelDistributionItem, LatencyBar } from '@/types/monitoring';
import { getObservabilityAlerts, getObservabilityDrift, getObservabilitySummary } from '@/lib/api';

export const metadata = {
  title: 'KHOps | Monitoring & Observability',
  description: 'Monitoring dashboard for model observability, drift analysis, and live event streaming.',
};

export default async function MonitoringPage() {
  const [summaryResponse, driftResponse, alertsResponse] = await Promise.all([
    getObservabilitySummary(),
    getObservabilityDrift(),
    getObservabilityAlerts(),
  ]);

  const latest = summaryResponse.summary?.latest_values ?? {};

  const monitoringMetrics = [
    {
      id: 'inference-volume',
      title: 'Inference Volume',
      value: String(latest['inference.volume'] ?? latest['requests.count'] ?? summaryResponse.metric_count ?? 'N/A'),
      detail: summaryResponse.metric_count ? `${summaryResponse.metric_count} metrics collected` : 'Live inference throughput',
      icon: 'analytics',
      trendClass: 'text-primary',
    },
    {
      id: 'p95-latency',
      title: 'P95 Latency',
      value: String(latest['latency.p95'] ?? latest['request.latency'] ?? 'N/A'),
      detail: 'Latest latency observation',
      icon: 'speed',
      trendClass: 'text-error',
    },
    {
      id: 'drift-status',
      title: 'Drift Status',
      value: `${driftResponse.drift_count} signals`,
      detail: `Threshold ${driftResponse.threshold}`,
      icon: 'warning',
      trendClass: 'text-on-tertiary-container',
    },
    {
      id: 'data-quality',
      title: 'Data Quality',
      value: String(latest['data.quality'] ?? latest['quality'] ?? '99.8%'),
      detail: 'Source distribution checks',
      icon: 'fact_check',
      trendClass: 'text-primary',
    },
  ];

  const rawAlerts = alertsResponse.alerts ?? [];

  const alerts: AlertItem[] = rawAlerts.map((alert, index) => {
    const severity = String((alert as any).severity ?? 'info');
    return {
      id: `alert-${index}`,
      level: severity === 'critical' ? 'critical' : severity === 'warning' ? 'warning' : 'info',
      title: String((alert as any).metric ?? 'Observability Alert'),
      description: String((alert as any).message ?? 'Review metric payload for details'),
      timestamp: String((alert as any).timestamp ?? 'unknown'),
      primaryClass: severity === 'critical' ? 'bg-error/40' : severity === 'warning' ? 'bg-tertiary/40' : 'bg-primary/20',
      actionText: severity === 'critical' ? 'Investigate' : 'Acknowledge',
    };
  });

  const driftFeatures = [
    {
      id: 'feature-drift',
      name: 'Drift signals',
      statusLabel: `${driftResponse.drift_count} detected`,
      statusClass: driftResponse.drift_count > 0 ? 'text-error' : 'text-primary',
      bars: driftResponse.signals.slice(0, 6).map((signal, index) => {
        const value = typeof signal.value === 'number' ? signal.value * 100 : 15 + index * 10;
        return Math.min(100, Math.max(10, value));
      }),
    },
  ];

  const labelDistribution: LabelDistributionItem[] = Object.entries(summaryResponse.summary?.groups ?? {}).map(([label, count], index) => ({
    id: `label-${index}`,
    label,
    value: String(count ?? 0),
    change: `${Math.round((Number(count) || 0) * 0.12)}%`,
    changeClass: 'text-primary',
  }));

  const latencyBars: LatencyBar[] = [
    Number(latest['latency.p50'] ?? latest['latency.p95'] ?? 120),
    Number(latest['latency.p75'] ?? 240),
    Number(latest['latency.p90'] ?? 340),
    Number(latest['latency.p95'] ?? 420),
    Number(latest['latency.p99'] ?? 520),
  ].map((value, index) => ({
    id: `latency-${index}`,
    height: `${Math.max(20, Math.min(100, Math.round(value / 4)))}%`,
    variant: index === 4 ? 'error' : 'primary',
  }));

  const liveEventStream: EventLog[] = rawAlerts.map((alert, index) => ({
    id: `event-${index}`,
    severity: String((alert as any).severity) === 'warning' ? 'warn' : 'info',
    timestamp: String((alert as any).timestamp ?? 'unknown'),
    message: String((alert as any).message ?? (alert as any).metric ?? 'Alert event'),
  }));

  return (
    <div>
      <Sidebar />
      <main className="min-h-screen ml-64">
        <Header />
        <div className="p-8 space-y-8 max-w-[1600px]">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="px-2 py-0.5 bg-tertiary-container text-on-tertiary-container text-[10px] font-bold rounded uppercase tracking-widest">Active Monitoring</span>
                <span className="text-on-surface-variant text-sm font-label">Production_v2.4_Stable</span>
              </div>
              <h2 className="text-3xl font-headline font-bold text-on-surface">Model Observability</h2>
            </div>
            <div className="flex gap-3">
              <div className="bg-surface-container-low px-4 py-2 rounded-md flex items-center gap-4">
                <span className="text-xs text-on-surface-variant font-label">TIME RANGE</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-primary">Last 24 Hours</span>
                  <span className="material-symbols-outlined text-sm text-outline">expand_more</span>
                </div>
              </div>
              <button className="bg-surface-container-high px-4 py-2 rounded-md text-sm font-bold hover:bg-surface-variant transition-colors border border-outline-variant/10">Export Report</button>
            </div>
          </div>

          <div className="grid grid-cols-12 gap-6">
            {monitoringMetrics.map((metric) => (
              <div key={metric.id} className="col-span-12 lg:col-span-3">
                <SummaryCard metric={metric} />
              </div>
            ))}

            <div className="col-span-12 lg:col-span-8 bg-surface-container p-6 rounded-lg">
              <div className="flex justify-between items-center mb-8">
                <h3 className="text-lg font-headline font-bold">Feature Drift Analysis</h3>
                <div className="flex items-center gap-4 text-[10px] font-bold tracking-widest uppercase">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-primary" /> Production
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-surface-container-highest border border-outline" /> Training
                  </div>
                </div>
              </div>
              <FeatureDriftChart features={driftFeatures} />
              <div className="mt-12">
                <h3 className="text-sm font-bold text-on-surface-variant uppercase mb-4 tracking-widest">Label Distribution (Pred vs Actual)</h3>
                <LabelHistogram labels={labelDistribution} />
              </div>
            </div>

            <div className="col-span-12 lg:col-span-4 space-y-6">
              <AlertsPanel alerts={alerts} />
            </div>

            <LatencyHistogram bars={latencyBars} />
          </div>

          <LiveEventStream events={liveEventStream} />
        </div>
      </main>
    </div>
  );
}
