#!/bin/bash

# QuantaEnergi Deployment Script
# Advanced deployment automation with hybrid cloud support and SLA monitoring

set -e  # Exit on any error

# Configuration
APP_NAME="quantaenergi"
VERSION=${VERSION:-"latest"}
ENVIRONMENT=${ENVIRONMENT:-"production"}
REGION=${REGION:-"us-east-1"}
CLUSTER_NAME=${CLUSTER_NAME:-"quantaenergi-cluster"}
NAMESPACE=${NAMESPACE:-"quantaenergi"}
REPLICA_COUNT=${REPLICA_COUNT:-3}
CPU_LIMIT=${CPU_LIMIT:-"2000m"}
MEMORY_LIMIT=${MEMORY_LIMIT:-"4Gi"}
CPU_REQUEST=${CPU_REQUEST:-"500m"}
MEMORY_REQUEST=${MEMORY_REQUEST:-"1Gi"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if required tools are installed
    local tools=("docker" "kubectl" "helm" "aws" "terraform")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is not installed or not in PATH"
            exit 1
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check Kubernetes cluster
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Kubernetes cluster is not accessible"
        exit 1
    fi
    
    log_success "All prerequisites are met"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    # Build backend image
    log_info "Building backend image..."
    docker build -t "$APP_NAME-backend:$VERSION" -f apps/backend/Dockerfile apps/backend/
    
    # Build frontend image
    log_info "Building frontend image..."
    docker build -t "$APP_NAME-frontend:$VERSION" -f apps/frontend/Dockerfile apps/frontend/
    
    # Build worker image
    log_info "Building worker image..."
    docker build -t "$APP_NAME-worker:$VERSION" -f apps/worker/Dockerfile apps/worker/
    
    log_success "Docker images built successfully"
}

# Push images to registry
push_images() {
    log_info "Pushing images to registry..."
    
    local registry=${REGISTRY:-"your-registry.com"}
    
    # Tag and push backend
    docker tag "$APP_NAME-backend:$VERSION" "$registry/$APP_NAME-backend:$VERSION"
    docker push "$registry/$APP_NAME-backend:$VERSION"
    
    # Tag and push frontend
    docker tag "$APP_NAME-frontend:$VERSION" "$registry/$APP_NAME-frontend:$VERSION"
    docker push "$registry/$APP_NAME-frontend:$VERSION"
    
    # Tag and push worker
    docker tag "$APP_NAME-worker:$VERSION" "$registry/$APP_NAME-worker:$VERSION"
    docker push "$registry/$APP_NAME-worker:$VERSION"
    
    log_success "Images pushed to registry successfully"
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."
    
    cd infrastructure/
    
    # Initialize Terraform
    terraform init
    
    # Plan infrastructure changes
    terraform plan -var="environment=$ENVIRONMENT" -var="region=$REGION" -var="cluster_name=$CLUSTER_NAME"
    
    # Apply infrastructure changes
    terraform apply -auto-approve -var="environment=$ENVIRONMENT" -var="region=$REGION" -var="cluster_name=$CLUSTER_NAME"
    
    cd ..
    
    log_success "Infrastructure deployed successfully"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    # Create namespace if it doesn't exist
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy with Helm
    helm upgrade --install "$APP_NAME" ./helm-chart \
        --namespace "$NAMESPACE" \
        --set image.tag="$VERSION" \
        --set environment="$ENVIRONMENT" \
        --set replicaCount="$REPLICA_COUNT" \
        --set resources.limits.cpu="$CPU_LIMIT" \
        --set resources.limits.memory="$MEMORY_LIMIT" \
        --set resources.requests.cpu="$CPU_REQUEST" \
        --set resources.requests.memory="$MEMORY_REQUEST" \
        --set ingress.enabled=true \
        --set ingress.host="$APP_NAME.$ENVIRONMENT.your-domain.com" \
        --wait --timeout=300s
    
    log_success "Kubernetes deployment completed successfully"
}

# Deploy database migrations
deploy_migrations() {
    log_info "Running database migrations..."
    
    # Run backend migrations
    kubectl run migration-job --image="$APP_NAME-backend:$VERSION" \
        --namespace "$NAMESPACE" \
        --restart=Never \
        --command -- python manage.py migrate
    
    # Wait for migration to complete
    kubectl wait --for=condition=complete job/migration-job --namespace "$NAMESPACE" --timeout=300s
    
    # Clean up migration job
    kubectl delete job migration-job --namespace "$NAMESPACE"
    
    log_success "Database migrations completed successfully"
}

