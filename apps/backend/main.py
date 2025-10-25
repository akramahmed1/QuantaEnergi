"""
QuantaEnergi ETRM/CTRM Platform
Enterprise Energy Trading and Risk Management System
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import hashlib
import secrets
import jwt
from passlib.context import CryptContext

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = "quantaenergi_etrm_secret_key_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create FastAPI app
app = FastAPI(
    title="QuantaEnergi ETRM/CTRM Platform",
    description="""
    ## Enterprise Energy Trading and Risk Management System
    
    QuantaEnergi is a comprehensive ETRM/CTRM platform designed for energy trading companies, 
    utilities, and financial institutions. This platform provides:
    
    ### Core Features
    - **Trading Management**: Complete trade lifecycle management
    - **Risk Management**: Advanced VaR calculations and risk monitoring
    - **Portfolio Management**: Real-time position tracking and P&L
    - **Analytics & Reporting**: Performance analytics and regulatory reporting
    - **Compliance**: Regulatory compliance and audit trail management
    
    ### Authentication
    Use the `/auth/login` endpoint to obtain a JWT token, then include it in the Authorization header:
    ```
    Authorization: Bearer <your_token>
    ```
    
    ### Demo Credentials
    - **Administrator**: admin / QuantaEnergi2024!
    - **Trader**: trader / trader123
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User authentication and authorization endpoints"
        },
        {
            "name": "Trading",
            "description": "Trade management and execution endpoints"
        },
        {
            "name": "Risk Management",
            "description": "Risk calculation and monitoring endpoints"
        },
        {
            "name": "Portfolio",
            "description": "Portfolio management and position tracking"
        },
        {
            "name": "Analytics",
            "description": "Performance analytics and reporting"
        },
        {
            "name": "Compliance",
            "description": "Regulatory compliance and audit management"
        },
        {
            "name": "Dashboard",
            "description": "Dashboard statistics and KPIs"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class User(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "trader"

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class PasswordReset(BaseModel):
    email: str

class Trade(BaseModel):
    id: str
    asset: str
    quantity: float
    price: float
    side: str
    status: str
    timestamp: str
    trader_id: str

class TradeCreate(BaseModel):
    asset: str
    quantity: float
    price: float
    side: str

class RiskMetrics(BaseModel):
    var_95: float
    var_99: float
    expected_shortfall: float
    sharpe_ratio: float
    max_drawdown: float

class PortfolioPosition(BaseModel):
    asset: str
    quantity: float
    current_price: float
    market_value: float
    unrealized_pnl: float

# Database (In-memory for demo)
users_db: Dict[str, Dict] = {
    "admin": {
        "id": "admin_001",
        "username": "admin",
        "email": "admin@quantaenergi.com",
        "password_hash": pwd_context.hash("QuantaEnergi2024!"),
        "role": "administrator",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    },
    "trader": {
        "id": "trader_001",
        "username": "trader",
        "email": "trader@quantaenergi.com",
        "password_hash": pwd_context.hash("trader123"),
        "role": "trader",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    }
}

trades_db: List[Dict] = []
portfolio_db: Dict[str, PortfolioPosition] = {}
risk_cache: Dict[str, Any] = {}

# Utility Functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = users_db.get(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Routes
@app.get("/")
async def root():
    return {"message": "QuantaEnergi ETRM/CTRM Platform", "status": "running", "version": "2.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Authentication Routes
@app.post("/auth/login", response_model=LoginResponse, tags=["Authentication"])
async def login(login_data: LoginRequest):
    user = users_db.get(login_data.username)
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.username}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=User(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            role=user["role"],
            is_active=user["is_active"],
            created_at=user["created_at"]
        )
    )

@app.post("/auth/logout", tags=["Authentication"])
async def logout(current_user: dict = Depends(get_current_user)):
    return {"message": "Successfully logged out"}

@app.post("/auth/change-password", tags=["Authentication"])
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    if not verify_password(password_data.current_password, current_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    users_db[current_user["username"]]["password_hash"] = get_password_hash(password_data.new_password)
    return {"message": "Password changed successfully"}

@app.post("/auth/reset-password", tags=["Authentication"])
async def reset_password(reset_data: PasswordReset):
    # In production, send email with reset link
    return {"message": "Password reset link sent to your email"}

# Trading Routes
@app.get("/trading/trades", response_model=List[Trade], tags=["Trading"])
async def get_trades(current_user: dict = Depends(get_current_user)):
    user_trades = [trade for trade in trades_db if trade["trader_id"] == current_user["id"]]
    return user_trades

@app.post("/trading/trades", response_model=Trade, tags=["Trading"])
async def create_trade(
    trade_data: TradeCreate,
    current_user: dict = Depends(get_current_user)
):
    trade = Trade(
        id=str(uuid.uuid4()),
        asset=trade_data.asset,
        quantity=trade_data.quantity,
        price=trade_data.price,
        side=trade_data.side,
        status="pending",
        timestamp=datetime.now().isoformat(),
        trader_id=current_user["id"]
    )
    
    trade_dict = trade.dict()
    trades_db.append(trade_dict)
    
    # Update portfolio
    portfolio_key = f"{current_user['id']}_{trade.asset}"
    if portfolio_key in portfolio_db:
        portfolio_db[portfolio_key].quantity += trade.quantity if trade.side == "buy" else -trade.quantity
    else:
        portfolio_db[portfolio_key] = PortfolioPosition(
            asset=trade.asset,
            quantity=trade.quantity if trade.side == "buy" else -trade.quantity,
            current_price=trade.price,
            market_value=trade.quantity * trade.price,
            unrealized_pnl=0.0
        )
    
    return trade

@app.put("/trading/trades/{trade_id}", tags=["Trading"])
async def update_trade(
    trade_id: str,
    status: str,
    current_user: dict = Depends(get_current_user)
):
    for trade in trades_db:
        if trade["id"] == trade_id and trade["trader_id"] == current_user["id"]:
            trade["status"] = status
            return {"message": "Trade updated successfully"}
    raise HTTPException(status_code=404, detail="Trade not found")

# Risk Management Routes
@app.get("/risk/var", tags=["Risk Management"])
async def get_var(current_user: dict = Depends(get_current_user)):
    # Calculate VaR based on portfolio positions
    total_exposure = sum(pos.market_value for pos in portfolio_db.values() if pos.asset.startswith(current_user["id"]))
    
    return {
        "var_95": total_exposure * 0.025,  # 2.5% VaR
        "var_99": total_exposure * 0.035,  # 3.5% VaR
        "expected_shortfall": total_exposure * 0.04,
        "confidence": "95%"
    }

@app.get("/risk/metrics", response_model=RiskMetrics, tags=["Risk Management"])
async def get_risk_metrics(current_user: dict = Depends(get_current_user)):
    return RiskMetrics(
        var_95=125000.0,
        var_99=180000.0,
        expected_shortfall=200000.0,
        sharpe_ratio=1.8,
        max_drawdown=0.05
    )

# Portfolio Routes
@app.get("/portfolio/overview", tags=["Portfolio"])
async def get_portfolio_overview(current_user: dict = Depends(get_current_user)):
    user_positions = [pos for key, pos in portfolio_db.items() if key.startswith(current_user["id"])]
    
    total_value = sum(pos.market_value for pos in user_positions)
    total_pnl = sum(pos.unrealized_pnl for pos in user_positions)
    
    return {
        "total_value": total_value,
        "total_pnl": total_pnl,
        "positions": user_positions,
        "risk_exposure": total_value * 0.05
    }

@app.get("/portfolio/positions", tags=["Portfolio"])
async def get_portfolio_positions(current_user: dict = Depends(get_current_user)):
    user_positions = [pos for key, pos in portfolio_db.items() if key.startswith(current_user["id"])]
    return user_positions

# Analytics Routes
@app.get("/analytics/performance", tags=["Analytics"])
async def get_performance_analytics(current_user: dict = Depends(get_current_user)):
    return {
        "monthly_pnl": [120000, 135000, 125000, 140000, 130000],
        "risk_metrics": {
            "sharpe_ratio": 1.8,
            "max_drawdown": 0.05,
            "volatility": 0.12
        },
        "returns": {
            "daily": 0.0025,
            "monthly": 0.075,
            "yearly": 0.15
        }
    }

@app.get("/analytics/reports", tags=["Analytics"])
async def get_analytics_reports(current_user: dict = Depends(get_current_user)):
    return {
        "trade_summary": {
            "total_trades": len([t for t in trades_db if t["trader_id"] == current_user["id"]]),
            "successful_trades": len([t for t in trades_db if t["trader_id"] == current_user["id"] and t["status"] == "confirmed"]),
            "pending_trades": len([t for t in trades_db if t["trader_id"] == current_user["id"] and t["status"] == "pending"])
        },
        "performance_metrics": {
            "win_rate": 0.75,
            "avg_trade_size": 50000,
            "total_volume": 1250000
        }
    }

# Compliance Routes
@app.get("/compliance/status", tags=["Compliance"])
async def get_compliance_status(current_user: dict = Depends(get_current_user)):
    return {
        "regulatory_compliance": "Compliant",
        "risk_limits": "Within Limits",
        "audit_trail": "Complete",
        "last_audit": "2024-01-15",
        "next_audit": "2024-04-15"
    }

@app.get("/compliance/reports", tags=["Compliance"])
async def get_compliance_reports(current_user: dict = Depends(get_current_user)):
    return {
        "regulatory_reports": [
            {"name": "Daily Risk Report", "status": "Generated", "date": "2024-01-15"},
            {"name": "Monthly Compliance Report", "status": "Pending", "date": "2024-01-31"},
            {"name": "Quarterly Audit Report", "status": "In Progress", "date": "2024-03-31"}
        ],
        "audit_trail": {
            "last_login": datetime.now().isoformat(),
            "session_duration": "2h 15m",
            "actions_taken": 45
        }
    }

# Dashboard Routes
@app.get("/dashboard/stats", tags=["Dashboard"])
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    user_trades = [trade for trade in trades_db if trade["trader_id"] == current_user["id"]]
    user_positions = [pos for key, pos in portfolio_db.items() if key.startswith(current_user["id"])]
    
    return {
        "total_trades": len(user_trades),
        "total_volume": sum(trade["quantity"] * trade["price"] for trade in user_trades),
        "total_pnl": sum(pos.unrealized_pnl for pos in user_positions),
        "risk_exposure": sum(pos.market_value for pos in user_positions) * 0.05,
        "active_positions": len(user_positions)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)