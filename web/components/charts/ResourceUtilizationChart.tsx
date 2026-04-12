import type { UtilizationSeries } from '@/types/dashboard';

interface ResourceUtilizationChartProps {
  utilization: UtilizationSeries[];
}

export function ResourceUtilizationChart({ utilization }: ResourceUtilizationChartProps) {
  return (
    <>
      <div className="flex justify-between items-center mb-8 relative z-10">
        <h3 className="font-headline font-bold text-xl">Resource Utilization</h3>
        <div className="flex gap-4">
          {utilization.map(series => (
            <div key={series.label} className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${series.dotColor}`} />
              <span className="text-xs text-outline">{series.label}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="h-64 flex items-end gap-3 relative z-10">
        {utilization[0].bars.map((bar, index) => (
          <div key={`${bar.label}-${index}`} className="flex-1 flex flex-col gap-1 justify-end h-full">
            <div className={`w-full rounded-t-sm ${bar.primaryColor}`} style={{ height: `${bar.primary}%` }} />
            <div className={`w-full rounded-b-sm ${bar.secondaryColor}`} style={{ height: `${bar.secondary}%` }} />
          </div>
        ))}
      </div>

      <div className="mt-4 grid grid-cols-7 text-center text-[10px] text-outline font-bold tracking-widest uppercase">
        {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => (
          <span key={day}>{day}</span>
        ))}
      </div>
    </>
  );
}