# Deploy monitoring and observability
deploy_monitoring() {
    log_info "Deploying monitoring and observability..."
    
    # Deploy Prometheus
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set grafana.adminPassword="admin123" \
        --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
        --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false
    
    # Deploy Jaeger for distributed tracing
    helm upgrade --install jaeger jaegertracing/jaeger \
        --namespace monitoring \
        --set provisionDataStore.cassandra=false \
        --set storage.type=elasticsearch \
        --set storage.elasticsearch.host=elasticsearch.monitoring.svc.cluster.local
    
    # Deploy ELK stack for logging
    helm upgrade --install elasticsearch elastic/elasticsearch \
        --namespace monitoring \
        --set replicas=1 \
        --set minimumMasterNodes=1
    
    helm upgrade --install kibana elastic/kibana \
        --namespace monitoring \
        --set elasticsearchHosts="http://elasticsearch.monitoring.svc.cluster.local:9200"
    
    log_success "Monitoring and observability deployed successfully"
}

# Deploy service mesh
deploy_service_mesh() {
    log_info "Deploying service mesh..."
    
    # Install Istio
    curl -L https://istio.io/downloadIstio | sh -
    export PATH=$PWD/istio-*/bin:$PATH
    istioctl install --set values.defaultRevision=default -y
    
    # Enable Istio sidecar injection for the namespace
    kubectl label namespace "$NAMESPACE" istio-injection=enabled --overwrite
    
    # Deploy Istio gateways and virtual services
    kubectl apply -f infrastructure/istio/ -n "$NAMESPACE"
    
    log_success "Service mesh deployed successfully"
}

# Deploy security policies
deploy_security() {
    log_info "Deploying security policies..."
    
    # Deploy network policies
    kubectl apply -f infrastructure/security/network-policies.yaml -n "$NAMESPACE"
    
    # Deploy pod security policies
    kubectl apply -f infrastructure/security/pod-security-policies.yaml -n "$NAMESPACE"
    
    # Deploy RBAC policies
    kubectl apply -f infrastructure/security/rbac.yaml -n "$NAMESPACE"
    
    # Deploy admission controllers
    kubectl apply -f infrastructure/security/admission-controllers.yaml -n "$NAMESPACE"
    
    log_success "Security policies deployed successfully"
}

# Deploy backup and disaster recovery
deploy_backup() {
    log_info "Deploying backup and disaster recovery..."
    
    # Deploy Velero for backup
    helm upgrade --install velero vmware-tanzu/velero \
        --namespace velero \
        --create-namespace \
        --set configuration.provider=aws \
        --set configuration.backupStorageLocation.name=default \
        --set configuration.backupStorageLocation.bucket=velero-backups \
        --set configuration.backupStorageLocation.config.region="$REGION" \
        --set credentials.useSecret=false
    
    # Create backup schedules
    kubectl apply -f infrastructure/backup/backup-schedules.yaml -n "$NAMESPACE"
    
    log_success "Backup and disaster recovery deployed successfully"
}

# Deploy multi-tenancy
deploy_multi_tenancy() {
    log_info "Deploying multi-tenancy..."
    
    # Deploy tenant isolation policies
    kubectl apply -f infrastructure/multi-tenancy/tenant-isolation.yaml -n "$NAMESPACE"
    
    # Deploy resource quotas
    kubectl apply -f infrastructure/multi-tenancy/resource-quotas.yaml -n "$NAMESPACE"
    
    # Deploy tenant-specific configurations
    kubectl apply -f infrastructure/multi-tenancy/tenant-configs.yaml -n "$NAMESPACE"
    
    log_success "Multi-tenancy deployed successfully"
}

# Deploy treasury management
deploy_treasury() {
    log_info "Deploying treasury management..."
    
    # Deploy treasury service
    kubectl apply -f infrastructure/treasury/treasury-service.yaml -n "$NAMESPACE"
    
    # Deploy treasury monitoring
    kubectl apply -f infrastructure/treasury/treasury-monitoring.yaml -n "$NAMESPACE"
    
    # Deploy treasury policies
    kubectl apply -f infrastructure/treasury/treasury-policies.yaml -n "$NAMESPACE"
    
    log_success "Treasury management deployed successfully"
}

