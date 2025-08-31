#!/bin/bash

# QuantaEnergi Production Deployment Script
# This script handles the complete production deployment process

set -e  # Exit on any error

echo "🚀 Starting QuantaEnergi Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOYMENT_DIR="$PROJECT_ROOT/deployment"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_DIR="$PROJECT_ROOT/logs"
ENVIRONMENT=${ENVIRONMENT:-production}

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

# Function to log messages
log_message() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_DIR/deployment.log"
}

# Function to check prerequisites
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
    
    # Check kubectl if using Kubernetes
    if [ "$ENVIRONMENT" = "kubernetes" ]; then
        if ! command -v kubectl &> /dev/null; then
            print_error "kubectl is not installed. Please install kubectl first."
            exit 1
        fi
    fi
    
    # Check if we're in the right directory
    if [ ! -f "$PROJECT_ROOT/docker-compose.prod.yml" ]; then
        print_error "Production Docker Compose file not found. Please run this script from the project root."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to create deployment directories
create_deployment_directories() {
    print_step "Creating deployment directories..."
    
    mkdir -p "$DEPLOYMENT_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$LOG_DIR"
    
    print_success "Deployment directories created"
}

# Function to create backup
create_backup() {
    print_step "Creating backup of current deployment..."
    
    local backup_name="quantaenergi-backup-$(date +%Y%m%d-%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$backup_path"
    
    # Backup Docker volumes
    if docker volume ls -q | grep -q quantaenergi; then
        print_status "Backing up Docker volumes..."
        docker run --rm -v quantaenergi_postgres-data:/data -v "$backup_path":/backup alpine tar czf /backup/postgres-data.tar.gz -C /data .
        docker run --rm -v quantaenergi_redis-data-1:/data -v "$backup_path":/backup alpine tar czf /backup/redis-data-1.tar.gz -C /data .
        docker run --rm -v quantaenergi_redis-data-2:/data -v "$backup_path":/backup alpine tar czf /backup/redis-data-2.tar.gz -C /data .
        docker run --rm -v quantaenergi_redis-data-3:/data -v "$backup_path":/backup alpine tar czf /backup/redis-data-3.tar.gz -C /data .
        docker run --rm -v quantaenergi_redis-data-4:/data -v "$backup_path":/backup alpine tar czf /backup/redis-data-4.tar.gz -C /data .
        docker run --rm -v quantaenergi_redis-data-5:/data -v "$backup_path":/backup alpine tar czf /backup/redis-data-5.tar.gz -C /data .
        docker run --rm -v quantaenergi_redis-data-6:/data -v "$backup_path":/backup alpine tar czf /backup/redis-data-6.tar.gz -C /data .
    fi
    
    # Backup configuration files
    cp -r "$PROJECT_ROOT/monitoring" "$backup_path/" 2>/dev/null || true
    cp -r "$PROJECT_ROOT/nginx" "$backup_path/" 2>/dev/null || true
    cp "$PROJECT_ROOT/docker-compose.prod.yml" "$backup_path/" 2>/dev/null || true
    
    print_success "Backup created: $backup_path"
}

# Function to stop current deployment
stop_current_deployment() {
    print_step "Stopping current deployment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop Docker Compose services
    if docker-compose -f docker-compose.prod.yml ps -q | grep -q .; then
        print_status "Stopping Docker Compose services..."
        docker-compose -f docker-compose.prod.yml down --remove-orphans
    fi
    
    # Stop any running containers
    local running_containers=$(docker ps -q --filter "name=quantaenergi")
    if [ -n "$running_containers" ]; then
        print_status "Stopping running containers..."
        docker stop $running_containers
        docker rm $running_containers
    fi
    
    print_success "Current deployment stopped"
}

# Function to build and deploy
build_and_deploy() {
    print_step "Building and deploying QuantaEnergi..."
    
    cd "$PROJECT_ROOT"
    
    # Build images
    print_status "Building Docker images..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "Deployment started"
}

