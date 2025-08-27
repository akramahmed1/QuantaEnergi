# 🔄 Sequence Diagrams

## User Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API Gateway
    participant B as Backend
    participant DB as Database
    participant JWT as JWT Service

    U->>F: Enter credentials
    F->>A: POST /api/auth/login
    A->>B: Forward request
    B->>DB: Query user by email
    DB-->>B: User data
    B->>B: Verify password hash
    B->>JWT: Generate access token
    JWT-->>B: JWT token
    B-->>A: Token response
    A-->>F: Authentication success
    F->>F: Store token in localStorage
    F-->>U: Redirect to dashboard
```

## Energy Data Optimization Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as Energy API
    participant OE as Optimization Engine
    participant DI as Data Integration
    participant FS as Forecasting Service
    participant QS as Quantum Service
    participant DB as Database

    U->>F: Request optimization
    F->>API: GET /api/energy-data/optimize
    API->>OE: Analyze market conditions
    OE->>DI: Get real-time market data
    DI-->>OE: Market data
    OE->>FS: Get forecasting data
    FS-->>OE: Forecast results
    OE->>QS: Quantum optimization
    QS-->>OE: Optimization results
    OE->>DB: Store recommendations
    DB-->>OE: Confirmation
    OE-->>API: Optimization results
    API-->>F: Recommendations data
    F-->>U: Display recommendations
```

## AI-Powered Scenario Simulation

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as Energy API
    participant AI as AI Service
    participant Grok as Grok API
    participant FS as Forecasting Service
    participant DB as Database

    U->>F: Request scenario simulation
    F->>API: POST /api/energy-data/scenarios/simulate
    API->>AI: Generate scenario
    AI->>Grok: Request AI analysis
    Grok-->>AI: AI insights
    AI->>FS: Get historical data
    FS-->>AI: Historical patterns
    AI->>AI: Apply scenario modifications
    AI->>DB: Store scenario results
    DB-->>AI: Confirmation
    AI-->>API: Scenario results
    API-->>F: Simulation data
    F-->>U: Display scenario analysis
```

## Real-Time Market Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as Energy API
    participant DI as Data Integration
    participant CME as CME API
    participant ICE as ICE API
    participant Weather as Weather API
    participant Cache as Redis Cache
    participant DB as Database

    U->>F: Request market data
    F->>API: GET /api/energy-data/real-time
    API->>Cache: Check cache
    alt Cache hit
        Cache-->>API: Cached data
    else Cache miss
        API->>DI: Fetch fresh data
        DI->>CME: Get crude oil prices
        CME-->>DI: Price data
        DI->>ICE: Get natural gas prices
        ICE-->>DI: Gas data
        DI->>Weather: Get weather data
        Weather-->>DI: Weather info
        DI->>Cache: Store in cache
        DI-->>API: Aggregated data
    end
    API->>DB: Log data access
    API-->>F: Market data
    F-->>U: Display real-time data
```

## Billing and Subscription Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as Admin API
    participant BS as Billing Service
    participant Stripe as Stripe API
    participant DB as Database
    participant Email as Email Service

    U->>F: Subscribe to plan
    F->>API: POST /api/admin/billing/subscribe
    API->>BS: Create subscription
    BS->>Stripe: Create customer
    Stripe-->>BS: Customer ID
    BS->>Stripe: Create subscription
    Stripe-->>BS: Subscription ID
    BS->>DB: Store subscription
    DB-->>BS: Confirmation
    BS->>Email: Send confirmation
    BS-->>API: Subscription created
    API-->>F: Success response
    F-->>U: Subscription confirmed
```

## Quantum Portfolio Optimization

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as Energy API
    participant QS as Quantum Service
    participant IBMQ as IBM Quantum
    participant CS as Classical Service
    participant DB as Database

    U->>F: Request portfolio optimization
    F->>API: POST /api/energy-data/quantum/optimize
    API->>QS: Optimize portfolio
    QS->>QS: Check quantum availability
    alt Quantum available
        QS->>IBMQ: Submit quantum job
        IBMQ-->>QS: Quantum results
    else Quantum unavailable
        QS->>CS: Use classical optimization
        CS-->>QS: Classical results
    end
    QS->>DB: Store optimization
    DB-->>QS: Confirmation
    QS-->>API: Optimization results
    API-->>F: Portfolio allocation
    F-->>U: Display optimized portfolio
```

## System Health Monitoring

```mermaid
sequenceDiagram
    participant M as Monitoring
    participant API as Health API
    participant DB as Database
    participant Redis as Redis Cache
    participant Ext as External APIs
    participant Log as Logging Service

    loop Every 30 seconds
        M->>API: GET /health
        API->>DB: Check database connection
        DB-->>API: Connection status
        API->>Redis: Check cache health
        Redis-->>API: Cache status
        API->>Ext: Check external APIs
        Ext-->>API: API status
        API->>Log: Log health metrics
        API-->>M: Health report
    end
```

## Error Handling and Recovery

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as API Gateway
    participant B as Backend
    participant DB as Database
    participant Log as Logging
    participant Alert as Alert Service

    U->>F: Make request
    F->>API: API call
    API->>B: Forward request
    B->>DB: Database operation
    alt Database error
        DB-->>B: Error response
        B->>Log: Log error
        B->>Alert: Send alert
        B-->>API: Error response
        API-->>F: Error message
        F-->>U: Display error
    else Success
        DB-->>B: Success response
        B-->>API: Success response
        API-->>F: Success data
        F-->>U: Display success
    end
```
