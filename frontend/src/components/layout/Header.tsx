'use client'

import Link from 'next/link'
import { useAccount, useDisconnect } from 'wagmi'
import { Wallet, Search, LogOut, User } from 'lucide-react'
import { WalletConnect } from './WalletConnect'

export default function Header() {
  const { address, isConnected } = useAccount()
  const { disconnect } = useDisconnect()

  return (
    <header className="sticky top-0 z-50 border-b border-dark-border bg-dark-bg/80 backdrop-blur-lg">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-nexus-400 to-nexus-600 flex items-center justify-center">
              <Search className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text hidden sm:block">NEXUS</span>
          </Link>
          
          {/* Navigation */}
          <nav className="flex items-center gap-4">
            <Link href="/search" className="text-gray-400 hover:text-white transition-colors">
              Поиск
            </Link>
            <Link href="/token" className="text-gray-400 hover:text-white transition-colors">
              Токен
            </Link>
            <Link href="/about" className="text-gray-400 hover:text-white transition-colors">
              О проекте
            </Link>
          </nav>
          
          {/* Wallet */}
          {isConnected ? (
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-dark-card border border-dark-border">
                <User className="w-4 h-4 text-nexus-400" />
                <span className="text-sm font-mono">
                  {address?.slice(0, 6)}...{address?.slice(-4)}
                </span>
              </div>
              <button
                onClick={() => disconnect()}
                className="p-2 rounded-lg bg-dark-card border border-dark-border hover:border-red-500 transition-colors"
                title="Disconnect"
              >
                <LogOut className="w-5 h-5 text-gray-400" />
              </button>
            </div>
          ) : (
            <WalletConnect />
          )}
        </div>
      </div>
    </header>
  )
}