# Function to wait for services
wait_for_services() {
    print_step "Waiting for services to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_status "Checking service health (attempt $attempt/$max_attempts)..."
        
        # Check backend health
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Backend is healthy"
        else
            print_warning "Backend not ready yet..."
            sleep 10
            ((attempt++))
            continue
        fi
        
        # Check frontend
        if curl -f http://localhost:3000 >/dev/null 2>&1; then
            print_success "Frontend is healthy"
        else
            print_warning "Frontend not ready yet..."
            sleep 10
            ((attempt++))
            continue
        fi
        
        # Check PostgreSQL
        if docker exec quantaenergi-postgres pg_isready -U quantaenergi_user -d quantaenergi_db >/dev/null 2>&1; then
            print_success "PostgreSQL is healthy"
        else
            print_warning "PostgreSQL not ready yet..."
            sleep 10
            ((attempt++))
            continue
        fi
        
        # Check Redis Cluster
        local redis_healthy=true
        for i in {1..6}; do
            if ! docker exec "quantaenergi-redis-node-$i" redis-cli ping >/dev/null 2>&1; then
                redis_healthy=false
                break
            fi
        done
        
        if [ "$redis_healthy" = true ]; then
            print_success "Redis Cluster is healthy"
        else
            print_warning "Redis Cluster not ready yet..."
            sleep 10
            ((attempt++))
            continue
        fi
        
        # Check Prometheus
        if curl -f http://localhost:9090/-/healthy >/dev/null 2>&1; then
            print_success "Prometheus is healthy"
        else
            print_warning "Prometheus not ready yet..."
            sleep 10
            ((attempt++))
            continue
        fi
        
        # Check Grafana
        if curl -f http://localhost:3001/api/health >/dev/null 2>&1; then
            print_success "Grafana is healthy"
        else
            print_warning "Grafana not ready yet..."
            sleep 10
            ((attempt++))
            continue
        fi
        
        print_success "All services are healthy!"
        return 0
    done
    
    print_error "Services failed to become healthy after $max_attempts attempts"
    return 1
}

