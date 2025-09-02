# QuantaEnergi Infrastructure Deployment Guide

## Overview
This guide covers the deployment and management of QuantaEnergi's production infrastructure on AWS EKS (Elastic Kubernetes Service). The infrastructure is designed to support a production-ready ETRM/CTRM platform with high availability, security, and scalability.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Environment                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Frontend      │  │    Backend      │  │  Monitoring │ │
│  │  (React/Next.js)│  │   (FastAPI)     │  │ (Prometheus)│ │
│  │   + Nginx       │  │   + Workers     │  │  + Grafana  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   PostgreSQL    │  │      Redis      │  │   Ingress   │ │
│  │   (StatefulSet) │  │   (Cluster)     │  │ Controller  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   EKS Cluster   │  │   Load Balancer │  │   Route53   │ │
│  │   (Kubernetes)  │  │   (AWS ALB)     │  │   (DNS)     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Required Tools
- **kubectl**: Kubernetes command-line tool
- **helm**: Kubernetes package manager
- **AWS CLI**: AWS command-line interface
- **eksctl**: EKS cluster management tool
- **Docker**: Container runtime
- **git**: Version control

### Required AWS Permissions
- EKS cluster creation and management
- EC2 instance management
- IAM role and policy management
- ECR repository management
- Route53 DNS management
- Load balancer creation

### System Requirements
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **OS**: Linux, macOS, or Windows with WSL2

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/akramahmed1/EnergyOpti-Pro.git
cd EnergyOpti-Pro
```

### 2. Install Prerequisites
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### 3. Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and default region
```

### 4. Deploy Infrastructure
```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

## Detailed Deployment Process

### Phase 1: EKS Cluster Creation
The deployment script will:
1. Create an EKS cluster with managed node groups
2. Install required add-ons (Load Balancer Controller, cert-manager)
3. Set up NGINX Ingress Controller
4. Create necessary namespaces

### Phase 2: Infrastructure Deployment
1. **Database Layer**
   - PostgreSQL StatefulSet with persistent storage
   - Redis cluster for caching and sessions
   - Database initialization and migrations

2. **Monitoring Stack**
   - Prometheus for metrics collection
   - Grafana for visualization
   - Node exporter for system metrics

3. **Application Layer**
   - Backend services with auto-scaling
   - Frontend services with Nginx
   - Ingress rules and SSL configuration

### Phase 3: External Access Setup
1. **DNS Configuration**
   - Route53 hosted zone creation
   - Subdomain routing (api, app, monitoring)
   - Load balancer integration

2. **SSL Certificates**
   - Let's Encrypt integration
   - Automatic certificate renewal
   - HTTPS enforcement

## Configuration Files

### Kubernetes Configurations
- `kubernetes/deployment.yaml` - Main application deployment
- `kubernetes/database.yaml` - Database and Redis configurations
- `kubernetes/monitoring.yaml` - Monitoring stack configuration

### Docker Configurations
- `backend/Dockerfile` - Backend container configuration
- `frontend/Dockerfile` - Frontend container configuration
- `frontend/nginx.conf` - Nginx server configuration

### Environment Configuration
- `backend/env.production.template` - Production environment template
- `backend/app/core/production_config.py` - Production configuration management

## Management and Operations

### Monitoring and Observability
- **Grafana Dashboards**: Access at `https://monitoring.quantaenergi.com`
- **Prometheus Metrics**: Available at `/metrics` endpoints
- **Application Logs**: Access via `kubectl logs`
- **Health Checks**: Available at `/health` endpoints

### Scaling and Performance
- **Auto-scaling**: HPA configured for backend services
- **Resource Limits**: CPU and memory limits configured
- **Load Balancing**: NGINX ingress with AWS ALB
- **Caching**: Redis cluster for session and data caching

### Security Features
- **OWASP Compliance**: Built-in security middleware
- **Rate Limiting**: API abuse prevention
- **JWT Authentication**: Secure token-based auth
- **HTTPS Enforcement**: SSL/TLS encryption
- **Non-root Containers**: Security-hardened images

## Testing and Validation

### Run Infrastructure Tests
```bash
# Make test script executable
chmod +x scripts/test_deployment.sh

# Run comprehensive tests
./scripts/test_deployment.sh
```

### Manual Testing
```bash
# Check pod status
kubectl get pods -n quantaenergi
kubectl get pods -n monitoring

# Check services
kubectl get services -n quantaenergi
kubectl get services -n monitoring

# Check ingress
kubectl get ingress -n quantaenergi
kubectl get ingress -n monitoring

# Check logs
kubectl logs -n quantaenergi -l app=quantaenergi-backend
kubectl logs -n quantaenergi -l app=quantaenergi-frontend
```

## Troubleshooting

### Common Issues

#### 1. Pod Startup Issues
```bash
# Check pod events
kubectl describe pod <pod-name> -n quantaenergi

# Check pod logs
kubectl logs <pod-name> -n quantaenergi

# Check resource usage
kubectl top pods -n quantaenergi
```

