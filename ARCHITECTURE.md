# NEXUS Search - Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Wallet  │  │  Search  │  │ Results  │  │  Token   │        │
│  │ Connect  │  │   Bar    │  │  Display │  │   Info   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (FastAPI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Search  │  │   Auth   │  │   IPFS   │  │  Health  │        │
│  │  Router  │  │  Router  │  │  Router  │  │  Router  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   Search Layer   │ │    Web3 Layer    │ │   Storage Layer  │
│ ┌──────────────┐ │ │ ┌──────────────┐ │ │ ┌──────────────┐ │
│ │ Aggregator   │ │ │ │   Signature  │ │ │ │    Redis     │ │
│ │   Provider   │ │ │ │   Verifier   │ │ │ │    Cache     │ │
│ └──────────────┘ │ │ └──────────────┘ │ │ └──────────────┘ │
│ ┌──────────────┐ │ │ ┌──────────────┐ │ │ ┌──────────────┐ │
│ │   Google     │ │ │ │     JWT      │ │ │ │    IPFS      │ │
│ │   DuckDuckGo │ │ │ │   Manager    │ │ │ │   Storage    │ │
│ │   Brave      │ │ │ └──────────────┘ │ │ └──────────────┘ │
│ │   Yandex     │ │ └──────────────────┘ └──────────────────┘
│ │   Dzen       │ │
│ │   Reddit     │ │
│ └──────────────┘ │
└──────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Anti-Bot Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Proxy   │  │ Circuit  │  │  Health  │  │  Request │        │
│  │ Manager  │  │ Breaker  │  │ Checker  │  │ Session  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Backend Structure

```
backend/
├── api/              # FastAPI routers
│   ├── main.py       # Application entry
│   ├── search.py     # Search endpoints
│   ├── auth.py       # Auth endpoints
│   ├── ipfs.py       # IPFS endpoints
│   └── health.py     # Health checks
├── core/             # Core configuration
│   ├── config.py     # Settings
│   ├── cache.py      # Redis client
│   ├── utils.py      # Utilities
│   └── exceptions.py # Custom exceptions
├── providers/        # Search providers
│   ├── base.py       # Base provider class
│   ├── aggregator.py # Provider aggregator
│   ├── google.py     # Google provider
│   ├── duckduckgo.py # DuckDuckGo provider
│   ├── brave.py      # Brave provider
│   ├── yandex.py     # Yandex provider
│   ├── dzen.py       # Dzen provider
│   └── reddit.py     # Reddit provider
├── anti_bot/         # Anti-bot layer
│   ├── proxy_manager.py    # Proxy rotation
│   ├── circuit_breaker.py  # Circuit breaker
│   ├── health_checker.py   # Health monitoring
│   └── request_session.py  # Anti-bot requests
├── filters/          # Content filtering
│   ├── blacklist.py  # Keyword blacklist
│   ├── ml_classifier.py  # ML classifier
│   └── content_filter.py # Combined filter
├── web3/             # Web3 authentication
│   ├── signature.py  # Signature verification
│   ├── jwt_manager.py # JWT handling
│   └── auth_service.py # Auth service
├── ipfs/             # IPFS integration
│   ├── client.py     # IPFS client
│   └── models.py     # IPFS models
└── models/           # Pydantic models
```

### Data Flow

1. **Search Flow**
```
User Query → Frontend → API Gateway → Cache Check
                                            │
                                            ▼ (miss)
                              Provider Aggregator → Anti-Bot Layer
                                                      │
                                                      ▼
                                         Multiple Providers (parallel)
                                                      │
                                                      ▼
                                         Results Merge & Dedup
                                                      │
                                                      ▼
                                         Content Filter → Cache → Response
```

2. **Authentication Flow**
```
User → Connect Wallet → Get Message → Sign → Verify → JWT Token → Authenticated Requests
```

3. **IPFS Storage Flow**
```
Search Results → Serialize → IPFS Add → Get CID → Store CID → Return to User
```

## Smart Contracts

### NXS Token (ERC20)
- Total Supply: 1,000,000,000 NXS
- Vesting for team and investors
- Rewards distribution
- Burnable and votable

### Staking Contract
- Stake NXS tokens
- Earn rewards (5% APY)
- Minimum lock period: 1 day
- Emergency withdrawal

### Subscription NFT (ERC721)
- Three tiers: Basic, Premium, Enterprise
- Time-based access
- Renewable subscriptions

## Security Measures

1. **Input Validation**
   - Pydantic models for all inputs
   - URL sanitization
   - Query length limits

2. **SSRF Prevention**
   - Blocked schemes (file, gopher, dict)
   - Only HTTP/HTTPS allowed

3. **Rate Limiting**
   - Per-minute, per-hour, per-day limits
   - Wallet-based or IP-based

4. **Authentication**
   - Wallet signature verification
   - JWT tokens with expiration
   - Token blacklist for logout

5. **Content Filtering**
   - Keyword blacklist
   - ML-based classification
   - Category-based blocking

## Scaling Considerations

1. **Horizontal Scaling**
   - Stateless API servers
   - Redis for shared cache
   - Load balancer ready

2. **Provider Scaling**
   - Easy to add new providers
   - Circuit breaker per provider
   - Health-based routing

3. **Cache Strategy**
   - Short TTL for news (5 min)
   - Long TTL for static (24 hours)
   - Query-based cache keys

4. **Database**
   - Redis for cache and sessions
   - IPFS for persistent storage
   - Optional: PostgreSQL for analytics
