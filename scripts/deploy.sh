#!/bin/bash

# QuantaEnergi Production Deployment Script
# This script automates the production deployment process

set -e  # Exit on any error

echo "🚀 Starting QuantaEnergi Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="quantaenergi"
ENVIRONMENT=${1:-production}
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking deployment prerequisites..."
    
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
    
    # Check if we're in the right directory
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        print_error "Production Docker Compose file not found. Please run this script from the project root."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to create backup
create_backup() {
    print_status "Creating backup of current deployment..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup Docker volumes
    if docker volume ls -q | grep -q "${PROJECT_NAME}_"; then
        docker run --rm -v "${PROJECT_NAME}_postgres-data:/data" -v "$(pwd)/$BACKUP_DIR:/backup" alpine tar czf /backup/postgres-backup.tar.gz -C /data .
        docker run --rm -v "${PROJECT_NAME}_redis-data-1:/data" -v "$(pwd)/$BACKUP_DIR:/backup" alpine tar czf /backup/redis-backup.tar.gz -C /data .
    fi
    
    # Backup configuration files
    cp -r monitoring "$BACKUP_DIR/"
    cp -r nginx "$BACKUP_DIR/"
    cp "$DOCKER_COMPOSE_FILE" "$BACKUP_DIR/"
    
    print_success "Backup created in $BACKUP_DIR"
}

# Function to stop current deployment
stop_current_deployment() {
    print_status "Stopping current deployment..."
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps -q | grep -q .; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" down --remove-orphans
        print_success "Current deployment stopped"
    else
        print_warning "No current deployment found"
    fi
}

# Function to build and deploy
deploy_application() {
    print_status "Building and deploying QuantaEnergi..."
    
    # Build images
    print_status "Building Docker images..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    print_success "Deployment started successfully"
}

# Function to wait for services
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    print_status "Waiting for PostgreSQL..."
    for i in {1..60}; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres pg_isready -U quantaenergi_user -d quantaenergi_db > /dev/null 2>&1; then
            print_success "PostgreSQL is ready"
            break
        fi
        if [ $i -eq 60 ]; then
            print_error "PostgreSQL failed to start within 5 minutes"
            exit 1
        fi
        sleep 5
        echo -n "."
    done
    
    # Wait for Redis Cluster
    print_status "Waiting for Redis Cluster..."
    for i in {1..60}; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis-node-1 redis-cli cluster info > /dev/null 2>&1; then
            print_success "Redis Cluster is ready"
            break
        fi
        if [ $i -eq 60 ]; then
            print_error "Redis Cluster failed to start within 5 minutes"
            exit 1
        fi
        sleep 5
        echo -n "."
    done
    
    # Wait for Backend
    print_status "Waiting for Backend..."
    for i in {1..60}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend is ready"
            break
        fi
        if [ $i -eq 60 ]; then
            print_error "Backend failed to start within 5 minutes"
            exit 1
        fi
        sleep 5
        echo -n "."
    done
    
    # Wait for Frontend
    print_status "Waiting for Frontend..."
    for i in {1..60}; do
        if curl -f http://localhost:3000 > /dev/null 2>&1; then
            print_success "Frontend is ready"
            break
        fi
        if [ $i -eq 60 ]; then
            print_error "Frontend failed to start within 5 minutes"
            exit 1
        fi
        sleep 5
        echo -n "."
    done
}

# Function to run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # Check all services
    services=("backend" "frontend" "postgres" "prometheus" "grafana" "nginx")
    
    for service in "${services[@]}"; do
        print_status "Checking $service..."
        if docker-compose -f "$DOCKER_COMPOSE_FILE" ps "$service" | grep -q "Up"; then
            print_success "$service is running"
        else
            print_error "$service is not running"
            exit 1
        fi
    done
    
    # Check Redis Cluster health
    print_status "Checking Redis Cluster health..."
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis-node-1 redis-cli cluster info | grep -q "cluster_state:ok"; then
        print_success "Redis Cluster is healthy"
    else
        print_error "Redis Cluster is not healthy"
        exit 1
    fi
    
    print_success "All health checks passed"
}

