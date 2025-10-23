# QuantaEnergi API Documentation

## Base URL
- Production: `https://api.quantaenergi.com`
- Development: `http://localhost:8000`

## Authentication
```bash
POST /v1/auth/login
{
  "username": "trader@company.com",
  "password": "secure_password"
}
```

## Core Endpoints

### Trading
- `GET /v1/trades` - List trades
- `POST /v1/trades` - Create trade
- `PUT /v1/trades/{id}` - Update trade

### Risk Management
- `GET /v1/risk/var` - Value at Risk calculation
- `GET /v1/risk/analytics` - Risk analytics

### Market Data
- `GET /v1/market/prices` - Real-time prices
- `GET /v1/market/volatility` - Market volatility

## WebSocket
- `ws://localhost:8000/ws` - Real-time updates

## Rate Limits
- 1000 requests per hour per user
- 100 requests per minute for market data
