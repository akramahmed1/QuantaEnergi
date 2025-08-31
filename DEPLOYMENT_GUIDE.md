# 🚀 EnergyOpti-Pro Deployment Guide

## 📋 Overview

This guide covers the complete deployment of EnergyOpti-Pro with horizontal scaling, Redis clustering, monitoring, and load balancing.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend 1    │    │   Frontend 2    │    │   Frontend 3    │
│   (Port 3000)   │    │   (Port 3001)   │    │   (Port 3002)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Nginx LB      │
                    │   (Port 80)     │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Backend 1     │    │   Backend 2     │    │   Backend 3     │
│   (Port 8001)   │    │   (Port 8002)   │    │   (Port 8003)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Redis Cluster  │
                    │  (3 Nodes)      │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │     Grafana     │    │   Monitoring    │
│   (Port 9090)   │    │   (Port 3000)   │    │     Stack       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🐳 Docker Compose Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- At least 8GB RAM
- 20GB free disk space

### Quick Start

1. **Clone and navigate to project:**
   ```bash
   cd energyopti-pro
   ```

2. **Make scripts executable:**
   ```bash
   chmod +x scripts/deploy-docker.sh
   chmod +x scripts/deploy-k8s.sh
   ```

3. **Deploy with Docker Compose:**
   ```bash
   ./scripts/deploy-docker.sh
   ```

### Manual Deployment

1. **Start Redis Cluster:**
   ```bash
   docker-compose up -d redis-node-1 redis-node-2 redis-node-3
   ```

2. **Initialize Redis Cluster:**
   ```bash
   docker exec redis-node-1 redis-cli --cluster create \
     redis-node-1:6379 \
     redis-node-2:6379 \
     redis-node-3:6379 \
     --cluster-replicas 0 \
     --cluster-yes
   ```

3. **Start monitoring:**
   ```bash
   docker-compose up -d prometheus grafana
   ```

4. **Start backend instances:**
   ```bash
   docker-compose up -d backend-1 backend-2 backend-3
   ```

5. **Start frontend instances:**
   ```bash
   docker-compose up -d frontend-1 frontend-2
   ```

6. **Start load balancer:**
   ```bash
   docker-compose up -d nginx
   ```

### Verification

```bash
# Check all services
docker-compose ps

# Check logs
docker-compose logs -f

# Health checks
curl http://localhost:8001/api/health
curl http://localhost:8002/api/health
curl http://localhost:8003/api/health
curl http://localhost:80/api/health
```

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes 1.20+
- kubectl configured
- At least 4 CPU cores
- 16GB RAM
- 50GB storage

### Quick Start

1. **Deploy with script:**
   ```bash
   ./scripts/deploy-k8s.sh
   ```

### Manual Deployment

1. **Create namespace:**
   ```bash
   kubectl apply -f k8s/monitoring.yaml
   ```

2. **Deploy Redis Cluster:**
   ```bash
   kubectl apply -f k8s/redis-cluster.yaml
   ```

3. **Deploy monitoring:**
   ```bash
   kubectl apply -f k8s/monitoring.yaml
   ```

4. **Deploy application:**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   ```

### Verification

```bash
# Check pods
kubectl get pods -n energyopti-pro

# Check services
kubectl get services -n energyopti-pro

# Check deployments
kubectl get deployments -n energyopti-pro

# Port forward for local access
kubectl port-forward service/energyopti-backend-service 8001:80
kubectl port-forward service/energyopti-frontend-service 3000:80
kubectl port-forward service/prometheus-service 9090:9090
kubectl port-forward service/grafana-service 3001:3000
```

## 📊 Monitoring & Observability

### Prometheus

- **URL:** http://localhost:9090
- **Metrics Endpoint:** `/api/monitoring/metrics`
- **Health Check:** `/-/healthy`

### Grafana

- **URL:** http://localhost:3000 (Docker) / http://localhost:3001 (K8s)
- **Credentials:** admin/admin
- **Dashboard:** EnergyOpti-Pro Production Dashboard

### Key Metrics

- **System:** CPU, Memory, Disk usage
- **API:** Request rate, response time, error rate
- **Redis:** Cache hit rate, memory usage, operations/sec
- **Business:** Trading volume, forecasting accuracy
- **Infrastructure:** Pod health, scaling metrics

## 🔧 Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_CLUSTER_HOSTS=redis-node-1:6379,redis-node-2:6379,redis-node-3:6379
REDIS_HOST=redis-node-1
REDIS_PORT=6379
REDIS_PASSWORD=your_password

# Database Configuration
DATABASE_URL=sqlite:///energyopti_pro.db

# Logging
LOG_LEVEL=INFO

# API Configuration
API_RATE_LIMIT=100
API_RATE_LIMIT_WINDOW=60
```

