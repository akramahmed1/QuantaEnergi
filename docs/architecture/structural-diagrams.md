# 🏗️ Structural Diagrams

## Class Structure Diagram

```mermaid
classDiagram
    class FastAPI {
        +app: FastAPI
        +startup_event()
        +shutdown_event()
    }

    class User {
        +id: int
        +email: str
        +hashed_password: str
        +company_name: str
        +is_active: bool
        +role: str
        +subscription_plan: str
        +api_calls_this_month: int
        +created_at: datetime
        +updated_at: datetime
        +energy_data: List[EnergyData]
    }

    class EnergyData {
        +id: int
        +user_id: int
        +timestamp: datetime
        +commodity_type: str
        +price: float
        +volume: float
        +region: str
        +source: str
        +user: User
    }

    class OptimizationEngine {
        +recommendation_history: List
        +optimization_rules: Dict
        +analyze_market_conditions()
        +generate_recommendations()
        +execute_recommendation()
        +get_recommendation_history()
    }

    class ForecastingService {
        +models: Dict
        +historical_data: DataFrame
        +train_model()
        +forecast_future_consumption()
        +get_forecast_insights()
        +retrain_model()
    }

    class QuantumOptimizationService {
        +ibmq_token: str
        +quantum_available: bool
        +optimization_history: List
        +optimize_portfolio()
        +_quantum_portfolio_optimization()
        +_classical_portfolio_optimization()
        +optimize_energy_scheduling()
    }

    class GenerativeAIService {
        +grok_client: GrokClient
        +scenario_history: List
        +simulate_scenario()
        +_generate_scenario_narrative()
        +_apply_scenario_modifications()
        +_generate_scenario_insights()
    }

    class BillingService {
        +stripe_client: Stripe
        +subscription_plans: Dict
        +create_customer()
        +create_subscription()
        +cancel_subscription()
        +update_subscription()
        +get_invoice_history()
        +calculate_bill()
    }

    class DataIntegrationService {
        +cme_api_key: str
        +ice_api_key: str
        +weather_api_key: str
        +get_real_time_market_data()
        +fetch_cme_prices()
        +fetch_ice_prices()
        +fetch_weather_data()
        +get_energy_demand_data()
    }

    class AuthService {
        +secret_key: str
        +algorithm: str
        +access_token_expire_minutes: int
        +create_access_token()
        +verify_token()
        +get_password_hash()
        +verify_password()
    }

    class DatabaseSession {
        +engine: Engine
        +SessionLocal: sessionmaker
        +get_db()
        +create_tables()
        +get_user_scoped_query()
    }

    %% Relationships
    FastAPI --> User
    FastAPI --> EnergyData
    User ||--o{ EnergyData : has
    OptimizationEngine --> EnergyData : analyzes
    ForecastingService --> EnergyData : forecasts
    QuantumOptimizationService --> EnergyData : optimizes
    GenerativeAIService --> EnergyData : simulates
    BillingService --> User : bills
    DataIntegrationService --> EnergyData : provides
    AuthService --> User : authenticates
    DatabaseSession --> User : manages
    DatabaseSession --> EnergyData : manages
```

## Database Schema Diagram

```mermaid
erDiagram
    USERS {
        int id PK
        string email UK
        string hashed_password
        string company_name
        boolean is_active
        string role
        string subscription_plan
        int api_calls_this_month
        datetime created_at
        datetime updated_at
    }

    ENERGY_DATA {
        int id PK
        int user_id FK
        datetime timestamp
        string commodity_type
        float price
        float volume
        string region
        string source
        json metadata
    }

    OPTIMIZATION_RECOMMENDATIONS {
        int id PK
        int user_id FK
        datetime created_at
        string recommendation_type
        string status
        float estimated_savings
        json parameters
        json results
    }

    FORECAST_MODELS {
        int id PK
        int user_id FK
        string model_name
        string model_type
        datetime trained_at
        float accuracy_score
        json model_parameters
        binary model_file
    }

    QUANTUM_OPTIMIZATIONS {
        int id PK
        int user_id FK
        datetime created_at
        string optimization_type
        boolean quantum_used
        float quantum_advantage
        json classical_results
        json quantum_results
    }

    AI_SCENARIOS {
        int id PK
        int user_id FK
        datetime created_at
        string scenario_type
        string ai_model_used
        json input_parameters
        json output_results
        text narrative_report
    }

    BILLING_SUBSCRIPTIONS {
        int id PK
        int user_id FK
        string stripe_customer_id
        string stripe_subscription_id
        string plan_name
        datetime start_date
        datetime end_date
        string status
        float monthly_amount
    }

    API_USAGE_LOGS {
        int id PK
        int user_id FK
        datetime timestamp
        string endpoint
        string method
        int response_time
        int status_code
        json request_data
    }

    %% Relationships
    USERS ||--o{ ENERGY_DATA : "has"
    USERS ||--o{ OPTIMIZATION_RECOMMENDATIONS : "receives"
    USERS ||--o{ FORECAST_MODELS : "owns"
    USERS ||--o{ QUANTUM_OPTIMIZATIONS : "performs"
    USERS ||--o{ AI_SCENARIOS : "creates"
    USERS ||--o{ BILLING_SUBSCRIPTIONS : "has"
    USERS ||--o{ API_USAGE_LOGS : "generates"
```

