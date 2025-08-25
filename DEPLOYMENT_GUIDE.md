# 🚀 EnergyOpti-Pro Deployment Guide

This guide will help you deploy the EnergyOpti-Pro application to Render, Railway, and Vercel.

## 📋 Prerequisites

Before deploying, ensure you have:

- **Git repository** with your code
- **GitHub account** (for connecting to deployment platforms)
- **API keys** for external services (optional for demo)
- **Domain names** (optional, for custom URLs)

## 🎯 Deployment Options

### Option 1: Automated Deployment (Recommended)

Use our deployment script:

```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

### Option 2: Manual Deployment

Follow the platform-specific instructions below.

## 🌐 Backend Deployment

### Render Deployment

1. **Sign up/Login to Render**
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository: `energyopti-pro`

3. **Configure Service**
   ```
   Name: energyopti-pro-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn src.energyopti_pro.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Set Environment Variables**
   ```
   ENVIRONMENT=production
   JWT_SECRET_KEY=your_super_secret_key_here
   CME_API_KEY=your_cme_api_key
   ICE_API_KEY=your_ice_api_key
   NYMEX_API_KEY=your_nymex_api_key
   OPENWEATHER_API_KEY=your_openweather_api_key
   ```

5. **Add PostgreSQL Database**
   - Go to "New +" → "PostgreSQL"
   - Name: `energyopti-pro-postgres`
   - Copy the connection string to `DATABASE_URL`

6. **Add Redis Cache**
   - Go to "New +" → "Redis"
   - Name: `energyopti-pro-redis`
   - Copy the connection string to `REDIS_URL`

7. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

**Your Render URL**: `https://energyopti-pro-backend.onrender.com`

### Railway Deployment

1. **Sign up/Login to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with your GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Service**
   - Railway will auto-detect Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.energyopti_pro.main:app --host 0.0.0.0 --port $PORT`

4. **Add PostgreSQL Database**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway will automatically link it

5. **Set Environment Variables**
   ```
   ENVIRONMENT=production
   JWT_SECRET_KEY=your_super_secret_key_here
   CME_API_KEY=your_cme_api_key
   ICE_API_KEY=your_ice_api_key
   NYMEX_API_KEY=your_nymex_api_key
   OPENWEATHER_API_KEY=your_openweather_api_key
   ```

6. **Deploy**
   - Railway will automatically deploy on push
   - Or click "Deploy" to trigger manual deployment

**Your Railway URL**: `https://energyopti-pro-backend-production.up.railway.app`

## 🎨 Frontend Deployment (Vercel)

### Vercel Deployment

1. **Sign up/Login to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with your GitHub account

2. **Import Project**
   - Click "New Project"
   - Import your GitHub repository
   - Select the `frontend` directory

3. **Configure Build Settings**
   ```
   Framework Preset: Vite
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

4. **Set Environment Variables**
   ```
   VITE_API_URL=https://energyopti-pro-backend.onrender.com
   VITE_WS_URL=wss://energyopti-pro-backend.onrender.com/ws
   VITE_ENVIRONMENT=production
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait for build and deployment to complete

**Your Vercel URL**: `https://energyopti-pro-frontend.vercel.app`

## 🔧 Environment Variables Setup

### Required Environment Variables

#### Backend (Render/Railway)
```bash
# Database
DATABASE_URL=postgresql://username:password@host:port/database

# Cache
REDIS_URL=redis://username:password@host:port/database

# Security
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys (Optional for demo)
CME_API_KEY=your_cme_api_key
ICE_API_KEY=your_ice_api_key
NYMEX_API_KEY=your_nymex_api_key
OPENWEATHER_API_KEY=your_openweather_api_key

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://energyopti-pro-frontend.vercel.app
```

#### Frontend (Vercel)
```bash
# API Configuration
VITE_API_URL=https://energyopti-pro-backend.onrender.com
VITE_WS_URL=wss://energyopti-pro-backend.onrender.com/ws
VITE_ENVIRONMENT=production

# App Configuration
VITE_APP_NAME=EnergyOpti-Pro
VITE_APP_VERSION=2.0.0
```

