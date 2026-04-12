export function PipelineCanvas() {
  return (
    <>
      <div className="absolute top-6 left-6 flex items-center gap-2 bg-surface-container-highest/80 backdrop-blur-xl p-2 rounded-xl shadow-2xl z-10">
        <button className="p-2 hover:bg-surface-container rounded transition-colors">➕</button>
        <button className="p-2 hover:bg-surface-container rounded transition-colors">➖</button>
        <div className="w-[1px] h-4 bg-outline-variant/30 mx-1" />
        <button className="p-2 hover:bg-surface-container rounded transition-colors">🎯</button>
        <div className="w-[1px] h-4 bg-outline-variant/30 mx-1" />
        <button className="p-2 hover:bg-surface-container rounded transition-colors">▶️</button>
      </div>

      <div className="min-w-full min-h-full p-20 relative">
        <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 1440 720" preserveAspectRatio="none">
          <path d="M 320 200 L 480 200" fill="none" stroke="#4cd6fb" strokeWidth="2" />
          <path d="M 680 200 L 840 250" fill="none" stroke="#4cd6fb" strokeDasharray="8 8" strokeWidth="2" />
          <path d="M 1040 250 L 1200 180" fill="none" stroke="#44474c" strokeWidth="2" />
        </svg>

        <div className="relative z-10 flex flex-wrap gap-x-40 gap-y-24 items-center">
          <div className="w-64 bg-surface-container-low rounded-xl overflow-hidden shadow-2xl ring-1 ring-outline-variant/10">
            <div className="bg-tertiary/10 p-3 flex justify-between items-center border-b border-outline-variant/10">
              <span className="text-[10px] font-bold text-tertiary tracking-widest uppercase">Input</span>
              <span className="text-tertiary text-lg">✔️</span>
            </div>
            <div className="p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-tertiary/20 rounded-lg">
                  <span className="text-tertiary text-xl">🗄️</span>
                </div>
                <div>
                  <h4 className="text-sm font-bold">PostgreSQL_Main</h4>
                  <p className="text-[10px] text-on-surface-variant">Data Ingestion</p>
                </div>
              </div>
              <div className="bg-surface-container-lowest p-2 rounded text-[10px] font-mono text-on-surface-variant">
                query: "SELECT * FROM training_set..."
              </div>
            </div>
          </div>

          <div className="w-64 bg-surface-container-low rounded-xl overflow-hidden shadow-2xl ring-2 ring-primary/40">
            <div className="bg-primary/10 p-3 flex justify-between items-center border-b border-outline-variant/10">
              <span className="text-[10px] font-bold text-primary tracking-widest uppercase">Processing</span>
              <div className="flex items-center gap-1">
                <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" />
                <span className="text-[10px] text-primary">Active</span>
              </div>
            </div>
            <div className="p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-primary/20 rounded-lg">
                  <span className="text-primary text-xl">🧹</span>
                </div>
                <div>
                  <h4 className="text-sm font-bold">Norm_Scaler_01</h4>
                  <p className="text-[10px] text-on-surface-variant">Preprocessing</p>
                </div>
              </div>
              <div className="space-y-2">
                <div className="h-1 bg-surface-container-highest rounded-full overflow-hidden">
                  <div className="h-full bg-primary w-2/3" />
                </div>
                <div className="flex justify-between text-[10px] text-on-surface-variant">
                  <span>Scaling rows...</span>
                  <span>67%</span>
                </div>
              </div>
            </div>
          </div>

          <div className="w-64 bg-surface-container-low rounded-xl overflow-hidden shadow-2xl ring-1 ring-outline-variant/10 opacity-60">
            <div className="bg-outline-variant/10 p-3 flex justify-between items-center border-b border-outline-variant/10">
              <span className="text-[10px] font-bold text-on-surface-variant tracking-widest uppercase">Compute</span>
              <span className="text-on-surface-variant text-lg">⏳</span>
            </div>
            <div className="p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-outline-variant/20 rounded-lg">
                  <span className="text-on-surface-variant text-xl">⚙️</span>
                </div>
                <div>
                  <h4 className="text-sm font-bold">XGBoost_Core</h4>
                  <p className="text-[10px] text-on-surface-variant">Training</p>
                </div>
              </div>
              <div className="flex items-center justify-center py-4 border-2 border-dashed border-outline-variant/20 rounded-lg">
                <span className="text-[10px] text-on-surface-variant">Awaiting features...</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="absolute bottom-6 right-6 flex items-center gap-4">
        <div className="bg-surface-container-highest/80 backdrop-blur-xl px-4 py-2 rounded-xl flex items-center gap-3 border border-outline-variant/10">
          <div className="flex -space-x-2">
            <div className="w-6 h-6 rounded-full border-2 border-surface-container-highest bg-[#1f1f23]" />
            <div className="w-6 h-6 rounded-full border-2 border-surface-container-highest bg-[#2a2a2e]" />
          </div>
          <span className="text-xs font-medium text-on-surface-variant">2 editors active</span>
        </div>
      </div>
    </>
  );
}
