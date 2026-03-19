# 🚀 Инструкция по деплою на GitHub

## Быстрый старт (3 команды)

```bash
# 1. Инициализировать Git и запушить
git init
git add -A
git commit -m "Initial commit: NEXUS Search"

# 2. Добавить remote (замените на свой URL)
git remote add origin https://github.com/zametkikostik/NEXUS-SEARCH.git

# 3. Запушить
git branch -M main
git push -u origin main
```

---

## 📋 Подробная инструкция

### Шаг 1: Подготовка репозитория на GitHub

#### Вариант A: Через браузер (рекомендуется)

1. Откройте https://github.com/new
2. Введите имя репозитория: `NEXUS-SEARCH`
3. Описание: `Decentralized Privacy-First Search Engine with Web3`
4. Выберите **Public** или **Private**
5. **НЕ** ставьте галочки на "Initialize this repository with..."
6. Нажмите **Create repository**

#### Вариант B: Через GitHub CLI

```bash
# Установить gh CLI (если не установлен)
# Ubuntu/Debian:
sudo apt install gh

# Авторизация
gh auth login

# Создать репозиторий
gh repo create NEXUS-SEARCH --public --description "Decentralized Search Engine" --source=. --remote=origin --push
```

### Шаг 2: Инициализация локального репозитория

```bash
# Перейти в директорию проекта
cd /home/kostik/Рабочий\ стол/папка\ для\ программирования/NEXUS\ SEARCH

# Инициализировать Git
git init

# Проверить статус
git status
```

### Шаг 3: Добавить файлы

```bash
# Добавить все файлы
git add -A

# Или выборочно (рекомендуется)
git add README.md
git add backend/
git add frontend/
git add contracts/
git add docker-compose.yml
git add scripts/

# Проверить что добавлено
git status
```

### Шаг 4: Создать первый коммит

```bash
git commit -m "Initial commit: NEXUS Search v1.0.0

Features:
- Multi-provider search (6 providers)
- Web3 authentication
- IPFS storage
- Anti-bot layer
- Tokenomics (ERC20 + Staking + NFT)
- Docker + CI/CD ready"
```

### Шаг 5: Добавить удалённый репозиторий

```bash
# Добавить remote
git remote add origin https://github.com/zametkikostik/NEXUS-SEARCH.git

# Проверить
git remote -v
```

### Шаг 6: Запушить на GitHub

```bash
# Переименовать branch в main
git branch -M main

# Запушить
git push -u origin main
```

---

## 🤖 Автоматический скрипт

Вместо ручных команд можно использовать автоматический скрипт:

```bash
# Перейти в директорию проекта
cd /home/kostik/Рабочий\ стол/папка\ для\ программирования/NEXUS\ SEARCH

# Запустить скрипт инициализации
./scripts/init-github.sh
```

Скрипт автоматически:
1. Инициализирует Git
2. Создаст .gitignore
3. Добавит все файлы
4. Создаст первый коммит
5. Попросит ввести URL репозитория
6. Запушит на GitHub

---

## 🔐 Настройка GitHub Secrets (для CI/CD)

После пуша настройте secrets для автоматического деплоя:

1. Откройте репозиторий на GitHub
2. Перейдите в **Settings** → **Secrets and variables** → **Actions**
3. Добавьте следующие secrets:

### Для деплоя контрактов:
```
PRIVATE_KEY=your_wallet_private_key
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
ETHERSCAN_API_KEY=your_etherscan_api_key
```

### Для деплоя backend:
```
WEB3_PROVIDER_URI=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
JWT_SECRET=your-super-secret-jwt-key
SENTRY_DSN=https://your-sentry-dsn
```

### Для frontend:
```
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=your-walletconnect-id
```

---

## ✅ Проверка после деплоя

### 1. Проверить файлы на GitHub
```
Откройте https://github.com/zametkikostik/NEXUS-SEARCH
Убедитесь что все файлы загружены
```

### 2. Проверить CI/CD
```
Перейдите в Actions tab
Убедитесь что pipeline запустился
Все тесты должны пройти успешно
```

### 3. Проверить README
```
Убедитесь что README.md отображается корректно
Все ссылки работают
```

---

## 🔧 Дополнительные команды

### Обновление после изменений

```bash
# Добавить изменения
git add -A

# Закоммитить
git commit -m "Add new feature"

# Запушить
git push origin main
```

### Ветка для разработки

```bash
# Создать dev branch
git checkout -b develop

# Запушить
git push -u origin develop
```

### Теги версий

```bash
# Создать тег
git tag -a v1.0.0 -m "Release version 1.0.0"

# Запушить теги
git push origin --tags
```

---

## 📊 GitHub Pages (опционально)

Для хостинга frontend на GitHub Pages:

1. Откройте **Settings** → **Pages**
2. Source: **GitHub Actions**
3. Настройте workflow для билда

Или используйте Vercel/Netlify для frontend.

---

## 🎯 Следующие шаги после деплоя

1. ✅ Настроить GitHub Actions (CI/CD)
2. ✅ Добавить environment secrets
3. ✅ Настроить автоматический деплою
4. ✅ Добавить badge в README
5. ✅ Настроить project board
6. ✅ Добавить contributors

---

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте что Git установлен: `git --version`
2. Проверьте подключение к GitHub: `gh auth status`
3. Убедитесь что у вас есть доступ к репозиторию

---

**Готово!** Ваш NEXUS Search теперь на GitHub! 🎉
