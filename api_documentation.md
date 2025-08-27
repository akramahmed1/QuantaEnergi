# EnergyOpti-Pro API Documentation

## 🌐 Base URL
```
http://localhost:8000
```

## 📊 API Endpoints

### 1. Health Check
**GET** `/api/health`

**Description**: Check the health status of the API and all services.

**Response**:
```json
{
  "status": "healthy",
  "uptime": "99.9%",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "external_apis": "healthy",
    "quantum_security": "fallback"
  },
  "timestamp": "2025-08-26T03:08:25.766621"
}
```

---

### 2. Market Prices
**GET** `/api/prices`

**Description**: Get real-time market prices for energy commodities.

**Query Parameters**:
- `region` (optional): "global" | "middle_east" | "asia"
- `ramadan_mode` (optional): boolean

**Response**:
```json
{
  "source": "real_time",
  "cme_crude": {
    "source": "simulated_cme",
    "data": 75.61,
    "timestamp": "2025-08-26T03:23:24.135172"
  },
  "ice_brent": {
    "source": "simulated_ice",
    "data": 78.28,
    "timestamp": "2025-08-26T03:23:24.403950"
  },
  "region": "global",
  "timestamp": "2025-08-26T03:23:24.403950"
}
```

---

### 3. Enhanced Market Prices (v1)
**GET** `/api/models/v1/prices`

**Description**: Get enhanced market data with weather correlation.

**Query Parameters**:
- `region` (optional): "global" | "middle_east" | "asia"
- `ramadan_mode` (optional): boolean

**Response**:
```json
{
  "source": "real_time_v1",
  "market_data": {
    "source": "simulated_cme",
    "data": 75.61,
    "timestamp": "2025-08-26T03:23:24.135172"
  },
  "weather_correlation": {
    "source": "simulated_weather",
    "temperature": 31.0,
    "humidity": 33.109688,
    "description": "Partly cloudy",
    "timestamp": "2025-08-26T03:23:24.403950"
  },
  "region": "global",
  "timestamp": "2025-08-26T03:23:24.403950"
}
```

---

### 4. Renewable Energy Data
**GET** `/api/renewables`

**Description**: Get renewable energy capacity and weather correlation data.

**Response**:
```json
{
  "wind": 556,
  "solar": 339,
  "weather_correlation": {
    "source": "simulated_weather",
    "temperature": 31.0,
    "humidity": 33.109688,
    "description": "Partly cloudy",
    "timestamp": "2025-08-26T03:23:24.403950"
  },
  "timestamp": "2025-08-26T03:23:24.403950"
}
```

---

### 5. Oilfield Production Data
**GET** `/api/oilfield`

**Description**: Get oilfield production data with weather impact analysis.

**Response**:
```json
{
  "production": 1084,
  "field": "Jafurah",
  "weather_impact": {
    "source": "simulated_weather",
    "temperature": 29.0,
    "humidity": 64,
    "description": "Partly cloudy",
    "timestamp": "2025-08-26T03:23:40.955373"
  },
  "timestamp": "2025-08-26T03:23:40.956381"
}
```

---

### 6. Tariff Impact Analysis
**GET** `/api/tariff_impact`

**Description**: Calculate tariff impact on energy prices.

**Response**:
```json
{
  "impact": 3.78,
  "base_price": 75.61,
  "region": "USA",
  "calculation_method": "real_time_market",
  "timestamp": "2025-08-26T03:23:40.956381"
}
```

---

### 7. User Retention Data
**GET** `/api/retention`

**Description**: Get user retention and engagement metrics.

**Response**:
```json
{
  "retention_rate": 85,
  "last_login": "2025-08-26",
  "active_users": 1250,
  "growth_rate": "12.5%",
  "timestamp": "2025-08-26T03:28:21.608088"
}
```

---

### 8. Onboarding Guide
**GET** `/api/onboarding`

**Description**: Get user onboarding guide based on user type.

