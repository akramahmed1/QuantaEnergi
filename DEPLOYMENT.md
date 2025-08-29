# 🚀 EnergyOpti-Pro Deployment Guide

This guide covers the complete deployment process for EnergyOpti-Pro, from local verification to production cloud deployment.

## 📋 Prerequisites

### Required Tools
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for local verification)
- [Git](https://git-scm.com/) (for version control)
- [Node.js](https://nodejs.org/) (for frontend deployment)
- [Python 3.11+](https://www.python.org/) (for backend development)

### Cloud Accounts
- [Render](https://render.com/) (for backend hosting)
- [Vercel](https://vercel.com/) (for frontend hosting)
- [PostgreSQL Database](https://www.postgresql.org/) (or use Render's managed database)

## 🏠 Local Verification

### Step 1: Start Docker Services
```bash
# Make deployment script executable (Linux/Mac)
chmod +x deploy.sh

# Run local verification
./deploy.sh
# Choose option 1: Local verification with Docker Compose

# Or manually:
docker-compose up --build -d
```

### Step 2: Verify Services
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health
- **Database**: localhost:5432
- **Redis**: localhost:6379

### Step 3: Test Core Functionality
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test user registration
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!","company_name":"Test Corp","role":"trader"}'
```

## ☁️ Cloud Deployment

### Backend Deployment (Render)

#### Step 1: Create Render Account
1. Sign up at [render.com](https://render.com/)
2. Create a new account
3. Verify your email

#### Step 2: Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select the `energyopti-pro` repository
4. Choose the `main` branch

#### Step 3: Configure Service
- **Name**: `energyopti-pro-backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Step 4: Set Environment Variables
```bash
# Required Variables
DATABASE_URL=postgresql://username:password@host:port/database_name
REDIS_URL=redis://username:password@host:port
SECRET_KEY=your-super-secret-key-here
ISSUER=energyopti-pro
AUDIENCE=energyopti-pro-users

# Optional Variables
CME_API_KEY=your_cme_api_key
ICE_API_KEY=your_ice_api_key
NYMEX_API_KEY=your_nymex_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
QUANTUM_SECURITY_ENABLED=false
GENERATIVE_AI_ENABLED=false
```

#### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for build and deployment to complete
3. Note your service URL (e.g., `https://energyopti-pro-backend.onrender.com`)

### Frontend Deployment (Vercel)

#### Step 1: Create Vercel Account
1. Sign up at [vercel.com](https://vercel.com/)
2. Connect your GitHub account
3. Import the `energyopti-pro` repository

#### Step 2: Configure Project
- **Framework Preset**: Next.js (or React)
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

#### Step 3: Set Environment Variables
```bash
# API Configuration
VITE_API_URL=https://your-backend-url.onrender.com
VITE_WS_URL=wss://your-backend-url.onrender.com/ws

# Feature Flags
VITE_QUANTUM_ENABLED=true
VITE_AI_ENABLED=true
VITE_BLOCKCHAIN_ENABLED=true
```

#### Step 4: Deploy
1. Click "Deploy"
2. Wait for build and deployment to complete
3. Your app will be available at `https://your-project.vercel.app`

## 🔧 Automated Deployment

### Using Deployment Scripts

#### Linux/Mac
```bash
# Full deployment
./deploy.sh
# Choose option 4: Full deployment (local + cloud)

# Individual deployments
./deploy.sh  # Choose specific options
```

#### Windows
```cmd
# Full deployment
deploy.bat
# Choose option 4: Full deployment (local + cloud)
```

### Manual Deployment Commands

#### Backend (Render)
```bash
# Install Render CLI
curl -L https://render.com/download-cli/linux | bash

# Login to Render
render login

# Deploy service
render deploy
```

#### Frontend (Vercel)
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

## 🗄️ Database Setup

### Option 1: Render Managed Database
1. Create new PostgreSQL service in Render
2. Use connection string from service dashboard
3. Set as `DATABASE_URL` environment variable

### Option 2: External PostgreSQL
1. Use services like [Supabase](https://supabase.com/) or [Neon](https://neon.tech/)
2. Create database and user
3. Set connection string in environment variables

### Database Initialization
```sql
-- Create database (if not exists)
CREATE DATABASE energyopti_pro;

-- Create user (if not exists)
CREATE USER energyopti_pro_user WITH PASSWORD 'your_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE energyopti_pro TO energyopti_pro_user;
```

## 🔐 Security Configuration

### JWT Configuration
```bash
# Generate secure secret key
openssl rand -hex 32

# Set in environment variables
SECRET_KEY=your-generated-secret-key
ISSUER=energyopti-pro
AUDIENCE=energyopti-pro-users
```

### CORS Configuration
```python
# Update CORS settings in backend
ALLOWED_ORIGINS=[
    "https://your-frontend-domain.vercel.app",
    "https://your-custom-domain.com"
]
```

### Rate Limiting
```bash
# Set rate limit per minute
RATE_LIMIT_PER_MINUTE=1000
```

## 📊 Monitoring & Health Checks

### Health Endpoints
- **Backend Health**: `GET /api/health`
- **Database Status**: Included in health check
- **Redis Status**: Included in health check

### Logging
```bash
# View application logs
docker-compose logs -f backend

# View Render logs
render logs energyopti-pro-backend

# View Vercel logs
vercel logs
```

## 🚨 Troubleshooting

### Common Issues

#### Backend Not Starting
```bash
# Check logs
docker-compose logs backend

# Verify environment variables
docker-compose exec backend env | grep DATABASE_URL

# Check database connectivity
docker-compose exec db pg_isready -U energyopti_pro_user
```

#### Frontend Build Failures
```bash
# Check Node.js version
node --version  # Should be 16+

# Clear dependencies
rm -rf node_modules package-lock.json
npm install

# Check build logs
npm run build
```

#### Database Connection Issues
```bash
# Verify connection string format
postgresql://username:password@host:port/database_name

# Test connection manually
psql "postgresql://username:password@host:port/database_name"
```

### Performance Optimization

#### Backend
```bash
# Enable caching
REDIS_URL=redis://your-redis-url

# Optimize database
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

#### Frontend
```bash
# Enable compression
VITE_COMPRESSION_ENABLED=true

# Optimize bundle size
VITE_ANALYZE_BUNDLE=true
```

## 🔄 Continuous Deployment

### GitHub Actions (Optional)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: |
          curl -L https://render.com/download-cli/linux | bash
          render deploy

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        run: |
          npm i -g vercel
          vercel --prod --token ${{ secrets.VERCEL_TOKEN }}
```

## 📈 Post-Deployment

### Verification Checklist
- [ ] Backend health endpoint responding
- [ ] Frontend loading without errors
- [ ] Database connections working
- [ ] User registration/login functional
- [ ] All disruptive features accessible
- [ ] SSL certificates valid
- [ ] Performance metrics acceptable

### Performance Testing
```bash
# Load testing with Apache Bench
ab -n 1000 -c 10 https://your-backend-url.onrender.com/api/health

# API testing with Postman/Insomnia
# Test all endpoints with proper authentication
```

### Security Audit
- [ ] JWT tokens properly validated
- [ ] Rate limiting working
- [ ] CORS properly configured
- [ ] No sensitive data in logs
- [ ] Database connections encrypted

## 🎯 Next Steps

After successful deployment:

1. **Set up monitoring** with services like Sentry, LogRocket
2. **Configure analytics** with Google Analytics, Mixpanel
3. **Set up alerts** for downtime and errors
4. **Plan scaling** strategy based on usage
5. **Implement CI/CD** for automated deployments
6. **Set up backup** and disaster recovery procedures

## 📞 Support

For deployment issues:
1. Check the troubleshooting section above
2. Review application logs
3. Verify environment variables
4. Check service status pages
5. Contact support teams for respective platforms

---

**🎉 Congratulations! You've successfully deployed EnergyOpti-Pro to production!**

Your disruptive energy trading SaaS is now live and ready to revolutionize the industry! 🚀⚡
