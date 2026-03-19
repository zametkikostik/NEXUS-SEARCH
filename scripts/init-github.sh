#!/bin/bash

# NEXUS SEARCH - GitHub Deployment Script
# Автоматическая инициализация и пуш на GitHub

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     NEXUS SEARCH - GitHub Deployment Script              ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Функция для вывода сообщений
log_info() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[*]${NC} $1"
}

# Проверка наличия Git
check_git() {
    if ! command -v git &> /dev/null; then
        log_error "Git не установлен. Установите Git и попробуйте снова."
        exit 1
    fi
    log_info "Git найден: $(git --version)"
}

# Проверка наличия GitHub CLI
check_gh() {
    if command -v gh &> /dev/null; then
        log_info "GitHub CLI найден"
        return 0
    else
        log_warn "GitHub CLI не найден. Будем использовать git напрямую."
        return 1
    fi
}

# Инициализация Git
init_git() {
    log_step "Инициализация Git репозитория..."
    
    if [ -d ".git" ]; then
        log_warn "Git репозиторий уже инициализирован"
    else
        git init
        log_info "Git репозиторий инициализирован"
    fi
}

# Создание .gitignore если отсутствует
create_gitignore() {
    if [ ! -f ".gitignore" ]; then
        log_step "Создание .gitignore..."
        cat > .gitignore << 'EOF'
# Environment
.env
.env.local
.env.*.local

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
.eggs/
dist/
build/
venv/
env/
.pytest_cache/
.coverage
htmlcov/

# Node
node_modules/
.next/
out/
npm-debug.log*

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Docker
docker-compose.override.yml

# Contracts
contracts/artifacts/
contracts/cache/
EOF
        log_info ".gitignore создан"
    fi
}

# Добавление файлов в Git
add_files() {
    log_step "Добавление файлов в Git..."
    git add -A
    log_info "Файлы добавлены"
}

# Первый коммит
first_commit() {
    log_step "Создание первого коммита..."
    git commit -m "Initial commit: NEXUS Search v1.0.0

Full production-ready decentralized search engine with:
- Multi-provider search (Google, DuckDuckGo, Brave, Yandex, Dzen, Reddit)
- Web3 authentication (Wallet signature + JWT)
- IPFS storage integration
- Anti-bot layer with proxy rotation
- Content filtering (blacklist + ML)
- Tokenomics (ERC20 + Staking + Subscription NFT)
- Docker + CI/CD ready
- Complete documentation"
    log_info "Первый коммит создан"
}

# Добавление удалённого репозитория
add_remote() {
    local repo_url="$1"
    
    log_step "Добавление удалённого репозитория..."
    
    # Удаляем existing remote если есть
    git remote remove origin 2>/dev/null || true
    
    git remote add origin "$repo_url"
    log_info "Remote 'origin' добавлен: $repo_url"
}

# Пуш на GitHub
push_to_github() {
    local branch="${1:-main}"
    
    log_step "Пуш на GitHub (branch: $branch)..."
    
    # Переименовываем branch в main если нужно
    git branch -M "$branch" 2>/dev/null || true
    
    git push -u origin "$branch"
    log_info "Успешно запушено на GitHub"
}

# Создание репозитория через GitHub CLI
create_gh_repo() {
    local repo_name="$1"
    local description="$2"
    local is_public="${3:-true}"
    
    log_step "Создание репозитория на GitHub..."
    
    visibility_flag="--public"
    if [ "$is_public" = "false" ]; then
        visibility_flag="--private"
    fi
    
    gh repo create "$repo_name" $visibility_flag --description "$description" --source=. --remote=origin --push
    
    log_info "Репозиторий создан: https://github.com/$repo_name"
}

# Основная функция
main() {
    echo ""
    
    # Проверки
    check_git
    has_gh=$(check_gh && echo "true" || echo "false")
    
    echo ""
    log_step "Подготовка к деплою..."
    echo ""
    
    # Создание .gitignore
    create_gitignore
    
    # Инициализация Git
    init_git
    
    # Добавление файлов
    add_files
    
    # Первый коммит
    first_commit
    
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    # Спрашиваем про GitHub CLI
    if [ "$has_gh" = "true" ]; then
        echo -e "${YELLOW}Обнаружен GitHub CLI. Хотите создать репозиторий на GitHub?${NC}"
        echo "1) Да, создать публичный репозиторий"
        echo "2) Да, создать приватный репозиторий"
        echo "3) Нет, у меня уже есть URL репозитория"
        echo "4) Выйти"
        echo ""
        read -p "Выберите опцию (1-4): " choice
        
        case $choice in
            1)
                read -p "Введите имя репозитория (например: NEXUS-SEARCH): " repo_name
                read -p "Введите описание репозитория: " description
                create_gh_repo "$repo_name" "$description" "true"
                exit 0
                ;;
            2)
                read -p "Введите имя репозитория (например: NEXUS-SEARCH): " repo_name
                read -p "Введите описание репозитория: " description
                create_gh_repo "$repo_name" "$description" "false"
                exit 0
                ;;
            3)
                read -p "Введите URL репозитория (например: https://github.com/zametkikostik/NEXUS-SEARCH): " repo_url
                add_remote "$repo_url"
                ;;
            4)
                log_info "Выход. Для пуша выполните:"
                echo "  git remote add origin <your-repo-url>"
                echo "  git push -u origin main"
                exit 0
                ;;
            *)
                log_error "Неверная опция"
                exit 1
                ;;
        esac
    else
        read -p "Введите URL вашего GitHub репозитория: " repo_url
        add_remote "$repo_url"
    fi
    
    echo ""
    
    # Спрашиваем про branch
    read -p "Введите имя branch (по умолчанию: main): " branch
    branch=${branch:-main}
    
    # Пуш
    push_to_github "$branch"
    
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    log_info "🎉 Деплой завершён успешно!"
    echo ""
    echo "Ваш репозиторий:"
    echo -e "${BLUE}https://github.com/zametkikostik/$repo_name${NC}"
    echo ""
    echo "Следующие шаги:"
    echo "1. Настройте GitHub Actions (опционально)"
    echo "2. Добавьте environment secrets на GitHub"
    echo "3. Настройте CI/CD pipeline"
    echo ""
}

# Запуск
main
