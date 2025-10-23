# QuantaEnergi Deployment Guide

## Quick Start

```bash
# Deploy to production
./deploy.sh production

# Deploy to cloud (Railway + Vercel)
./deploy.sh cloud

# Local development
./deploy.sh local
```

## Environment Setup

1. **Backend**: Railway deployment with PostgreSQL
2. **Frontend**: Vercel deployment with React
3. **Database**: PostgreSQL with Redis caching
4. **Monitoring**: Prometheus + Grafana

## Configuration

- Environment variables in `apps/backend/config.env`
- Frontend config in `apps/frontend/env.production`
- Docker configuration in `docker-compose.yml`

## Security

- JWT authentication
- Enterprise security middleware
- OWASP compliance
- Multi-tenant architecture
