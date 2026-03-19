'use client'

import { ConnectButton } from '@rainbow-me/rainbowkit'
import { Wallet } from 'lucide-react'

export function WalletConnect() {
  return (
    <ConnectButton.Custom>
      {({
        account,
        chain,
        openAccountModal,
        openChainModal,
        openConnectModal,
        mounted,
      }) => {
        const ready = mounted
        const connected = ready && account && chain

        return (
          <div
            {...(!ready && {
              'aria-hidden': true,
              style: {
                opacity: 0,
              },
            })}
          >
            {(() => {
              if (!connected) {
                return (
                  <button
                    onClick={openConnectModal}
                    className="btn-primary flex items-center gap-2"
                    type="button"
                  >
                    <Wallet className="w-5 h-5" />
                    <span>Connect</span>
                  </button>
                )
              }

              if (chain.unsupported) {
                return (
                  <button
                    onClick={openChainModal}
                    className="btn-secondary border-red-500 text-red-500"
                    type="button"
                  >
                    Wrong network
                  </button>
                )
              }

              return (
                <div className="flex items-center gap-2">
                  {chain.hasIcon && (
                    <button
                      onClick={openChainModal}
                      className="btn-secondary text-sm hidden sm:flex items-center gap-2"
                      type="button"
                    >
                      <div
                        style={{
                          background: chain.iconBackground,
                          width: 12,
                          height: 12,
                          borderRadius: 999,
                          overflow: 'hidden',
                        }}
                      >
                        {chain.iconUrl && (
                          <img
                            alt={chain.name ?? 'Chain icon'}
                            src={chain.iconUrl}
                            style={{ width: 12, height: 12 }}
                          />
                        )}
                      </div>
                      <span>{chain.name}</span>
                    </button>
                  )}

                  <button 
                    onClick={openAccountModal} 
                    className="btn-secondary text-sm font-mono"
                    type="button"
                  >
                    {account.displayName}
                    {account.displayBalance
                      ? ` (${account.displayBalance})`
                      : ''}
                  </button>
                </div>
              )
            })()}
          </div>
        )
      }}
    </ConnectButton.Custom>
  )
}
