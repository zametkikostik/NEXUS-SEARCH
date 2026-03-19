'use client'

import '@rainbow-me/rainbowkit/styles.css'
import { getDefaultConfig, RainbowKitProvider } from '@rainbow-me/rainbowkit'
import { WagmiProvider } from 'wagmi'
import { mainnet, sepolia, polygon, localhost } from 'wagmi/chains'
import { QueryClientProvider, QueryClient } from "@tanstack/react-query"
import { ReactNode, useState } from 'react'

const config = getDefaultConfig({
  appName: 'NEXUS Search',
  projectId: process.env.NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID || 'nexus-search',
  chains: [
    mainnet,
    sepolia,
    polygon,
    localhost,
  ],
  ssr: true,
})

const queryClient = new QueryClient()

export function Web3Provider({ children }: { children: ReactNode }) {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>
          {children}
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  )
}
