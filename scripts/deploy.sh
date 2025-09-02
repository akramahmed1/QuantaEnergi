#!/bin/bash

# QuantaEnergi Production Deployment Script
# This script deploys the complete QuantaEnergi platform to production

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
CLUSTER_NAME="quantaenergi-cluster"
REGION="us-east-1"
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

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed. Please install kubectl first."
    fi
    
    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        error "helm is not installed. Please install helm first."
    fi
    
    # Check if aws CLI is installed
    if ! command -v aws &> /dev/null; then
        error "AWS CLI is not installed. Please install AWS CLI first."
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    log "All prerequisites are satisfied."
}

# Create EKS cluster
create_eks_cluster() {
    log "Creating EKS cluster: $CLUSTER_NAME"
    
    # Check if cluster already exists
    if aws eks describe-cluster --name $CLUSTER_NAME --region $REGION &> /dev/null; then
        log "Cluster $CLUSTER_NAME already exists. Skipping creation."
        return
    fi
    
    # Create EKS cluster
    eksctl create cluster \
        --name $CLUSTER_NAME \
        --region $REGION \
        --nodegroup-name standard-workers \
        --node-type t3.medium \
        --nodes 3 \
        --nodes-min 1 \
        --nodes-max 5 \
        --managed
    
    log "EKS cluster created successfully."
}

# Install required add-ons
install_addons() {
    log "Installing required add-ons..."
    
    # Install AWS Load Balancer Controller
    log "Installing AWS Load Balancer Controller..."
    helm repo add eks https://aws.github.io/eks-charts
    helm repo update
    
    helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
        -n kube-system \
        --set clusterName=$CLUSTER_NAME \
        --set serviceAccount.create=false \
        --set serviceAccount.name=aws-load-balancer-controller
    
    # Install cert-manager for SSL certificates
    log "Installing cert-manager..."
    helm repo add jetstack https://charts.jetstack.io
    helm repo update
    
    helm install cert-manager jetstack/cert-manager \
        --namespace cert-manager \
        --create-namespace \
        --version v1.13.0 \
        --set installCRDs=true
    
    # Wait for cert-manager to be ready
    log "Waiting for cert-manager to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s
    
    # Install NGINX Ingress Controller
    log "Installing NGINX Ingress Controller..."
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    
    helm install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer \
        --set controller.ingressClassResource.name=nginx \
        --set controller.ingressClassResource.default=true
    
    log "All add-ons installed successfully."
}

# Create namespaces
create_namespaces() {
    log "Creating namespaces..."
    
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace $MONITORING_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    log "Namespaces created successfully."
}

# Build and push Docker images
build_images() {
    log "Building and pushing Docker images..."
    
    # Set AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
    
    # Create ECR repositories
    aws ecr create-repository --repository-name quantaenergi/backend --region $REGION --output text || true
    aws ecr create-repository --repository-name quantaenergi/frontend --region $REGION --output text || true
    
    # Login to ECR
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
    
    # Build and push backend image
    log "Building backend image..."
    docker build -t $ECR_REGISTRY/quantaenergi/backend:latest backend/
    docker push $ECR_REGISTRY/quantaenergi/backend:latest
    
    # Build and push frontend image
    log "Building frontend image..."
    docker build -t $ECR_REGISTRY/quantaenergi/frontend:latest frontend/
    docker push $ECR_REGISTRY/quantaenergi/frontend:latest
    
    # Update deployment files with ECR registry
    sed -i "s|quantaenergi/backend:latest|$ECR_REGISTRY/quantaenergi/backend:latest|g" kubernetes/deployment.yaml
    sed -i "s|quantaenergi/frontend:latest|$ECR_REGISTRY/quantaenergi/frontend:latest|g" kubernetes/deployment.yaml
    
    log "Docker images built and pushed successfully."
}

# Deploy database and Redis
deploy_infrastructure() {
    log "Deploying infrastructure components..."
    
    # Deploy PostgreSQL and Redis
    kubectl apply -f kubernetes/database.yaml
    
    # Wait for database to be ready
    log "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod -l app=quantaenergi-postgres -n $NAMESPACE --timeout=300s
    
    log "Waiting for Redis to be ready..."
    kubectl wait --for=condition=ready pod -l app=quantaenergi-redis-cluster -n $NAMESPACE --timeout=300s
    
    log "Infrastructure components deployed successfully."
}

# Deploy monitoring stack
deploy_monitoring() {
    log "Deploying monitoring stack..."
    
    kubectl apply -f kubernetes/monitoring.yaml
    
    # Wait for monitoring components to be ready
    log "Waiting for Prometheus to be ready..."
    kubectl wait --for=condition=ready pod -l app=prometheus -n $MONITORING_NAMESPACE --timeout=300s
    
    log "Waiting for Grafana to be ready..."
    kubectl wait --for=condition=ready pod -l app=grafana -n $MONITORING_NAMESPACE --timeout=300s
    
    log "Monitoring stack deployed successfully."
}

# Deploy application
deploy_application() {
    log "Deploying QuantaEnergi application..."
    
    kubectl apply -f kubernetes/deployment.yaml
    
    # Wait for application to be ready
    log "Waiting for backend to be ready..."
    kubectl wait --for=condition=ready pod -l app=quantaenergi-backend -n $NAMESPACE --timeout=300s
    
    log "Waiting for frontend to be ready..."
    kubectl wait --for=condition=ready pod -l app=quantaenergi-frontend -n $NAMESPACE --timeout=300s
    
    log "Application deployed successfully."
}

