import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import { MetricCard } from '@/components/cards/MetricCard';
import { ClusterSummary } from '@/components/cards/ClusterSummary';
import { DeploymentsTable } from '@/components/deployments/DeploymentsTable';
import { ResourceUtilizationChart } from '@/components/charts/ResourceUtilizationChart';
import { StatusWidget } from '@/components/StatusWidget';
import { getDashboardData } from '@/lib/api';

export default async function HomePage() {
  const { metrics, clusters, deployments, utilization } = await getDashboardData();

  return (
    <div>
      <Sidebar />
      <main className="min-h-screen ml-64">
        <Header />
        <section className="p-8 max-w-7xl mx-auto space-y-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h2 className="text-4xl font-headline font-bold text-on-surface tracking-tight">Executive Overview</h2>
            <p className="text-on-surface-variant mt-2 max-w-xl">Real-time heuristics and architectural health status for current active neural deployments.</p>
          </div>
          <div className="flex gap-3">
            <div className="bg-surface-container-low px-4 py-2 rounded-lg flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="text-sm font-medium text-on-surface">Live System Sync</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {metrics.map(metric => (
            <MetricCard key={metric.id} metric={metric} />
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-7 gap-6">
          <div className="lg:col-span-4 bg-surface-container p-8 rounded-xl relative overflow-hidden">
            <ResourceUtilizationChart utilization={utilization} />
          </div>
          <div className="lg:col-span-3 space-y-6">
            <ClusterSummary clusters={clusters} />
            <div className="glass-panel p-6 rounded-xl border border-outline-variant/10">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-headline font-bold">System Integrity</h3>
                <span className="text-xs font-bold text-primary px-2 py-0.5 bg-primary/10 rounded">99.9% UP</span>
              </div>
              <div className="grid grid-cols-12 gap-1 h-8">
                {Array.from({ length: 12 }).map((_, index) => (
                  <span key={index} className={`rounded-sm ${index % 4 === 0 ? 'bg-primary/40' : 'bg-primary'}`} />
                ))}
              </div>
              <p className="text-[10px] text-outline mt-3 leading-relaxed">Cross-region synchronization verified. Heartbeat latency at 4ms across all nodes.</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 bg-surface-container p-6 rounded-xl">
            <div className="flex justify-between items-center mb-6">
              <h3 className="font-headline font-bold text-xl">Recent Deployments</h3>
              <button className="text-sm text-primary font-medium hover:underline">View All</button>
            </div>
            <DeploymentsTable deployments={deployments} />
          </div>
          <StatusWidget />
        </div>
      </section>
    </main>
  </div>
  );
}