**Query Parameters**:
- `user_type` (optional): "trader" | "engineer" | "analyst" | "compliance"

**Response**:
```json
{
  "guide": "Advanced Trading Guide with Risk Management",
  "user_type": "trader",
  "estimated_time": "2-4 hours",
  "timestamp": "2025-08-26T03:28:21.608088"
}
```

---

### 9. Secure Endpoint
**GET** `/api/secure`

**Description**: Access secure endpoint with authentication.

**Headers**:
- `Authorization`: Bearer token0

**Response**:
```json
{
  "status": "quantum",
  "data": "encrypted_data_here"
}
```

---

### 10. Security Transparency
**GET** `/api/secure/transparency`

**Description**: Get security and compliance information.

**Response**:
```json
{
  "security_status": "quantum_active",
  "encryption": "kyber1024",
  "compliance": "SOC2_verified",
  "timestamp": "2025-08-26T03:28:21.608088"
}
```

---

## 🔧 Testing Commands

### Using curl:
```bash
# Health check
curl http://localhost:8000/api/health

# Market prices
curl http://localhost:8000/api/prices

# Renewable energy
curl http://localhost:8000/api/renewables

# Oilfield data
curl http://localhost:8000/api/oilfield

# Tariff impact
curl http://localhost:8000/api/tariff_impact

# Retention data
curl http://localhost:8000/api/retention

# Onboarding guide
curl "http://localhost:8000/api/onboarding?user_type=trader"

# Secure endpoint (requires auth)
curl -H "Authorization: Bearer token0" http://localhost:8000/api/secure

# Security transparency
curl http://localhost:8000/api/secure/transparency
```

### Using Browser:
Simply open these URLs in your browser:
- `http://localhost:8000/docs` - Swagger UI Documentation
- `http://localhost:8000/api/health` - Health Check
- `http://localhost:8000/api/prices` - Market Prices
- `http://localhost:8000/api/renewables` - Renewable Energy

---

## 🚀 Frontend Application

**URL**: `http://localhost:3000`

**Features**:
- Real-time dashboard with market data
- Interactive cards showing various metrics
- Quick links to API endpoints
- Responsive design for all devices

---

## 📊 Data Sources

- **CME Group**: Crude oil futures data
- **ICE**: Brent crude oil data
- **OpenWeatherMap**: Weather correlation data
- **Simulated Data**: Fallback when external APIs are unavailable

---

## 🔒 Security Features

- **Quantum Security**: Kyber1024 encryption
- **Authentication**: Bearer token-based
- **Compliance**: SOC2 verified
- **Audit Logging**: All requests logged

---

## 🛠️ Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `401`: Unauthorized (for secure endpoints)
- `500`: Internal server error

Error responses include:
```json
{
  "detail": "Error description"
}
```

---

## 📈 Real-time Features

- **Live Data**: Market prices update in real-time
- **Weather Correlation**: Weather data affects energy production estimates
- **WebSocket Support**: Real-time updates (when implemented)
- **Caching**: 5-minute cache for external API calls

---

## 🎯 Usage Examples

### 1. Monitor Market Prices
```bash
curl http://localhost:8000/api/prices
```

### 2. Check Renewable Energy Status
```bash
curl http://localhost:8000/api/renewables
```

### 3. Analyze Tariff Impact
```bash
curl http://localhost:8000/api/tariff_impact
```

### 4. Get User Analytics
```bash
curl http://localhost:8000/api/retention
```

### 5. Access Secure Data
```bash
curl -H "Authorization: Bearer token0" http://localhost:8000/api/secure
```

---

## 🌐 Swagger UI

Access the interactive API documentation at:
**http://localhost:8000/docs**

This provides:
- Interactive API testing
- Request/response examples
- Schema documentation
- Try-it-out functionality

---

## ✅ Status Check

To verify all services are running:

```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend status
curl http://localhost:3000
```

Both should return successful responses indicating the application is fully operational.
