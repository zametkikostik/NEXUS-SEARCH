'use client'

import { Provider } from 'zustand'

export function StoreProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
