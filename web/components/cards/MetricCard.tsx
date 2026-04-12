import type { DashboardMetric } from '@/types/dashboard';

interface MetricCardProps {
  metric: DashboardMetric;
}

export function MetricCard({ metric }: MetricCardProps) {
  return (
    <div className="bg-surface-container-low p-6 rounded-xl border-none flex flex-col justify-between">
      <div className="flex justify-between items-start">
        <span className="text-outline uppercase text-[10px] font-bold tracking-[0.2em]">{metric.title}</span>
        <span className={`text-lg ${metric.iconColor}`}>{metric.icon}</span>
      </div>
      <div className="mt-4">
        <span className="text-4xl font-headline font-bold text-on-surface">{metric.value}</span>
        <div className={`flex items-center gap-1 mt-1 text-xs ${metric.trendColor}`}>
          <span className="text-xs">{metric.trendIcon}</span>
          <span>{metric.trendText}</span>
        </div>
      </div>
    </div>
  );
}
