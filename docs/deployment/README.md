# 🚀 EnergyOpti-Pro Deployment Guide

This guide covers the complete deployment process for EnergyOpti-Pro, from local development to production cloud deployment.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Monitoring & Observability](#monitoring--observability)
7. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### Required Software
- **Python 3.11+** - Backend development
- **Node.js 18+** - Frontend development
- **PostgreSQL 15+** - Database
- **Redis 7+** - Caching
- **Git** - Version control

### Optional Software
- **Docker & Docker Compose** - Containerized deployment
- **Nginx** - Reverse proxy (if not using Docker)

## 🏠 Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-username/energyopti-pro.git
cd energyopti-pro
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp env.example .env
# Edit .env with your configuration

# Run database migrations
python -m alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

### 4. Database Setup
```bash
# Install PostgreSQL and Redis
# On Windows: Use WSL or Docker
# On macOS: brew install postgresql redis
# On Ubuntu: sudo apt install postgresql redis-server

# Create database
createdb energyopti_pro

# Start Redis
redis-server
```

## 🐳 Docker Deployment

### 1. Install Docker
- **Windows**: Install Docker Desktop
- **macOS**: Install Docker Desktop
- **Linux**: Follow [Docker installation guide](https://docs.docker.com/engine/install/)

### 2. Start Services
```bash
# Build and start all services
docker compose up -d

# View logs
docker compose logs -f

# Check status
docker compose ps
```

### 3. Service URLs
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **Nginx**: http://localhost:80
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001

### 4. Management Commands
```bash
# Stop services
docker compose down

# Restart services
docker compose restart

# Rebuild images
docker compose build --no-cache

# Clean up
docker compose down -v --remove-orphans
```

## ☁️ Cloud Deployment

### Render (Backend)

#### 1. Create Render Account
- Sign up at [render.com](https://render.com)
- Create a new account

#### 2. Create Web Service
```yaml
# render.yaml
services:
  - type: web
    name: energyopti-pro-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: DATABASE_URL
        fromDatabase:
          name: energyopti-pro-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: energyopti-pro-redis
          property: connectionString
```

#### 3. Create Database
```yaml
  - type: pserv
    name: energyopti-pro-db
    env: postgresql
    plan: free
```

#### 4. Create Redis
```yaml
  - type: redis
    name: energyopti-pro-redis
    plan: free
```

#### 5. Deploy
```bash
# Push to GitHub (Render auto-deploys)
git push origin main

# Or manually deploy
render deploy
```

### Vercel (Frontend)

#### 1. Create Vercel Account
- Sign up at [vercel.com](https://vercel.com)
- Connect your GitHub account

#### 2. Import Project
- Click "New Project"
- Import from GitHub
- Select your repository
- Set root directory to `frontend`

#### 3. Environment Variables
```bash
REACT_APP_API_URL=https://your-backend.onrender.com
REACT_APP_ENVIRONMENT=production
```

#### 4. Deploy
```bash
# Vercel auto-deploys on push
git push origin main

# Or manually deploy
vercel --prod
```

## 🔄 CI/CD Pipeline

### GitHub Actions

The project includes a comprehensive CI/CD pipeline in `.github/workflows/deploy.yml`:

#### Features
- **Automated Testing**: Runs all tests on every push
- **Security Scanning**: Bandit, Safety, Trivy vulnerability scanning
- **Code Coverage**: Generates coverage reports
- **Auto-deployment**: Deploys to Render and Vercel on main branch
- **Integration Testing**: End-to-end testing after deployment

#### Setup
1. Add repository secrets in GitHub:
   ```
   RENDER_TOKEN=your_render_token
   RENDER_SERVICE_ID=your_service_id
   VERCEL_TOKEN=your_vercel_token
   VERCEL_ORG_ID=your_org_id
   VERCEL_PROJECT_ID=your_project_id
   ```

2. Push to main branch to trigger deployment

#### Manual Deployment
```bash
# Trigger workflow manually
gh workflow run deploy.yml
```

## 📊 Monitoring & Observability

### Prometheus Metrics
- **Backend Metrics**: `/metrics` endpoint
- **System Metrics**: Node exporter
- **Custom Metrics**: Business KPIs

### Grafana Dashboards
- **System Health**: CPU, memory, disk usage
- **Application Metrics**: Request rate, response time, error rate
- **Business Metrics**: Trading volume, user activity

### Health Checks
```bash
# Backend health
curl https://your-backend.onrender.com/api/health

# Frontend health
curl https://your-frontend.vercel.app
```

### Logging
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Log Aggregation**: Centralized log collection

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check database status
docker compose ps postgres

# Check logs
docker compose logs postgres

# Restart database
docker compose restart postgres
```

#### 2. JWT Validation Issues
```bash
# Check environment variables
echo $SECRET_KEY
echo $ISSUER
echo $AUDIENCE

# Regenerate JWT secret
openssl rand -hex 32
```

#### 3. Frontend-Backend Connection
```bash
# Check API URL in frontend
cat frontend/.env.local

# Test API endpoint
curl https://your-backend.onrender.com/api/health
```

#### 4. Rate Limiting
```bash
# Check rate limit configuration
grep RATE_LIMIT .env

# Monitor rate limit headers
curl -I https://your-backend.onrender.com/api/prices
```

### Performance Issues

#### 1. Slow Database Queries
```sql
-- Enable query logging
SET log_statement = 'all';

-- Check slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

#### 2. Memory Issues
```bash
# Check memory usage
docker stats

# Restart services
docker compose restart
```

#### 3. Network Latency
```bash
# Test latency to cloud services
ping your-backend.onrender.com
ping your-frontend.vercel.app
```

## 🔒 Security Considerations

### Environment Variables
- Never commit `.env` files
- Use strong, unique secrets
- Rotate secrets regularly

### SSL/TLS
- Enable HTTPS on all endpoints
- Use Let's Encrypt for free certificates
- Configure security headers

### Access Control
- Implement proper authentication
- Use role-based access control
- Monitor access logs

### Data Protection
- Encrypt data at rest
- Use secure connections
- Implement data backup

## 📈 Scaling Considerations

### Horizontal Scaling
- Multiple backend instances
- Load balancer configuration
- Database read replicas

### Caching Strategy
- Redis for session storage
- CDN for static assets
- Application-level caching

### Database Optimization
- Connection pooling
- Query optimization
- Index management

## 📞 Support

### Getting Help
1. Check the [troubleshooting section](#troubleshooting)
2. Review [GitHub issues](https://github.com/your-username/energyopti-pro/issues)
3. Create a new issue with detailed information

### Useful Commands
```bash
# Check service status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs

# Health check
./scripts/deploy.sh health

# Run tests
./scripts/deploy.sh test
```

---

**🎯 Next Steps**
1. Set up your environment variables
2. Deploy to Render and Vercel
3. Configure monitoring and alerts
4. Set up CI/CD pipeline
5. Test end-to-end functionality

**📚 Additional Resources**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