#### 2. Database Connection Issues
```bash
# Check database pod status
kubectl get pods -n quantaenergi -l app=quantaenergi-postgres

# Check database logs
kubectl logs -n quantaenergi -l app=quantaenergi-postgres

# Test database connectivity
kubectl run test-db --image=postgres:15-alpine --rm -i --restart=Never -- psql -h quantaenergi-postgres.quantaenergi.svc.cluster.local -U quantaenergi_user -d quantaenergi_db -c "SELECT 1;"
```

#### 3. Monitoring Issues
```bash
# Check monitoring pod status
kubectl get pods -n monitoring

# Check Prometheus configuration
kubectl get configmap prometheus-config -n monitoring -o yaml

# Check Grafana configuration
kubectl get configmap grafana-datasources -n monitoring -o yaml
```

#### 4. Ingress Issues
```bash
# Check ingress controller status
kubectl get pods -n ingress-nginx

# Check ingress rules
kubectl get ingress -A

# Check load balancer
kubectl get service -n ingress-nginx ingress-nginx-controller
```

### Performance Optimization

#### 1. Resource Tuning
```bash
# Adjust resource limits
kubectl edit deployment quantaenergi-backend -n quantaenergi
kubectl edit deployment quantaenergi-frontend -n quantaenergi

# Scale services
kubectl scale deployment quantaenergi-backend -n quantaenergi --replicas=5
kubectl scale deployment quantaenergi-frontend -n quantaenergi --replicas=3
```

#### 2. Database Optimization
```bash
# Check database performance
kubectl exec -n quantaenergi quantaenergi-postgres-0 -- psql -U quantaenergi_user -d quantaenergi_db -c "SELECT * FROM pg_stat_activity;"

# Optimize PostgreSQL settings
kubectl edit configmap quantaenergi-config -n quantaenergi
```

## Backup and Disaster Recovery

### Database Backups
```bash
# Create database backup
kubectl exec -n quantaenergi quantaenergi-postgres-0 -- pg_dump -U quantaenergi_user quantaenergi_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database backup
kubectl exec -i -n quantaenergi quantaenergi-postgres-0 -- psql -U quantaenergi_user -d quantaenergi_db < backup_file.sql
```

### Configuration Backups
```bash
# Backup Kubernetes configurations
kubectl get all -n quantaenergi -o yaml > quantaenergi_backup_$(date +%Y%m%d_%H%M%S).yaml
kubectl get all -n monitoring -o yaml > monitoring_backup_$(date +%Y%m%d_%H%M%S).yaml
```

### Disaster Recovery
1. **Cluster Recovery**: Use eksctl to recreate cluster
2. **Data Recovery**: Restore from database backups
3. **Application Recovery**: Redeploy from configuration backups

## Security Considerations

### Network Security
- **VPC Configuration**: Private subnets for database and application
- **Security Groups**: Restrictive access rules
- **Network Policies**: Kubernetes network policies for pod communication

### Access Control
- **RBAC**: Role-based access control for Kubernetes
- **Service Accounts**: Limited permissions for applications
- **IAM Roles**: AWS IAM roles for EKS nodes

### Data Security
- **Encryption**: Data encrypted at rest and in transit
- **Secrets Management**: Kubernetes secrets for sensitive data
- **Audit Logging**: Comprehensive logging of all activities

## Cost Optimization

### Resource Management
- **Auto-scaling**: Scale down during low usage
- **Spot Instances**: Use spot instances for non-critical workloads
- **Resource Limits**: Set appropriate CPU and memory limits

### Storage Optimization
- **EBS Optimization**: Use appropriate EBS volume types
- **Data Lifecycle**: Implement data retention policies
- **Backup Strategy**: Optimize backup frequency and retention

## Maintenance and Updates

### Regular Maintenance
1. **Security Updates**: Monthly security patches
2. **Performance Monitoring**: Weekly performance reviews
3. **Backup Verification**: Daily backup validation
4. **Log Rotation**: Weekly log management

### Update Procedures
1. **Application Updates**: Rolling updates with zero downtime
2. **Infrastructure Updates**: Blue-green deployment for major changes
3. **Database Updates**: Maintenance windows for database changes

## Support and Resources

### Documentation
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Helm Documentation](https://helm.sh/docs/)

### Community Support
- [Kubernetes Slack](https://slack.k8s.io/)
- [AWS Developer Forums](https://forums.aws.amazon.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/kubernetes)

### Professional Support
- **AWS Support**: Enterprise support for AWS services
- **Kubernetes Support**: Community and commercial support options
- **QuantaEnergi Support**: Internal support team

## Conclusion

This infrastructure deployment provides a robust, scalable, and secure foundation for the QuantaEnergi ETRM/CTRM platform. The comprehensive monitoring, security, and automation features ensure high availability and operational excellence.

For additional support or questions, please refer to the troubleshooting section or contact the QuantaEnergi support team.

---

**Last Updated**: $(date)
**Version**: 1.0.0
**Status**: Production Ready