## Component Structure Diagram

```mermaid
graph TB
    subgraph "Frontend Components"
        App[App.jsx]
        Router[React Router]
        Login[Login.jsx]
        Signup[Signup.jsx]
        Dashboard[TradingDashboard.jsx]
        Optimization[Optimization.jsx]
        ProtectedRoute[ProtectedRoute.jsx]
    end

    subgraph "Frontend Services"
        ApiService[api.js]
        AuthService[Auth Service]
        DataService[Data Service]
    end

    subgraph "Frontend Components"
        PriceDisplay[PriceDisplay.jsx]
        AnalyticsDashboard[AnalyticsDashboard.jsx]
        GamifiedHub[GamifiedHub.jsx]
        MarketplaceMockup[MarketplaceMockup.jsx]
        PortfolioSummary[PortfolioSummary.tsx]
        MarketOverview[MarketOverview.tsx]
        ESGScore[ESGScore.tsx]
        AIInsights[AIInsights.tsx]
    end

    subgraph "Backend API Routes"
        AuthRouter[auth.py]
        EnergyRouter[energy_data.py]
        AdminRouter[admin.py]
    end

    subgraph "Backend Services"
        OptimizationEngine[optimization_engine.py]
        ForecastingService[forecasting_service.py]
        QuantumService[quantum_optimization_service.py]
        AIService[generative_ai_service.py]
        BillingService[billing_service.py]
        DataIntegrationService[data_integration_service.py]
    end

    subgraph "Backend Core"
        Config[config.py]
        Security[security.py]
        DatabaseSession[session.py]
    end

    subgraph "Backend Models"
        UserModel[user.py]
        EnergyDataModel[energy_data.py]
    end

    %% Frontend relationships
    App --> Router
    Router --> Login
    Router --> Signup
    Router --> ProtectedRoute
    ProtectedRoute --> Dashboard
    ProtectedRoute --> Optimization
    Dashboard --> PriceDisplay
    Dashboard --> AnalyticsDashboard
    Dashboard --> GamifiedHub
    Dashboard --> MarketplaceMockup
    Optimization --> PortfolioSummary
    Optimization --> MarketOverview
    Optimization --> ESGScore
    Optimization --> AIInsights

    %% Service relationships
    Login --> ApiService
    Signup --> ApiService
    Dashboard --> ApiService
    Optimization --> ApiService
    ApiService --> AuthService
    ApiService --> DataService

    %% Backend relationships
    AuthRouter --> Security
    EnergyRouter --> OptimizationEngine
    EnergyRouter --> ForecastingService
    EnergyRouter --> QuantumService
    EnergyRouter --> AIService
    AdminRouter --> BillingService
    EnergyRouter --> DataIntegrationService

    %% Core relationships
    AuthRouter --> DatabaseSession
    EnergyRouter --> DatabaseSession
    AdminRouter --> DatabaseSession
    OptimizationEngine --> DatabaseSession
    ForecastingService --> DatabaseSession
    QuantumService --> DatabaseSession
    AIService --> DatabaseSession
    BillingService --> DatabaseSession
    DataIntegrationService --> DatabaseSession

    %% Model relationships
    DatabaseSession --> UserModel
    DatabaseSession --> EnergyDataModel

    classDef frontend fill:#e1f5fe
    classDef service fill:#f3e5f5
    classDef backend fill:#e8f5e8
    classDef core fill:#fff3e0
    classDef model fill:#fce4ec

    class App,Router,Login,Signup,Dashboard,Optimization,ProtectedRoute,PriceDisplay,AnalyticsDashboard,GamifiedHub,MarketplaceMockup,PortfolioSummary,MarketOverview,ESGScore,AIInsights frontend
    class ApiService,AuthService,DataService service
    class AuthRouter,EnergyRouter,AdminRouter,OptimizationEngine,ForecastingService,QuantumService,AIService,BillingService,DataIntegrationService backend
    class Config,Security,DatabaseSession core
    class UserModel,EnergyDataModel model
```

## Package Structure Diagram

