export function InspectorPanel() {
  return (
    <div className="h-full flex flex-col">
      <div className="p-6 border-b border-outline-variant/10">
        <h3 className="headline text-lg font-bold text-on-surface">Node Inspector</h3>
        <div className="mt-4 flex items-center gap-2 p-2 bg-primary/5 rounded-lg border border-primary/20">
          <span className="text-primary">ℹ️</span>
          <span className="text-[11px] text-on-primary-container">Select a node to edit parameters</span>
        </div>
      </div>

      <div className="p-6 space-y-8 overflow-y-auto flex-1">
        <div>
          <div className="flex justify-between items-center mb-4">
            <span className="text-xs font-bold uppercase tracking-tighter text-on-surface-variant">Active Instance</span>
            <span className="bg-primary/10 text-primary text-[10px] px-2 py-0.5 rounded">ID: PR-092</span>
          </div>
          <div className="space-y-4">
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-on-surface-variant">Instance Name</label>
              <input className="w-full bg-surface-container-highest border-none focus:ring-1 focus:ring-primary rounded py-2 text-sm" type="text" defaultValue="Norm_Scaler_01" />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-on-surface-variant">Scaling Method</label>
              <select className="w-full bg-surface-container-highest border-none focus:ring-1 focus:ring-primary rounded py-2 text-sm">
                <option>StandardScaler</option>
                <option>MinMaxScaler</option>
                <option>RobustScaler</option>
              </select>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm">Handle Outliers</span>
              <div className="w-10 h-5 bg-primary rounded-full relative">
                <div className="absolute right-1 top-1 w-3 h-3 bg-on-primary rounded-full" />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-surface-container p-4 rounded-xl border-l-4 border-primary">
          <h4 className="text-xs font-bold mb-3">Live Distribution</h4>
          <div className="h-24 flex items-end gap-1 px-1">
            <div className="flex-1 bg-primary/20 h-8 rounded-t-sm" />
            <div className="flex-1 bg-primary/40 h-12 rounded-t-sm" />
            <div className="flex-1 bg-primary/60 h-20 rounded-t-sm" />
            <div className="flex-1 bg-primary h-16 rounded-t-sm" />
            <div className="flex-1 bg-primary/50 h-10 rounded-t-sm" />
            <div className="flex-1 bg-primary/20 h-4 rounded-t-sm" />
          </div>
          <div className="mt-2 flex justify-between text-[9px] text-on-surface-variant font-mono">
            <span>-3σ</span>
            <span>0</span>
            <span>+3σ</span>
          </div>
        </div>

        <div className="pt-4 space-y-3">
          <button className="w-full py-2.5 rounded bg-surface-container-highest text-sm font-bold border border-outline-variant/10 hover:bg-surface-variant transition-colors">Clone Instance</button>
          <button className="w-full py-2.5 rounded text-error text-sm font-bold border border-error/20 hover:bg-error/5 transition-colors">Delete Node</button>
        </div>
      </div>
    </div>
  );
}
