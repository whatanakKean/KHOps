'use client';

import { useEffect, useRef } from 'react';

export function useAutoRefresh(callback: () => void, interval: number = 10000) {
  const callbackRef = useRef(callback);

  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    const handle = setInterval(() => {
      callbackRef.current();
    }, interval);

    return () => clearInterval(handle);
  }, [interval]);
}
