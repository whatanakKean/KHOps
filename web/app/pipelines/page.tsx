import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import { NodeLibrary } from '@/components/pipeline/NodeLibrary';
import { PipelineCanvas } from '@/components/pipeline/PipelineCanvas';
import { InspectorPanel } from '@/components/pipeline/InspectorPanel';
import { getPipelineList } from '@/lib/api';

export const metadata = {
  title: 'Pipeline Designer | KHOps',
  description: 'Design and manage machine learning pipelines in the KHOps dashboard.',
};

export default async function PipelinePage() {
  const pipelineList = await getPipelineList();
  const pipelines = pipelineList.pipelines ?? [];

  return (
    <div>
      <Sidebar />
      <main className="min-h-screen ml-64">
        <Header />
        <div className="flex flex-col min-h-[calc(100vh-4rem)]">
          <div className="border-b border-outline-variant/10 bg-[#131317] px-6 py-4">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="text-2xl font-headline text-on-surface">KHOps</div>
                <div className="h-6 w-px bg-outline-variant/30" />
                <div className="flex items-center gap-2 text-sm text-on-surface-variant font-medium">
                  <span>folder_open</span>
                  <span>Project_Gamma_v2</span>
                </div>
              </div>
              <div className="hidden md:flex items-center bg-surface-container-lowest px-3 py-1.5 rounded-lg border border-outline-variant/10">
                <span className="text-on-surface-variant text-sm mr-2">🔎</span>
                <input className="bg-transparent border-none focus:ring-0 text-sm text-on-surface w-48 placeholder:text-outline/60" placeholder="Search pipeline nodes..." type="text" />
              </div>
            </div>
          </div>

          <div className="flex-1 flex overflow-hidden">
            <aside className="w-72 bg-surface-container-low border-r border-outline-variant/10">
              <NodeLibrary pipelines={pipelines} />
            </aside>
            <div className="flex-1 relative overflow-auto canvas-grid bg-surface">
              <PipelineCanvas />
            </div>
            <aside className="w-80 bg-surface-container-low border-l border-outline-variant/10">
              <InspectorPanel />
            </aside>
          </div>
        </div>
      </main>
    </div>
  );
}
