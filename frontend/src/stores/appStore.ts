import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SearchHistory {
  query: string
  timestamp: number
  results: number
}

interface AppState {
  // Search
  searchHistory: SearchHistory[]
  addToHistory: (query: string, results: number) => void
  clearHistory: () => void
  
  // Preferences
  defaultProviders: string[]
  setDefaultProviders: (providers: string[]) => void
  
  // Wallet
  lastConnectedWallet: string | null
  setLastConnectedWallet: (address: string | null) => void
  
  // UI
  darkMode: boolean
  toggleDarkMode: () => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Search
      searchHistory: [],
      addToHistory: (query, results) =>
        set((state) => ({
          searchHistory: [
            { query, timestamp: Date.now(), results },
            ...state.searchHistory.slice(0, 9),
          ],
        })),
      clearHistory: () => set({ searchHistory: [] }),
      
      // Preferences
      defaultProviders: ['google', 'duckduckgo', 'brave'],
      setDefaultProviders: (providers) => set({ defaultProviders: providers }),
      
      // Wallet
      lastConnectedWallet: null,
      setLastConnectedWallet: (address) => set({ lastConnectedWallet: address }),
      
      // UI
      darkMode: true,
      toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),
    }),
    {
      name: 'nexus-storage',
    }
  )
)
