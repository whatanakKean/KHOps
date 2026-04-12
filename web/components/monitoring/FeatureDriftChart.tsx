import type { FeatureDrift } from '@/types/monitoring';

interface FeatureDriftChartProps {
  features: FeatureDrift[];
}

export function FeatureDriftChart({ features }: FeatureDriftChartProps) {
  return (
    <div className="space-y-6">
      {features.map(feature => (
        <div key={feature.id} className="space-y-2">
          <div className="flex justify-between items-end">
            <span className="text-sm font-medium text-on-surface">{feature.name}</span>
            <span className={`text-xs ${feature.statusClass}`}>{feature.statusLabel}</span>
          </div>
          <div className="h-16 flex items-end gap-1">
            {feature.bars.map((height, index) => (
              <div key={index} className="flex-1 bg-surface-container-highest rounded-t-sm relative" style={{ height: `${height}%` }}>
                <div className={`absolute bottom-0 left-0 w-full h-full ${feature.statusClass.includes('error') ? 'bg-error' : 'bg-primary'} rounded-t-sm`} />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
