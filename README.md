# NEXUS SEARCH

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/zametkikostik/NEXUS-SEARCH)
[![Deploy to Fly.io](https://fly.io/public/button.svg)](https://fly.io/launch?repo=https://github.com/zametkikostik/NEXUS-SEARCH)

## 🚀 Децентрализованная поисковая система нового поколения

**NEXUS Search** — это privacy-first поисковая система с Web3 аутентификацией, IPFS хранением и токеномикой.

### ✨ Особенности

- 🔍 **6+ поисковых провайдеров** — Google, DuckDuckGo, Brave, Yandex, Dzen, Reddit
- 🛡️ **Privacy-First** — никаких логов, никакого трекинга
- 🔐 **Web3 Аутентификация** — вход через криптокошелёк (MetaMask, WalletConnect)
- 📦 **IPFS Интеграция** — децентрализованное хранение результатов
- 🔄 **Анти-Бан Система** — ротация прокси, обход блокировок
- 💰 **Токеномика** — ERC20 токен NXS, стейкинг rewards
- 🎯 **Контент Фильтры** — блокировка экстремизма, терроризма, пропаганды
- ⚡ **Vercel Ready** — frontend готов к деплою на Vercel
- 🐳 **Dockerized Backend** — backend готов к деплою на Fly.io/Railway/Render

---

## 📁 Структура проекта

```
NEXUS-SEARCH/
├── frontend/                 # Next.js 14 + TypeScript (Vercel)
│   ├── src/
│   │   ├── app/             # App Router страницы
│   │   ├── components/      # React компоненты
│   │   ├── hooks/           # Custom hooks
│   │   ├── stores/          # Zustand stores
│   │   └── utils/           # API client
│   ├── vercel.json          # Vercel конфигурация
│   ├── next.config.js       # Next.js конфиг
│   └── package.json
├── backend/                  # FastAPI + Python (Fly.io/Railway)
│   ├── api/                 # API endpoints
│   ├── core/                # Core модули
│   ├── providers/           # Search providers
│   ├── anti_bot/            # Anti-bot layer
│   ├── filters/             # Content filters
│   ├── web3/                # Web3 auth
│   ├── ipfs/                # IPFS integration
│   ├── tests/               # Unit tests
│   ├── Dockerfile           # Production Docker
│   ├── fly.toml             # Fly.io конфиг
│   └── requirements-prod.txt
├── contracts/               # Smart Contracts
│   ├── NXS_Token.sol        # ERC20 токен
│   ├── NXS_Staking.sol      # Стейкинг
│   └── NXS_Subscription.sol # NFT подписка
├── scripts/
│   ├── deploy.sh            # Deploy скрипт
│   └── init-github.sh       # GitHub инициализация
├── docker-compose.yml       # Local development
└── README.md
```

---

## 🚀 Быстрый старт

### Вариант 1: Docker (локальная разработка)

```bash
# Клонировать репозиторий
git clone https://github.com/zametkikostik/NEXUS-SEARCH.git
cd NEXUS-SEARCH

# Скопировать .env
cp .env.example .env

# Запустить все сервисы
docker-compose up -d

# Доступ
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Вариант 2: Vercel + Внешний Backend

#### 1. Деплой Frontend на Vercel

```bash
cd frontend

# Установить зависимости
npm install

# Настроить .env.local
cp .env.example .env.local
nano .env.local  # Изменить NEXT_PUBLIC_API_URL

# Деплой на Vercel
vercel --prod
```

Или нажмите кнопку:

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/zametkikostik/NEXUS-SEARCH&project-name=nexus-search-frontend&repository-name=nexus-search-frontend&env=NEXT_PUBLIC_API_URL,NEXT_PUBLIC_WEB3_CHAIN_ID,NEXT_PUBLIC_CONTRACT_ADDRESS)

#### 2. Деплой Backend на Fly.io

```bash
cd backend

# Установить Fly.io CLI
curl -L https://fly.io/install.sh | sh

# Авторизация
fly auth login

# Создать приложение
fly launch --name nexus-search-api

# Настроить переменные окружения
fly secrets set JWT_SECRET=your-secret \
  WEB3_PROVIDER_URI=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY \
  REDIS_URL=redis://your-redis-url

# Деплой
fly deploy
```

Или используйте Railway/Render:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/nexus-search)
[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

---

## 🔌 API Endpoints

### Поиск

```bash
# Базовый поиск
curl "https://your-backend-url.com/api/v1/search?q=blockchain"

# С провайдерами
curl "https://your-backend-url.com/api/v1/search?q=crypto&providers=google,duckduckgo&limit=10"
```

### Аутентификация

```bash
# Получить сообщение для подписи
curl "https://your-backend-url.com/api/v1/auth/message?address=0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"

# Верифицировать подпись
curl -X POST "https://your-backend-url.com/api/v1/auth/verify" \
  -H "Content-Type: application/json" \
  -d '{"address":"0x...","message":"...","signature":"0x..."}'
```

### IPFS

```bash
# Получить из IPFS
curl "https://your-backend-url.com/api/v1/ipfs/retrieve/QmYourCID"
```

### Health

```bash
curl "https://your-backend-url.com/health"
```

---

## 🔐 Настройка окружения

### Frontend (.env.local)

```bash
# API URL (ваш backend)
NEXT_PUBLIC_API_URL=https://nexus-search-api.fly.dev

# Web3
NEXT_PUBLIC_WEB3_CHAIN_ID=1
NEXT_PUBLIC_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000
NEXT_PUBLIC_TOKEN_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=your-walletconnect-id

# IPFS
NEXT_PUBLIC_IPFS_GATEWAY=https://ipfs.io/ipfs/
```

### Backend (.env)

```bash
# Обязательно
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
WEB3_PROVIDER_URI=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379

# IPFS
IPFS_HOST=localhost
IPFS_PORT=5001

# Опционально
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CX=your-google-cx
BRAVE_API_KEY=your-brave-api-key
SENTRY_DSN=your-sentry-dsn
```

---

## 💰 Токеномика NXS

| Категория | Процент | Описание |
|-----------|---------|----------|
| Пользователи | 30% | Rewards за поиск и стейкинг |
| Команда | 20% | 4 года вестинга |
| Инвесторы | 20% | 2 года вестинга |
| Экосистема | 20% | Гранты, партнёрства |
| Ликвидность | 10% | DEX листинги |

### Развёртывание контрактов

```bash
cd contracts

# Установить зависимости
npm install

# Скомпилировать
npm run compile

# Деплой на testnet
npx hardhat run scripts/deploy.js --network sepolia

# Деплой на mainnet
npx hardhat run scripts/deploy.js --network mainnet
```

---

## 🧪 Тестирование

### Backend

```bash
cd backend
pip install -r requirements.txt
pytest --cov=.
```

### Frontend

```bash
cd frontend
npm install
npm test
```

---

## 📊 Мониторинг

### Prometheus метрики

```bash
curl https://your-backend-url.com/metrics
```

### Health checks

```bash
# Backend health
curl https://your-backend-url.com/health

# Provider status
curl https://your-backend-url.com/providers
```

---

## 🚀 Production Deployment Checklist

### Перед деплоем

- [ ] Сгенерировать secure JWT_SECRET (минимум 32 символа)
- [ ] Настроить Web3 provider (Infura/Alchemy)
- [ ] Получить API ключи для провайдеров (Google, Brave)
- [ ] Настроить Redis (production instance)
- [ ] Настроить IPFS node (или использовать Pinata)
- [ ] Развернуть смарт-контракты
- [ ] Обновить адреса контрактов в .env

### Деплой

- [ ] Задеплоить backend (Fly.io/Railway/Render)
- [ ] Задеплоить frontend (Vercel)
- [ ] Настроить домен и SSL
- [ ] Настроить CORS для frontend domain
- [ ] Проверить health endpoints
- [ ] Протестировать поиск
- [ ] Протестировать Web3 auth

### После деплоя

- [ ] Настроить мониторинг (Sentry, Prometheus)
- [ ] Настроить логирование
- [ ] Настроить backup (Redis, IPFS)
- [ ] Настроить auto-scaling
- [ ] Добавить rate limiting

---

## 🔒 Безопасность

### Настройки безопасности

- ✅ Input validation (Pydantic)
- ✅ SSRF prevention
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ Security headers
- ✅ HTTPS only

### Рекомендации

1. Используйте secure JWT_SECRET (минимум 32 символа)
2. Включите HTTPS в production
3. Настройте firewall правила
4. Регулярно обновляйте зависимости
5. Используйте multi-sig для контрактов

---

## 🤝 Contributing

1. Fork репозиторий
2. Создать feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Открыть Pull Request

---

## 📞 Контакты

- **GitHub**: https://github.com/zametkikostik/NEXUS-SEARCH
- **Email**: intelligent.swallow.aybm@mask.me

---

## 📄 Лицензия

MIT License — см. файл [LICENSE](LICENSE) для деталей.

---

**NEXUS SEARCH** — Децентрализованное будущее поиска 🌐

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/zametkikostik/NEXUS-SEARCH)
[![Deploy to Fly.io](https://fly.io/public/button.svg)](https://fly.io/launch?repo=https://github.com/zametkikostik/NEXUS-SEARCH)
