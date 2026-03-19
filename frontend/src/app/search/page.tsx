'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { Search, Filter, ExternalLink, Shield, Clock, Globe } from 'lucide-react'
import Header from '@components/layout/Header'
import Footer from '@components/layout/Footer'
import SearchBar from '@components/search/SearchBar'
import SearchResult from '@components/search/SearchResult'
import { searchApi } from '@utils/api'

interface SearchResult {
  title: string
  url: string
  snippet: string
  source: string
  rank: number
  relevance_score: number
}

export default function SearchPage() {
  const searchParams = useSearchParams()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchTime, setSearchTime] = useState(0)
  const [providers, setProviders] = useState<string[]>([])

  useEffect(() => {
    const q = searchParams.get('q')
    if (q) {
      setQuery(q)
      performSearch(q)
    }
  }, [searchParams])

  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      const startTime = Date.now()
      const data = await searchApi.search(searchQuery)
      
      setResults(data.results || [])
      setProviders(data.providers_used || [])
      setSearchTime(data.time_ms || 0)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = (newQuery: string) => {
    performSearch(newQuery)
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 py-8 px-4">
        <div className="max-w-5xl mx-auto">
          {/* Search Bar */}
          <div className="mb-8">
            <SearchBar 
              onSearch={handleSearch} 
              placeholder="Поиск..."
              size="md"
            />
          </div>
          
          {/* Loading State */}
          {isLoading && (
            <div className="text-center py-12">
              <div className="inline-block w-8 h-8 border-2 border-nexus-500 border-t-transparent rounded-full animate-spin" />
              <p className="mt-4 text-gray-400">Поиск в децентрализованной сети...</p>
            </div>
          )}
          
          {/* Error State */}
          {error && (
            <div className="card border-red-500/50 mb-6">
              <p className="text-red-400">{error}</p>
            </div>
          )}
          
          {/* Results */}
          {!isLoading && results.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-4"
            >
              {/* Stats */}
              <div className="flex items-center gap-4 text-sm text-gray-400 mb-6">
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {searchTime.toFixed(0)}ms
                </span>
                <span className="flex items-center gap-1">
                  <Globe className="w-4 h-4" />
                  {results.length} результатов
                </span>
                {providers.length > 0 && (
                  <span className="flex items-center gap-1">
                    <Shield className="w-4 h-4" />
                    {providers.join(', ')}
                  </span>
                )}
              </div>
              
              {/* Results List */}
              {results.map((result, index) => (
                <motion.div
                  key={result.url}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <SearchResult result={result} index={index + 1} />
                </motion.div>
              ))}
            </motion.div>
          )}
          
          {/* No Results */}
          {!isLoading && !error && results.length === 0 && query && (
            <div className="text-center py-12">
              <Search className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Ничего не найдено</h3>
              <p className="text-gray-400">Попробуйте другой запрос или провайдера</p>
            </div>
          )}
          
          {/* Welcome State */}
          {!isLoading && !query && (
            <div className="text-center py-12">
              <Search className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Начните поиск</h3>
              <p className="text-gray-400">Введите запрос для поиска в децентрализованной сети</p>
            </div>
          )}
        </div>
      </main>
      
      <Footer />
    </div>
  )
}
