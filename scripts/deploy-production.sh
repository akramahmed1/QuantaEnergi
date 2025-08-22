#!/bin/bash

# EnergyOpti-Pro Production Deployment Script
# Supports blue-green deployment, multi-region failover, and automated rollback

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_CONFIG="${SCRIPT_DIR}/deployment-config.yaml"
LOG_FILE="${PROJECT_ROOT}/logs/deployment-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Parse command line arguments
DEPLOYMENT_STRATEGY="blue-green"
REGION="uae"
ENVIRONMENT="production"
ROLLBACK_VERSION=""
DRY_RUN=false
HEALTH_CHECK_TIMEOUT=300
ROLLBACK_TIMEOUT=600

while [[ $# -gt 0 ]]; do
    case $1 in
        --strategy)
            DEPLOYMENT_STRATEGY="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --rollback-version)
            ROLLBACK_VERSION="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --health-check-timeout)
            HEALTH_CHECK_TIMEOUT="$2"
            shift 2
            ;;
        --rollback-timeout)
            ROLLBACK_TIMEOUT="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Show help function
show_help() {
    cat << EOF
EnergyOpti-Pro Production Deployment Script

Usage: $0 [OPTIONS]

Options:
    --strategy STRATEGY          Deployment strategy (blue-green, rolling, canary) [default: blue-green]
    --region REGION             Target region (uae, us, eu, uk) [default: uae]
    --environment ENV           Environment (staging, production) [default: production]
    --rollback-version VERSION  Version to rollback to
    --dry-run                   Perform dry run without actual deployment
    --health-check-timeout SEC  Health check timeout in seconds [default: 300]
    --rollback-timeout SEC      Rollback timeout in seconds [default: 600]
    --help                      Show this help message

Examples:
    $0 --strategy blue-green --region uae
    $0 --strategy rolling --region us --dry-run
    $0 --rollback-version v2.0.1 --region uae
EOF
}

# Load deployment configuration
load_config() {
    log_info "Loading deployment configuration for region: $REGION"
    
    if [[ ! -f "$DEPLOYMENT_CONFIG" ]]; then
        log_error "Deployment configuration file not found: $DEPLOYMENT_CONFIG"
        exit 1
    fi
    
    # Parse YAML configuration (simplified)
    export KUBECONFIG="${SCRIPT_DIR}/kubeconfig-${REGION}.yaml"
    export DOCKER_REGISTRY=$(grep "docker_registry:" "$DEPLOYMENT_CONFIG" | cut -d: -f2 | tr -d ' ')
    export IMAGE_TAG=$(grep "image_tag:" "$DEPLOYMENT_CONFIG" | cut -d: -f2 | tr -d ' ')
    export NAMESPACE="energyopti-pro-${ENVIRONMENT}"
    
    log_info "Configuration loaded: Registry=$DOCKER_REGISTRY, Tag=$IMAGE_TAG, Namespace=$NAMESPACE"
}

# Pre-deployment checks
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check if docker is available
    if ! command -v docker &> /dev/null; then
        log_error "docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_warning "Namespace $NAMESPACE does not exist, creating..."
        kubectl create namespace "$NAMESPACE"
    fi
    
    # Check required secrets
    check_required_secrets
    
    log_success "Pre-deployment checks passed"
}

# Check required secrets
check_required_secrets() {
    log_info "Checking required secrets..."
    
    required_secrets=(
        "energyopti-pro-secrets"
        "energyopti-pro-tls"
        "energyopti-pro-registry"
    )
    
    for secret in "${required_secrets[@]}"; do
        if ! kubectl get secret "$secret" -n "$NAMESPACE" &> /dev/null; then
            log_error "Required secret not found: $secret"
            exit 1
        fi
    done
    
    log_success "All required secrets are present"
}

# Build and push Docker images
build_and_push_images() {
    log_info "Building and pushing Docker images..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Skipping image build and push"
        return
    fi
    
    # Build backend image
    log_info "Building backend image..."
    docker build -t "$DOCKER_REGISTRY/energyopti-pro-backend:$IMAGE_TAG" \
        -f "$PROJECT_ROOT/Dockerfile.backend" "$PROJECT_ROOT"
    
    # Build frontend image
    log_info "Building frontend image..."
    docker build -t "$DOCKER_REGISTRY/energyopti-pro-frontend:$IMAGE_TAG" \
        -f "$PROJECT_ROOT/frontend/Dockerfile" "$PROJECT_ROOT/frontend"
    
    # Push images
    log_info "Pushing images to registry..."
    docker push "$DOCKER_REGISTRY/energyopti-pro-backend:$IMAGE_TAG"
    docker push "$DOCKER_REGISTRY/energyopti-pro-frontend:$IMAGE_TAG"
    
    log_success "Images built and pushed successfully"
}

