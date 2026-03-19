# 🚀 БЫСТРЫЙ ДЕПЛОЙ NEXUS SEARCH

## 3 шага для деплоя на Vercel + Fly.io

---

## Шаг 1: Задеплоить Backend на Fly.io

```bash
# 1. Перейти в backend директорию
cd backend

# 2. Установить Fly.io CLI
curl -L https://fly.io/install.sh | sh
export PATH="$HOME/.fly/bin:$PATH"

# 3. Авторизоваться
fly auth login

# 4. Создать приложение
fly launch --name nexus-search-api --region fra --no-deploy

# 5. Настроить секреты
fly secrets set JWT_SECRET=$(openssl rand -hex 32)
fly secrets set WEB3_PROVIDER_URI=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY

# 6. Задеплоить
fly deploy
```

**Backend URL:** `https://nexus-search-api.fly.dev`

---

## Шаг 2: Задеплоить Frontend на Vercel

### Вариант A: Через CLI (быстро)

```bash
# 1. Перейти в frontend директорию
cd frontend

# 2. Установить Vercel CLI
npm install -g vercel

# 3. Авторизоваться
vercel login

# 4. Настроить .env.local
cp .env.example .env.local
nano .env.local

# Изменить строку:
NEXT_PUBLIC_API_URL=https://nexus-search-api.fly.dev

# 5. Задеплоить
vercel --prod
```

### Вариант B: Через веб-интерфейс

1. Открыть https://vercel.com/new
2. Импортировать GitHub репозиторий
3. Указать Environment Variables:
   - `NEXT_PUBLIC_API_URL` = `https://nexus-search-api.fly.dev`
   - `NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID` = `nexus-search`
4. Нажать **Deploy**

**Frontend URL:** `https://nexus-search.vercel.app`

---

## Шаг 3: Проверить

```bash
# Проверить backend
curl https://nexus-search-api.fly.dev/health

# Проверить frontend
# Открыть в браузере https://your-frontend.vercel.app
```

---

## 🎉 Готово!

Ваш NEXUS Search задеплоен!

- **Frontend:** https://your-app.vercel.app
- **Backend:** https://nexus-search-api.fly.dev
- **API Docs:** https://nexus-search-api.fly.dev/docs

---

## 📝 Дополнительные команды

### Обновление backend

```bash
cd backend
fly deploy
```

### Обновление frontend

```bash
cd frontend
vercel --prod
```

### Просмотр логов

```bash
# Backend логи
fly logs

# Frontend логи
vercel logs
```

### Добавить домен

```bash
# Backend (Fly.io)
fly certs add api.your-domain.com

# Frontend (Vercel)
# Vercel Dashboard → Project Settings → Domains
```

---

## 💰 Стоимость

- **Vercel Hobby:** $0 (бесплатно)
- **Fly.io:** ~$5-10/month (pay as you go)

**Итого:** ~$5-10/month

---

## 🔧 Troubleshooting

### Backend не работает

```bash
# Проверить статус
fly status

# Проверить логи
fly logs

# Перезапустить
fly restart
```

### Frontend не подключается

Проверьте `.env.local`:
```bash
NEXT_PUBLIC_API_URL=https://nexus-search-api.fly.dev
```

### Web3 не работает

Проверьте `WEB3_PROVIDER_URI` в секретах:
```bash
fly secrets list
fly secrets set WEB3_PROVIDER_URI=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
```

---

## 📞 Поддержка

- GitHub Issues: https://github.com/zametkikostik/NEXUS-SEARCH/issues
- Email: intelligent.swallow.aybm@mask.me

---

**Успешного деплоя!** 🚀
