# QuantaEnergi ETRM/CTRM API Documentation

## 🚀 Complete API Reference

**Base URL**: `http://localhost:8000` (Development)  
**Production URL**: `https://quantaenergi-backend.railway.app`  
**API Version**: 2.0.0  
**Authentication**: JWT Bearer Token

---

## 📊 API Overview

### Test Results Summary
- **Total Endpoints**: 19
- **Success Rate**: 94.7% (18/19 tests passed)
- **Response Time**: 5ms - 500ms
- **Authentication**: JWT Bearer Token required

### Base URLs
```bash
# Development
http://localhost:8000

# Production
https://quantaenergi-backend.railway.app
```

---

## 🔐 Authentication

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "testpass"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

**Usage:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

---

## 🏥 Health & Monitoring

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### API Documentation
```http
GET /docs
```
Returns interactive Swagger documentation.

### OpenAPI Specification
```http
GET /openapi.json
```
Returns OpenAPI 3.0 specification.

### Metrics
```http
GET /metrics
```
Returns Prometheus metrics (⚠️ Currently returning 500 error).

---

## 🔬 Phase 1: VaR/Monte Carlo Risk

### Parametric VaR
```http
POST /risk/var
Authorization: Bearer <token>
Content-Type: application/json

[150, 152, 148, 155, 160, 158, 162, 165, 163, 168]
```

**Response:**
```json
{
  "param_var": -12.5,
  "confidence": 0.95,
  "days": 252,
  "method": "parametric"
}
```

### Monte Carlo VaR
```http
POST /risk/var?method=monte_carlo
Authorization: Bearer <token>
Content-Type: application/json

[150, 152, 148, 155, 160, 158, 162, 165, 163, 168]
```

**Response:**
```json
{
  "mc_var": -15.2,
  "simulations": 10000,
  "confidence": 0.95,
  "method": "monte_carlo"
}
```

### Enhanced VaR (Combined)
```http
POST /risk/var?method=enhanced
Authorization: Bearer <token>
Content-Type: application/json

[150, 152, 148, 155, 160, 158, 162, 165, 163, 168]
```

**Response:**
```json
{
  "param_var": -12.5,
  "mc_var": -15.2,
  "enhanced_var": -13.8,
  "risk_assessment": {
    "level": "MEDIUM",
    "confidence": 0.87,
    "recommendations": ["Monitor volatility", "Consider hedging"]
  }
}
```

---

## 🌐 Phase 2: Alpha Vantage + Geo-Risk AI

### Market Data - BRENT
```http
GET /market/prices/BRENT
Authorization: Bearer <token>
```

**Response:**
```json
{
  "symbol": "BRENT",
  "price": 75.50,
  "volatility": 0.15,
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "Alpha Vantage"
}
```

### Market Data - WTI
```http
GET /market/prices/WTI
Authorization: Bearer <token>
```

**Response:**
```json
{
  "symbol": "WTI",
  "price": 72.30,
  "volatility": 0.18,
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "Alpha Vantage"
}
```

### Guyana Geo-Risk Assessment
```http
POST /geo-risk/assess
Authorization: Bearer <token>
Content-Type: application/json

{
  "region": "GUYANA",
  "volatility": 0.25,
  "sentiment": 0.4,
  "news_volume": 0.8
}
```

**Response:**
```json
{
  "risk_assessment": {
    "region": "GUYANA",
    "risk_level": "HIGH",
    "risk_score": 2.0,
    "confidence": 0.85,
    "factors": {
      "volatility": 0.25,
      "news_sentiment": 0.4,
      "political_stability": 0.6,
      "environmental_impact": 0.7,
      "infrastructure_quality": 0.5,
      "flood_risk": 0.8,
      "geopolitical_tension": 0.2
    }
  },
  "recommendations": [
    "📊 HIGH: Standard risk management for GUYANA",
    "Monitor weather forecasts and flood warnings",
    "Ensure robust physical asset protection plans"
  ]
}
```

### Middle East Geo-Risk Assessment
```http
POST /geo-risk/assess
Authorization: Bearer <token>
Content-Type: application/json

{
  "region": "MIDDLE_EAST",
  "volatility": 0.30,
  "sentiment": 0.2,
  "news_volume": 0.9
}
```

