# QuantaEnergi Deployment Guide

## 🚀 Complete Deployment Setup for Vercel + Railway

### Prerequisites

1. **Node.js 18+** and **npm**
2. **Python 3.12+** and **Poetry**
3. **Git** for version control
4. **Railway CLI**: `npm install -g @railway/cli`
5. **Vercel CLI**: `npm install -g vercel`

### Step 1: Backend Deployment (Railway)

#### 1.1 Railway Setup
```bash
# Login to Railway
railway login

# Create new project
railway new

# Link to existing project (if you have one)
railway link
```

#### 1.2 Environment Variables
Set these in Railway dashboard:

```bash
# Core Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=$PORT

# Database (Auto-configured by Railway)
DATABASE_URL=$DATABASE_URL
REDIS_URL=$REDIS_URL

# Security (Generate strong keys)
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# CORS (Update with your frontend URL)
CORS_ORIGINS=https://quantaenergi-frontend.vercel.app,https://quantaenergi.vercel.app

# External APIs
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
```

#### 1.3 Deploy Backend
```bash
cd backend
railway up
```

### Step 2: Frontend Deployment (Vercel)

#### 2.1 Vercel Setup
```bash
# Login to Vercel
vercel login

# Link to existing project
vercel link
```

#### 2.2 Environment Variables
Set these in Vercel dashboard:

```bash
# API Configuration
VITE_API_URL=https://your-backend.railway.app
VITE_WS_URL=wss://your-backend.railway.app

# App Configuration
VITE_APP_NAME=QuantaEnergi
VITE_APP_VERSION=2.0.0

# Feature Flags
VITE_ENABLE_QUANTUM=true
VITE_ENABLE_GEO_RISK=true
VITE_ENABLE_REMIT_COMPLIANCE=true
```

#### 2.3 Deploy Frontend
```bash
cd frontend
npm run build
vercel --prod
```

### Step 3: Database Setup

#### 3.1 Railway PostgreSQL
Railway automatically provisions PostgreSQL. Update your `DATABASE_URL`:

```bash
# Get database URL from Railway dashboard
railway variables
```

#### 3.2 Run Migrations
```bash
cd backend
poetry run alembic upgrade head
```

### Step 4: Redis Setup

#### 4.1 Railway Redis
Railway automatically provisions Redis. Update your `REDIS_URL`:

```bash
# Get Redis URL from Railway dashboard
railway variables
```

### Step 5: Domain Configuration

#### 5.1 Custom Domains (Optional)
- **Railway**: Configure custom domain in Railway dashboard
- **Vercel**: Configure custom domain in Vercel dashboard

#### 5.2 SSL Certificates
Both Railway and Vercel provide automatic SSL certificates.

### Step 6: Monitoring Setup

#### 6.1 Health Checks
- **Backend**: `https://your-backend.railway.app/health`
- **Frontend**: `https://your-frontend.vercel.app/`

#### 6.2 Monitoring
- **Railway**: Built-in monitoring and logs
- **Vercel**: Built-in analytics and performance monitoring

### Step 7: Testing Deployment

#### 7.1 Backend Tests
```bash
# Test API endpoints
curl https://your-backend.railway.app/health
curl https://your-backend.railway.app/docs
```

#### 7.2 Frontend Tests
```bash
# Test frontend
curl https://your-frontend.vercel.app/
```

### Step 8: Production Checklist

#### 8.1 Security
- [ ] Strong SECRET_KEY and JWT_SECRET_KEY
- [ ] CORS properly configured
- [ ] Environment variables secured
- [ ] SSL certificates active

#### 8.2 Performance
- [ ] Database indexes optimized
- [ ] Redis caching configured
- [ ] CDN enabled (Vercel)
- [ ] Monitoring alerts set up

#### 8.3 Compliance
- [ ] REMIT compliance enabled
- [ ] Data retention policies
- [ ] Audit logging configured
- [ ] Backup strategies in place

### Step 9: Automated Deployment

#### 9.1 GitHub Actions (Optional)
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy QuantaEnergi

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: vercel --prod
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
```

### Step 10: Troubleshooting

#### 10.1 Common Issues
- **CORS errors**: Check CORS_ORIGINS configuration
- **Database connection**: Verify DATABASE_URL
- **Redis connection**: Verify REDIS_URL
- **Environment variables**: Check all required variables are set

#### 10.2 Logs
- **Railway**: `railway logs`
- **Vercel**: Check Vercel dashboard logs

#### 10.3 Debug Mode
```bash
# Enable debug mode for troubleshooting
DEBUG=true
LOG_LEVEL=DEBUG
```

### Step 11: Scaling

#### 11.1 Railway Scaling
- **Hobby Plan**: $5/month (Railway)
- **Pro Plan**: $20/month (Railway)
- **Enterprise**: Custom pricing

#### 11.2 Vercel Scaling
- **Hobby Plan**: Free (Vercel)
- **Pro Plan**: $20/month (Vercel)
- **Enterprise**: Custom pricing

### Step 12: Maintenance

#### 12.1 Regular Updates
- Update dependencies monthly
- Monitor security advisories
- Backup database regularly
- Review and rotate secrets

#### 12.2 Performance Monitoring
- Monitor API response times
- Track error rates
- Monitor database performance
- Review user analytics

## 🎯 Deployment Summary

### Architecture
```
Frontend (Vercel) → Backend (Railway) → Database (Railway PostgreSQL)
                                    → Cache (Railway Redis)
```

### Costs
- **Frontend**: Free (Vercel Hobby)
- **Backend**: $5/month (Railway Hobby)
- **Database**: Included (Railway)
- **Cache**: Included (Railway)
- **Total**: ~$5/month

### Features Deployed
- ✅ VaR/Monte Carlo Risk Calculations
- ✅ Alpha Vantage Market Data Integration
- ✅ Geo-Risk AI for Guyana/ME
- ✅ Quantum Portfolio Optimization
- ✅ REMIT Compliance for Europe/UK
- ✅ Real-time WebSocket Streaming
- ✅ Comprehensive API Documentation
- ✅ Production-ready Security

## 🚀 Ready for Production!

Your QuantaEnergi ETRM/CTRM disruptor is now deployed and ready to disrupt the energy trading market!
