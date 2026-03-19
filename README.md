# 🌍 Zametki Kostik NEXUS SEARCH

## Global Decentralized Search Engine - Production Ready

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](https://github.com/zametkikostik/NEXUS-SEARCH/blob/main/LICENSE)
[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/zametkikostik/NEXUS-SEARCH)
[![Deploy to Fly.io](https://fly.io/public/button.svg)](https://fly.io/launch?repo=https://github.com/zametkikostik/NEXUS-SEARCH)

**Languages:** 🇬🇧 English | 🇷🇺 Русский | 🇧🇬 Български

---

## 🌐 Worldwide Deployment Ready

Zametki Kostik NEXUS SEARCH is a **production-ready, decentralized, privacy-first search engine** designed for global deployment with:

- ✅ **Multi-region support** (EU, US, APAC, LatAm)
- ✅ **Multi-language** (EN, RU, BG + extensible)
- ✅ **Regional compliance** (GDPR, CCPA, LGPD, APPI)
- ✅ **Privacy-first architecture** (no tracking, no logs)
- ✅ **Web3 integration** (wallet auth, tokenomics)
- ✅ **Anti-ban scraping** (rotating proxies, circuit breakers)
- ✅ **IPFS storage** (decentralized content)
- ✅ **Global CDN** (Vercel Edge Network)

---

## 📍 Regional Deployment

| Region | Frontend CDN | Backend Regions | Compliance |
|--------|--------------|-----------------|------------|
| **Europe** | Frankfurt | Frankfurt, Amsterdam | GDPR |
| **North America** | East/West US | New York, San Francisco | CCPA |
| **Asia Pacific** | Singapore | Singapore, Tokyo | PDPA |
| **Latin America** | São Paulo | São Paulo | LGPD |
| **Eastern Europe** | Frankfurt | Frankfurt, Warsaw | GDPR |

---

## 🚀 Quick Start

### Option 1: Docker (Local Development)

```bash
git clone https://github.com/zametkikostik/NEXUS-SEARCH.git
cd NEXUS-SEARCH
cp .env.example .env
docker-compose up -d
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Global Deployment (Vercel + Fly.io)

See **[GLOBAL_DEPLOYMENT.md](GLOBAL_DEPLOYMENT.md)** for complete worldwide deployment guide.

---

## 🏗️ Architecture

```
NEXUS-SEARCH/
├── frontend/                 # Next.js 14 + TypeScript (Vercel)
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # React components
│   │   ├── i18n/            # Multi-language support
│   │   │   ├── en.json      # English
│   │   │   ├── ru.json      # Russian
│   │   │   └── bg.json      # Bulgarian
│   │   ├── hooks/           # Custom hooks
│   │   ├── stores/          # Zustand stores
│   │   └── utils/           # API client
│   ├── vercel.json          # Vercel config (global CDN)
│   └── package.json
├── backend/                  # FastAPI + Python (Fly.io/Railway)
│   ├── api/                 # REST API endpoints
│   ├── core/                # Core modules
│   │   ├── compliance/      # Regional compliance (GDPR, CCPA)
│   │   ├── geo_routing.py   # Geo-based routing
│   │   └── privacy.py       # Privacy settings
│   ├── providers/           # Search providers (6+ sources)
│   ├── anti_bot/            # Anti-bot layer
│   ├── filters/             # Content filters (regional)
│   ├── web3/                # Web3 authentication
│   ├── ipfs/                # IPFS integration
│   └── tests/               # Unit tests
├── contracts/               # Smart Contracts (ERC20 + Staking + NFT)
│   ├── NXS_Token.sol
│   ├── NXS_Staking.sol
│   └── NXS_Subscription.sol
├── GLOBAL_DEPLOYMENT.md     # Complete global deployment guide
├── LICENSE                  # Proprietary commercial license
└── README.md
```

---

## 🔌 API Endpoints

### Search

```bash
# Global search
curl "https://api.nexus-search.io/api/v1/search?q=blockchain"

# With region
curl "https://eu-api.nexus-search.io/api/v1/search?q=crypto&region=eu"

# With language
curl "https://api.nexus-search.io/api/v1/search?q=web3&lang=bg"
```

### Authentication

```bash
# Get message to sign
curl "https://api.nexus-search.io/api/v1/auth/message?address=0x..."

# Verify signature
curl -X POST "https://api.nexus-search.io/api/v1/auth/verify" \
  -H "Content-Type: application/json" \
  -d '{"address":"0x...","message":"...","signature":"0x..."}'
```

### Health

```bash
# Global health check
curl "https://api.nexus-search.io/health"

# Regional health
curl "https://eu-api.nexus-search.io/health"
```

---

## 🌐 Multi-Language Support

### Default Languages

- 🇬🇧 **English** (en)
- 🇷🇺 **Russian** (ru)
- 🇧🇬 **Bulgarian** (bg)

### Adding Languages

```typescript
// frontend/src/i18n/index.ts
export const supportedLanguages = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'ru', name: 'Русский', flag: '🇷🇺' },
  { code: 'bg', name: 'Български', flag: '🇧🇬' },
  { code: 'es', name: 'Español', flag: '🇪🇸' }, // Add Spanish
]
```

---

## ⚖️ Regional Compliance

### Europe (GDPR)

- ✅ No user tracking
- ✅ No cookies (except essential)
- ✅ Data deletion on request
- ✅ Privacy by default

### USA (CCPA/CPRA)

- ✅ Opt-out of data selling
- ✅ Disclosure requirements
- ✅ Right to know

### Bulgaria (Local)

- ✅ GDPR compliance
- ✅ Bulgarian language support
- ✅ Local content filtering

---

## 💰 Tokenomics

| Category | Percentage | Description |
|----------|------------|-------------|
| **Users** | 30% | Search rewards, staking |
| **Team** | 20% | 4-year vesting |
| **Investors** | 20% | 2-year vesting |
| **Ecosystem** | 20% | Grants, partnerships |
| **Liquidity** | 10% | DEX listings |

### Global Pricing

| Region | Price per Search | Currency |
|--------|-----------------|----------|
| USA | $0.01 | USD |
| EU | €0.01 | EUR |
| Bulgaria | лв0.02 | BGN |
| India | ₹0.80 | INR (PPP adjusted) |

---

## 🔒 Privacy & Security

### Privacy-First Architecture

```python
PRIVACY_SETTINGS = {
    'no_logs': True,
    'no_tracking': True,
    'no_analytics': True,
    'anonymous_search': True,
    'no_ip_storage': True,
    'data_encryption': 'AES-256',
    'https_only': True,
}
```

### Regional Content Filtering

```python
REGIONAL_FILTERS = {
    'bg': {  # Bulgaria
        'blocked_categories': ['extremism', 'gambling', 'adult'],
        'language_priority': ['bg', 'en'],
    },
    'de': {  # Germany
        'blocked_categories': ['hate_speech', 'nazi_content'],
        'language_priority': ['de', 'en'],
    },
    # Add more regions...
}
```

---

## 🚀 Deployment

### Backend (Multi-Region)

```bash
cd backend

# Deploy to Fly.io (multiple regions)
fly launch --name nexus-search-api
fly regions set fra,iad,sin,sao
fly secrets set JWT_SECRET=$(openssl rand -hex 32)
fly secrets set WEB3_PROVIDER_URI=...
fly deploy
fly scale count 6  # 2 per region
```

### Frontend (Global CDN)

```bash
cd frontend

# Deploy to Vercel
vercel --prod

# Add custom domain
vercel domains add nexus-search.io
```

---

## 📊 Monitoring

### Global Health Dashboard

```bash
# Check all regions
curl "https://api.nexus-search.io/health/global"

# Response:
{
  "status": "operational",
  "regions": {
    "EU": "healthy",
    "US": "healthy",
    "APAC": "healthy",
    "LatAm": "healthy"
  }
}
```

### Metrics to Track

- Response time by region
- Error rates by country
- Search volume by language
- Token usage globally

---

## 📱 Mobile Optimization

- ✅ Responsive design (mobile-first)
- ✅ PWA support (installable)
- ✅ Touch-optimized UI
- ✅ Offline mode (cached searches)

---

## 🤝 Contributing

This is a **proprietary commercial project**. Contributions require written approval from the licensor.

For licensing inquiries: **intelligent.swallow.aybm@mask.me**

---

## 📞 Global Support

| Region | Email | Hours |
|--------|-------|-------|
| **Global** | intelligent.swallow.aybm@mask.me | 24/7 |
| **Europe** | eu-support@nexus-search.io | 9-18 CET |
| **Americas** | us-support@nexus-search.io | 9-18 EST |
| **APAC** | apac-support@nexus-search.io | 9-18 SGT |

---

## 📄 License

**Proprietary Commercial License**

- ✅ Use only under written agreement
- ✅ Revenue sharing required ([X]% of revenue)
- ❌ No unauthorized distribution
- ❌ No forks without approval
- ❌ No publication without consent

See **[LICENSE](LICENSE)** for full terms.

---

## 🎯 Ready for Worldwide Launch

- [x] Multi-region deployment
- [x] Multi-language support (EN, RU, BG)
- [x] Regional compliance (GDPR, CCPA, LGPD)
- [x] Global CDN (Vercel Edge Network)
- [x] Multi-currency pricing
- [x] Privacy-first architecture
- [x] Web3 integration
- [x] Anti-ban scraping
- [x] IPFS storage
- [x] Tokenomics ready
- [x] Mobile optimized
- [x] Monitoring configured

---

**Zametki Kostik NEXUS SEARCH** - Deploy Anywhere. Search Everywhere. 🌍

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/zametkikostik/NEXUS-SEARCH)
[![Deploy to Fly.io](https://fly.io/public/button.svg)](https://fly.io/launch?repo=https://github.com/zametkikostik/NEXUS-SEARCH)

---

*Last Updated: January 2026*  
*Version: 1.0 - Global Production Ready*
