import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Web3Provider } from '@/components/providers/Web3Provider'
import { StoreProvider } from '@/components/providers/StoreProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'NEXUS Search - Децентрализованная поисковая система',
  description: 'Privacy-first поисковая система с Web3 аутентификацией, IPFS хранением и токеномикой',
  keywords: ['search', 'decentralized', 'web3', 'privacy', 'ipfs', 'crypto'],
  authors: [{ name: 'NEXUS Search' }],
  openGraph: {
    title: 'NEXUS Search',
    description: 'Децентрализованная поисковая система нового поколения',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Web3Provider>
          <StoreProvider>
            {children}
          </StoreProvider>
        </Web3Provider>
      </body>
    </html>
  )
}
