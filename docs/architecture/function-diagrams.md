# 🔧 Function Diagrams

## Function Call Hierarchy

```mermaid
graph TB
    subgraph "🚀 Application Entry"
        Main[main.py]
        FastAPI[FastAPI App]
        Startup[Startup Event]
    end

    subgraph "🔌 API Layer"
        Auth_Router[Auth Router]
        Energy_Router[Energy Data Router]
        Admin_Router[Admin Router]
    end

    subgraph "🧠 Service Layer"
        Auth_Service[Authentication Service]
        Optimization_Service[Optimization Engine]
        Forecasting_Service[Forecasting Service]
        Quantum_Service[Quantum Service]
        AI_Service[AI Service]
        Billing_Service[Billing Service]
        Data_Service[Data Integration Service]
    end

    subgraph "💾 Data Layer"
        DB_Session[Database Session]
        User_Model[User Model]
        Energy_Model[Energy Data Model]
        Cache[Redis Cache]
    end

    subgraph "🔒 Security Layer"
        JWT_Service[JWT Service]
        Password_Hash[Password Hashing]
        RBAC_Service[RBAC Service]
    end

    %% Application flow
    Main --> FastAPI
    FastAPI --> Startup
    Startup --> DB_Session

    %% API routing
    FastAPI --> Auth_Router
    FastAPI --> Energy_Router
    FastAPI --> Admin_Router

    %% Service calls
    Auth_Router --> Auth_Service
    Energy_Router --> Optimization_Service
    Energy_Router --> Forecasting_Service
    Energy_Router --> Quantum_Service
    Energy_Router --> AI_Service
    Admin_Router --> Billing_Service
    Energy_Router --> Data_Service

    %% Data access
    Auth_Service --> User_Model
    Optimization_Service --> Energy_Model
    Forecasting_Service --> Energy_Model
    Quantum_Service --> Energy_Model
    AI_Service --> Energy_Model
    Billing_Service --> User_Model
    Data_Service --> Cache

    %% Security
    Auth_Service --> JWT_Service
    Auth_Service --> Password_Hash
    FastAPI --> RBAC_Service

    classDef entry fill:#e3f2fd
    classDef api fill:#f3e5f5
    classDef service fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef security fill:#fce4ec

    class Main,FastAPI,Startup entry
    class Auth_Router,Energy_Router,Admin_Router api
    class Auth_Service,Optimization_Service,Forecasting_Service,Quantum_Service,AI_Service,Billing_Service,Data_Service service
    class DB_Session,User_Model,Energy_Model,Cache data
    class JWT_Service,Password_Hash,RBAC_Service security
```

## Function Flow for User Authentication

```mermaid
flowchart TD
    A[User enters credentials] --> B{Valid email format?}
    B -->|No| C[Show email error]
    B -->|Yes| D[Send POST to /api/auth/login]
    D --> E[Validate request body]
    E --> F{Valid request?}
    F -->|No| G[Return 422 validation error]
    F -->|Yes| H[Query database for user]
    H --> I{User exists?}
    I -->|No| J[Return 401 unauthorized]
    I -->|Yes| K[Verify password hash]
    K --> L{Password correct?}
    L -->|No| J
    L -->|Yes| M{User active?}
    M -->|No| N[Return 401 account deactivated]
    M -->|Yes| O[Generate JWT token]
    O --> P[Store token in response]
    P --> Q[Return 200 with token]
    Q --> R[Frontend stores token]
    R --> S[Redirect to dashboard]
```

## Function Flow for Energy Optimization

```mermaid
flowchart TD
    A[User requests optimization] --> B[Validate JWT token]
    B --> C{Token valid?}
    C -->|No| D[Return 401 unauthorized]
    C -->|Yes| E[Get user from token]
    E --> F[Check user permissions]
    F --> G{Has optimization access?}
    G -->|No| H[Return 403 forbidden]
    G -->|Yes| I[Get market conditions]
    I --> J[Analyze price thresholds]
    J --> K[Get demand patterns]
    K --> L[Get weather data]
    L --> M[Generate optimization rules]
    M --> N[Apply ML models]
    N --> O[Calculate recommendations]
    O --> P[Store in database]
    P --> Q[Return optimization results]
    Q --> R[Frontend displays recommendations]
```

## Function Flow for AI Scenario Simulation

