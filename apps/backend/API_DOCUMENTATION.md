# QuantaEnergi API Documentation

## Overview

This directory contains comprehensive API documentation for the QuantaEnergi ETRM/CTRM (Energy Trading and Risk Management) API, including:

- **OpenAPI Specification** (`openapi.yaml`)
- **Postman Collection** (`QuantaEnergi_API.postman_collection.json`)
- **Swagger UI Integration** (`swagger_ui_setup.py`)
- **Standalone Swagger UI Preview** (`swagger_ui_preview.html`)

## Quick Start

### 1. Swagger UI Preview

Open `swagger_ui_preview.html` in your browser to view the interactive API documentation.

### 2. Postman Collection

1. Import `QuantaEnergi_API.postman_collection.json` into Postman
2. Set the `base_url` variable to your API endpoint
3. Run the "Login" request to get an access token
4. All subsequent requests will automatically use the Bearer token

### 3. Integrate with FastAPI

```python
# Add to your main.py
from swagger_ui_setup import setup_swagger_ui

# Set up Swagger UI
app = setup_swagger_ui(app)
```

## API Endpoints Overview

### Authentication
- `POST /auth/login` - User authentication
- `POST /v1/auth/login` - User authentication (v1)

### Health & Monitoring
- `GET /health` - Health check
- `GET /api/status` - API status
- `GET /api/test` - Test endpoint

### Trading
- `POST /api/v1/trade/capture` - Capture energy trade
- `GET /api/trades/recent` - Recent trades
- `POST /api/v1/trading/trades` - Create trade
- `GET /api/v1/trading/positions/{id}/pnl` - Position P&L

### Risk Management
- `GET /api/v1/risk/var` - Calculate VaR
- `GET /api/v1/risk/stress-test` - Stress testing
- `POST /api/v1/risk/var/parametric` - Parametric VaR
- `POST /api/v1/risk/var/monte-carlo` - Monte Carlo VaR

### Market Data
- `GET /api/market/prices` - Market prices
- `GET /api/analytics` - User analytics
- `GET /api/renewables` - Renewable energy data

### AI & Forecasting
- `GET /api/signals` - Trading signals
- `GET /api/forecast/energy` - Energy forecasts
- `GET /api/v1/ai/forecast` - AI forecasts
- `POST /api/v1/ai/optimize` - Portfolio optimization

### ESG
- `GET /api/esg/metrics` - ESG metrics

### Weather
- `GET /api/weather/current` - Current weather
- `GET /api/weather/forecast` - Weather forecast

### Portfolio
- `GET /api/portfolio/summary` - Portfolio summary

### Quantum Computing
- `POST /api/v1/quantum/optimize` - Quantum optimization
- `POST /api/v1/quantum/risk` - Quantum risk analysis
- `POST /api/v1/quantum/simulate` - Quantum simulation

### Billing
- `POST /api/v1/billing/subscribe` - Create subscription
- `GET /api/v1/billing/subscription/{user_id}` - Get subscription
- `GET /api/v1/billing/usage/{user_id}` - Get usage

### Admin
- `GET /api/v1/admin/overview` - System overview
- `GET /api/v1/admin/metrics` - Performance metrics
- `GET /api/v1/admin/users` - User analytics

## Authentication

All endpoints require JWT authentication via Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/portfolio/summary
```

## Rate Limiting

- Standard endpoints: 1000 requests/hour
- AI/ML endpoints: 100 requests/hour  
- Quantum endpoints: 10 requests/hour

## Testing

### Using Postman

1. Import the collection
2. Set environment variables:
   - `base_url`: Your API endpoint
   - `access_token`: JWT token (auto-set after login)
   - `user_id`: User ID (auto-set after login)

### Using cURL

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use token for authenticated requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/portfolio/summary
```

## Development

### Adding New Endpoints

1. Add endpoint to your FastAPI router
2. Update `openapi.yaml` with new endpoint definition
3. Add request to Postman collection
4. Test with Swagger UI

### Customizing Swagger UI

Edit `swagger_ui_setup.py` to customize:
- UI theme and styling
- Authentication flow
- Request/response interceptors
- Custom JavaScript

## Deployment

### Production Setup

1. Update `openapi.yaml` servers section with production URLs
2. Configure authentication for production
3. Set up rate limiting
4. Enable HTTPS

### Docker

```dockerfile
# Add to your Dockerfile
COPY openapi.yaml /app/
COPY swagger_ui_setup.py /app/
```

## Support

For API support and questions:
- Email: team@quantaenergi.com
- GitHub: https://github.com/akramahmed1/QuantaEnergi
- Documentation: This README and Swagger UI

## License

MIT License - see LICENSE file for details.