### Scaling Configuration

```bash
# Scale backend instances
docker-compose up -d --scale backend=5

# Scale Kubernetes deployment
kubectl scale deployment energyopti-backend --replicas=5

# Auto-scaling (Kubernetes)
kubectl get hpa -n energyopti-pro
```

## 🧪 Testing

### Run PR5 Tests

```bash
# Install dependencies
pip install requests

# Run comprehensive tests
python scripts/test-pr5.py
```

### Load Testing

```bash
# Test with Apache Bench
ab -n 1000 -c 10 http://localhost:80/api/health

# Test with wrk
wrk -t12 -c400 -d30s http://localhost:80/api/health
```

### Cache Testing

```bash
# Test Redis cluster
docker exec redis-node-1 redis-cli cluster info
docker exec redis-node-1 redis-cli cluster nodes

# Test cache performance
curl -X POST http://localhost:8001/api/forecast \
  -H "Content-Type: application/json" \
  -d '{"commodity": "crude_oil", "forecast_days": 7, "use_cache": true}'
```

## 🚨 Troubleshooting

### Common Issues

1. **Redis Connection Failed:**
   ```bash
   # Check Redis cluster status
   docker exec redis-node-1 redis-cli cluster info
   
   # Restart Redis nodes
   docker-compose restart redis-node-1 redis-node-2 redis-node-3
   ```

2. **Backend Health Check Failed:**
   ```bash
   # Check backend logs
   docker-compose logs backend-1
   
   # Check database connection
   curl http://localhost:8001/api/monitoring/health/detailed
   ```

3. **Load Balancer Issues:**
   ```bash
   # Check Nginx configuration
   docker exec energyopti-nginx nginx -t
   
   # Check Nginx logs
   docker-compose logs nginx
   ```

4. **Monitoring Issues:**
   ```bash
   # Check Prometheus targets
   curl http://localhost:9090/api/v1/targets
   
   # Check Grafana datasources
   curl http://localhost:3000/api/datasources
   ```

### Performance Tuning

1. **Redis Optimization:**
   ```bash
   # Increase memory limit
   docker-compose up -d --scale redis-node-1=1 --scale redis-node-2=1 --scale redis-node-3=1
   ```

2. **Backend Optimization:**
   ```bash
   # Increase worker processes
   environment:
     - WORKERS=4
     - MAX_REQUESTS=1000
   ```

3. **Nginx Optimization:**
   ```bash
   # Adjust worker processes
   worker_processes auto;
   worker_connections 1024;
   ```

## 📈 Scaling Strategies

### Horizontal Scaling

- **Backend:** 3-10 instances based on CPU/memory
- **Frontend:** 2-5 instances for redundancy
- **Redis:** 3-6 nodes for high availability

### Auto-scaling

- **CPU Threshold:** 70%
- **Memory Threshold:** 80%
- **Scale Up:** Aggressive (100% increase)
- **Scale Down:** Conservative (10% decrease)

### Load Balancing

- **Algorithm:** Least connections
- **Health Checks:** Every 10 seconds
- **Failover:** Automatic
- **Sticky Sessions:** Disabled

## 🔒 Security

### Network Security

- **Internal Communication:** Docker network isolation
- **External Access:** Nginx reverse proxy
- **Rate Limiting:** 100 requests/minute per IP
- **SSL/TLS:** Configured in Nginx

### Access Control

- **API Authentication:** JWT tokens
- **Monitoring Access:** Basic auth
- **Database Access:** Connection pooling
- **Redis Access:** Password protected

## 📚 Additional Resources

### Documentation

- [API Documentation](api_documentation.md)
- [Architecture Diagrams](docs/architecture/)
- [Testing Guide](tests/README.md)

### Support

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Wiki:** Project Wiki

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🎯 Production Checklist

- [ ] All health checks passing
- [ ] Monitoring dashboards active
- [ ] Alerting rules configured
- [ ] Backup strategy implemented
- [ ] SSL certificates configured
- [ ] Rate limiting enabled
- [ ] Log aggregation setup
- [ ] Performance benchmarks met
- [ ] Security scan completed
- [ ] Disaster recovery tested

---

**🎉 Congratulations!** Your EnergyOpti-Pro deployment is now ready for production use with enterprise-grade scalability, monitoring, and reliability features.
