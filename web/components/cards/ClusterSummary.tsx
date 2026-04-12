import type { ClusterStatus } from '@/types/dashboard';

interface ClusterSummaryProps {
  clusters: ClusterStatus[];
}

export function ClusterSummary({ clusters }: ClusterSummaryProps) {
  return (
    <div className="bg-surface-container p-6 rounded-xl border-l-4 border-primary">
      <h3 className="font-headline font-bold text-lg mb-4">Core Clusters</h3>
      <div className="space-y-4">
        {clusters.map(cluster => (
          <div key={cluster.id} className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-surface-container-highest rounded-lg">
                <span className={`text-sm ${cluster.iconColor}`}>•</span>
              </div>
              <div>
                <p className="text-sm font-medium">{cluster.name}</p>
                <p className="text-xs text-outline">{cluster.tagline}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm font-bold">{cluster.load}</p>
              <p className={`text-[10px] uppercase font-bold tracking-tighter ${cluster.statusColor}`}>{cluster.status}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