```mermaid
graph TB
    subgraph "EnergyOpti-Pro"
        Root[energyopti-pro/]
        
        subgraph "Backend Package"
            Backend[backend/]
            BackendApp[app/]
            BackendMain[main.py]
            BackendReq[requirements.txt]
        end
        
        subgraph "Frontend Package"
            Frontend[frontend/]
            FrontendSrc[src/]
            FrontendPkg[package.json]
            FrontendConfig[vite.config.ts]
        end
        
        subgraph "Documentation"
            Docs[docs/]
            Readme[README.md]
            ApiDocs[api_documentation.md]
        end
        
        subgraph "Configuration"
            Config[Configuration Files]
            Docker[Dockerfile]
            DockerCompose[docker-compose.yml]
            Render[render.yaml]
        end
        
        subgraph "Testing"
            Tests[test_e2e.py]
            TestDir[tests/]
        end
    end

    subgraph "Backend App Structure"
        App[app/]
        Api[api/]
        Services[services/]
        Schemas[schemas/]
        Core[core/]
        Db[db/]
    end

    subgraph "Frontend Src Structure"
        Src[src/]
        Components[components/]
        Pages[pages/]
        Services[services/]
        Types[types/]
        Store[store/]
    end

    %% Main structure
    Root --> Backend
    Root --> Frontend
    Root --> Docs
    Root --> Config
    Root --> Tests

    %% Backend structure
    Backend --> BackendApp
    Backend --> BackendMain
    Backend --> BackendReq

    %% Backend app structure
    BackendApp --> Api
    BackendApp --> Services
    BackendApp --> Schemas
    BackendApp --> Core
    BackendApp --> Db

    %% Frontend structure
    Frontend --> FrontendSrc
    Frontend --> FrontendPkg
    Frontend --> FrontendConfig

    %% Frontend src structure
    FrontendSrc --> Components
    FrontendSrc --> Pages
    FrontendSrc --> Services
    FrontendSrc --> Types
    FrontendSrc --> Store

    classDef root fill:#e3f2fd
    classDef backend fill:#f3e5f5
    classDef frontend fill:#e8f5e8
    classDef docs fill:#fff3e0
    classDef config fill:#fce4ec
    classDef testing fill:#f1f8e9

    class Root root
    class Backend,BackendApp,BackendMain,BackendReq,Api,Services,Schemas,Core,Db backend
    class Frontend,FrontendSrc,FrontendPkg,FrontendConfig,Components,Pages,Services,Types,Store frontend
    class Docs,Readme,ApiDocs docs
    class Config,Docker,DockerCompose,Render config
    class Tests,TestDir testing
```

## Module Dependency Diagram

```mermaid
graph TB
    subgraph "Entry Points"
        Main[main.py]
        FrontendEntry[index.jsx]
    end

    subgraph "API Layer"
        AuthAPI[auth.py]
        EnergyAPI[energy_data.py]
        AdminAPI[admin.py]
    end

    subgraph "Service Layer"
        OptimizationSvc[optimization_engine.py]
        ForecastingSvc[forecasting_service.py]
        QuantumSvc[quantum_optimization_service.py]
        AISvc[generative_ai_service.py]
        BillingSvc[billing_service.py]
        DataSvc[data_integration_service.py]
    end

    subgraph "Core Layer"
        Config[config.py]
        Security[security.py]
        Database[session.py]
    end

    subgraph "Model Layer"
        UserModel[user.py]
        EnergyModel[energy_data.py]
    end

    subgraph "Frontend Layer"
        App[App.jsx]
        Router[React Router]
        Components[Components]
        Services[Services]
    end

    %% Backend dependencies
    Main --> AuthAPI
    Main --> EnergyAPI
    Main --> AdminAPI
    Main --> Config
    Main --> Database

    AuthAPI --> Security
    AuthAPI --> UserModel
    AuthAPI --> Database

    EnergyAPI --> OptimizationSvc
    EnergyAPI --> ForecastingSvc
    EnergyAPI --> QuantumSvc
    EnergyAPI --> AISvc
    EnergyAPI --> DataSvc
    EnergyAPI --> EnergyModel
    EnergyAPI --> Database

    AdminAPI --> BillingSvc
    AdminAPI --> UserModel
    AdminAPI --> Database

    %% Service dependencies
    OptimizationSvc --> DataSvc
    OptimizationSvc --> EnergyModel
    OptimizationSvc --> Database

    ForecastingSvc --> EnergyModel
    ForecastingSvc --> Database

    QuantumSvc --> EnergyModel
    QuantumSvc --> Database

    AISvc --> EnergyModel
    AISvc --> Database

    BillingSvc --> UserModel
    BillingSvc --> Database

    DataSvc --> Config
    DataSvc --> Database

    %% Frontend dependencies
    FrontendEntry --> App
    App --> Router
    Router --> Components
    Components --> Services

    %% Cross-layer dependencies
    Services --> AuthAPI
    Services --> EnergyAPI
    Services --> AdminAPI

    classDef entry fill:#e3f2fd
    classDef api fill:#f3e5f5
    classDef service fill:#e8f5e8
    classDef core fill:#fff3e0
    classDef model fill:#fce4ec
    classDef frontend fill:#f1f8e9

    class Main,FrontendEntry entry
    class AuthAPI,EnergyAPI,AdminAPI api
    class OptimizationSvc,ForecastingSvc,QuantumSvc,AISvc,BillingSvc,DataSvc service
    class Config,Security,Database core
    class UserModel,EnergyModel model
    class App,Router,Components,Services frontend
```
