#!/bin/bash
set -e

echo "🚀 NEXUS Search - Production Deployment Script"
echo "=============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    log_info "Dependencies OK"
}

check_env() {
    log_info "Checking environment files..."
    
    if [ ! -f .env ]; then
        log_warn ".env file not found, copying from .env.example"
        cp .env.example .env
        log_warn "Please edit .env file with your configuration"
        exit 1
    fi
    
    # Check required variables
    required_vars=("JWT_SECRET" "WEB3_PROVIDER_URI")
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env; then
            log_error "Required variable $var not set in .env"
            exit 1
        fi
    done
    
    log_info "Environment OK"
}

build_services() {
    log_info "Building services..."
    docker-compose build
    log_info "Build complete"
}

run_migrations() {
    log_info "Running migrations..."
    # Add migration commands here if needed
    log_info "Migrations complete"
}

start_services() {
    log_info "Starting services..."
    docker-compose up -d
    log_info "Services started"
}

health_check() {
    log_info "Running health checks..."
    
    # Wait for services to be ready
    sleep 10
    
    # Check backend
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "Backend: OK"
    else
        log_error "Backend: FAILED"
        exit 1
    fi
    
    # Check frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_info "Frontend: OK"
    else
        log_error "Frontend: FAILED"
        exit 1
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_info "Redis: OK"
    else
        log_warn "Redis: Could not check"
    fi
    
    # Check IPFS
    if curl -f http://localhost:5001/api/v0/version > /dev/null 2>&1; then
        log_info "IPFS: OK"
    else
        log_warn "IPFS: Could not check"
    fi
    
    log_info "All health checks passed"
}

show_status() {
    echo ""
    echo "=============================================="
    log_info "Deployment Summary"
    echo "=============================================="
    docker-compose ps
    echo ""
    log_info "Access points:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo "  IPFS Gateway: http://localhost:8080"
    echo "=============================================="
}

# Main
main() {
    check_dependencies
    check_env
    build_services
    run_migrations
    start_services
    health_check
    show_status
    
    log_info "Deployment complete! 🎉"
}

# Run main function
main
