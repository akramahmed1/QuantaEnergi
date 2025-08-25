# 🚀 EnergyOpti-Pro Local Development Startup Guide

## 📋 Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.9+** (Check with `py --version`)
- **Node.js 18+** (Check with `node --version`)
- **npm 9+** (Check with `npm --version`)
- **Docker** (Optional, for containerized deployment)
- **Git** (Already installed)

## 🎯 Quick Start Options

### Option 1: Automated Script (Recommended)

**Windows PowerShell:**
```powershell
.\start_local.ps1
```

**Windows Command Prompt:**
```cmd
start_local.bat
```

### Option 2: Manual Setup

Follow the step-by-step instructions below.

## 🔧 Step-by-Step Manual Setup

### Step 1: Environment Setup

```powershell
# Navigate to project directory
cd D:\Documents\energyopti-pro

# Create virtual environment
py -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -e .
```

### Step 2: Environment Configuration

```powershell
# Copy environment template
copy env.example .env

# Edit .env file with your API keys (optional for demo)
notepad .env
```

**Key Environment Variables:**
- `CME_API_KEY`: CME Group API key
- `ICE_API_KEY`: ICE API key
- `OPENWEATHER_API_KEY`: Weather data API key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

### Step 3: Database Setup

**Option A: Using Docker (Recommended)**
```powershell
# Start PostgreSQL and Redis with Docker
docker-compose up -d postgres redis
```

**Option B: Local Installation**
```powershell
# Install PostgreSQL dependencies
pip install psycopg2-binary

# Run database migrations
alembic upgrade head
```

### Step 4: Start Backend

```powershell
# Navigate to backend directory
cd backend

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend Features Available:**
- 🌐 **API Documentation**: http://localhost:8000/docs
- 🔍 **Interactive API**: http://localhost:8000/redoc
- 🏥 **Health Check**: http://localhost:8000/api/health
- 📊 **Market Data**: http://localhost:8000/api/prices
- 🤖 **AI Insights**: http://localhost:8000/api/models/v1/prices

### Step 5: Start Frontend

**Open a new terminal:**
```powershell
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

**Frontend Features Available:**
- 🎨 **Trading Dashboard**: http://localhost:3000
- 📈 **Real-time Charts**: http://localhost:3000/charts
- 💼 **Portfolio Management**: http://localhost:3000/portfolio
- ⚙️ **Settings**: http://localhost:3000/settings

## 🐳 Docker Compose (Full Stack)

For a complete setup with all services:

```powershell
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

**Services Started:**
- ✅ **Backend API**: http://localhost:8000
- ✅ **Frontend**: http://localhost:3000
- ✅ **PostgreSQL**: localhost:5432
- ✅ **Redis**: localhost:6379
- ✅ **Monitoring**: http://localhost:9090 (Prometheus)

## 🧪 Testing the Application

### API Testing

```powershell
# Test health endpoint
curl http://localhost:8000/api/health

# Test market data
curl http://localhost:8000/api/prices

# Test AI predictions
curl http://localhost:8000/api/models/v1/prices
```

### Frontend Testing

1. Open http://localhost:3000 in your browser
2. Navigate through the trading dashboard
3. Test real-time data updates
4. Explore AI insights and predictions

## 🔍 Key Features to Test

### 🧠 AI/ML Features
- **Price Forecasting**: Navigate to AI Insights
- **Risk Management**: Check VaR calculations
- **ESG Scoring**: View sustainability metrics

### 🔗 Blockchain Features
- **P2P Trading**: Test peer-to-peer energy trading
- **Smart Contracts**: View contract management
- **Transparency**: Explore blockchain audit trail

### ☪️ Sharia Compliance
- **Halal Screening**: Check investment compliance
- **Zakat Calculation**: View automated Zakat
- **Riba-Free Trading**: Test Islamic finance features

### 🌍 Multi-Region Support
- **Regulatory Compliance**: Switch between regions
- **Local Currencies**: Test multi-currency support
- **Regional Markets**: Access local exchanges

## 🛠️ Troubleshooting

### Common Issues

**1. Port Already in Use**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**2. Database Connection Issues**
```powershell
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

**3. Frontend Build Issues**
```powershell
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**4. Python Dependencies**
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt
```

### Performance Optimization

**1. Enable Caching**
```powershell
# Start Redis for caching
docker-compose up -d redis
```

**2. Database Optimization**
```powershell
# Run database migrations
alembic upgrade head

# Seed initial data
python scripts/seed_data.py
```

## 📊 Monitoring & Logs

### View Application Logs

```powershell
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# Database logs
docker-compose logs -f postgres
```

### Performance Monitoring

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **Application Metrics**: http://localhost:8000/metrics

## 🎉 Success Indicators

You'll know everything is working when you see:

✅ **Backend**: "Uvicorn running on http://0.0.0.0:8000"
✅ **Frontend**: "Local: http://localhost:3000"
✅ **Database**: "Connected to PostgreSQL"
✅ **Redis**: "Redis connection established"
✅ **API Docs**: Interactive documentation at http://localhost:8000/docs

## 🚀 Next Steps

Once the application is running:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test the Dashboard**: Navigate to http://localhost:3000
3. **Run Tests**: Execute `pytest` in the project root
4. **Deploy**: Use `docker-compose -f docker-compose.prod.yml up -d`

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review application logs
3. Verify all prerequisites are installed
4. Ensure ports are not in use by other applications

---

**🎯 Your EnergyOpti-Pro platform is now ready for local development and testing!**
