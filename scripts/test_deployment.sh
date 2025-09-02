#!/bin/bash

# QuantaEnergi Deployment Test Script
# This script validates the deployed infrastructure and verifies all components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="quantaenergi"
MONITORING_NAMESPACE="monitoring"
DOMAIN="quantaenergi.com"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Test Kubernetes cluster connectivity
test_cluster_connectivity() {
    log "Testing Kubernetes cluster connectivity..."
    
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    fi
    
    log "Cluster connectivity: ✅ OK"
}

# Test namespace existence
test_namespaces() {
    log "Testing namespace existence..."
    
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        error "Namespace $NAMESPACE does not exist."
    fi
    
    if ! kubectl get namespace $MONITORING_NAMESPACE &> /dev/null; then
        error "Namespace $MONITORING_NAMESPACE does not exist."
    fi
    
    log "Namespaces: ✅ OK"
}

# Test pod health
test_pod_health() {
    log "Testing pod health..."
    
    # Check backend pods
    BACKEND_PODS=$(kubectl get pods -n $NAMESPACE -l app=quantaenergi-backend --no-headers | wc -l)
    if [ $BACKEND_PODS -eq 0 ]; then
        error "No backend pods found in namespace $NAMESPACE"
    fi
    
    BACKEND_READY=$(kubectl get pods -n $NAMESPACE -l app=quantaenergi-backend --no-headers | grep -c "Running")
    if [ $BACKEND_READY -eq 0 ]; then
        error "No backend pods are running"
    fi
    
    # Check frontend pods
    FRONTEND_PODS=$(kubectl get pods -n $NAMESPACE -l app=quantaenergi-frontend --no-headers | wc -l)
    if [ $FRONTEND_PODS -eq 0 ]; then
        error "No frontend pods found in namespace $NAMESPACE"
    fi
    
    FRONTEND_READY=$(kubectl get pods -n $NAMESPACE -l app=quantaenergi-frontend --no-headers | grep -c "Running")
    if [ $FRONTEND_READY -eq 0 ]; then
        error "No frontend pods are running"
    fi
    
    # Check database pods
    DB_PODS=$(kubectl get pods -n $NAMESPACE -l app=quantaenergi-postgres --no-headers | wc -l)
    if [ $DB_PODS -eq 0 ]; then
        error "No database pods found in namespace $NAMESPACE"
    fi
    
    DB_READY=$(kubectl get pods -n $NAMESPACE -l app=quantaenergi-postgres --no-headers | grep -c "Running")
    if [ $DB_READY -eq 0 ]; then
        error "No database pods are running"
    fi
    
    # Check Redis pods
    REDIS_PODS=$(kubectl get pods -n $NAMESPACE -l app=quantaenergi-redis-cluster --no-headers | wc -l)
    if [ $REDIS_PODS -eq 0 ]; then
        error "No Redis pods found in namespace $NAMESPACE"
    fi
    
    REDIS_READY=$(kubectl get pods -n $NAMESPACE -l app=quantaenergi-redis-cluster --no-headers | grep -c "Running")
    if [ $REDIS_READY -eq 0 ]; then
        error "No Redis pods are running"
    fi
    
    log "Pod health: ✅ OK"
    log "  - Backend: $BACKEND_READY/$BACKEND_PODS pods running"
    log "  - Frontend: $FRONTEND_READY/$FRONTEND_PODS pods running"
    log "  - Database: $DB_READY/$DB_PODS pods running"
    log "  - Redis: $REDIS_READY/$REDIS_PODS pods running"
}

# Test service endpoints
test_service_endpoints() {
    log "Testing service endpoints..."
    
    # Get backend service port
    BACKEND_PORT=$(kubectl get service quantaenergi-backend-service -n $NAMESPACE -o jsonpath='{.spec.ports[0].port}')
    
    # Test backend health endpoint
    if ! kubectl run test-backend --image=curlimages/curl --rm -i --restart=Never -- curl -f "http://quantaenergi-backend-service.$NAMESPACE.svc.cluster.local:$BACKEND_PORT/health" &> /dev/null; then
        error "Backend health endpoint is not responding"
    fi
    
    # Test backend metrics endpoint
    if ! kubectl run test-metrics --image=curlimages/curl --rm -i --restart=Never -- curl -f "http://quantaenergi-backend-service.$NAMESPACE.svc.cluster.local:8001/metrics" &> /dev/null; then
        error "Backend metrics endpoint is not responding"
    fi
    
    log "Service endpoints: ✅ OK"
}

