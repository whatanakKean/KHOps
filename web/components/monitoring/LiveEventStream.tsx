import type { EventLog } from '@/types/monitoring';

interface LiveEventStreamProps {
  events: EventLog[];
}

const severityClass = {
  info: 'text-primary',
  warn: 'text-tertiary'
} as const;

export function LiveEventStream({ events }: LiveEventStreamProps) {
  return (
    <div className="glass-panel p-4 rounded-t-lg border-x border-t border-outline-variant/20 shadow-2xl">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
          <span className="text-[10px] font-bold tracking-widest uppercase">Live Event Stream</span>
        </div>
        <span className="material-symbols-outlined text-sm text-outline cursor-pointer">keyboard_arrow_down</span>
      </div>
      <div className="space-y-2 font-mono text-[10px] text-on-surface-variant h-32 overflow-hidden">
        {events.map(event => (
          <div key={event.id} className="flex gap-4">
            <span className={severityClass[event.severity]}>[{event.severity.toUpperCase()}]</span>
            <span className="text-outline">{event.timestamp}</span>
            <span>{event.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
