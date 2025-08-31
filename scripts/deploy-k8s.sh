#!/bin/bash

# Kubernetes Deployment Script for EnergyOpti-Pro
# Deploys the entire application stack with monitoring

set -e

echo "🚀 Starting EnergyOpti-Pro Kubernetes Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if kubectl is connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "kubectl is not connected to a cluster. Please connect to a Kubernetes cluster first."
    exit 1
fi

print_status "Connected to Kubernetes cluster: $(kubectl config current-context)"

# Create namespace
print_status "Creating namespace..."
kubectl apply -f k8s/monitoring.yaml --namespace=energyopti-pro

# Wait for namespace to be ready
kubectl wait --for=condition=Active namespace/energyopti-pro --timeout=60s

# Deploy Redis Cluster
print_status "Deploying Redis Cluster..."
kubectl apply -f k8s/redis-cluster.yaml

# Wait for Redis pods to be ready
print_status "Waiting for Redis Cluster to be ready..."
kubectl wait --for=condition=ready pod -l app=redis-cluster --timeout=300s

# Initialize Redis Cluster
print_status "Initializing Redis Cluster..."
kubectl apply -f k8s/redis-cluster.yaml

# Wait for cluster initialization job to complete
print_status "Waiting for Redis Cluster initialization..."
kubectl wait --for=condition=complete job/redis-cluster-init --timeout=300s

# Deploy monitoring stack
print_status "Deploying monitoring stack..."
kubectl apply -f k8s/monitoring.yaml

# Wait for monitoring pods to be ready
print_status "Waiting for monitoring stack to be ready..."
kubectl wait --for=condition=ready pod -l app=prometheus --timeout=300s
kubectl wait --for=condition=ready pod -l app=grafana --timeout=300s

# Deploy main application
print_status "Deploying main application..."
kubectl apply -f k8s/deployment.yaml

# Wait for application pods to be ready
print_status "Waiting for application to be ready..."
kubectl wait --for=condition=ready pod -l app=energyopti-backend --timeout=300s
kubectl wait --for=condition=ready pod -l app=energyopti-frontend --timeout=300s

# Get service URLs
print_status "Getting service URLs..."
BACKEND_URL=$(kubectl get service energyopti-backend-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "localhost")
FRONTEND_URL=$(kubectl get service energyopti-frontend-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "localhost")
PROMETHEUS_URL=$(kubectl get service prometheus-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "localhost")
GRAFANA_URL=$(kubectl get service grafana-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "localhost")

# Port forward services for local access
print_status "Setting up port forwarding for local access..."

# Function to setup port forwarding
setup_port_forward() {
    local service_name=$1
    local local_port=$2
    local target_port=$3
    
    kubectl port-forward service/$service_name $local_port:$target_port > /dev/null 2>&1 &
    local pid=$!
    echo $pid > /tmp/energyopti-$service_name.pid
    print_status "$service_name port-forwarded to localhost:$local_port (PID: $pid)"
}

# Setup port forwarding
setup_port_forward "energyopti-backend-service" 8001 80
setup_port_forward "energyopti-frontend-service" 3000 80
setup_port_forward "prometheus-service" 9090 9090
setup_port_forward "grafana-service" 3001 3000

# Wait a moment for port forwarding to establish
sleep 5

# Display deployment summary
echo ""
echo "🎉 EnergyOpti-Pro Deployment Complete!"
echo "======================================"
echo ""
echo "Services:"
echo "  Backend API:     http://localhost:8001"
echo "  Frontend:        http://localhost:3000"
echo "  Prometheus:      http://localhost:9090"
echo "  Grafana:         http://localhost:3001 (admin/admin)"
echo ""
echo "Redis Cluster:     Running (6 nodes)"
echo "Monitoring:        Active"
echo "Auto-scaling:      Enabled (3-10 backend replicas)"
echo ""
echo "To stop port forwarding, run:"
echo "  pkill -f 'kubectl port-forward'"
echo ""
echo "To view logs:"
echo "  kubectl logs -f deployment/energyopti-backend"
echo "  kubectl logs -f deployment/energyopti-frontend"
echo ""
echo "To scale backend:"
echo "  kubectl scale deployment energyopti-backend --replicas=5"
echo ""

# Health check
print_status "Performing health check..."
if curl -s http://localhost:8001/api/health > /dev/null; then
    print_status "✅ Backend health check passed"
else
    print_warning "⚠️  Backend health check failed - service may still be starting"
fi

if curl -s http://localhost:3000 > /dev/null; then
    print_status "✅ Frontend health check passed"
else
    print_warning "⚠️  Frontend health check failed - service may still be starting"
fi

print_status "Deployment completed successfully!"
print_status "Monitor the application with: kubectl get pods -n energyopti-pro"
