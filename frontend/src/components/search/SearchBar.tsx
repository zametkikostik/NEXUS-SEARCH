'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Search as SearchIcon, Loader2, X } from 'lucide-react'

interface SearchBarProps {
  onSearch?: (query: string) => void
  placeholder?: string
  size?: 'sm' | 'md' | 'lg'
}

export default function SearchBar({ 
  onSearch, 
  placeholder = 'Найти в децентрализованной сети...',
  size = 'lg'
}: SearchBarProps) {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const sizeClasses = {
    sm: 'py-2 px-4',
    md: 'py-3 px-6',
    lg: 'py-4 px-8'
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!query.trim()) return
    
    setIsLoading(true)
    
    try {
      if (onSearch) {
        onSearch(query)
      } else {
        router.push(`/search?q=${encodeURIComponent(query)}`)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleClear = () => {
    setQuery('')
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className={`relative flex items-center bg-dark-card border border-dark-border rounded-2xl overflow-hidden focus-within:border-nexus-500 focus-within:ring-2 focus-within:ring-nexus-500/20 transition-all ${sizeClasses[size]}`}>
        <SearchIcon className="w-5 h-5 text-gray-400 mr-3 flex-shrink-0" />
        
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="flex-1 bg-transparent outline-none text-white placeholder-gray-500"
          disabled={isLoading}
        />
        
        {query && !isLoading && (
          <button
            type="button"
            onClick={handleClear}
            className="ml-2 p-1 rounded-full hover:bg-dark-border transition-colors"
          >
            <X className="w-4 h-4 text-gray-400" />
          </button>
        )}
        
        {isLoading && (
          <Loader2 className="w-5 h-5 text-nexus-400 animate-spin ml-2" />
        )}
      </div>
    </form>
  )
}