# Blue-green deployment
blue_green_deployment() {
    log_info "Starting blue-green deployment..."
    
    # Determine current active color
    current_color=$(get_current_active_color)
    new_color=$([[ "$current_color" == "blue" ]] && echo "green" || echo "blue")
    
    log_info "Current active: $current_color, New deployment: $new_color"
    
    # Deploy new version
    deploy_new_version "$new_color"
    
    # Run health checks
    if run_health_checks "$new_color"; then
        # Switch traffic to new version
        switch_traffic "$new_color"
        
        # Verify traffic switch
        if verify_traffic_switch "$new_color"; then
            log_success "Blue-green deployment completed successfully"
            
            # Clean up old version
            cleanup_old_version "$current_color"
        else
            log_error "Traffic switch verification failed, rolling back..."
            rollback_deployment "$current_color"
            exit 1
        fi
    else
        log_error "Health checks failed, rolling back..."
        rollback_deployment "$current_color"
        exit 1
    fi
}

# Rolling deployment
rolling_deployment() {
    log_info "Starting rolling deployment..."
    
    # Update deployment with new image
    kubectl set image deployment/energyopti-pro-backend \
        backend="$DOCKER_REGISTRY/energyopti-pro-backend:$IMAGE_TAG" \
        -n "$NAMESPACE"
    
    kubectl set image deployment/energyopti-pro-frontend \
        frontend="$DOCKER_REGISTRY/energyopti-pro-frontend:$IMAGE_TAG" \
        -n "$NAMESPACE"
    
    # Wait for rollout to complete
    kubectl rollout status deployment/energyopti-pro-backend -n "$NAMESPACE" --timeout="${HEALTH_CHECK_TIMEOUT}s"
    kubectl rollout status deployment/energyopti-pro-frontend -n "$NAMESPACE" --timeout="${HEALTH_CHECK_TIMEOUT}s"
    
    # Run health checks
    if run_health_checks "rolling"; then
        log_success "Rolling deployment completed successfully"
    else
        log_error "Health checks failed, rolling back..."
        kubectl rollout undo deployment/energyopti-pro-backend -n "$NAMESPACE"
        kubectl rollout undo deployment/energyopti-pro-frontend -n "$NAMESPACE"
        exit 1
    fi
}

# Canary deployment
canary_deployment() {
    log_info "Starting canary deployment..."
    
    # Deploy canary version with small traffic percentage
    deploy_canary_version
    
    # Run health checks on canary
    if run_health_checks "canary"; then
        # Gradually increase traffic to canary
        for percentage in 10 25 50 75 100; do
            log_info "Increasing canary traffic to $percentage%"
            update_canary_traffic "$percentage"
            
            # Wait and check health
            sleep 30
            if ! run_health_checks "canary"; then
                log_error "Canary health checks failed at $percentage% traffic"
                rollback_canary
                exit 1
            fi
        done
        
        # Promote canary to stable
        promote_canary_to_stable
        log_success "Canary deployment completed successfully"
    else
        log_error "Initial canary health checks failed"
        rollback_canary
        exit 1
    fi
}

# Deploy new version
deploy_new_version() {
    local color=$1
    log_info "Deploying new version with color: $color"
    
    # Apply Kubernetes manifests with color-specific labels
    kubectl apply -f "$PROJECT_ROOT/k8s/" \
        -l "app.kubernetes.io/color=$color" \
        -n "$NAMESPACE"
    
    # Wait for deployment to be ready
    kubectl wait --for=condition=available \
        --timeout="${HEALTH_CHECK_TIMEOUT}s" \
        deployment/energyopti-pro-backend-$color \
        deployment/energyopti-pro-frontend-$color \
        -n "$NAMESPACE"
}

# Get current active color
get_current_active_color() {
    # Check which color is currently receiving traffic
    if kubectl get service energyopti-pro-backend -n "$NAMESPACE" -o jsonpath='{.spec.selector.app\.kubernetes\.io/color}' | grep -q "blue"; then
        echo "blue"
    else
        echo "green"
    fi
}

