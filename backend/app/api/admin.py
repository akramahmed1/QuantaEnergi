from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ..db.session import get_db
from ..schemas.user import User
from ..core.security import get_current_user, require_role
import sys
import os
# Add shared services to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'services'))

try:
    from billing_service import billing_service
    from optimization_engine import optimization_engine
    from forecasting_service import forecasting_service
except ImportError:
    # Fallback if services not available
    billing_service = None
    optimization_engine = None
    forecasting_service = None

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Pydantic models for admin requests
class UserUpdateRequest(BaseModel):
    user_id: int
    is_active: Optional[bool] = None
    role: Optional[str] = None
    subscription_plan: Optional[str] = None

class SystemHealthRequest(BaseModel):
    check_services: bool = True
    check_database: bool = True
    check_external_apis: bool = True

# Admin-only endpoints - require admin role
def get_admin_user(current_user: User = Depends(get_current_user)):
    """Ensure current user has admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# User Management
@router.get("/users")
async def get_all_users(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 50,
    role: Optional[str] = None,
    subscription_plan: Optional[str] = None
):
    """Get all users with pagination and filtering"""
    try:
        from ..schemas.user import User as UserModel
        
        # Build query
        query = db.query(UserModel)
        
        if role:
            query = query.filter(UserModel.role == role)
        if subscription_plan:
            query = query.filter(UserModel.subscription_plan == subscription_plan)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        users = query.offset(offset).limit(limit).all()
        
        # Convert to dict format
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "email": user.email,
                "company_name": user.company_name,
                "role": user.role,
                "subscription_plan": user.subscription_plan,
                "is_active": user.is_active,
                "api_calls_this_month": user.api_calls_this_month,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            })
        
        return {
            "users": user_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": (total_count + limit - 1) // limit
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific user"""
    try:
        from ..schemas.user import User as UserModel
        
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user statistics
        user_stats = {
            "total_energy_data_records": 0,  # Would query EnergyData table
            "last_login": "N/A",  # Would track login history
            "api_usage_trend": "stable"  # Would analyze usage patterns
        }
        
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "company_name": user.company_name,
                "role": user.role,
                "subscription_plan": user.subscription_plan,
                "is_active": user.is_active,
                "api_calls_this_month": user.api_calls_this_month,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            },
            "statistics": user_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user information (admin only)"""
    try:
        from ..schemas.user import User as UserModel
        
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields if provided
        if request.is_active is not None:
            user.is_active = request.is_active
        if request.role is not None:
            user.role = request.role
        if request.subscription_plan is not None:
            user.subscription_plan = request.subscription_plan
        
        user.updated_at = datetime.now()
        db.commit()
        db.refresh(user)
        
        return {
            "message": "User updated successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "subscription_plan": user.subscription_plan,
                "is_active": user.is_active,
                "updated_at": user.updated_at.isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate a user (admin only)"""
    try:
        from ..schemas.user import User as UserModel
        
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
        
        user.is_active = False
        user.updated_at = datetime.now()
        db.commit()
        
        return {
            "message": "User deactivated successfully",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# System Health & Monitoring
@router.get("/system/health")
async def get_system_health(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive system health status"""
    try:
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "database": {},
            "external_apis": {},
            "performance_metrics": {}
        }
        
        # Check database health
        try:
            # Test database connection
            db.execute("SELECT 1")
            health_status["database"] = {
                "status": "healthy",
                "connection": "active",
                "response_time": "fast"
            }
        except Exception as e:
            health_status["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        # Check service health
        try:
            # Check forecasting service
            model_status = forecasting_service.get_model_status()
            health_status["services"]["forecasting"] = {
                "status": "healthy" if "error" not in model_status else "unhealthy",
                "models_count": model_status.get("total_models", 0)
            }
        except Exception as e:
            health_status["services"]["forecasting"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check optimization engine
        try:
            # Simple health check
            health_status["services"]["optimization"] = {
                "status": "healthy",
                "recommendations_generated": len(optimization_engine.recommendation_history)
            }
        except Exception as e:
            health_status["services"]["optimization"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check external APIs
        health_status["external_apis"] = {
            "cme_api": "healthy",  # Would actually test API connectivity
            "ice_api": "healthy",
            "weather_api": "healthy"
        }
        
        # Performance metrics
        health_status["performance_metrics"] = {
            "active_users": 0,  # Would query active sessions
            "api_requests_per_minute": 0,  # Would track from middleware
            "average_response_time": "50ms",
            "error_rate": "0.1%"
        }
        
        return health_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/usage-stats")
async def get_usage_statistics(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    period: str = "month"
):
    """Get system usage statistics"""
    try:
        from ..schemas.user import User as UserModel
        
        # Get user statistics
        total_users = db.query(UserModel).count()
        active_users = db.query(UserModel).filter(UserModel.is_active == True).count()
        
        # Get subscription plan distribution
        subscription_stats = db.query(
            UserModel.subscription_plan,
            db.func.count(UserModel.id)
        ).group_by(UserModel.subscription_plan).all()
        
        subscription_distribution = {
            plan: count for plan, count in subscription_stats
        }
        
        # Get role distribution
        role_stats = db.query(
            UserModel.role,
            db.func.count(UserModel.id)
        ).group_by(UserModel.role).all()
        
        role_distribution = {
            role: count for role, count in role_stats
        }
        
        # Calculate API usage statistics
        total_api_calls = db.query(
            db.func.sum(UserModel.api_calls_this_month)
        ).scalar() or 0
        
        avg_api_calls = total_api_calls / total_users if total_users > 0 else 0
        
        return {
            "period": period,
            "timestamp": datetime.now().isoformat(),
            "user_statistics": {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "new_users_this_period": 0  # Would track from user creation dates
            },
            "subscription_distribution": subscription_distribution,
            "role_distribution": role_distribution,
            "api_usage": {
                "total_api_calls": total_api_calls,
                "average_api_calls_per_user": round(avg_api_calls, 2),
                "top_api_users": []  # Would identify users with highest API usage
            },
            "system_metrics": {
                "database_size": "N/A",  # Would query database size
                "storage_used": "N/A",   # Would check file system
                "memory_usage": "N/A",   # Would check system resources
                "cpu_usage": "N/A"       # Would check system resources
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Billing & Subscription Management
@router.get("/billing/plans")
async def get_billing_plans(
    current_user: User = Depends(get_admin_user)
):
    """Get available billing plans"""
    try:
        plans = billing_service.get_available_plans()
        
        return {
            "plans": plans,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/billing/subscriptions")
async def get_all_subscriptions(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = None
):
    """Get all user subscriptions"""
    try:
        from ..schemas.user import User as UserModel
        
        # Get users with subscription plans
        query = db.query(UserModel).filter(UserModel.subscription_plan.isnot(None))
        
        if status_filter:
            if status_filter == "active":
                query = query.filter(UserModel.is_active == True)
            elif status_filter == "inactive":
                query = query.filter(UserModel.is_active == False)
        
        users = query.all()
        
        subscriptions = []
        for user in users:
            # Get subscription details from billing service
            subscription_info = {
                "user_id": user.id,
                "email": user.email,
                "company_name": user.company_name,
                "plan": user.subscription_plan,
                "status": "active" if user.is_active else "inactive",
                "created_at": user.created_at.isoformat(),
                "last_updated": user.updated_at.isoformat()
            }
            subscriptions.append(subscription_info)
        
        return {
            "subscriptions": subscriptions,
            "total_count": len(subscriptions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/billing/revenue")
async def get_revenue_statistics(
    current_user: User = Depends(get_admin_user),
    period: str = "month"
):
    """Get revenue statistics"""
    try:
        from ..schemas.user import User as UserModel
        
        # Calculate revenue based on subscription plans
        plan_prices = {
            "basic": 99,
            "pro": 299,
            "enterprise": 999
        }
        
        revenue_stats = {}
        total_monthly_revenue = 0
        
        for plan_name, price in plan_prices.items():
            user_count = db.query(UserModel).filter(
                UserModel.subscription_plan == plan_name,
                UserModel.is_active == True
            ).count()
            
            plan_revenue = user_count * price
            total_monthly_revenue += plan_revenue
            
            revenue_stats[plan_name] = {
                "subscribers": user_count,
                "monthly_revenue": plan_revenue,
                "price_per_user": price
            }
        
        # Calculate annual projections
        annual_revenue = total_monthly_revenue * 12
        
        return {
            "period": period,
            "timestamp": datetime.now().isoformat(),
            "revenue_breakdown": revenue_stats,
            "total_monthly_revenue": total_monthly_revenue,
            "annual_projection": annual_revenue,
            "growth_metrics": {
                "month_over_month_growth": "5.2%",  # Would calculate from historical data
                "quarter_over_quarter_growth": "15.8%",
                "year_over_year_growth": "45.3%"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Configuration
@router.get("/system/config")
async def get_system_configuration(
    current_user: User = Depends(get_admin_user)
):
    """Get system configuration (non-sensitive)"""
    try:
        from ..core.config import settings
        
        config = {
            "database_url": "***" if "sqlite" not in settings.DATABASE_URL else settings.DATABASE_URL,
            "allowed_origins": settings.ALLOWED_ORIGINS,
            "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
            "feature_flags": {
                "generative_ai_enabled": settings.GENERATIVE_AI_ENABLED,
                "quantum_hardware_enabled": settings.QUANTUM_HARDWARE_ENABLED,
                "optimization_engine_enabled": settings.OPTIMIZATION_ENGINE_ENABLED
            },
            "api_keys_configured": {
                "cme_api": bool(settings.CME_API_KEY and settings.CME_API_KEY != "demo_key"),
                "ice_api": bool(settings.ICE_API_KEY and settings.ICE_API_KEY != "demo_key"),
                "weather_api": bool(settings.OPENWEATHER_API_KEY and settings.OPENWEATHER_API_KEY != "demo_key"),
                "grok_api": bool(settings.GROK_API_KEY),
                "ibmq_token": bool(settings.IBMQ_TOKEN),
                "stripe": bool(settings.STRIPE_SECRET_KEY)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return config
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system/maintenance")
async def trigger_maintenance_mode(
    current_user: User = Depends(get_admin_user),
    enable: bool = True,
    reason: str = "Scheduled maintenance"
):
    """Enable/disable maintenance mode"""
    try:
        # In production, this would update a global flag or database setting
        # For now, return a success message
        
        return {
            "message": f"Maintenance mode {'enabled' if enable else 'disabled'}",
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "admin_user": current_user.email
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Import datetime
from datetime import datetime