```mermaid
flowchart TD
    A[User requests scenario] --> B[Validate parameters]
    B --> C{Parameters valid?}
    C -->|No| D[Return validation error]
    C -->|Yes| E[Check AI service availability]
    E --> F{AI service available?}
    F -->|No| G[Use fallback simulation]
    F -->|Yes| H[Call Grok API]
    H --> I[Get AI insights]
    I --> J[Get historical data]
    J --> K[Apply scenario modifications]
    K --> L[Generate probabilistic outcomes]
    L --> M[Create narrative report]
    M --> N[Store scenario results]
    N --> O[Return scenario data]
    O --> P[Frontend displays analysis]
```

## Function Flow for Quantum Optimization

```mermaid
flowchart TD
    A[User requests quantum optimization] --> B[Validate portfolio data]
    B --> C{Data valid?}
    C -->|No| D[Return validation error]
    C -->|Yes| E[Check quantum availability]
    E --> F{Quantum hardware available?}
    F -->|No| G[Use classical optimization]
    F -->|Yes| H[Prepare quantum problem]
    H --> I[Submit to IBM Quantum]
    I --> J{Quantum job successful?}
    J -->|No| K[Fallback to classical]
    J -->|Yes| L[Process quantum results]
    L --> M[Compare with classical]
    M --> N[Generate optimization report]
    N --> O[Store results]
    O --> P[Return quantum results]
    P --> Q[Frontend displays portfolio]
```

## Function Flow for Real-Time Data Integration

```mermaid
flowchart TD
    A[Request market data] --> B[Check Redis cache]
    B --> C{Cache hit?}
    C -->|Yes| D[Return cached data]
    C -->|No| E[Fetch from CME API]
    E --> F[Fetch from ICE API]
    F --> G[Fetch weather data]
    G --> H[Aggregate data]
    H --> I[Validate data quality]
    I --> J{Data valid?}
    J -->|No| K[Use fallback data]
    J -->|Yes| L[Store in cache]
    L --> M[Return aggregated data]
    M --> N[Frontend updates display]
```

## Function Flow for Billing and Subscription

```mermaid
flowchart TD
    A[User subscribes to plan] --> B[Validate subscription data]
    B --> C{Data valid?}
    C -->|No| D[Return validation error]
    C -->|Yes| E[Check Stripe availability]
    E --> F{Stripe available?}
    F -->|No| G[Store pending subscription]
    F -->|Yes| H[Create Stripe customer]
    H --> I[Create Stripe subscription]
    I --> J{Subscription created?}
    J -->|No| K[Return payment error]
    J -->|Yes| L[Update user plan]
    L --> M[Send confirmation email]
    M --> N[Return success response]
    N --> O[Frontend shows confirmation]
```

## Function Flow for Error Handling

```mermaid
flowchart TD
    A[Function execution] --> B{Exception occurs?}
    B -->|No| C[Return success]
    B -->|Yes| D[Log error details]
    D --> E[Determine error type]
    E --> F{Database error?}
    F -->|Yes| G[Return 500 database error]
    F -->|No| H{Validation error?}
    H -->|Yes| I[Return 422 validation error]
    H -->|No| J{Authentication error?}
    J -->|Yes| K[Return 401 unauthorized]
    J -->|No| L{Permission error?}
    L -->|Yes| M[Return 403 forbidden]
    L -->|No| N[Return 500 internal error]
    N --> O[Send alert to admin]
    O --> P[Frontend displays error]
```

## Function Performance Metrics

```mermaid
graph LR
    subgraph "Function Categories"
        Auth[Authentication Functions]
        Data[Data Processing Functions]
        AI[AI/ML Functions]
        Quantum[Quantum Functions]
        Business[Business Logic Functions]
    end

    subgraph "Performance Metrics"
        ResponseTime[Response Time]
        MemoryUsage[Memory Usage]
        CPUUsage[CPU Usage]
        ErrorRate[Error Rate]
        Throughput[Throughput]
    end

    Auth --> ResponseTime
    Auth --> ErrorRate
    Data --> ResponseTime
    Data --> MemoryUsage
    AI --> CPUUsage
    AI --> ResponseTime
    Quantum --> CPUUsage
    Quantum --> ResponseTime
    Business --> ResponseTime
    Business --> Throughput

    classDef functions fill:#e1f5fe
    classDef metrics fill:#e8f5e8

    class Auth,Data,AI,Quantum,Business functions
    class ResponseTime,MemoryUsage,CPUUsage,ErrorRate,Throughput metrics
```