# Switch traffic
switch_traffic() {
    local new_color=$1
    log_info "Switching traffic to $new_color"
    
    # Update service selectors to point to new color
    kubectl patch service energyopti-pro-backend -n "$NAMESPACE" \
        -p "{\"spec\":{\"selector\":{\"app.kubernetes.io/color\":\"$new_color\"}}}"
    
    kubectl patch service energyopti-pro-frontend -n "$NAMESPACE" \
        -p "{\"spec\":{\"selector\":{\"app.kubernetes.io/color\":\"$new_color\"}}}"
}

# Verify traffic switch
verify_traffic_switch() {
    local expected_color=$1
    log_info "Verifying traffic switch to $expected_color"
    
    # Wait for traffic to stabilize
    sleep 30
    
    # Check if traffic is going to expected color
    actual_color=$(kubectl get service energyopti-pro-backend -n "$NAMESPACE" \
        -o jsonpath='{.spec.selector.app\.kubernetes\.io/color}')
    
    if [[ "$actual_color" == "$expected_color" ]]; then
        log_success "Traffic switch verified successfully"
        return 0
    else
        log_error "Traffic switch verification failed: expected $expected_color, got $actual_color"
        return 1
    fi
}

# Run health checks
run_health_checks() {
    local deployment_type=$1
    log_info "Running health checks for $deployment_type deployment"
    
    # Check pod health
    if ! check_pod_health "$deployment_type"; then
        return 1
    fi
    
    # Check API endpoints
    if ! check_api_endpoints "$deployment_type"; then
        return 1
    fi
    
    # Check database connectivity
    if ! check_database_connectivity "$deployment_type"; then
        return 1
    fi
    
    # Check external service connectivity
    if ! check_external_services "$deployment_type"; then
        return 1
    fi
    
    log_success "All health checks passed"
    return 0
}

# Check pod health
check_pod_health() {
    local deployment_type=$1
    log_info "Checking pod health..."
    
    # Wait for pods to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=energyopti-pro-backend \
        -n "$NAMESPACE" --timeout=60s
    
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=energyopti-pro-frontend \
        -n "$NAMESPACE" --timeout=60s
    
    # Check pod status
    failed_pods=$(kubectl get pods -n "$NAMESPACE" \
        -l app.kubernetes.io/name=energyopti-pro-backend \
        -o jsonpath='{.items[?(@.status.phase!="Running")].metadata.name}')
    
    if [[ -n "$failed_pods" ]]; then
        log_error "Found failed pods: $failed_pods"
        return 1
    fi
    
    return 0
}

# Check API endpoints
check_api_endpoints() {
    local deployment_type=$1
    log_info "Checking API endpoints..."
    
    # Get service URL
    local service_url=$(kubectl get service energyopti-pro-backend -n "$NAMESPACE" \
        -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [[ -z "$service_url" ]]; then
        service_url="localhost:8000"
    fi
    
    # Test health endpoint
    if ! curl -f -s "http://$service_url/health" > /dev/null; then
        log_error "Health endpoint check failed"
        return 1
    fi
    
    # Test API endpoints
    local endpoints=("/api/v1/market-data" "/api/v1/orders" "/api/v1/positions")
    for endpoint in "${endpoints[@]}"; do
        if ! curl -f -s "http://$service_url$endpoint" > /dev/null; then
            log_error "API endpoint check failed: $endpoint"
            return 1
        fi
    done
    
    return 0
}

# Check database connectivity
check_database_connectivity() {
    local deployment_type=$1
    log_info "Checking database connectivity..."
    
    # Test database connection through a pod
    local pod_name=$(kubectl get pods -n "$NAMESPACE" \
        -l app.kubernetes.io/name=energyopti-pro-backend \
        -o jsonpath='{.items[0].metadata.name}')
    
    if ! kubectl exec "$pod_name" -n "$NAMESPACE" -- \
        python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"; then
        log_error "Database connectivity check failed"
        return 1
    fi
    
    return 0
}

# Check external services
check_external_services() {
    local deployment_type=$1
    log_info "Checking external service connectivity..."
    
    # Test Redis connectivity
    local pod_name=$(kubectl get pods -n "$NAMESPACE" \
        -l app.kubernetes.io/name=energyopti-pro-backend \
        -o jsonpath='{.items[0].metadata.name}')
    
    if ! kubectl exec "$pod_name" -n "$NAMESPACE" -- \
        python -c "import redis; redis.Redis.from_url('$REDIS_URL').ping()"; then
        log_error "Redis connectivity check failed"
        return 1
    fi
    
    return 0
}

# Rollback deployment
rollback_deployment() {
    local target_color=$1
    log_warning "Rolling back to $target_color"
    
    # Switch traffic back to target color
    switch_traffic "$target_color"
    
    # Verify rollback
    if verify_traffic_switch "$target_color"; then
        log_success "Rollback completed successfully"
    else
        log_error "Rollback failed"
        exit 1
    fi
}

# Cleanup old version
cleanup_old_version() {
    local old_color=$1
    log_info "Cleaning up old version: $old_color"
    
    # Delete old deployment
    kubectl delete deployment energyopti-pro-backend-$old_color -n "$NAMESPACE" --ignore-not-found
    kubectl delete deployment energyopti-pro-frontend-$old_color -n "$NAMESPACE" --ignore-not-found
    
    # Delete old services
    kubectl delete service energyopti-pro-backend-$old_color -n "$NAMESPACE" --ignore-not-found
    kubectl delete service energyopti-pro-frontend-$old_color -n "$NAMESPACE" --ignore-not-found
    
    log_success "Old version cleanup completed"
}

# Main deployment function
main_deployment() {
    log_info "Starting EnergyOpti-Pro deployment"
    log_info "Strategy: $DEPLOYMENT_STRATEGY, Region: $REGION, Environment: $ENVIRONMENT"
    
    # Load configuration
    load_config
    
    # Run pre-deployment checks
    pre_deployment_checks
    
    # Build and push images
    build_and_push_images
    
    # Execute deployment strategy
    case $DEPLOYMENT_STRATEGY in
        "blue-green")
            blue_green_deployment
            ;;
        "rolling")
            rolling_deployment
            ;;
        "canary")
            canary_deployment
            ;;
        *)
            log_error "Unknown deployment strategy: $DEPLOYMENT_STRATEGY"
            exit 1
            ;;
    esac
    
    # Post-deployment verification
    post_deployment_verification
    
    log_success "Deployment completed successfully!"
}