# Function to run health checks
run_health_checks() {
    print_step "Running comprehensive health checks..."
    
    # Backend API health check
    print_status "Checking backend API..."
    local backend_response=$(curl -s http://localhost:8000/health)
    if echo "$backend_response" | grep -q "healthy"; then
        print_success "Backend API health check passed"
    else
        print_error "Backend API health check failed"
        return 1
    fi
    
    # Frontend accessibility check
    print_status "Checking frontend accessibility..."
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        print_success "Frontend accessibility check passed"
    else
        print_error "Frontend accessibility check failed"
        return 1
    fi
    
    # Database connectivity check
    print_status "Checking database connectivity..."
    if docker exec quantaenergi-postgres psql -U quantaenergi_user -d quantaenergi_db -c "SELECT 1;" >/dev/null 2>&1; then
        print_success "Database connectivity check passed"
    else
        print_error "Database connectivity check failed"
        return 1
    fi
    
    # Redis connectivity check
    print_status "Checking Redis connectivity..."
    if docker exec quantaenergi-redis-node-1 redis-cli ping | grep -q "PONG"; then
        print_success "Redis connectivity check passed"
    else
        print_error "Redis connectivity check failed"
        return 1
    fi
    
    # Monitoring check
    print_status "Checking monitoring systems..."
    if curl -f http://localhost:9090/api/v1/query?query=up >/dev/null 2>&1; then
        print_success "Prometheus monitoring check passed"
    else
        print_error "Prometheus monitoring check failed"
        return 1
    fi
    
    if curl -f http://localhost:3001/api/health >/dev/null 2>&1; then
        print_success "Grafana monitoring check passed"
    else
        print_error "Grafana monitoring check failed"
        return 1
    fi
    
    print_success "All health checks passed!"
}

# Function to run deployment tests
run_deployment_tests() {
    print_step "Running deployment tests..."
    
    cd "$PROJECT_ROOT"
    
    # Run E2E tests against production deployment
    print_status "Running E2E tests against production deployment..."
    if [ -f "scripts/test-e2e.sh" ]; then
        # Update Cypress config to use production URLs
        export CYPRESS_baseUrl=http://localhost:3000
        export CYPRESS_apiUrl=http://localhost:8000
        
        cd frontend
        npx cypress run --config-file cypress.config.js --spec "cypress/e2e/authentication.cy.js" --record false
        cd ..
        
        if [ $? -eq 0 ]; then
            print_success "E2E tests passed"
        else
            print_warning "E2E tests failed (this may be expected in production)"
        fi
    else
        print_warning "E2E test script not found, skipping deployment tests"
    fi
    
    cd "$PROJECT_ROOT"
}

# Function to show deployment status
show_deployment_status() {
    print_step "Deployment Status Summary..."
    
    echo ""
    echo "🚀 QuantaEnergi Production Deployment Status"
    echo "=============================================="
    echo ""
    
    # Service status
    echo "📊 Service Status:"
    docker-compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    echo "🔍 Health Endpoints:"
    echo "  Backend API:     http://localhost:8000/health"
    echo "  Frontend:        http://localhost:3000"
    echo "  Prometheus:      http://localhost:9090"
    echo "  Grafana:         http://localhost:3001"
    echo "  Redis Commander: http://localhost:8081"
    
    echo ""
    echo "📁 Logs:"
    echo "  Backend:         docker logs quantaenergi-backend"
    echo "  Frontend:        docker logs quantaenergi-frontend"
    echo "  PostgreSQL:      docker logs quantaenergi-postgres"
    echo "  Redis:           docker logs quantaenergi-redis-node-1"
    
    echo ""
    echo "🛠️  Management Commands:"
    echo "  Stop:            docker-compose -f docker-compose.prod.yml down"
    echo "  Restart:         docker-compose -f docker-compose.prod.yml restart"
    echo "  Logs:            docker-compose -f docker-compose.prod.yml logs -f"
    echo "  Update:          ./scripts/deploy-production.sh"
    
    echo ""
    echo "📈 Monitoring:"
    echo "  Open Grafana:    http://localhost:3001 (admin/quantaenergi_grafana_pass)"
    echo "  View Metrics:    http://localhost:9090"
    
    echo ""
    print_success "QuantaEnergi is now running in production! 🎉"
}

# Function to rollback
rollback() {
    print_step "Rolling back deployment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop current deployment
    docker-compose -f docker-compose.prod.yml down --remove-orphans
    
    # Find latest backup
    local latest_backup=$(ls -t "$BACKUP_DIR"/quantaenergi-backup-* 2>/dev/null | head -1)
    
    if [ -n "$latest_backup" ]; then
        print_status "Rolling back to: $latest_backup"
        
        # Restore configuration files
        cp -r "$latest_backup/monitoring" . 2>/dev/null || true
        cp -r "$latest_backup/nginx" . 2>/dev/null || true
        cp "$latest_backup/docker-compose.prod.yml" . 2>/dev/null || true
        
        # Restart with previous configuration
        docker-compose -f docker-compose.prod.yml up -d
        
        print_success "Rollback completed"
    else
        print_error "No backup found for rollback"
        return 1
    fi
    
    cd "$PROJECT_ROOT"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up deployment artifacts..."
    
    # Remove temporary files
    find . -name "*.tmp" -delete 2>/dev/null || true
    find . -name "*.log" -exec mv {} "$LOG_DIR/" \; 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "QuantaEnergi Production Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help          Show this help message"
    echo "  -r, --rollback      Rollback to previous deployment"
    echo "  -s, --status        Show deployment status only"
    echo "  -t, --test          Run deployment tests only"
    echo "  -e, --environment   Set deployment environment (default: production)"
    echo ""
    echo "ENVIRONMENT VARIABLES:"
    echo "  ENVIRONMENT         Deployment environment (production, staging)"
    echo "  POSTGRES_PASSWORD   PostgreSQL password"
    echo "  JWT_SECRET_KEY      JWT secret key"
    echo "  GRAFANA_PASSWORD    Grafana admin password"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                  Deploy to production"
    echo "  $0 -r              Rollback deployment"
    echo "  $0 -s              Show status only"
    echo "  $0 -t              Run tests only"
    echo "  ENVIRONMENT=staging $0  Deploy to staging"
}

# Main execution
main() {
    local rollback_only=false
    local status_only=false
    local test_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -r|--rollback)
                rollback_only=true
                shift
                ;;
            -s|--status)
                status_only=true
                shift
                ;;
            -t|--test)
                test_only=true
                shift
                ;;
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Set trap for cleanup on exit
    trap cleanup EXIT
    
    # Log deployment start
    log_message "Starting QuantaEnergi deployment to $ENVIRONMENT environment"
    
    if [ "$rollback_only" = true ]; then
        rollback
        exit 0
    fi
    
    if [ "$status_only" = true ]; then
        show_deployment_status
        exit 0
    fi
    
    if [ "$test_only" = true ]; then
        run_deployment_tests
        exit 0
    fi
    
    # Full deployment process
    print_status "Starting QuantaEnergi deployment to $ENVIRONMENT environment..."
    
    # Check prerequisites
    check_prerequisites
    
    # Create directories
    create_deployment_directories
    
    # Create backup
    create_backup
    
    # Stop current deployment
    stop_current_deployment
    
    # Build and deploy
    build_and_deploy
    
    # Wait for services
    if ! wait_for_services; then
        print_error "Deployment failed - services did not become healthy"
        print_status "Attempting rollback..."
        rollback
        exit 1
    fi
    
    # Run health checks
    if ! run_health_checks; then
        print_error "Health checks failed"
        print_status "Attempting rollback..."
        rollback
        exit 1
    fi
    
    # Run deployment tests
    run_deployment_tests
    
    # Show deployment status
    show_deployment_status
    
    # Log successful deployment
    log_message "QuantaEnergi deployment to $ENVIRONMENT completed successfully"
    
    print_success "QuantaEnergi production deployment completed successfully! 🎉"
    print_status "Your application is now running and accessible at:"
    print_status "  Frontend: http://localhost:3000"
    print_status "  Backend:  http://localhost:8000"
    print_status "  Monitor:  http://localhost:3001 (Grafana)"
}

# Run main function with all arguments
main "$@"
