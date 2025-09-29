'use client';

import { useEffect, useState } from 'react';

async function enableMocking() {
  if (process.env.NODE_ENV !== 'development') {
    return;
  }

  const { worker } = await import('@/mocks/browser');
  return worker.start({
    onUnhandledRequest: 'bypass',
  });
}

export function MSWProvider({ children }: { children: React.ReactNode }) {
  const [mswReady, setMswReady] = useState(false);

  useEffect(() => {
    enableMocking().then(() => {
      setMswReady(true);
    });
  }, []);

  if (!mswReady) {
    return null;
  }

  return <>{children}</>;
}