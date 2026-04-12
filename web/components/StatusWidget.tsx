'use client';

import { useState } from 'react';
import { useAutoRefresh } from '@/lib/hooks';

const statusStates = [
  { label: 'Stable', detail: 'No issues detected', badgeClass: 'bg-primary/10 text-primary' },
  { label: 'Review', detail: 'Drift signal requires validation', badgeClass: 'bg-tertiary/10 text-tertiary' }
];

export function StatusWidget() {
  const [statusIndex, setStatusIndex] = useState(0);
  const status = statusStates[statusIndex];

  useAutoRefresh(() => {
    setStatusIndex(prev => (prev + 1) % statusStates.length);
  }, 18000);

  return (
    <div className="bg-surface-container p-6 rounded-xl flex flex-col justify-between">
      <div>
        <h3 className="font-headline font-bold text-xl mb-1">Architecture Shift</h3>
        <p className="text-xs text-outline mb-6">Structural drift detected in core cluster</p>
        <div className="relative w-full aspect-square max-w-[200px] mx-auto">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            <circle className="text-surface-container-highest" cx="50" cy="50" fill="transparent" r="40" stroke="currentColor" strokeWidth="8" />
            <circle
              className="text-primary"
              cx="50"
              cy="50"
              fill="transparent"
              r="40"
              stroke="currentColor"
              strokeDasharray="251.2"
              strokeDashoffset="62.8"
              strokeWidth="8"
            />
            <circle
              className="text-tertiary"
              cx="50"
              cy="50"
              fill="transparent"
              r="40"
              stroke="currentColor"
              strokeDasharray="251.2"
              strokeDashoffset="180"
              strokeWidth="8"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold font-headline">76%</span>
            <span className="text-[8px] uppercase tracking-widest text-outline">Congruence</span>
          </div>
        </div>
      </div>

      <div className="mt-4 space-y-2">
        <div className="flex justify-between text-[10px] font-bold">
          <span className="text-primary uppercase">{status.label}</span>
          <span>{status.detail.split(' ')[0]}</span>
        </div>
        <div className="w-full bg-surface-container-highest h-1 rounded-full overflow-hidden">
          <div className="bg-primary h-full w-[45%]" />
        </div>
        <div className="text-[10px] text-outline">{status.detail}</div>
      </div>
    </div>
  );
}