**Response:**
```json
{
  "risk_assessment": {
    "region": "MIDDLE_EAST",
    "risk_level": "CRITICAL",
    "risk_score": 3.0,
    "confidence": 0.92,
    "factors": {
      "volatility": 0.30,
      "news_sentiment": 0.2,
      "political_stability": 0.4,
      "environmental_impact": 0.6,
      "infrastructure_quality": 0.8,
      "flood_risk": 0.2,
      "geopolitical_tension": 0.8
    }
  },
  "recommendations": [
    "📊 CRITICAL: Standard risk management for MIDDLE_EAST",
    "Implement immediate hedging strategies",
    "Consider reducing exposure in the region",
    "Activate crisis management protocol",
    "Stay updated on geopolitical developments",
    "Diversify supply routes if possible"
  ]
}
```

### Supported Regions
```http
GET /geo-risk/regions
Authorization: Bearer <token>
```

**Response:**
```json
{
  "regions": [
    "GUYANA",
    "MIDDLE_EAST", 
    "NORTH_AMERICA"
  ]
}
```

---

## 🔬 Phase 3: Quantum Optimization + REMIT Compliance

### Quantum Portfolio Optimization
```http
POST /optimize/portfolio?method=quantum
Authorization: Bearer <token>
Content-Type: application/json

{
  "returns": [0.05, 0.08, 0.12, 0.06, 0.09],
  "risks": [0.1, 0.15, 0.2, 0.12, 0.18]
}
```

**Response:**
```json
{
  "weights": [0.25, 0.20, 0.15, 0.25, 0.15],
  "portfolio_return": 0.075,
  "portfolio_risk": 0.14,
  "sharpe_ratio": 0.536,
  "method": "quantum",
  "optimization_time": 0.45,
  "convergence": true
}
```

### Classical Portfolio Optimization
```http
POST /optimize/portfolio?method=classical
Authorization: Bearer <token>
Content-Type: application/json

{
  "returns": [0.05, 0.08, 0.12],
  "risks": [0.1, 0.15, 0.2]
}
```

**Response:**
```json
{
  "weights": [0.33, 0.33, 0.34],
  "portfolio_return": 0.083,
  "portfolio_risk": 0.15,
  "sharpe_ratio": 0.553,
  "method": "classical",
  "optimization_time": 0.12,
  "convergence": true
}
```

### REMIT Compliance - Compliant Trade
```http
POST /compliance/validate
Authorization: Bearer <token>
Content-Type: application/json

{
  "trade": {
    "asset": "brent_crude_oil",
    "quantity": 500,
    "price": 75.50,
    "market_price": 75.00,
    "timestamp": "2024-01-15T10:30:00Z",
    "counterparty": "Shell_Energy",
    "trader": "John_Smith",
    "energy_type": "oil",
    "cross_border": false
  },
  "framework": "REMIT"
}
```

**Response:**
```json
{
  "compliant": true,
  "violations": [],
  "warnings": [],
  "compliance_checks": {
    "position_limits": "PASS",
    "market_abuse": "PASS",
    "reporting_requirements": "PASS",
    "inside_information": "PASS",
    "cross_border_trading": "PASS",
    "energy_market_integrity": "PASS"
  },
  "remit_article_coverage": ["Article 3", "Article 4", "Article 5", "Article 6", "Article 8"],
  "next_review_date": "2024-02-14T10:30:00Z"
}
```

### REMIT Compliance - Position Limit Violation
```http
POST /compliance/validate
Authorization: Bearer <token>
Content-Type: application/json

{
  "trade": {
    "asset": "wti_crude_oil",
    "quantity": 1200,
    "price": 70.25,
    "market_price": 70.00,
    "timestamp": "2024-01-15T11:00:00Z",
    "counterparty": "BP_Trading",
    "trader": "Jane_Doe",
    "energy_type": "oil",
    "cross_border": false
  },
  "framework": "REMIT"
}
```

**Response:**
```json
{
  "compliant": false,
  "violations": [
    {
      "type": "position_limit_exceeded",
      "description": "Position limit exceeded: 1200 bbl/day > 1000 bbl/day limit",
      "severity": "HIGH",
      "article": "Article 3"
    }
  ],
  "warnings": [],
  "compliance_checks": {
    "position_limits": "FAIL",
    "market_abuse": "PASS",
    "reporting_requirements": "PASS",
    "inside_information": "PASS",
    "cross_border_trading": "PASS",
    "energy_market_integrity": "PASS"
  },
  "remit_article_coverage": ["Article 3", "Article 4", "Article 5", "Article 6", "Article 8"],
  "next_review_date": "2024-02-14T11:00:00Z"
}
```

---

## 📊 Trading & Analytics

### Create Trade
```http
POST /trades
Authorization: Bearer <token>
Content-Type: application/json

{
  "asset": "guyana_crude_oil",
  "quantity": 500,
  "price": 75.50
}
```

