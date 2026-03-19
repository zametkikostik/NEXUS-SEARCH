'use client'

import { useAccount, useSignMessage } from 'wagmi'
import { useCallback } from 'react'
import { authApi } from '@utils/api'

export function useWeb3Search() {
  const { address } = useAccount()
  const { signMessageAsync } = useSignMessage()

  const searchWithAuth = useCallback(async (
    query: string,
    options?: any
  ) => {
    if (!address) {
      throw new Error('Wallet not connected')
    }

    try {
      // Get message to sign
      const { message } = await authApi.getMessage(address)

      // Sign message
      const signature = await signMessageAsync({ message })

      // Verify and get token
      const { access_token } = await authApi.verify(address, message, signature)

      // Perform search with token
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/search?q=${encodeURIComponent(query)}`,
        {
          headers: {
            Authorization: `Bearer ${access_token}`,
          },
        }
      )

      return response.json()
    } catch (error) {
      console.error('Web3 search failed:', error)
      throw error
    }
  }, [address, signMessageAsync])

  return { searchWithAuth }
}
