#!/bin/bash
# QuantaEnergi Consolidated Deployment Script
# Handles local testing, cloud deployment, and production deployment

set -e

echo "🚀 QuantaEnergi Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVIRONMENT=${ENVIRONMENT:-development}
DEPLOYMENT_TYPE=${1:-test}

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking deployment prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Local testing function
test_local() {
    print_step "Testing local deployment..."
    
    # Build Docker image
    print_status "Building Docker image..."
    docker build -t quantaenergi-backend ./backend
    
    # Run container in background
    print_status "Starting container..."
    docker run -d --name quantaenergi-test -p 8000:8000 \
        -e DATABASE_URL="sqlite:///app/test.db" \
        -e REDIS_URL="redis://localhost:6379" \
        -e SECRET_KEY="test-secret-key" \
        quantaenergi-backend
    
    # Wait for container to start
    print_status "Waiting for container to start..."
    sleep 10
    
    # Test health endpoint
    print_status "Testing health endpoint..."
    if curl -f http://localhost:8000/health; then
        print_success "Backend health check passed!"
    else
        print_error "Backend health check failed!"
        docker logs quantaenergi-test
        exit 1
    fi
    
    # Cleanup
    print_status "Cleaning up test container..."
    docker stop quantaenergi-test
    docker rm quantaenergi-test
    
    print_success "Local test completed successfully!"
}

# Deploy backend to Railway
deploy_backend() {
    print_step "Deploying backend to Railway..."
    cd backend
    
    # Check if railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI not found. Install with: npm install -g @railway/cli"
        exit 1
    fi
    
    # Deploy to Railway
    railway up --detach
    print_success "Backend deployed to Railway"
    cd ..
}

# Deploy frontend to Vercel
deploy_frontend() {
    print_step "Deploying frontend to Vercel..."
    cd frontend
    
    # Check if vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        print_error "Vercel CLI not found. Install with: npm install -g vercel"
        exit 1
    fi
    
    # Build frontend
    print_status "Building frontend..."
    npm run build
    
    # Deploy to Vercel
    vercel --prod
    print_success "Frontend deployed to Vercel"
    cd ..
}

# Deploy to cloud
deploy_cloud() {
    print_step "Starting cloud deployment..."
    
    # Deploy backend
    deploy_backend
    
    # Wait a bit for backend to be ready
    print_status "Waiting for backend to be ready..."
    sleep 30
    
    # Deploy frontend
    deploy_frontend
    
    print_success "Cloud deployment completed successfully!"
    print_warning "Next steps:"
    echo "1. Update CORS_ORIGINS in Railway with your Vercel domain"
    echo "2. Test the deployed application"
    echo "3. Configure environment variables in Railway dashboard"
}

# Production deployment with Docker Compose
deploy_production() {
    print_step "Starting production deployment..."
    
    # Environment setup
    print_status "Setting up production environment..."
    export NODE_ENV=production
    export PYTHON_ENV=production
    export DATABASE_URL="postgresql://user:pass@localhost:5432/quantaenergi_prod"
    export REDIS_URL="redis://localhost:6379"
    export JWT_SECRET=$(openssl rand -base64 32 2>/dev/null || echo "fallback-secret-key")
    export ENCRYPTION_KEY=$(openssl rand -base64 32 2>/dev/null || echo "fallback-encryption-key")
    
    # Create production directories
    mkdir -p logs data/postgres data/redis ssl
    
    # Stop any existing containers
    print_status "Stopping existing containers..."
    docker-compose down --remove-orphans 2>/dev/null || true
    
    # Build and start with production configuration
    print_status "Building and starting production services..."
    docker-compose -f docker-compose.yml up -d --build
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 30
    
    # Health checks
    print_step "Running health checks..."
    
    # Backend health check
    print_status "Checking backend health..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend is healthy"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend health check failed"
            exit 1
        fi
        sleep 2
    done
    
    # Frontend health check
    print_status "Checking frontend health..."
    for i in {1..30}; do
        if curl -f http://localhost:3000 > /dev/null 2>&1; then
            print_success "Frontend is healthy"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Frontend health check failed"
            exit 1
        fi
        sleep 2
    done
    
    print_success "Production deployment completed successfully!"
}

# Docker Compose deployment with scaling
deploy_docker() {
    print_step "Starting Docker Compose deployment with scaling..."
    
    # Stop any existing containers
    print_status "Stopping existing containers..."
    docker-compose down --remove-orphans 2>/dev/null || true
    
    # Build images
    print_status "Building Docker images..."
    docker-compose build --no-cache
    
    # Start Redis Cluster first
    print_status "Starting Redis Cluster..."
    docker-compose up -d redis-node-1 redis-node-2 redis-node-3 2>/dev/null || true
    
    # Wait for Redis nodes to be ready
    print_status "Waiting for Redis nodes to be ready..."
    sleep 10
    
    # Start backend instances
    print_status "Starting backend instances..."
    docker-compose up -d backend-1 backend-2 backend-3 2>/dev/null || true
    
    # Wait for backends to be ready
    print_status "Waiting for backend instances to be ready..."
    sleep 20
    
    # Start frontend instances
    print_status "Starting frontend instances..."
    docker-compose up -d frontend-1 frontend-2 2>/dev/null || true
    
    # Wait for frontends to be ready
    print_status "Waiting for frontend instances to be ready..."
    sleep 15
    
    # Start Nginx load balancer
    print_status "Starting Nginx load balancer..."
    docker-compose up -d nginx 2>/dev/null || true
    
    # Wait for all services to be ready
    print_status "Waiting for all services to be ready..."
    sleep 10
    
    print_success "Docker Compose deployment completed!"
}

# Show usage
show_usage() {
    echo "Usage: $0 [test|local|cloud|production|docker]"
    echo ""
    echo "Commands:"
    echo "  test        - Run local tests and show deployment status (default)"
    echo "  local       - Test deployment locally with Docker"
    echo "  cloud       - Deploy to Railway (backend) and Vercel (frontend)"
    echo "  production  - Deploy to production with Docker Compose"
    echo "  docker      - Deploy with Docker Compose and scaling"
    echo ""
    echo "Environment Variables:"
    echo "  ENVIRONMENT - Set deployment environment (development, production)"
    echo ""
    echo "Examples:"
    echo "  $0 test       # Run local tests"
    echo "  $0 local      # Test locally"
    echo "  $0 cloud      # Deploy to cloud"
    echo "  $0 production # Deploy to production"
    echo "  ENVIRONMENT=production $0 docker  # Deploy with Docker Compose"
}

# Main function
main() {
    case "${DEPLOYMENT_TYPE}" in
        "test")
            check_prerequisites
            test_local
            echo ""
            print_warning "To deploy to cloud, run: $0 cloud"
            print_warning "To deploy to production, run: $0 production"
            ;;
        "local")
            check_prerequisites
            test_local
            ;;
        "cloud")
            check_prerequisites
            deploy_cloud
            ;;
        "production")
            check_prerequisites
            deploy_production
            ;;
        "docker")
            check_prerequisites
            deploy_docker
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