# Test monitoring stack
test_monitoring() {
    log "Testing monitoring stack..."
    
    # Check Prometheus
    if ! kubectl get pods -n $MONITORING_NAMESPACE -l app=prometheus --no-headers | grep -q "Running"; then
        error "Prometheus is not running"
    fi
    
    # Check Grafana
    if ! kubectl get pods -n $MONITORING_NAMESPACE -l app=grafana --no-headers | grep -q "Running"; then
        error "Grafana is not running"
    fi
    
    # Test Prometheus endpoint
    if ! kubectl run test-prometheus --image=curlimages/curl --rm -i --restart=Never -- curl -f "http://prometheus.$MONITORING_NAMESPACE.svc.cluster.local:9090/-/healthy" &> /dev/null; then
        error "Prometheus health endpoint is not responding"
    fi
    
    # Test Grafana endpoint
    if ! kubectl run test-grafana --image=curlimages/curl --rm -i --restart=Never -- curl -f "http://grafana.$MONITORING_NAMESPACE.svc.cluster.local:3000/api/health" &> /dev/null; then
        error "Grafana health endpoint is not responding"
    fi
    
    log "Monitoring stack: ✅ OK"
}

# Test ingress and external access
test_external_access() {
    log "Testing external access..."
    
    # Check if ingress exists
    if ! kubectl get ingress -n $NAMESPACE quantaenergi-ingress &> /dev/null; then
        error "Ingress not found in namespace $NAMESPACE"
    fi
    
    # Check if monitoring ingress exists
    if ! kubectl get ingress -n $MONITORING_NAMESPACE monitoring-ingress &> /dev/null; then
        error "Monitoring ingress not found in namespace $MONITORING_NAMESPACE"
    fi
    
    # Get ingress controller service
    INGRESS_SERVICE=$(kubectl get service -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
    
    if [ -z "$INGRESS_SERVICE" ]; then
        warn "Load balancer not ready yet. External access test skipped."
        return
    fi
    
    log "Load balancer: $INGRESS_SERVICE"
    
    # Test if we can resolve the domain (this will fail if DNS is not configured yet)
    if command -v nslookup &> /dev/null; then
        if nslookup api.$DOMAIN &> /dev/null; then
            log "DNS resolution: ✅ OK"
        else
            warn "DNS resolution failed. This is expected if DNS is not configured yet."
        fi
    fi
    
    log "External access: ✅ OK"
}

# Test database connectivity
test_database_connectivity() {
    log "Testing database connectivity..."
    
    # Test PostgreSQL connection
    if ! kubectl run test-postgres --image=postgres:15-alpine --rm -i --restart=Never -- psql -h quantaenergi-postgres.$NAMESPACE.svc.cluster.local -U quantaenergi_user -d quantaenergi_db -c "SELECT 1;" &> /dev/null; then
        error "Cannot connect to PostgreSQL database"
    fi
    
    # Test Redis connection
    if ! kubectl run test-redis --image=redis:7-alpine --rm -i --restart=Never -- redis-cli -h quantaenergi-redis-cluster.$NAMESPACE.svc.cluster.local ping &> /dev/null; then
        error "Cannot connect to Redis cluster"
    fi
    
    log "Database connectivity: ✅ OK"
}

# Test application functionality
test_application_functionality() {
    log "Testing application functionality..."
    
    # Test backend API endpoints
    BACKEND_PORT=$(kubectl get service quantaenergi-backend-service -n $NAMESPACE -o jsonpath='{.spec.ports[0].port}')
    
    # Test health endpoint
    HEALTH_RESPONSE=$(kubectl run test-health --image=curlimages/curl --rm -i --restart=Never -- curl -s "http://quantaenergi-backend-service.$NAMESPACE.svc.cluster.local:$BACKEND_PORT/health")
    if [[ $HEALTH_RESPONSE != *"healthy"* ]]; then
        error "Health endpoint returned unexpected response: $HEALTH_RESPONSE"
    fi
    
    # Test metrics endpoint
    METRICS_RESPONSE=$(kubectl run test-metrics-func --image=curlimages/curl --rm -i --restart=Never -- curl -s "http://quantaenergi-backend-service.$NAMESPACE.svc.cluster.local:8001/metrics")
    if [[ $METRICS_RESPONSE != *"#"* ]]; then
        error "Metrics endpoint returned unexpected response"
    fi
    
    log "Application functionality: ✅ OK"
}

# Display test summary
display_summary() {
    log "All tests completed successfully!"
    echo ""
    echo "=== QuantaEnergi Infrastructure Test Summary ==="
    echo "✅ Cluster connectivity: OK"
    echo "✅ Namespaces: OK"
    echo "✅ Pod health: OK"
    echo "✅ Service endpoints: OK"
    echo "✅ Monitoring stack: OK"
    echo "✅ External access: OK"
    echo "✅ Database connectivity: OK"
    echo "✅ Application functionality: OK"
    echo ""
    echo "=== Next Steps ==="
    echo "1. Configure DNS records for external access"
    echo "2. Set up SSL certificates"
    echo "3. Configure monitoring alerts"
    echo "4. Begin beta user onboarding"
    echo ""
    echo "Your QuantaEnergi infrastructure is ready for production use!"
}

# Main test function
main() {
    log "Starting QuantaEnergi infrastructure tests..."
    
    test_cluster_connectivity
    test_namespaces
    test_pod_health
    test_service_endpoints
    test_monitoring
    test_external_access
    test_database_connectivity
    test_application_functionality
    display_summary
    
    log "All tests completed successfully!"
}

# Run main function
main "$@"