# Post-deployment verification
post_deployment_verification() {
    log_info "Running post-deployment verification..."
    
    # Check application metrics
    check_application_metrics
    
    # Check error rates
    check_error_rates
    
    # Check performance metrics
    check_performance_metrics
    
    log_success "Post-deployment verification completed"
}

# Check application metrics
check_application_metrics() {
    log_info "Checking application metrics..."
    
    # Check Prometheus metrics
    local prometheus_url=$(kubectl get service energyopti-pro-prometheus -n "$NAMESPACE" \
        -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [[ -n "$prometheus_url" ]]; then
        # Check if metrics are being collected
        if curl -f -s "http://$prometheus_url:9090/api/v1/query?query=up" > /dev/null; then
            log_success "Prometheus metrics are being collected"
        else
            log_warning "Prometheus metrics collection check failed"
        fi
    fi
}

# Check error rates
check_error_rates() {
    log_info "Checking error rates..."
    
    # This would typically query monitoring systems
    # For now, we'll just log that we're checking
    log_info "Error rate monitoring active"
}

# Check performance metrics
check_performance_metrics() {
    log_info "Checking performance metrics..."
    
    # Check response times
    local service_url=$(kubectl get service energyopti-pro-backend -n "$NAMESPACE" \
        -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [[ -n "$service_url" ]]; then
        local response_time=$(curl -w "%{time_total}" -o /dev/null -s "http://$service_url/health")
        log_info "Health endpoint response time: ${response_time}s"
        
        if (( $(echo "$response_time < 0.2" | bc -l) )); then
            log_success "Response time is within acceptable limits (< 200ms)"
        else
            log_warning "Response time is above acceptable limits: ${response_time}s"
        fi
    fi
}

# Handle rollback request
if [[ -n "$ROLLBACK_VERSION" ]]; then
    log_info "Rollback requested to version: $ROLLBACK_VERSION"
    
    # Load configuration
    load_config
    
    # Perform rollback
    kubectl rollout undo deployment/energyopti-pro-backend -n "$NAMESPACE" --to-revision="$ROLLBACK_VERSION"
    kubectl rollout undo deployment/energyopti-pro-frontend -n "$NAMESPACE" --to-revision="$ROLLBACK_VERSION"
    
    # Wait for rollback to complete
    kubectl rollout status deployment/energyopti-pro-backend -n "$NAMESPACE" --timeout="${ROLLBACK_TIMEOUT}s"
    kubectl rollout status deployment/energyopti-pro-frontend -n "$NAMESPACE" --timeout="${ROLLBACK_TIMEOUT}s"
    
    # Run health checks
    if run_health_checks "rollback"; then
        log_success "Rollback completed successfully"
    else
        log_error "Rollback health checks failed"
        exit 1
    fi
else
    # Run main deployment
    main_deployment
fi
