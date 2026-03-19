# NEXUS SEARCH

[![CI/CD](https://github.com/zametkikostik/NEXUS-SEARCH/actions/workflows/ci.yml/badge.svg)](https://github.com/zametkikostik/NEXUS-SEARCH/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Децентрализованная поисковая система нового поколения

NEXUS Search — это privacy-first поисковая система с Web3 аутентификацией, IPFS хранением и токеномикой.

### Особенности

- 🔍 **Мульти-провайдер поиск** — Google, DuckDuckGo, Brave, Yandex, Dzen, Reddit
- 🛡️ **Privacy-First** — никаких логов, никакого трекинга
- 🔐 **Web3 Аутентификация** — вход через криптокошелёк (MetaMask, WalletConnect)
- 📦 **IPFS Интеграция** — децентрализованное хранение результатов
- 🔄 **Анти-Бан Система** — ротация прокси, обход блокировок
- 💰 **Токеномика** — ERC20 токен NXS, стейкинг rewards
- 🎯 **Контент Фильтры** — блокировка экстремизма, терроризма, пропаганды

## 📁 Структура проекта

```
NEXUS-SEARCH/
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints
│   ├── core/               # Core configuration
│   ├── providers/          # Search providers
│   ├── anti_bot/           # Anti-bot layer
│   ├── filters/            # Content filters
│   ├── web3/               # Web3 authentication
│   ├── ipfs/               # IPFS integration
│   └── tests/              # Unit tests
├── frontend/               # Next.js 14 frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── stores/        # Zustand stores
│   │   └── utils/         # Utilities
│   └── public/
├── contracts/              # Smart contracts
│   ├── NXS_Token.sol      # ERC20 token
│   ├── NXS_Staking.sol    # Staking contract
│   └── NXS_Subscription.sol # Subscription NFT
├── scripts/
│   └── deploy.sh          # Deployment script
├── docker-compose.yml      # Docker orchestration
└── README.md
```

## 🛠️ Быстрый старт

### Требования

- Docker & Docker Compose
- Node.js 18+ (для локальной разработки)
- Python 3.11+ (для локальной разработки)
- MetaMask или Web3 кошелёк

### 1. Клонирование репозитория

```bash
git clone https://github.com/zametkikostik/NEXUS-SEARCH.git
cd NEXUS-SEARCH
```

### 2. Настройка окружения

```bash
# Скопировать файл окружения
cp .env.example .env

# Отредактировать .env (обязательно измените JWT_SECRET!)
nano .env
```

**Минимальная конфигурация (.env):**
```bash
# Обязательно измените!
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
WEB3_PROVIDER_URI=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY

# Опционально (для продакшн)
ALLOWED_ORIGINS=https://your-domain.com
```

### 3. Запуск с Docker

```bash
# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps

# Посмотреть логи
docker-compose logs -f
```

### 4. Доступ к приложению

| Сервис | URL |
|--------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| IPFS Gateway | http://localhost:8080 |

## 🔌 API Endpoints

### Поиск
```bash
# Базовый поиск
curl "http://localhost:8000/api/v1/search?q=blockchain"

# С выбором провайдеров
curl "http://localhost:8000/api/v1/search?q=crypto&providers=google,duckduckgo&limit=10"
```

### Аутентификация
```bash
# Получить сообщение для подписи
curl "http://localhost:8000/api/v1/auth/message?address=0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"

# Верифицировать подпись
curl -X POST "http://localhost:8000/api/v1/auth/verify" \
  -H "Content-Type: application/json" \
  -d '{"address":"0x...","message":"...","signature":"0x..."}'
```

### IPFS
```bash
# Получить из IPFS
curl "http://localhost:8000/api/v1/ipfs/retrieve/QmYourCID"
```

### Health Check
```bash
curl "http://localhost:8000/health"
```

## 🌐 Провайдеры поиска

| Провайдер | Статус | API Key |
|-----------|--------|---------|
| Google | ✅ | Требуется (Custom Search API) |
| DuckDuckGo | ✅ | Не требуется |
| Brave | ✅ | Требуется (Search API) |
| Yandex | ✅ | Не требуется |
| Dzen | ✅ | Не требуется |
| Reddit | ✅ | Не требуется |

## 💰 Токеномика NXS

| Категория | Процент | Описание |
|-----------|---------|----------|
| Пользователи | 30% | Rewards за поиск и стейкинг |
| Команда | 20% | 4 года вестинга |
| Инвесторы | 20% | 2 года вестинга |
| Экосистема | 20% | Гранты, партнёрства |
| Ликвидность | 10% | DEX листинги |

## 📄 Смарт-контракты

### Развёртывание контрактов

```bash
cd contracts

# Установить зависимости
npm install

# Скомпилировать
npm run compile

# Запустить локальный блокчейн
npx hardhat node

# Задеплоить (в другом терминале)
npm run deploy:local
```

### Контракты
- `NXS_Token.sol` — ERC20 токен с vesting
- `NXS_Staking.sol` — Стейкинг с 5% APY
- `NXS_Subscription.sol` — NFT подписка (Basic/Premium/Enterprise)

## 🧪 Тестирование

### Backend тесты
```bash
cd backend
pip install -r requirements.txt
pytest --cov=.
```

### Frontend тесты
```bash
cd frontend
npm install
npm test
```

### Контракты тесты
```bash
cd contracts
npm test
```

## 🚀 Production Deployment

### 1. Настройка production окружения

```bash
# Создать production .env
cp .env.example .env

# Изменить переменные для production
nano .env
```

**Production .env:**
```bash
# Backend
JWT_SECRET=<secure-random-64-chars>
WEB3_PROVIDER_URI=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
ALLOWED_ORIGINS=https://your-domain.com
SENTRY_DSN=https://your-sentry-dsn

# Frontend
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_WEB3_CHAIN_ID=1
NEXT_PUBLIC_CONTRACT_ADDRESS=0xYourTokenAddress
NEXT_PUBLIC_TOKEN_CONTRACT_ADDRESS=0xYourTokenAddress
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=your-project-id
```

### 2. Развёртывание на сервере

```bash
# На сервере (Ubuntu/Debian)

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установить Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Клонировать репозиторий
git clone https://github.com/zametkikostik/NEXUS-SEARCH.git
cd NEXUS-SEARCH

# Настроить окружение
cp .env.example .env
nano .env

# Запустить production compose
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Настройка Nginx (опционально)

```bash
# Создать директорию для nginx
mkdir -p nginx/ssl

# Положить SSL сертификаты в nginx/ssl/
# certificate.crt
# private.key

# Запустить с nginx
docker-compose -f docker-compose.prod.yml --profile with-nginx up -d
```

### 4. Автоматический деплой скриптом

```bash
# Запустить deploy скрипт
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 📊 Мониторинг

### Prometheus метрики
```bash
curl http://localhost:8000/metrics
```

### Health endpoints
```bash
# Общий health
curl http://localhost:8000/health

# Liveness probe
curl http://localhost:8000/health/live

# Readiness probe
curl http://localhost:8000/health/ready

# Статус провайдеров
curl http://localhost:8000/providers
```

## 🔒 Безопасность

### Настройки безопасности
- ✅ Input validation (Pydantic)
- ✅ SSRF prevention
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ Security headers
- ✅ HTTPS only (production)

### Рекомендации
1. Измените все default значения
2. Используйте secure JWT_SECRET (минимум 32 символа)
3. Включите HTTPS в production
4. Настройте firewall правила
5. Регулярно обновляйте зависимости

## 🤝 Contributing

1. Fork репозиторий
2. Создать feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Открыть Pull Request

## 📞 Контакты

- **GitHub**: https://github.com/zametkikostik/NEXUS-SEARCH
- **Email**: zametkikostik@gmail.com
- **Telegram**: @zametkikostik

## 📄 Лицензия

MIT License — см. файл [LICENSE](LICENSE) для деталей.

## 🙏 Благодарности

- OpenZeppelin — смарт-контракты
- FastAPI — backend фреймворк
- Next.js — frontend фреймворк
- RainbowKit — Web3 UI
- IPFS — децентрализованное хранение

---

**NEXUS SEARCH** — Децентрализованное будущее поиска 🌐

[![Star History Chart](https://api.star-history.com/svg?repos=zametkikostik/NEXUS-SEARCH&type=Date)](https://star-history.com/#zametkikostik/NEXUS-SEARCH&Date)