## 🔄 Database Migration

After deployment, run database migrations:

### Render
```bash
# Connect to your Render service
render exec energyopti-pro-backend -- alembic upgrade head
```

### Railway
```bash
# Connect to your Railway service
railway run alembic upgrade head
```

## 🧪 Testing Your Deployment

### Backend Health Check
```bash
# Test Render backend
curl https://energyopti-pro-backend.onrender.com/health

# Test Railway backend
curl https://energyopti-pro-backend-production.up.railway.app/health
```

### Frontend Test
1. Open your Vercel URL in a browser
2. Navigate through the application
3. Test API connections
4. Verify real-time features

## 🔗 Custom Domains

### Render Custom Domain
1. Go to your Render service dashboard
2. Click "Settings" → "Custom Domains"
3. Add your domain
4. Update DNS records as instructed

### Railway Custom Domain
1. Go to your Railway project
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Configure DNS records

### Vercel Custom Domain
1. Go to your Vercel project dashboard
2. Click "Settings" → "Domains"
3. Add your domain
4. Configure DNS records

## 📊 Monitoring & Logs

### Render Monitoring
- **Logs**: Service dashboard → "Logs"
- **Metrics**: Service dashboard → "Metrics"
- **Health Checks**: Automatic health monitoring

### Railway Monitoring
- **Logs**: Project dashboard → "Deployments" → "View Logs"
- **Metrics**: Project dashboard → "Metrics"
- **Health Checks**: Automatic health monitoring

### Vercel Monitoring
- **Analytics**: Project dashboard → "Analytics"
- **Functions**: Project dashboard → "Functions"
- **Performance**: Project dashboard → "Speed Insights"

## 🚨 Troubleshooting

### Common Issues

#### Backend Deployment Issues
1. **Build Failures**
   - Check Python version compatibility
   - Verify all dependencies in `requirements.txt`
   - Check build logs for specific errors

2. **Database Connection Issues**
   - Verify `DATABASE_URL` format
   - Check database credentials
   - Ensure database is accessible from deployment region

3. **Environment Variables**
   - Verify all required variables are set
   - Check variable names and values
   - Restart service after adding variables

#### Frontend Deployment Issues
1. **Build Failures**
   - Check Node.js version compatibility
   - Verify all dependencies in `package.json`
   - Check build logs for specific errors

2. **API Connection Issues**
   - Verify `VITE_API_URL` is correct
   - Check CORS configuration
   - Ensure backend is accessible

3. **Environment Variables**
   - Verify all VITE_* variables are set
   - Check variable names and values
   - Redeploy after adding variables

### Getting Help

1. **Check Logs**: Always check deployment logs first
2. **Platform Documentation**: Refer to platform-specific docs
3. **Community Support**: Use platform community forums
4. **Contact Support**: Reach out to platform support teams

## 🎉 Success Indicators

You'll know your deployment is successful when:

✅ **Backend Health Check**: Returns 200 OK
✅ **Frontend Loads**: Application loads without errors
✅ **API Connections**: Frontend can connect to backend
✅ **Database**: Migrations run successfully
✅ **Real-time Features**: WebSocket connections work
✅ **External APIs**: Market data loads (if API keys provided)

## 🔄 Continuous Deployment

### Automatic Deployments
- **Render**: Automatically deploys on Git push
- **Railway**: Automatically deploys on Git push
- **Vercel**: Automatically deploys on Git push

### Manual Deployments
```bash
# Render
render deploy --service energyopti-pro-backend

# Railway
railway up

# Vercel
vercel --prod
```

## 📈 Scaling Considerations

### Render Scaling
- **Free Tier**: 750 hours/month
- **Paid Plans**: Start at $7/month
- **Auto-scaling**: Available on paid plans

### Railway Scaling
- **Free Tier**: $5 credit/month
- **Paid Plans**: Pay-as-you-go
- **Auto-scaling**: Built-in

### Vercel Scaling
- **Free Tier**: 100GB bandwidth/month
- **Paid Plans**: Start at $20/month
- **Auto-scaling**: Built-in

---

**🎯 Your EnergyOpti-Pro application is now deployed and ready for production use!**
