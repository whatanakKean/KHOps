import type { Deployment } from '@/types/dashboard';

interface DeploymentsTableProps {
  deployments: Deployment[];
}

export function DeploymentsTable({ deployments }: DeploymentsTableProps) {
  return (
    <div className="space-y-1">
      {deployments.map(deployment => (
        <div key={deployment.id} className="grid grid-cols-12 items-center py-3 px-4 rounded-lg hover:bg-surface-container-highest transition-colors group">
          <div className="col-span-1 text-primary">{deployment.icon}</div>
          <div className="col-span-4">
            <p className="text-sm font-medium text-on-surface">{deployment.name}</p>
            <p className="text-[10px] text-outline uppercase font-bold tracking-tight">{deployment.version}</p>
          </div>
          <div className="col-span-3">
            <span className={`${deployment.badgeColor} text-[10px] px-2 py-1 rounded font-bold`}>{deployment.phase}</span>
          </div>
          <div className="col-span-3 text-right">
            <p className="text-xs text-on-surface">{deployment.timestamp}</p>
          </div>
          <div className="col-span-1 text-right text-outline group-hover:text-primary transition-colors cursor-pointer">⋮</div>
        </div>
      ))}
    </div>
  );
}
