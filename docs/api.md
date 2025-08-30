# EnergyOpti-Pro API Documentation

## Overview
EnergyOpti-Pro provides a comprehensive REST API for energy trading, analytics, and compliance management.

## Authentication
All API endpoints require JWT authentication via Bearer token in the Authorization header.

## Base URL
```
https://api.energyopti-pro.com
```

## Endpoints

### Market Data
- `GET /api/prices` - Real-time energy prices
- `GET /api/renewables` - Renewable energy capacity data
- `GET /api/oilfield` - Oilfield production data

### Trading
- `POST /api/trading/execute` - Execute energy trades
- `GET /api/trading/portfolio` - Portfolio overview

### Analytics
- `GET /api/analytics/forecast` - AI-powered price forecasting
- `GET /api/analytics/risk` - Risk assessment metrics

### Compliance
- `GET /api/compliance/status` - Regulatory compliance status
- `POST /api/compliance/audit` - Submit compliance audit

## Example Response
```json
{
  "status": "success",
  "data": {
    "price": 85.50,
    "currency": "USD",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Rate Limits
- Standard: 100 requests per minute
- Premium: 1000 requests per minute
