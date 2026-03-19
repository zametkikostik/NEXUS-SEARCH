/**
 * API Client for NEXUS Search Backend
 * Works with both local and deployed backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_PREFIX = '/api/v1'

interface SearchResponse {
  query: string
  results: Array<{
    title: string
    url: string
    snippet: string
    source: string
    rank: number
    relevance_score?: number
  }>
  total: number
  providers_used: string[]
  time_ms: number
  cached?: boolean
  ipfs_cid?: string
}

interface AuthMessageResponse {
  address: string
  message: string
  expires_in: number
}

interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  address: string
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${API_PREFIX}${endpoint}`
  
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  }
  
  const response = await fetch(url, config)
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }))
    throw new Error(error.message || `HTTP ${response.status}`)
  }
  
  return response.json()
}

export const searchApi = {
  /**
   * Perform search
   */
  async search(
    query: string,
    options?: {
      providers?: string[]
      limit?: number
      timeout?: number
      cache?: boolean
      filterContent?: boolean
      storeIpfs?: boolean
    }
  ): Promise<SearchResponse> {
    const params = new URLSearchParams({ q: query })
    
    if (options?.providers) {
      params.append('providers', options.providers.join(','))
    }
    if (options?.limit) {
      params.append('limit', options.limit.toString())
    }
    if (options?.timeout) {
      params.append('timeout', options.timeout.toString())
    }
    if (options?.cache !== undefined) {
      params.append('cache_enabled', options.cache.toString())
    }
    if (options?.filterContent !== undefined) {
      params.append('filter_content', options.filterContent.toString())
    }
    if (options?.storeIpfs !== undefined) {
      params.append('store_ipfs', options.storeIpfs.toString())
    }
    
    return request<SearchResponse>(`/search?${params.toString()}`)
  },
  
  /**
   * Get available providers
   */
  async getProviders(): Promise<{ providers: string[]; status: Record<string, any> }> {
    return request(`/search/providers`)
  }
}

export const authApi = {
  /**
   * Get auth message to sign
   */
  async getMessage(address: string): Promise<AuthMessageResponse> {
    return request(`/auth/message?address=${address}`)
  },
  
  /**
   * Verify signature and get tokens
   */
  async verify(
    address: string,
    message: string,
    signature: string
  ): Promise<AuthResponse> {
    return request('/auth/verify', {
      method: 'POST',
      body: JSON.stringify({ address, message, signature }),
    })
  },
  
  /**
   * Refresh tokens
   */
  async refresh(refreshToken: string): Promise<AuthResponse> {
    return request(`/auth/refresh?refresh_token=${refreshToken}`)
  },
  
  /**
   * Logout
   */
  async logout(token: string): Promise<{ success: boolean }> {
    return request('/auth/logout', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  }
}

export const ipfsApi = {
  /**
   * Store data in IPFS
   */
  async store(data: any, pin = true): Promise<{ cid: string; gateway_url: string; size: number }> {
    return request('/ipfs/store', {
      method: 'POST',
      body: JSON.stringify({ data, pin }),
    })
  },
  
  /**
   * Retrieve data from IPFS
   */
  async retrieve(cid: string): Promise<any> {
    return request(`/ipfs/retrieve/${cid}`)
  },
  
  /**
   * Get IPFS stats
   */
  async getStats(): Promise<{ connected: boolean; version?: string }> {
    return request('/ipfs/stats')
  }
}

export const healthApi = {
  /**
   * Health check
   */
  async check(): Promise<{ status: string; services: Record<string, boolean> }> {
    return request('/health')
  },
  
  /**
   * Get providers status
   */
  async getProvidersStatus(): Promise<{ providers: any[]; total: number; healthy: number }> {
    return request('/providers')
  }
}

// Export API URL for direct use
export { API_URL }
