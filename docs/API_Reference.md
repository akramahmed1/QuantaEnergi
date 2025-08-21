# EnergyOpti-Pro API Reference

## Overview

EnergyOpti-Pro provides a comprehensive REST API for Energy Trading and Risk Management (ETRM) / Commodity Trading and Risk Management (CTRM) operations. The API supports multi-region trading, Islamic finance compliance, real-time market data, and advanced risk management.

## Base URL

```
https://api.energyopti-pro.com/api/v1
```

## Authentication

All API endpoints require authentication using JWT Bearer tokens.

```http
Authorization: Bearer <your-jwt-token>
```

## Rate Limiting

- **Standard**: 100 requests per minute
- **Premium**: 1000 requests per minute
- **Enterprise**: 10000 requests per minute

## Common Response Format

```json
{
  "status": "success",
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Responses

```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": [
    {
      "field": "price",
      "message": "Price must be positive"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## ETRM/CTRM Endpoints

### Contract Management

#### Create Contract

```http
POST /etrm/contracts/
```

**Request Body:**
```json
{
  "contract_type": "PPA",
  "counterparty_id": 1,
  "commodity": "power",
  "delivery_location": "Dubai",
  "delivery_period_start": "2024-02-01T00:00:00Z",
  "delivery_period_end": "2024-03-01T00:00:00Z",
  "quantity": 100.0,
  "unit": "MWh",
  "price": 75.50,
  "currency": "USD",
  "region": "ME",
  "compliance_flags": {
    "sharia_compliant": true
  }
}
```

**Response:**
```json
{
  "status": "created",
  "contract_id": "uuid-string",
  "contract_number": "CTR-ME-ABC12345",
  "message": "Contract created successfully"
}
```

#### Get Contracts

```http
GET /etrm/contracts/
```

**Query Parameters:**
- `region` (optional): Filter by region (ME, US, UK, EU, GUYANA)
- `status` (optional): Filter by status (active, expired, terminated)
- `commodity` (optional): Filter by commodity (power, gas, oil, carbon)

**Response:**
```json
[
  {
    "id": "uuid-string",
    "contract_number": "CTR-ME-ABC12345",
    "contract_type": "PPA",
    "commodity": "power",
    "delivery_location": "Dubai",
    "delivery_period_start": "2024-02-01T00:00:00Z",
    "delivery_period_end": "2024-03-01T00:00:00Z",
    "quantity": 100.0,
    "unit": "MWh",
    "price": 75.50,
    "currency": "USD",
    "status": "active",
    "region": "ME",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### Trading Operations

#### Execute Trade

```http
POST /etrm/trades/
```

**Request Body:**
```json
{
  "contract_id": "contract-uuid",
  "trader_id": 1,
  "side": "buy",
  "quantity": 50.0,
  "price": 75.50,
  "trade_date": "2024-01-15T10:30:00Z",
  "region": "ME"
}
```

**Response:**
```json
{
  "status": "executed",
  "trade_id": "TRD-ME-XYZ67890",
  "message": "Trade executed successfully"
}
```

#### Get Trades

```http
GET /etrm/trades/
```

**Query Parameters:**
- `region` (optional): Filter by region
- `status` (optional): Filter by status (executed, pending, cancelled)
- `start_date` (optional): Filter by start date
- `end_date` (optional): Filter by end date

**Response:**
```json
[
  {
    "trade_id": "TRD-ME-XYZ67890",
    "contract_id": "contract-uuid",
    "trader_id": 1,
    "side": "buy",
    "quantity": 50.0,
    "price": 75.50,
    "trade_date": "2024-01-15T10:30:00Z",
    "status": "executed",
    "region": "ME"
  }
]
```

### Position Management

#### Get Positions

```http
GET /etrm/positions/
```

**Query Parameters:**
- `region` (optional): Filter by region
- `commodity` (optional): Filter by commodity

**Response:**
```json
[
  {
    "id": 1,
    "contract_id": "contract-uuid",
    "trader_id": 1,
    "commodity": "power",
    "net_quantity": 100.0,
    "average_price": 75.50,
    "market_value": 7550.0,
    "unrealized_pnl": 500.0,
    "region": "ME",
    "last_updated": "2024-01-15T10:30:00Z"
  }
]
```

### Risk Management

#### Calculate VaR

```http
GET /etrm/risk/var
```

**Query Parameters:**
- `region` (required): Region for VaR calculation
- `confidence_level` (optional): Confidence level (default: 0.95)

**Response:**
```json
{
  "var": 15000.0,
  "var_percentage": 0.02,
  "confidence_level": 0.95,
  "portfolio_value": 750000.0,
  "region": "ME",
  "calculation_method": "historical_simulation"
}
```

#### Get Risk Limits

```http
GET /etrm/risk/limits
```

**Query Parameters:**
- `region` (required): Region for risk limits

**Response:**
```json
{
  "region": "ME",
  "risk_limits": {
    "var_limit": 1000000.0,
    "position_limit": 5000000.0,
    "correlation_limit": 0.7,
    "concentration_limit": 0.3
  },
  "last_updated": "2024-01-15T10:30:00Z"
}
```

### Compliance Management

#### Get Compliance Status

```http
GET /etrm/compliance/status
```

**Query Parameters:**
- `region` (optional): Filter by region

**Response:**
```json
[
  {
    "region": "ME",
    "regulation": "ADNOC",
    "status": "compliant",
    "last_check": "2024-01-15T10:30:00Z",
    "next_check": "2024-02-15T10:30:00Z"
  }
]
```

#### Submit Compliance Report

```http
POST /etrm/compliance/report
```

**Request Body:**
```json
{
  "regulation_name": "ADNOC",
  "report_period": "Q1-2024",
  "data": {
    "emissions": 1000,
    "compliance_score": 95
  },
  "region": "ME"
}
```

**Response:**
```json
{
  "status": "submitted",
  "compliance_id": 1,
  "message": "Compliance report submitted successfully"
}
```

### Market Data

#### Get Market Prices

```http
GET /etrm/market/prices
```

**Query Parameters:**
- `commodity` (optional): Filter by commodity
- `region` (optional): Filter by region

**Response:**
```json
[
  {
    "commodity": "power",
    "region": "ME",
    "price": 75.50,
    "currency": "USD",
    "unit": "MWh",
    "timestamp": "2024-01-15T10:30:00Z",
    "source": "exchange"
  }
]
```

### Settlement Management

#### Get Settlements

```http
GET /etrm/settlements/
```

**Query Parameters:**
- `region` (optional): Filter by region
- `status` (optional): Filter by status

**Response:**
```json
[
  {
    "id": 1,
    "trade_id": "trade-uuid",
    "settlement_amount": 3775.0,
    "settlement_currency": "USD",
    "settlement_date": "2024-01-15T10:30:00Z",
    "status": "completed",
    "region": "ME"
  }
]
```

### Regional Compliance Rules

#### Get Regional Compliance Rules

```http
GET /etrm/compliance/rules/{region}
```

**Path Parameters:**
- `region`: Region code (ME, US, UK, EU, GUYANA)

**Response:**
```json
{
  "region": "ME",
  "compliance_rules": {
    "ADNOC": {
      "description": "Abu Dhabi National Oil Company regulations",
      "requirements": [
        "Environmental reporting",
        "Safety standards",
        "Local content"
      ],
      "penalties": [
        "Fines up to $100,000",
        "License suspension"
      ],
      "reporting_frequency": "Monthly"
    }
  },
  "last_updated": "2024-01-15T10:30:00Z"
}
```

---

## Islamic Finance Endpoints

### Islamic Compliance

#### Check Sharia Compliance

```http
POST /islamic/compliance/check
```

**Request Body:**
```json
{
  "transaction_type": "murabaha",
  "transaction_details": {
    "asset_type": "equipment",
    "profit_margin": 0.05,
    "payment_terms": "monthly"
  }
}
```

**Response:**
```json
{
  "is_compliant": true,
  "reasons": ["No interest involved", "Asset-backed transaction"],
  "principles_checked": ["riba_prohibition", "asset_backed"],
  "recommendations": []
}
```

### Zakat Calculation

#### Calculate Zakat

```http
POST /islamic/zakat/calculate
```

**Request Body:**
```json
{
  "assets": {
    "cash": 10000.0,
    "gold": 5000.0,
    "silver": 2000.0,
    "business_assets": 15000.0
  },
  "liabilities": {
    "short_term_debt": 3000.0
  },
  "calculation_date": "2024-01-15T10:30:00Z",
  "region": "ME"
}
```

**Response:**
```json
{
  "zakat_amount": 725.0,
  "zakat_rate": 0.025,
  "net_assets": 29000.0,
  "nisab_threshold": 5000.0,
  "calculation_date": "2024-01-15T10:30:00Z",
  "breakdown": {
    "cash_gold_silver": 500.0,
    "business_assets": 225.0
  }
}
```

---

## IoT Device Endpoints

### Device Management

#### Register Device

```http
POST /iot/devices/register
```

**Request Body:**
```json
{
  "device_id": "device-123",
  "device_type": "smart_meter",
  "protocol": "mqtt",
  "location": "Dubai",
  "metadata": {
    "manufacturer": "Siemens",
    "model": "SM-2000"
  }
}
```

**Response:**
```json
{
  "status": "registered",
  "device_id": "device-123",
  "registration_date": "2024-01-15T10:30:00Z",
  "initial_status": "offline"
}
```

#### Get Device Data

```http
GET /iot/devices/{device_id}/data
```

**Query Parameters:**
- `start_time`: Start time for data range
- `end_time`: End time for data range

**Response:**
```json
[
  {
    "timestamp": "2024-01-15T10:30:00Z",
    "energy_consumption": 45.2,
    "voltage": 220.0,
    "current": 0.21,
    "power_factor": 0.95
  }
]
```

---

## Mobile App Endpoints

### Device Registration

#### Register Mobile Device

```http
POST /mobile/devices/register
```

**Request Body:**
```json
{
  "platform": "ios",
  "app_version": "1.0.0",
  "os_version": "17.0",
  "device_model": "iPhone 15 Pro",
  "features": ["push_notifications", "biometric_auth"],
  "metadata": {
    "device_id": "device-uuid",
    "push_token": "apns-token"
  }
}
```

**Response:**
```json
{
  "status": "registered",
  "device_id": "device-uuid",
  "certificate": "base64-certificate",
  "platform": "ios",
  "supported_features": ["push_notifications", "biometric_auth"],
  "registration_date": "2024-01-15T10:30:00Z"
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 422 | Validation Error - Data validation failed |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

## Webhooks

EnergyOpti-Pro supports webhooks for real-time notifications on various events:

- **Trade Execution**: When a trade is executed
- **Risk Alerts**: When risk limits are breached
- **Compliance Updates**: When compliance status changes
- **Market Events**: When significant market movements occur

### Webhook Configuration

```http
POST /webhooks/configure
```

**Request Body:**
```json
{
  "url": "https://your-domain.com/webhook",
  "events": ["trade_execution", "risk_alerts"],
  "secret": "webhook-secret-key"
}
```

## SDKs and Libraries

Official SDKs are available for:

- **Python**: `pip install energyopti-pro-python`
- **JavaScript/Node.js**: `npm install energyopti-pro-js`
- **Java**: Maven dependency available
- **C#**: NuGet package available

## Support

For API support and questions:

- **Documentation**: https://docs.energyopti-pro.com
- **API Status**: https://status.energyopti-pro.com
- **Support Email**: api-support@energyopti-pro.com
- **Developer Community**: https://community.energyopti-pro.com 