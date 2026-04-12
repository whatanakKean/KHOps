import type { MonitoringMetric } from '@/types/monitoring';

interface SummaryCardProps {
  metric: MonitoringMetric;
}

export function SummaryCard({ metric }: SummaryCardProps) {
  return (
    <div className="bg-surface-container-low p-6 rounded-lg relative overflow-hidden">
      <div className="absolute top-0 left-0 w-1 h-full bg-primary shadow-[4px_0_15px_rgba(76,214,251,0.3)]"></div>
      <div className="flex justify-between items-start mb-4">
        <span className="text-xs font-bold text-on-surface-variant tracking-wider uppercase">{metric.title}</span>
        <span className={`material-symbols-outlined text-xl ${metric.trendClass}`}>{metric.icon}</span>
      </div>
      <div className="text-3xl font-headline font-bold mb-1 text-on-surface">{metric.value}</div>
      <div className={`text-xs ${metric.trendClass} flex items-center gap-1`}>{metric.detail}</div>
    </div>
  );
}