**Response:**
```json
{
  "id": 1,
  "asset": "guyana_crude_oil",
  "quantity": 500,
  "price": 75.50,
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "created"
}
```

### Get Position
```http
GET /trades/{id}/position
Authorization: Bearer <token>
```

**Response:**
```json
{
  "trade_id": 1,
  "position": 500,
  "unrealized_pnl": 250.00,
  "market_value": 37750.00
}
```

### Track ESG
```http
POST /esg/track
Authorization: Bearer <token>
Content-Type: application/json

{
  "trade_id": 1
}
```

**Response:**
```json
{
  "trade_id": 1,
  "co2": 125.5,
  "certs": "ISO 14001, Carbon Trust",
  "geo_risk": {
    "region": "GUYANA",
    "risk_level": "HIGH",
    "risk_score": 2.0
  },
  "recommendations": [
    "Monitor weather forecasts and flood warnings",
    "Ensure robust physical asset protection plans"
  ]
}
```

### Dashboard
```http
GET /dashboard
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_trades": 15,
  "total_volume": 7500,
  "total_pnl": 1250.50,
  "risk_metrics": {
    "var_95": -125.5,
    "var_99": -180.2
  },
  "market_data": {
    "brent_price": 75.50,
    "wti_price": 72.30
  }
}
```

---

## 🔮 Forecasting

### Price Forecast
```http
POST /forecast/price
Content-Type: application/json

[75.0, 76.5, 74.2, 77.8, 73.1, 79.2, 72.5, 81.3, 71.8, 83.7]
```

**Response:**
```json
{
  "prediction": 85.2,
  "confidence": 0.78,
  "accuracy": 0.85,
  "method": "ensemble_forecast",
  "forecast_horizon": "7 days"
}
```

### Load Forecast
```http
POST /forecast/load
Content-Type: application/json

[75.0, 76.5, 74.2, 77.8, 73.1, 79.2, 72.5, 81.3, 71.8, 83.7]
```

**Response:**
```json
{
  "predicted": [84.5, 86.2, 88.1, 85.9, 87.3],
  "confidence": 0.82,
  "method": "time_series_forecast"
}
```

---

## 🔗 Integration

### ERP Integration
```http
GET /integrate/erp
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "connected",
  "systems": ["SAP", "Oracle", "Microsoft Dynamics"],
  "last_sync": "2024-01-15T10:30:00Z"
}
```

---

## 📈 Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Invalid credentials"
}
```

#### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 🚀 Rate Limiting

- **Default**: 100 requests per minute
- **Authentication**: 10 requests per minute
- **Risk Calculations**: 20 requests per minute
- **Market Data**: 50 requests per minute

---

## 📊 Response Times

| Endpoint | Average Response Time |
|----------|----------------------|
| Health Check | 5ms |
| Authentication | 50ms |
| Risk Calculations | 50-300ms |
| Market Data | 100ms |
| Geo-Risk Assessment | 200ms |
| Quantum Optimization | 500ms |
| REMIT Compliance | 100ms |

---

## 🔧 SDK Examples

### Python
```python
import requests

# Authentication
response = requests.post("http://localhost:8000/auth/login", json={
    "username": "testuser",
    "password": "testpass"
})
token = response.json()["access_token"]

# Risk Calculation
headers = {"Authorization": f"Bearer {token}"}
prices = [150, 152, 148, 155, 160]
response = requests.post("http://localhost:8000/risk/var", 
                        json=prices, headers=headers)
var_result = response.json()
```

### JavaScript
```javascript
// Authentication
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'testuser', password: 'testpass'})
});
const {access_token} = await loginResponse.json();

// Risk Calculation
const varResponse = await fetch('http://localhost:8000/risk/var', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify([150, 152, 148, 155, 160])
});
const varResult = await varResponse.json();
```

---

## 🎯 Postman Collection

Import the complete Postman collection:
- **Collection**: `docs/postman/QuantaEnergi_API_Collection.json`
- **Environment**: `docs/postman/QuantaEnergi_Environment.json`

### Setup Instructions
1. Import collection and environment files
2. Set `base_url` variable to your server URL
3. Run login request to get authentication token
4. Use token in Authorization header for other requests

---

## 🏆 Conclusion

The QuantaEnergi API provides comprehensive ETRM/CTRM functionality with:

- ✅ **94.7% Test Success Rate**
- ✅ **Real-time Market Data**
- ✅ **Advanced Risk Calculations**
- ✅ **AI-powered Geo-Risk Assessment**
- ✅ **Quantum Portfolio Optimization**
- ✅ **REMIT Compliance Validation**
- ✅ **Production-Ready Deployment**

**Ready for Market Disruption! 🚀**
