'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { label: 'Dashboard', href: '/' },
  { label: 'Pipelines', href: '/pipelines' },
  { label: 'Registry', href: '/registry' },
  { label: 'Monitoring', href: '/monitoring' },
  { label: 'Experiments', href: '/experiments' }
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex flex-col fixed left-0 top-0 h-full py-8 bg-[#1b1b1f] w-64 z-50">
      <div className="px-6 mb-10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-primary to-on-primary-container flex items-center justify-center">
            <span className="text-on-primary text-xl">A</span>
          </div>
          <div>
            <h2 className="text-[#e4e1e7] font-headline font-bold tracking-tight">KHOps Architect</h2>
            <p className="text-[10px] uppercase tracking-widest text-outline">V0.84 Beta</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-2">
        {navItems.map(item => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.label}
              href={item.href}
              className={`group flex items-center gap-3 text-sm font-medium px-4 py-3 rounded-xl transition-all ${
                isActive ? 'bg-gradient-to-r from-[#4cd6fb]/10 to-transparent border-l-4 border-[#4cd6fb] text-[#4cd6fb]' : 'text-[#c4c6cc] hover:bg-[#1f1f23] hover:text-[#e4e1e7]'
              }`}
            >
              <span className="text-lg">•</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="px-4 mt-auto space-y-4">
        <button className="w-full py-3 rounded-lg bg-gradient-to-r from-primary to-on-primary-container text-on-primary font-bold text-sm shadow-lg shadow-primary/10 active:scale-95 transition-transform">
          Deploy Model
        </button>
        <div className="pt-4 space-y-1">
          <Link href="#" className="text-[#c4c6cc] px-4 py-2 flex items-center gap-3 text-sm font-medium hover:text-[#e4e1e7] transition-colors">
            <span className="text-sm">📘</span>
            Docs
          </Link>
          <Link href="#" className="text-[#c4c6cc] px-4 py-2 flex items-center gap-3 text-sm font-medium hover:text-[#e4e1e7] transition-colors">
            <span className="text-sm">↩</span>
            Logout
          </Link>
        </div>
      </div>
    </aside>
  );
}
