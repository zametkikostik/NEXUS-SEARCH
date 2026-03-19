import { ExternalLink, Shield } from 'lucide-react'

interface SearchResultProps {
  result: {
    title: string
    url: string
    snippet: string
    source: string
    rank: number
    relevance_score?: number
  }
  index: number
}

export default function SearchResult({ result, index }: SearchResultProps) {
  const getFaviconUrl = (url: string) => {
    try {
      const domain = new URL(url).hostname
      return `https://www.google.com/s2/favicons?domain=${domain}&sz=32`
    } catch {
      return '/favicon.ico'
    }
  }

  return (
    <div className="card hover:border-nexus-500/50 transition-colors group">
      <div className="flex items-start gap-3">
        {/* Index */}
        <div className="text-sm text-gray-500 w-6 flex-shrink-0">
          {index}
        </div>
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Title & URL */}
          <div className="flex items-center gap-2 mb-1">
            <a
              href={result.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-nexus-400 hover:text-nexus-300 font-medium truncate flex-1"
            >
              {result.title}
            </a>
            <a
              href={result.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-gray-300 flex-shrink-0"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
          
          {/* URL & Source */}
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <img
              src={getFaviconUrl(result.url)}
              alt=""
              className="w-4 h-4"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
            <span className="truncate">{new URL(result.url).hostname}</span>
            <span className="px-2 py-0.5 rounded bg-dark-border text-xs">
              {result.source}
            </span>
          </div>
          
          {/* Snippet */}
          <p className="text-gray-400 text-sm line-clamp-2">
            {result.snippet}
          </p>
          
          {/* Relevance Score */}
          {result.relevance_score && result.relevance_score > 0 && (
            <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
              <Shield className="w-3 h-3" />
              <span>Relevance: {(result.relevance_score * 100).toFixed(0)}%</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