# Configure SSL certificates
configure_ssl() {
    log "Configuring SSL certificates..."
    
    # Create ClusterIssuer for Let's Encrypt
    cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@$DOMAIN
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
    
    log "SSL certificates configured successfully."
}

# Setup DNS and CDN
setup_dns_cdn() {
    log "Setting up DNS and CDN..."
    
    # Get Load Balancer DNS name
    LB_DNS=$(kubectl get service -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    
    if [ -z "$LB_DNS" ]; then
        warn "Load Balancer DNS name not available yet. Please wait a few minutes and run this script again."
        return
    fi
    
    log "Load Balancer DNS: $LB_DNS"
    
    # Create Route53 hosted zone if it doesn't exist
    HOSTED_ZONE_ID=$(aws route53 list-hosted-zones-by-name --dns-name $DOMAIN --query 'HostedZones[0].Id' --output text 2>/dev/null || echo "")
    
    if [ -z "$HOSTED_ZONE_ID" ]; then
        log "Creating Route53 hosted zone for $DOMAIN..."
        HOSTED_ZONE_ID=$(aws route53 create-hosted-zone --name $DOMAIN --caller-reference $(date +%s) --query 'HostedZone.Id' --output text)
        HOSTED_ZONE_ID=${HOSTED_ZONE_ID#/hostedzone/}
    fi
    
    # Create DNS records
    log "Creating DNS records..."
    
    # API subdomain
    aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch '{
        "Changes": [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": "api.'$DOMAIN'",
                    "Type": "CNAME",
                    "TTL": 300,
                    "ResourceRecords": [
                        {
                            "Value": "'$LB_DNS'"
                        }
                    ]
                }
            }
        ]
    }'
    
    # App subdomain
    aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch '{
        "Changes": [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": "app.'$DOMAIN'",
                    "Type": "CNAME",
                    "TTL": 300,
                    "ResourceRecords": [
                        {
                            "Value": "'$LB_DNS'"
                        }
                    ]
                }
            }
        ]
    }'
    
    # Monitoring subdomain
    aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch '{
        "Changes": [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": "monitoring.'$DOMAIN'",
                    "Type": "CNAME",
                    "TTL": 300,
                    "ResourceRecords": [
                        {
                            "Value": "'$LB_DNS'"
                        }
                    ]
                }
            }
        ]
    }'
    
    log "DNS records created successfully."
    
    # Setup Cloudflare CDN (if configured)
    if [ ! -z "$CLOUDFLARE_API_TOKEN" ]; then
        log "Setting up Cloudflare CDN..."
        # Add Cloudflare configuration here
    fi
    
    log "DNS and CDN setup completed."
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Wait for database initialization job to complete
    kubectl wait --for=condition=complete job/quantaenergi-db-init -n $NAMESPACE --timeout=600s
    
    log "Database migrations completed successfully."
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Check backend health
    BACKEND_HEALTH=$(kubectl get pods -n $NAMESPACE -l app=quantaenergi-backend -o jsonpath='{.items[0].status.phase}')
    if [ "$BACKEND_HEALTH" != "Running" ]; then
        error "Backend is not healthy. Status: $BACKEND_HEALTH"
    fi
    
    # Check frontend health
    FRONTEND_HEALTH=$(kubectl get pods -n $NAMESPACE -l app=quantaenergi-frontend -o jsonpath='{.items[0].status.phase}')
    if [ "$FRONTEND_HEALTH" != "Running" ]; then
        error "Frontend is not healthy. Status: $FRONTEND_HEALTH"
    fi
    
    # Check monitoring health
    PROMETHEUS_HEALTH=$(kubectl get pods -n $MONITORING_NAMESPACE -l app=prometheus -o jsonpath='{.items[0].status.phase}')
    if [ "$PROMETHEUS_HEALTH" != "Running" ]; then
        error "Prometheus is not healthy. Status: $PROMETHEUS_HEALTH"
    fi
    
    log "All components are healthy!"
}

# Display deployment information
display_info() {
    log "Deployment completed successfully!"
    echo ""
    echo "=== QuantaEnergi Production Deployment ==="
    echo "Cluster Name: $CLUSTER_NAME"
    echo "Region: $REGION"
    echo "Domain: $DOMAIN"
    echo ""
    echo "=== Access URLs ==="
    echo "Main Application: https://app.$DOMAIN"
    echo "API: https://api.$DOMAIN"
    echo "API Documentation: https://api.$DOMAIN/docs"
    echo "Monitoring: https://monitoring.$DOMAIN"
    echo ""
    echo "=== Monitoring Credentials ==="
    echo "Grafana: admin / admin123"
    echo "Prometheus: No authentication required"
    echo ""
    echo "=== Next Steps ==="
    echo "1. Update DNS records if using custom domain"
    echo "2. Configure monitoring alerts"
    echo "3. Set up backup and disaster recovery"
    echo "4. Run security scans and penetration tests"
    echo "5. Begin beta user onboarding"
    echo ""
}

# Main deployment function
main() {
    log "Starting QuantaEnergi production deployment..."
    
    check_prerequisites
    create_eks_cluster
    install_addons
    create_namespaces
    build_images
    deploy_infrastructure
    deploy_monitoring
    deploy_application
    configure_ssl
    setup_dns_cdn
    run_migrations
    health_check
    display_info
    
    log "Deployment completed successfully!"
}

# Run main function
main "$@"
