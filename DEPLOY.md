# 🚀 Полная инструкция по деплою NEXUS SEARCH

## Варианты деплоя

### Вариант 1: Vercel (Frontend) + Fly.io (Backend) ⭐ Рекомендуемый

### Вариант 2: Vercel (Frontend) + Railway (Backend)

### Вариант 3: Vercel (Frontend) + Render (Backend)

### Вариант 4: Docker (локально)

---

## 📋 Вариант 1: Vercel + Fly.io

### Шаг 1: Деплой Backend на Fly.io

```bash
# Перейти в директорию backend
cd backend

# Установить Fly.io CLI (если не установлен)
curl -L https://fly.io/install.sh | sh

# Перезагрузить терминал или добавить в PATH
export PATH="$HOME/.fly/bin:$PATH"

# Авторизация
fly auth login

# Создать приложение
fly launch --name nexus-search-api --region fra --no-deploy

# Настроить переменные окружения
fly secrets set JWT_SECRET=$(openssl rand -hex 32)
fly secrets set WEB3_PROVIDER_URI=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
fly secrets set REDIS_URL=redis://your-redis-url:6379

# Если нужен Redis на Fly.io
fly redis create

# Деплой
fly deploy
```

**Проверка:**
```bash
# Проверить статус
fly status

# Посмотреть логи
fly logs

# Проверить health
curl https://nexus-search-api.fly.dev/health
```

### Шаг 2: Деплой Frontend на Vercel

```bash
# Перейти в директорию frontend
cd frontend

# Установить Vercel CLI (если не установлен)
npm install -g vercel

# Авторизация
vercel login

# Настроить .env.local
cp .env.example .env.local
nano .env.local

# Изменить NEXT_PUBLIC_API_URL на ваш backend
NEXT_PUBLIC_API_URL=https://nexus-search-api.fly.dev

# Деплой
vercel --prod
```

Или через веб-интерфейс:

1. Откройте https://vercel.com/new
2. Импортируйте GitHub репозиторий
3. Укажите переменные окружения
4. Нажмите Deploy

### Шаг 3: Настройка домена (опционально)

#### Backend (Fly.io)
```bash
# Добавить custom domain
fly certs add api.your-domain.com

# Обновить DNS записи
# CNAME api.your-domain.com -> nexus-search-api.fly.dev
```

#### Frontend (Vercel)
1. Откройте Vercel Dashboard
2. Project Settings → Domains
3. Добавьте ваш домен
4. Настройте DNS у регистратора

---

## 📋 Вариант 2: Vercel + Railway

### Шаг 1: Деплой Backend на Railway

```bash
# Создать аккаунт на https://railway.app

# Нажать "New Project"
# Выбрать "Deploy from GitHub repo"
# Выбрать репозиторий NEXUS-SEARCH

# Настроить переменные окружения в Railway Dashboard:
JWT_SECRET=your-secret
WEB3_PROVIDER_URI=your-rpc-url
REDIS_URL=your-redis-url

# Railway автоматически задеплоит
```

### Шаг 2: Деплой Frontend на Vercel

Аналогично Варианту 1.

---

## 📋 Вариант 3: Vercel + Render

### Шаг 1: Деплой Backend на Render

1. Создать аккаунт на https://render.com
2. New → Web Service
3. Connect GitHub репозиторий
4. Configure:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements-prod.txt`
   - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port 8000`
5. Добавить Environment Variables
6. Deploy

### Шаг 2: Деплой Frontend на Vercel

Аналогично Варианту 1.

---

## 📋 Вариант 4: Docker (локально)

```bash
# Клонировать репозиторий
git clone https://github.com/zametkikostik/NEXUS-SEARCH.git
cd NEXUS-SEARCH

# Скопировать .env
cp .env.example .env
nano .env  # Изменить переменные

# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

---

## 🔐 Настройка переменных окружения

### Обязательные переменные

#### Backend (.env)
```bash
# Критически важно!
JWT_SECRET=<secure-random-64-chars>
WEB3_PROVIDER_URI=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY

# Redis
REDIS_URL=redis://localhost:6379

# IPFS
IPFS_HOST=localhost
IPFS_PORT=5001
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=your-walletconnect-id
```

### Опциональные переменные

#### Search Providers API Keys
```bash
GOOGLE_API_KEY=your-google-key
GOOGLE_CX=your-google-cx
BRAVE_API_KEY=your-brave-key
```

#### Monitoring
```bash
SENTRY_DSN=https://your-sentry-dsn
```

---

## ✅ Чеклист после деплоя

### Backend
- [ ] Health endpoint отвечает: `/health`
- [ ] API docs доступны: `/docs`
- [ ] Redis подключён
- [ ] IPFS подключён
- [ ] Web3 provider работает
- [ ] Поиск работает
- [ ] Auth работает

### Frontend
- [ ] Сайт открывается
- [ ] WalletConnect подключается
- [ ] Поиск работает
- [ ] Результаты отображаются
- [ ] Нет ошибок в консоли

### Безопасность
- [ ] HTTPS включён
- [ ] CORS настроен
- [ ] Rate limiting работает
- [ ] JWT_SECRET изменён
- [ ] Security headers настроены

---

## 🔧 Troubleshooting

### Backend не запускается

```bash
# Проверить логи
fly logs  # или Railway/Render logs

# Проверить переменные окружения
fly secrets list

# Перезапустить
fly restart
```

### Frontend не подключается к backend

```bash
# Проверить NEXT_PUBLIC_API_URL
cat .env.local | grep API_URL

# Проверить CORS настройки на backend
# ALLOWED_ORIGINS должен включать frontend domain
```

### Web3 не работает

```bash
# Проверить WEB3_PROVIDER_URI
# Убедитесь что RPC URL работает
curl https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY \
  -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

---

## 📊 Мониторинг

### Backend метрики

```bash
# Prometheus metrics
curl https://your-backend-url.com/metrics

# Health check
curl https://your-backend-url.com/health

# Provider status
curl https://your-backend-url.com/providers
```

### Frontend аналитика

- Vercel Analytics (встроенная)
- Google Analytics (опционально)
- Sentry для ошибок

---

## 💰 Стоимость

### Vercel
- Hobby: $0 (бесплатно для личных проектов)
- Pro: $20/month

### Fly.io
- Free tier: 3 shared-cpu-1x VMs (256MB)
- Pay as you go: ~$5-20/month в зависимости от нагрузки

### Railway
- Trial: $5 credit
- Pay as you go: ~$5-20/month

### Render
- Free tier: ограничен
- Starter: $7/month

**Итого:** ~$0-40/month в зависимости от нагрузки

---

## 🎯 Следующие шаги

1. Настроить CI/CD (GitHub Actions)
2. Настроить мониторинг (Sentry, Prometheus)
3. Настроить backup (Redis, IPFS)
4. Настроить auto-scaling
5. Добавить custom domain
6. Настроить SSL сертификаты

---

**Готово!** Ваш NEXUS Search задеплоен! 🎉
