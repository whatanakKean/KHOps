import type { LatencyBar } from '@/types/monitoring';

interface LatencyHistogramProps {
  bars: LatencyBar[];
}

const variantStyles = {
  primary: 'bg-primary/20 hover:bg-primary',
  error: 'bg-error/40 hover:bg-error'
} as const;

export function LatencyHistogram({ bars }: LatencyHistogramProps) {
  return (
    <div className="col-span-12 bg-surface-container p-6 rounded-lg">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h3 className="text-lg font-headline font-bold">End-to-End Latency Histogram</h3>
          <p className="text-xs text-on-surface-variant mt-1">Measured from request arrival to finalized prediction response</p>
        </div>
        <div className="flex gap-2">
          <span className="px-2 py-1 bg-surface-container-highest rounded text-[10px] font-bold">MEAN: 112ms</span>
          <span className="px-2 py-1 bg-surface-container-highest rounded text-[10px] font-bold">P95: 142ms</span>
          <span className="px-2 py-1 bg-error/20 text-error rounded text-[10px] font-bold">P99: 384ms</span>
        </div>
      </div>
      <div className="h-48 flex items-end gap-1 px-4 relative">
        <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-5">
          <div className="border-b border-on-surface"></div>
          <div className="border-b border-on-surface"></div>
          <div className="border-b border-on-surface"></div>
          <div className="border-b border-on-surface"></div>
        </div>
        {bars.map(bar => (
          <div
            key={bar.id}
            className={`flex-1 rounded-t-sm transition-colors cursor-help ${variantStyles[bar.variant]}`}
            style={{ height: bar.height }}
          />
        ))}
      </div>
      <div className="flex justify-between mt-4 text-[10px] font-bold text-on-surface-variant tracking-widest border-t border-outline-variant/10 pt-4">
        <span>0ms</span>
        <span>50ms</span>
        <span>100ms</span>
        <span>150ms</span>
        <span>200ms</span>
        <span>250ms</span>
        <span className="text-error">Tail (300ms+)</span>
      </div>
    </div>
  );
}
