#!/bin/bash

# Docker Compose Deployment Script for EnergyOpti-Pro
# Deploys the entire application stack with horizontal scaling

set -e

echo "🐳 Starting EnergyOpti-Pro Docker Compose Deployment..."

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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running. Please start Docker first."
    exit 1
fi

print_status "Docker version: $(docker --version)"
print_status "Docker Compose version: $(docker-compose --version)"

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Clean up any existing images (optional)
read -p "Do you want to rebuild all images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Removing existing images..."
    docker-compose down --rmi all --volumes --remove-orphans 2>/dev/null || true
    docker system prune -f
fi

# Build images
print_status "Building Docker images..."
docker-compose build --no-cache

# Start Redis Cluster first
print_status "Starting Redis Cluster..."
docker-compose up -d redis-node-1 redis-node-2 redis-node-3

# Wait for Redis nodes to be ready
print_status "Waiting for Redis nodes to be ready..."
sleep 10

# Initialize Redis Cluster
print_status "Initializing Redis Cluster..."
docker exec redis-node-1 redis-cli --cluster create \
    redis-node-1:6379 \
    redis-node-2:6379 \
    redis-node-3:6379 \
    --cluster-replicas 0 \
    --cluster-yes

# Start monitoring stack
print_status "Starting monitoring stack..."
docker-compose up -d prometheus grafana

# Wait for monitoring to be ready
print_status "Waiting for monitoring stack to be ready..."
sleep 15

# Start backend instances
print_status "Starting backend instances..."
docker-compose up -d backend-1 backend-2 backend-3

# Wait for backends to be ready
print_status "Waiting for backend instances to be ready..."
sleep 20

# Start frontend instances
print_status "Starting frontend instances..."
docker-compose up -d frontend-1 frontend-2

# Wait for frontends to be ready
print_status "Waiting for frontend instances to be ready..."
sleep 15

# Start Nginx load balancer
print_status "Starting Nginx load balancer..."
docker-compose up -d nginx

# Wait for all services to be ready
print_status "Waiting for all services to be ready..."
sleep 10

# Display deployment summary
echo ""
echo "🎉 EnergyOpti-Pro Docker Compose Deployment Complete!"
echo "===================================================="
echo ""
echo "Services:"
echo "  Backend Instances:"
echo "    - Backend 1:     http://localhost:8001"
echo "    - Backend 2:     http://localhost:8002"
echo "    - Backend 3:     http://localhost:8003"
echo "  Frontend Instances:"
echo "    - Frontend 1:    http://localhost:3000"
echo "    - Frontend 2:    http://localhost:3001"
echo "  Load Balancer:     http://localhost:80"
echo "  Monitoring:"
echo "    - Prometheus:    http://localhost:9090"
echo "    - Grafana:       http://localhost:3000 (admin/admin)"
echo ""
echo "Redis Cluster:"
echo "  - Node 1:          localhost:6379"
echo "  - Node 2:          localhost:6380"
echo "  - Node 3:          localhost:6381"
echo ""
echo "Container Status:"
docker-compose ps
echo ""

# Health check
print_status "Performing health checks..."

# Check backend instances
for port in 8001 8002 8003; do
    if curl -s http://localhost:$port/api/health > /dev/null; then
        print_status "✅ Backend on port $port: Healthy"
    else
        print_warning "⚠️  Backend on port $port: Unhealthy"
    fi
done

# Check frontend instances
for port in 3000 3001; do
    if curl -s http://localhost:$port > /dev/null; then
        print_status "✅ Frontend on port $port: Healthy"
    else
        print_warning "⚠️  Frontend on port $port: Unhealthy"
    fi
done

# Check load balancer
if curl -s http://localhost:80 > /dev/null; then
    print_status "✅ Load Balancer: Healthy"
else
    print_warning "⚠️  Load Balancer: Unhealthy"
fi

# Check Redis cluster
if docker exec redis-node-1 redis-cli ping > /dev/null 2>&1; then
    print_status "✅ Redis Cluster: Healthy"
else
    print_warning "⚠️  Redis Cluster: Unhealthy"
fi

# Check monitoring
if curl -s http://localhost:9090/-/healthy > /dev/null; then
    print_status "✅ Prometheus: Healthy"
else
    print_warning "⚠️  Prometheus: Unhealthy"
fi

if curl -s http://localhost:3000/api/health > /dev/null; then
    print_status "✅ Grafana: Healthy"
else
    print_warning "⚠️  Grafana: Unhealthy"
fi

echo ""
print_status "Deployment completed successfully!"
print_status "Monitor the application with: docker-compose logs -f"
print_status "Scale backend: docker-compose up -d --scale backend=5"
print_status "Stop all services: docker-compose down"
