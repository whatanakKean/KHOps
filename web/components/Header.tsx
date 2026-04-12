export function Header() {
  return (
    <header className="flex justify-between items-center px-6 w-full sticky top-0 z-50 bg-[#1b1b1f] h-16 border-b border-outline-variant/10">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold text-[#e4e1e7] tracking-tighter font-headline">KHOps</h1>
        <div className="h-4 w-px bg-outline-variant/30" />
        <div className="flex items-center bg-surface-container-lowest px-3 py-1.5 rounded-lg">
          <span className="text-outline text-sm mr-2">🔎</span>
          <input
            className="bg-transparent border-none focus:ring-0 text-sm text-on-surface w-64 placeholder:text-outline/50"
            placeholder="Search architecture..."
            type="text"
          />
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-4 text-[#c4c6cc]">
          <button className="hover:text-[#4cd6fb] transition-colors duration-200 active:scale-95">🔔</button>
          <button className="hover:text-[#4cd6fb] transition-colors duration-200 active:scale-95">⚙️</button>
          <button className="hover:text-[#4cd6fb] transition-colors duration-200 active:scale-95">❔</button>
        </div>
        <div className="flex items-center gap-3 pl-4 border-l border-outline-variant/20">
          <div className="w-8 h-8 rounded-full bg-surface-container-highest" />
        </div>
      </div>
    </header>
  );
}
