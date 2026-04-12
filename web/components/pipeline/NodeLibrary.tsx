import type { PipelineSummary } from '@/types/pipeline';

interface NodeLibraryProps {
  pipelines: PipelineSummary[];
}

export function NodeLibrary({ pipelines }: NodeLibraryProps) {
  return (
    <div className="p-6 h-full flex flex-col justify-between">
      <div>
        <h3 className="headline text-lg font-bold text-on-surface mb-1">Node Library</h3>
        <p className="text-xs text-on-surface-variant mb-6">Drag components onto the canvas</p>

        <div className="space-y-6">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-primary mb-3 block">Data Operations</span>
            <div className="space-y-2">
              <div className="bg-surface-container p-3 rounded-xl cursor-grab hover:bg-surface-container-high transition-all flex items-center gap-3 border-l-2 border-[#deb7ff]">
                <span className="text-tertiary text-xl">🗄️</span>
                <span className="text-sm font-medium">Data Ingestion</span>
              </div>
              <div className="bg-surface-container p-3 rounded-xl cursor-grab hover:bg-surface-container-high transition-all flex items-center gap-3 border-l-2 border-[#deb7ff]">
                <span className="text-tertiary text-xl">🧹</span>
                <span className="text-sm font-medium">Preprocessing</span>
              </div>
            </div>
          </div>

          <div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-primary mb-3 block">Model Engine</span>
            <div className="space-y-2">
              <div className="bg-surface-container p-3 rounded-xl cursor-grab hover:bg-surface-container-high transition-all flex items-center gap-3 border-l-2 border-primary">
                <span className="text-primary text-xl">⚙️</span>
                <span className="text-sm font-medium">Training</span>
              </div>
              <div className="bg-surface-container p-3 rounded-xl cursor-grab hover:bg-surface-container-high transition-all flex items-center gap-3 border-l-2 border-primary">
                <span className="text-primary text-xl">✔️</span>
                <span className="text-sm font-medium">Validation</span>
              </div>
            </div>
          </div>

          <div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-primary mb-3 block">Orchestration</span>
            <div className="space-y-2">
              <div className="bg-surface-container p-3 rounded-xl cursor-grab hover:bg-surface-container-high transition-all flex items-center gap-3 border-l-2 border-on-primary-container">
                <span className="text-on-primary-container text-xl">☁️</span>
                <span className="text-sm font-medium">Deployment</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-10">
          <span className="text-[10px] font-bold uppercase tracking-widest text-primary mb-3 block">Backed Pipelines</span>
          <div className="space-y-2">
            {pipelines.length > 0 ? (
              pipelines.map((pipeline) => (
                <div key={pipeline.id} className="bg-surface-container p-3 rounded-xl border border-outline-variant/10 text-sm">
                  <div className="font-semibold text-on-surface">{pipeline.name}</div>
                  <div className="text-[10px] text-on-surface-variant uppercase tracking-wider">{pipeline.version}</div>
                </div>
              ))
            ) : (
              <div className="text-[10px] text-on-surface-variant">No pipeline definitions found.</div>
            )}
          </div>
        </div>
      </div>

      <div className="mt-6 p-6 bg-surface-container-lowest/80">
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-bold text-on-surface">Auto-Save</span>
          <div className="w-8 h-4 bg-primary/20 rounded-full relative">
            <div className="absolute right-1 top-1 w-2 h-2 bg-primary rounded-full" />
          </div>
        </div>
        <button className="w-full py-2 border border-outline-variant/30 rounded text-xs hover:bg-surface-container transition-colors">
          Clear Canvas
        </button>
      </div>
    </div>
  );
}
