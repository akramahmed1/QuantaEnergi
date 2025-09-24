import { rest } from 'msw';

// Mock API handlers
export const handlers = [
  // Auth endpoints
  rest.post('/api/auth/login', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        user: {
          id: 'user-123',
          email: 'test@quantaenergi.com',
          firstName: 'Test',
          lastName: 'User',
          roles: ['trader'],
          tenantId: 'tenant-123'
        }
      })
    );
  }),

  rest.post('/api/auth/logout', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({ message: 'Logged out successfully' }));
  }),

  rest.post('/api/auth/refresh', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token'
      })
    );
  }),

  // Market data endpoints
  rest.get('/api/market/prices', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        crude_oil: {
          price: 85.50,
          change: '+1.20',
          volume: 1000000,
          source: 'CME',
          timestamp: new Date().toISOString()
        },
        natural_gas: {
          price: 3.45,
          change: '-0.05',
          volume: 500000,
          source: 'ICE',
          timestamp: new Date().toISOString()
        },
        electricity: {
          price: 52.50,
          change: '+2.10',
          volume: 200000,
          source: 'NYMEX',
          timestamp: new Date().toISOString()
        },
        carbon_credits: {
          price: 31.50,
          change: '+0.75',
          volume: 100000,
          source: 'ICE',
          timestamp: new Date().toISOString()
        }
      })
    );
  }),

  rest.get('/api/signals', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        signals: [
          {
            id: 1,
            signal: 'BUY',
            commodity: 'crude_oil',
            confidence: 85,
            price: 85.50,
            target: 90.00,
            stop_loss: 80.00,
            timeframe: '1D',
            source: 'AI',
            timestamp: new Date().toISOString(),
            risk: 'Medium',
            volume: 'High',
            trend: 'Bullish',
            esg_impact: 'Neutral'
          },
          {
            id: 2,
            signal: 'SELL',
            commodity: 'natural_gas',
            confidence: 72,
            price: 3.45,
            target: 3.20,
            stop_loss: 3.60,
            timeframe: '4H',
            source: 'Technical',
            timestamp: new Date().toISOString(),
            risk: 'Low',
            volume: 'Medium',
            trend: 'Bearish',
            esg_impact: 'Positive'
          }
        ]
      })
    );
  }),

  // Trading endpoints
  rest.get('/api/trades', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        trades: [
          {
            id: 'T000001',
            commodity: 'crude_oil',
            type: 'BUY',
            quantity: 1000,
            price: 85.50,
            totalValue: 85500.00,
            timestamp: new Date().toISOString(),
            status: 'completed',
            commission: 15.00,
            strategy: 'Momentum',
            tenantId: 'tenant-123'
          },
          {
            id: 'T000002',
            commodity: 'natural_gas',
            type: 'SELL',
            quantity: 5000,
            price: 3.45,
            totalValue: 17250.00,
            timestamp: new Date().toISOString(),
            status: 'pending',
            commission: 12.00,
            strategy: 'Mean Reversion',
            tenantId: 'tenant-123'
          }
        ],
        total: 2,
        page: 1,
        pageSize: 20
      })
    );
  }),

  rest.post('/api/trades', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 'T000003',
        commodity: 'crude_oil',
        type: 'BUY',
        quantity: 1000,
        price: 85.50,
        totalValue: 85500.00,
        timestamp: new Date().toISOString(),
        status: 'pending',
        commission: 15.00,
        strategy: 'Momentum',
        tenantId: 'tenant-123'
      })
    );
  }),

  // Portfolio endpoints
  rest.get('/api/portfolio/summary', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        total_value: 1000000.00,
        cash: 100000.00,
        invested: 900000.00,
        daily_change: 2.5,
        daily_change_amount: 25000.00,
        monthly_change: 8.2,
        yearly_change: 15.7,
        total_return: 15.7,
        positions: [
          {
            commodity: 'crude_oil',
            quantity: 1000,
            avg_price: 85.50,
            current_price: 85.50,
            market_value: 85500.00,
            unrealized_pnl: 0.00,
            weight: 0.085
          },
          {
            commodity: 'natural_gas',
            quantity: 5000,
            avg_price: 3.45,
            current_price: 3.45,
            market_value: 17250.00,
            unrealized_pnl: 0.00,
            weight: 0.017
          }
        ],
        allocation: {
          'crude_oil': 0.085,
          'natural_gas': 0.017,
          'electricity': 0.045,
          'carbon_credits': 0.023
        },
        risk_metrics: {
          var_95: 50000.00,
          var_99: 75000.00,
          sharpe_ratio: 1.25,
          beta: 0.85,
          alpha: 0.05
        },
        timestamp: new Date().toISOString()
      })
    );
  }),

  // Risk analytics endpoints
  rest.post('/api/risk-analytics/var/monte-carlo', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        var_value: 50000.00,
        expected_shortfall: 65000.00,
        max_loss: 100000.00,
        confidence_level: 0.95,
        time_horizon: 1,
        num_simulations: 10000,
        calculation_time: 2.5,
        timestamp: new Date().toISOString(),
        tenant_id: 'tenant-123'
      })
    );
  }),

  rest.post('/api/risk-analytics/stress-test', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        portfolio_id: 'portfolio-123',
        scenario_name: 'market_crash',
        portfolio_loss: 75000.00,
        position_losses: [
          {
            commodity: 'crude_oil',
            position_loss: 50000.00,
            shock: -0.3,
            stressed_price: 59.85
          },
          {
            commodity: 'natural_gas',
            position_loss: 25000.00,
            shock: -0.2,
            stressed_price: 2.76
          }
        ],
        market_shocks: {
          crude_oil: -0.3,
          natural_gas: -0.2
        },
        calculation_time: 1.2,
        timestamp: new Date().toISOString(),
        tenant_id: 'tenant-123'
      })
    );
  }),

  // ESG endpoints
  rest.get('/api/esg/metrics', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        overall_esg_score: 85,
        environmental_score: 88,
        social_score: 82,
        governance_score: 85,
        carbon_offset: 1500,
        renewable_ratio: 0.75,
        sustainability_score: 87,
        climate_risk_score: 12,
        social_impact_score: 83,
        governance_quality: 86,
        esg_trend: 'Improving',
        esg_rank: 'A+',
        carbon_intensity: 0.45,
        water_efficiency: 0.92,
        waste_reduction: 0.78,
        diversity_score: 0.85,
        labor_rights: 0.90,
        board_independence: 0.88,
        executive_compensation: 0.82,
        shareholder_rights: 0.91,
        timestamp: new Date().toISOString()
      })
    );
  }),

  // Weather endpoints
  rest.get('/api/weather/current', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        temp: 22.5,
        humidity: 65,
        description: 'Partly cloudy',
        wind_speed: 12.3,
        pressure: 1013.25,
        visibility: 10,
        timestamp: new Date().toISOString(),
        location: { lat: 40.7128, lon: -74.0060 },
        source: 'OpenWeatherMap'
      })
    );
  }),

  rest.get('/api/weather/forecast', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        forecasts: [
          {
            time: '2024-01-01T12:00:00Z',
            temp: 22.5,
            description: 'Partly cloudy',
            humidity: 65,
            wind_speed: 12.3,
            energy_impact: 'Moderate'
          },
          {
            time: '2024-01-01T18:00:00Z',
            temp: 20.1,
            description: 'Clear',
            humidity: 58,
            wind_speed: 8.7,
            energy_impact: 'Low'
          }
        ],
        location: { lat: 40.7128, lon: -74.0060 },
        generated_at: new Date().toISOString(),
        source: 'OpenWeatherMap'
      })
    );
  }),

  // Forecast endpoints
  rest.get('/api/forecast/energy', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        forecasts: [
          {
            date: '2024-01-01',
            price: 85.50,
            confidence: 0.85,
            factors: 'Supply constraints, demand growth',
            trend: 'Bullish',
            volatility: 0.15
          },
          {
            date: '2024-01-02',
            price: 87.20,
            confidence: 0.82,
            factors: 'Market sentiment, geopolitical risks',
            trend: 'Bullish',
            volatility: 0.18
          }
        ],
        summary: {
          avg_price: 86.35,
          price_range: [85.50, 87.20],
          avg_confidence: 0.835,
          trend: 'Bullish',
          volatility: 0.165
        },
        commodity: 'crude_oil',
        days: 7
      })
    );
  }),

  // Tenant management endpoints
  rest.get('/api/v1/tenant-management/tenants', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        tenants: [
          {
            tenant_id: 'tenant-123',
            name: 'Test Tenant',
            region: 'us',
            subscription_tier: 'premium',
            max_users: 100,
            max_trades_per_day: 10000,
            features: ['trading', 'analytics', 'compliance'],
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
            is_active: true
          }
        ],
        total_count: 1,
        page: 1,
        page_size: 20
      })
    );
  }),

  rest.get('/api/v1/tenant-management/tenants/:tenantId', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        tenant_id: 'tenant-123',
        name: 'Test Tenant',
        region: 'us',
        subscription_tier: 'premium',
        max_users: 100,
        max_trades_per_day: 10000,
        features: ['trading', 'analytics', 'compliance'],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        is_active: true
      })
    );
  }),

  rest.get('/api/v1/tenant-management/tenants/:tenantId/stats', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        tenant_id: 'tenant-123',
        trade_count: 150,
        portfolio_count: 5,
        position_count: 25,
        total_trade_value: 1500000.00,
        database_stats: {
          size: '2.5MB',
          tables: 4,
          rows: 1000
        },
        timestamp: new Date().toISOString()
      })
    );
  }),

  // Health check
  rest.get('/health', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        status: 'healthy',
        service: 'QuantaEnergi API',
        version: '2.0.0',
        timestamp: new Date().toISOString()
      })
    );
  }),

  // Catch-all handler for unmatched requests
  rest.get('*', (req, res, ctx) => {
    console.warn(`Unhandled GET request: ${req.url}`);
    return res(ctx.status(404), ctx.json({ error: 'Not found' }));
  }),

  rest.post('*', (req, res, ctx) => {
    console.warn(`Unhandled POST request: ${req.url}`);
    return res(ctx.status(404), ctx.json({ error: 'Not found' }));
  }),

  rest.put('*', (req, res, ctx) => {
    console.warn(`Unhandled PUT request: ${req.url}`);
    return res(ctx.status(404), ctx.json({ error: 'Not found' }));
  }),

  rest.delete('*', (req, res, ctx) => {
    console.warn(`Unhandled DELETE request: ${req.url}`);
    return res(ctx.status(404), ctx.json({ error: 'Not found' }));
  })
];
