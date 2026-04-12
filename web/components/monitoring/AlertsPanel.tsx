import type { AlertItem } from '@/types/monitoring';

interface AlertsPanelProps {
  alerts: AlertItem[];
}

const statusClasses = {
  critical: 'text-error',
  warning: 'text-tertiary',
  info: 'text-primary'
} as const;

export function AlertsPanel({ alerts }: AlertsPanelProps) {
  return (
    <div className="bg-surface-container p-6 rounded-lg h-full">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-headline font-bold">Recent Alerts</h3>
        <span className="material-symbols-outlined text-outline">history</span>
      </div>
      <div className="space-y-4">
        {alerts.map(alert => (
          <div key={alert.id} className="bg-surface-container-low p-4 rounded relative overflow-hidden group">
            <div className={`absolute left-0 top-0 bottom-0 w-1 ${alert.primaryClass}`}></div>
            <div className="flex justify-between items-start mb-2">
              <span className={`text-xs font-bold ${statusClasses[alert.level]}`}>{alert.level.toUpperCase()} ALERT</span>
              <span className="text-[10px] text-on-surface-variant font-label">{alert.timestamp}</span>
            </div>
            <p className="text-sm font-medium mb-1 text-on-surface">{alert.title}</p>
            <p className="text-xs text-on-surface-variant leading-relaxed">{alert.description}</p>
            {alert.level !== 'info' && (
              <div className="mt-3 flex gap-2">
                <button className="text-[10px] font-bold py-1 px-3 bg-error-container text-on-error-container rounded">{alert.actionText}</button>
                <button className="text-[10px] font-bold py-1 px-3 text-on-surface-variant border border-outline-variant/20 rounded">Mute</button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
