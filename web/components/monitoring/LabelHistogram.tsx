import type { LabelDistributionItem } from '@/types/monitoring';

interface LabelHistogramProps {
  labels: LabelDistributionItem[];
}

export function LabelHistogram({ labels }: LabelHistogramProps) {
  return (
    <div className="grid grid-cols-2 gap-4">
      {labels.map(item => (
        <div key={item.id} className="bg-surface-container-low p-4 rounded border border-outline-variant/10">
          <div className="text-xs text-on-surface-variant mb-1">{item.label}</div>
          <div className="flex items-center gap-2">
            <div className="text-lg font-bold">{item.value}</div>
            <span className={`text-[10px] ${item.changeClass}`}>{item.change}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
