#!/bin/bash

# 🚀 EnergyOpti-Pro Deployment Script
# This script handles local development, testing, and cloud deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="energyopti-pro"
BACKEND_PORT=8000
FRONTEND_PORT=3000
NGINX_PORT=80

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_warning "Node.js is not installed. Frontend development may not work."
    fi
    
    # Check Python
    if ! command -v python &> /dev/null; then
        log_warning "Python is not installed. Backend development may not work."
    fi
    
    log_success "Dependencies check completed"
}

build_images() {
    log_info "Building Docker images..."
    
    docker-compose build --no-cache
    
    log_success "Docker images built successfully"
}

start_services() {
    log_info "Starting services..."
    
    docker-compose up -d
    
    log_success "Services started successfully"
}

stop_services() {
    log_info "Stopping services..."
    
    docker-compose down
    
    log_success "Services stopped successfully"
}

restart_services() {
    log_info "Restarting services..."
    
    docker-compose restart
    
    log_success "Services restarted successfully"
}

check_health() {
    log_info "Checking service health..."
    
    # Wait for services to be ready
    sleep 10
    
    # Check backend health
    if curl -f http://localhost:$BACKEND_PORT/api/health > /dev/null 2>&1; then
        log_success "Backend is healthy"
    else
        log_error "Backend health check failed"
        return 1
    fi
    
    # Check frontend
    if curl -f http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        log_success "Frontend is accessible"
    else
        log_warning "Frontend health check failed"
    fi
    
    # Check nginx
    if curl -f http://localhost:$NGINX_PORT > /dev/null 2>&1; then
        log_success "Nginx reverse proxy is working"
    else
        log_warning "Nginx health check failed"
    fi
    
    log_success "Health checks completed"
}

run_tests() {
    log_info "Running tests..."
    
    # Backend tests
    cd backend
    python -m pytest tests/ -v --cov=app --cov-report=html
    
    # Frontend tests (if available)
    if [ -d "../frontend" ]; then
        cd ../frontend
        if [ -f "package.json" ]; then
            npm test -- --watchAll=false
        fi
    fi
    
    cd ..
    
    log_success "Tests completed"
}

deploy_to_render() {
    log_info "Deploying to Render..."
    
    if [ -z "$RENDER_TOKEN" ] || [ -z "$RENDER_SERVICE_ID" ]; then
        log_error "RENDER_TOKEN and RENDER_SERVICE_ID environment variables are required"
        exit 1
    fi
    
    # Trigger Render deployment
    curl -X POST "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys" \
        -H "Authorization: Bearer $RENDER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"clearCache": "do_not_clear"}'
    
    log_success "Render deployment triggered"
}

deploy_to_vercel() {
    log_info "Deploying to Vercel..."
    
    if [ -z "$VERCEL_TOKEN" ]; then
        log_error "VERCEL_TOKEN environment variable is required"
        exit 1
    fi
    
    cd frontend
    
    # Install Vercel CLI if not present
    if ! command -v vercel &> /dev/null; then
        npm install -g vercel
    fi
    
    # Deploy to Vercel
    vercel --prod --token $VERCEL_TOKEN
    
    cd ..
    
    log_success "Vercel deployment completed"
}

show_logs() {
    log_info "Showing service logs..."
    
    docker-compose logs -f
}

show_status() {
    log_info "Service status:"
    
    docker-compose ps
    
    echo ""
    log_info "Service URLs:"
    echo "  Backend API: http://localhost:$BACKEND_PORT"
    echo "  Frontend: http://localhost:$FRONTEND_PORT"
    echo "  Nginx: http://localhost:$NGINX_PORT"
    echo "  Prometheus: http://localhost:9090"
    echo "  Grafana: http://localhost:3001"
}

cleanup() {
    log_info "Cleaning up..."
    
    docker-compose down -v --remove-orphans
    docker system prune -f
    
    log_success "Cleanup completed"
}

# Main script
case "${1:-help}" in
    "start")
        check_dependencies
        build_images
        start_services
        check_health
        show_status
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        check_health
        ;;
    "build")
        build_images
        ;;
    "test")
        run_tests
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "health")
        check_health
        ;;
    "deploy-render")
        deploy_to_render
        ;;
    "deploy-vercel")
        deploy_to_vercel
        ;;
    "deploy-all")
        deploy_to_render
        deploy_to_vercel
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|*)
        echo "🚀 EnergyOpti-Pro Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start         - Start all services"
        echo "  stop          - Stop all services"
        echo "  restart       - Restart all services"
        echo "  build         - Build Docker images"
        echo "  test          - Run tests"
        echo "  logs          - Show service logs"
        echo "  status        - Show service status"
        echo "  health        - Check service health"
        echo "  deploy-render - Deploy backend to Render"
        echo "  deploy-vercel - Deploy frontend to Vercel"
        echo "  deploy-all    - Deploy to both platforms"
        echo "  cleanup       - Clean up Docker resources"
        echo "  help          - Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  RENDER_TOKEN      - Render API token"
        echo "  RENDER_SERVICE_ID - Render service ID"
        echo "  VERCEL_TOKEN      - Vercel API token"
        ;;
esac
