# 🚀 QuantaEnergi ETRM/CTRM Deployment Guide

## 📋 Overview

QuantaEnergi is a complete Enterprise Energy Trading and Risk Management (ETRM/CTRM) platform with:

- **Frontend**: React/TypeScript with Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: PostgreSQL with Redis caching
- **Security**: Enterprise-grade authentication and authorization
- **Compliance**: REMIT, FERC, CFTC, NERC, EMIR, GDPR compliance

## 🏗️ Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (optional, SQLite for development)
- Redis (optional, in-memory for development)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/akramahmed1/QuantaEnergi.git
cd QuantaEnergi

# Start the complete application
python start_etrm.py
```

This will:
1. Install all dependencies
2. Create default admin user (admin/admin123)
3. Start backend on http://localhost:8000
4. Start frontend on http://localhost:3000

### Manual Setup

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python create_default_user.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 🌐 Production Deployment

### Option 1: Railway (Backend) + Vercel (Frontend)

#### Backend Deployment on Railway
1. **Connect to Railway**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and connect
   railway login
   railway link
   ```

2. **Deploy Backend**:
   ```bash
   railway up
   ```

3. **Set Environment Variables**:
   - `DATABASE_URL`: PostgreSQL connection string
   - `JWT_SECRET`: Strong secret key (32+ characters)
   - `REDIS_URL`: Redis connection string
   - `TLS_ENABLED`: true
   - `RATE_LIMIT_ENABLED`: true
   - `AUDIT_LOGGING_ENABLED`: true

#### Frontend Deployment on Vercel
1. **Connect to Vercel**:
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Login and deploy
   vercel login
   vercel --prod
   ```

2. **Set Environment Variables**:
   - `REACT_APP_API_URL`: Your Railway backend URL
   - `REACT_APP_WS_URL`: Your Railway WebSocket URL
   - `REACT_APP_ENVIRONMENT`: production

### Option 2: Render (Full Stack)

#### Backend on Render
1. Create new **Web Service**
2. Connect GitHub repository
3. Set build command: `cd backend && pip install -r requirements.txt`
4. Set start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Set environment variables

#### Frontend on Render
1. Create new **Static Site**
2. Connect GitHub repository
3. Set build command: `cd frontend && npm install && npm run build`
4. Set publish directory: `frontend/dist`

## 🔧 Environment Configuration

### Backend Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://host:port

# Security
JWT_SECRET=your-super-secret-jwt-key-32-chars-min
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_BASE_URL=https://your-backend-url.com
CORS_ORIGINS=["https://your-frontend-url.com"]

# Compliance
COMPLIANCE_MODE=strict
AUDIT_LOGGING_ENABLED=true
```

### Frontend Environment Variables
```bash
# API Configuration
REACT_APP_API_URL=https://your-backend-url.com
REACT_APP_WS_URL=wss://your-backend-url.com
REACT_APP_ENVIRONMENT=production
```

## 🗄️ Database Setup

### PostgreSQL (Production)
```sql
-- Create database
CREATE DATABASE quantaenergi;

-- Create user
CREATE USER quantaenergi_user WITH PASSWORD 'secure_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE quantaenergi TO quantaenergi_user;
```

### Database Migration
```bash
cd backend
alembic upgrade head
python create_default_user.py
```

## 🔐 Security Configuration

### JWT Secret Generation
```bash
# Generate secure JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### SSL/TLS Setup
- Railway/Render provide automatic SSL
- Custom domains require SSL certificates
- Use Let's Encrypt for free certificates

## 📊 Monitoring & Logging

### Health Checks
- Backend: `GET /health`
- Database: Automatic connection monitoring
- Redis: Automatic connection monitoring

### Logging
- Structured JSON logging
- Audit trail for all operations
- Compliance reporting

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Default user created
- [ ] SSL certificates configured
- [ ] CORS origins updated
- [ ] Security headers enabled

### Post-Deployment
- [ ] Health checks passing
- [ ] Login functionality working
- [ ] Trade creation working
- [ ] API documentation accessible
- [ ] Frontend-backend communication working
- [ ] WebSocket connections working

## 🔍 Troubleshooting

### Common Issues

#### Backend Not Starting
```bash
# Check logs
railway logs

# Common fixes
pip install -r requirements.txt
python create_default_user.py
```

#### Frontend Build Failing
```bash
# Clear cache and rebuild
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### Database Connection Issues
```bash
# Check connection string
echo $DATABASE_URL

# Test connection
python -c "from app.db.session import db_manager; print(db_manager.health_check())"
```

#### Authentication Issues
```bash
# Create new user
python create_default_user.py

# Check JWT secret
echo $JWT_SECRET
```

## 📈 Performance Optimization

### Backend Optimization
- Enable Redis caching
- Configure connection pooling
- Enable gzip compression
- Set up CDN for static assets

### Frontend Optimization
- Enable code splitting
- Configure service worker
- Optimize bundle size
- Enable lazy loading

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: railway up
```

## 📞 Support

### Documentation
- API Documentation: `/docs` endpoint
- Frontend Documentation: README.md
- Security Documentation: docs/security/

### Contact
- Email: team@quantaenergi.com
- GitHub: https://github.com/akramahmed1/QuantaEnergi
- Issues: GitHub Issues

---

**Status**: ✅ Production Ready
**Last Updated**: December 30, 2024
**Version**: 2.0.0