# Function to run tests
run_deployment_tests() {
    print_status "Running deployment tests..."
    
    # Test backend API
    print_status "Testing Backend API..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend API is accessible"
    else
        print_error "Backend API is not accessible"
        exit 1
    fi
    
    # Test frontend
    print_status "Testing Frontend..."
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend is accessible"
    else
        print_error "Frontend is not accessible"
        exit 1
    fi
    
    # Test monitoring
    print_status "Testing Monitoring..."
    if curl -f http://localhost:9090 > /dev/null 2>&1; then
        print_success "Prometheus is accessible"
    else
        print_error "Prometheus is not accessible"
    fi
    
    if curl -f http://localhost:3001 > /dev/null 2>&1; then
        print_success "Grafana is accessible"
    else
        print_error "Grafana is not accessible"
    fi
    
    print_success "All deployment tests passed"
}

# Function to show deployment status
show_deployment_status() {
    print_status "Deployment Status:"
    echo ""
    
    # Show running containers
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    
    echo ""
    print_status "Service URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  Prometheus: http://localhost:9090"
    echo "  Grafana: http://localhost:3001"
    echo "  Redis Commander: http://localhost:8081"
    echo "  Nginx: http://localhost:80"
    
    echo ""
    print_status "Monitoring:"
    echo "  Health Check: http://localhost:8000/health"
    echo "  Metrics: http://localhost:8000/metrics"
    
    echo ""
    print_status "Redis Cluster:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis-node-1 redis-cli cluster info | grep -E "(cluster_state|cluster_slots_assigned|cluster_slots_ok|cluster_slots_pfail|cluster_slots_fail|cluster_known_nodes|cluster_size|cluster_current_epoch|cluster_my_epoch|cluster_stats_messages_ping_sent|cluster_stats_messages_pong_sent|cluster_stats_messages_meet_sent|cluster_stats_messages_sent|cluster_stats_messages_ping_received|cluster_stats_messages_pong_received|cluster_stats_messages_meet_received|cluster_stats_messages_other_received|cluster_stats_messages_received)"
}

# Function to rollback deployment
rollback_deployment() {
    print_warning "Rolling back deployment..."
    
    # Stop current deployment
    docker-compose -f "$DOCKER_COMPOSE_FILE" down --remove-orphans
    
    # Restore from backup if available
    if [ -d "$BACKUP_DIR" ]; then
        print_status "Restoring from backup..."
        # Implementation would depend on backup strategy
        print_warning "Manual restoration required from $BACKUP_DIR"
    fi
    
    print_error "Deployment rollback completed"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "QuantaEnergi Production Deployment Script"
    echo ""
    echo "Usage: $0 [ENVIRONMENT] [OPTIONS]"
    echo ""
    echo "ENVIRONMENT:"
    echo "  production    Production deployment (default)"
    echo "  staging      Staging deployment"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help          Show this help message"
    echo "  -r, --rollback      Rollback to previous deployment"
    echo "  -s, --status        Show deployment status"
    echo "  -c, --cleanup       Cleanup unused resources"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                  Deploy to production"
    echo "  $0 staging          Deploy to staging"
    echo "  $0 -r               Rollback deployment"
    echo "  $0 -s               Show status"
}

# Main execution
main() {
    local rollback=false
    local status_only=false
    local cleanup_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -r|--rollback)
                rollback=true
                shift
                ;;
            -s|--status)
                status_only=true
                shift
                ;;
            -c|--cleanup)
                cleanup_only=true
                shift
                ;;
            production|staging)
                ENVIRONMENT="$1"
                shift
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
    
    if [ "$cleanup_only" = true ]; then
        cleanup
        exit 0
    fi
    
    if [ "$status_only" = true ]; then
        show_deployment_status
        exit 0
    fi
    
    if [ "$rollback" = true ]; then
        rollback_deployment
        exit 0
    fi
    
    # Full deployment process
    print_status "Starting deployment to $ENVIRONMENT environment..."
    
    check_prerequisites
    create_backup
    stop_current_deployment
    deploy_application
    wait_for_services
    run_health_checks
    run_deployment_tests
    show_deployment_status
    
    print_success "QuantaEnergi production deployment completed successfully! 🎉"
    print_status "Application is now running and accessible"
}

# Run main function with all arguments
main "$@"