# Health checks
run_health_checks() {
    log_info "Running health checks..."
    
    # Wait for pods to be ready
    kubectl wait --for=condition=ready pod -l app="$APP_NAME-backend" --namespace "$NAMESPACE" --timeout=300s
    kubectl wait --for=condition=ready pod -l app="$APP_NAME-frontend" --namespace "$NAMESPACE" --timeout=300s
    kubectl wait --for=condition=ready pod -l app="$APP_NAME-worker" --namespace "$NAMESPACE" --timeout=300s
    
    # Check service endpoints
    local backend_service="$APP_NAME-backend-service"
    local frontend_service="$APP_NAME-frontend-service"
    
    kubectl get service "$backend_service" --namespace "$NAMESPACE"
    kubectl get service "$frontend_service" --namespace "$NAMESPACE"
    
    # Test application endpoints
    local backend_url=$(kubectl get service "$backend_service" --namespace "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    local frontend_url=$(kubectl get service "$frontend_service" --namespace "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    
    if [ -n "$backend_url" ]; then
        log_info "Testing backend endpoint: http://$backend_url/health"
        curl -f "http://$backend_url/health" || log_warning "Backend health check failed"
    fi
    
    if [ -n "$frontend_url" ]; then
        log_info "Testing frontend endpoint: http://$frontend_url"
        curl -f "http://$frontend_url" || log_warning "Frontend health check failed"
    fi
    
    log_success "Health checks completed"
}

# Performance testing
run_performance_tests() {
    log_info "Running performance tests..."
    
    # Deploy performance testing job
    kubectl apply -f infrastructure/testing/performance-tests.yaml -n "$NAMESPACE"
    
    # Wait for performance tests to complete
    kubectl wait --for=condition=complete job/performance-tests --namespace "$NAMESPACE" --timeout=600s
    
    # Get performance test results
    kubectl logs job/performance-tests --namespace "$NAMESPACE"
    
    # Clean up performance test job
    kubectl delete job performance-tests --namespace "$NAMESPACE"
    
    log_success "Performance tests completed"
}

# Deploy CI/CD pipelines
deploy_cicd() {
    log_info "Deploying CI/CD pipelines..."
    
    # Deploy Jenkins
    helm upgrade --install jenkins jenkins/jenkins \
        --namespace jenkins \
        --create-namespace \
        --set controller.adminUser=admin \
        --set controller.adminPassword=admin123 \
        --set service.type=LoadBalancer
    
    # Deploy GitLab CI/CD
    helm upgrade --install gitlab gitlab/gitlab \
        --namespace gitlab \
        --create-namespace \
        --set global.hosts.domain=gitlab.your-domain.com \
        --set global.hosts.externalIP=your-external-ip
    
    # Deploy ArgoCD for GitOps
    helm upgrade --install argocd argo/argo-cd \
        --namespace argocd \
        --create-namespace \
        --set server.service.type=LoadBalancer
    
    log_success "CI/CD pipelines deployed successfully"
}

# Main deployment function
main() {
    log_info "Starting QuantaEnergi deployment..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Version: $VERSION"
    log_info "Region: $REGION"
    log_info "Cluster: $CLUSTER_NAME"
    log_info "Namespace: $NAMESPACE"
    
    # Check prerequisites
            check_prerequisites
    
    # Deploy infrastructure
    deploy_infrastructure
    
    # Build and push images
    build_images
    push_images
    
    # Deploy to Kubernetes
    deploy_kubernetes
    
    # Deploy database migrations
    deploy_migrations
    
    # Deploy monitoring and observability
    deploy_monitoring
    
    # Deploy service mesh
    deploy_service_mesh
    
    # Deploy security policies
    deploy_security
    
    # Deploy backup and disaster recovery
    deploy_backup
    
    # Deploy multi-tenancy
    deploy_multi_tenancy
    
    # Deploy treasury management
    deploy_treasury
    
    # Deploy CI/CD pipelines
    deploy_cicd
    
    # Run health checks
    run_health_checks
    
    # Run performance tests
    run_performance_tests
    
    log_success "QuantaEnergi deployment completed successfully!"
    log_info "Application is now running in the $ENVIRONMENT environment"
    log_info "Backend URL: http://$APP_NAME-backend-service.$NAMESPACE.svc.cluster.local"
    log_info "Frontend URL: http://$APP_NAME-frontend-service.$NAMESPACE.svc.cluster.local"
}

# Handle script arguments
case "${1:-}" in
    "infrastructure")
        deploy_infrastructure
        ;;
    "kubernetes")
        deploy_kubernetes
        ;;
    "monitoring")
        deploy_monitoring
        ;;
    "security")
        deploy_security
        ;;
    "backup")
        deploy_backup
        ;;
    "multi-tenancy")
        deploy_multi_tenancy
        ;;
    "treasury")
        deploy_treasury
        ;;
    "health")
        run_health_checks
        ;;
    "performance")
        run_performance_tests
        ;;
    "cicd")
        deploy_cicd
        ;;
    *)
        main
            ;;
    esac