"""
US Power & Gas Market Data API Endpoints.

This module provides comprehensive API access to:
- PJM market data (LMPs, FTRs, scheduling)
- REC management and trading
- Henry Hub futures and basis trading
- Natural gas storage and pipeline flows
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel

from ...services.market_data.pjm_service import PJMService, PJMMarketType, PJMDataType
from ...services.market_data.rec_service import RECService, RECRegistry, RECStatus, RECFuelType
from ...services.market_data.henry_hub_service import HenryHubService, GasHub, BasisType
from ...api.dependencies import get_current_user, require_trader
from ...db.schemas import User

router = APIRouter()

# Pydantic Models for API Requests/Responses
class PJMDataRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    nodes: Optional[List[str]] = None
    market_type: str = "real_time"
    data_type: str = "lmp"

class RECQueryRequest(BaseModel):
    owner_id: str
    registry: Optional[str] = None
    status: Optional[str] = None
    fuel_type: Optional[str] = None
    vintage_year: Optional[int] = None

class RECTransferRequest(BaseModel):
    rec_ids: List[str]
    from_owner: str
    to_owner: str
    price_per_mwh: float
    transaction_type: str = "sale"

class RECRetirementRequest(BaseModel):
    rec_ids: List[str]
    owner_id: str
    retirement_reason: str
    compliance_period: str
    registry: str

class HenryHubRequest(BaseModel):
    contract_month: Optional[str] = None
    contract_year: Optional[int] = None
    limit: int = 20

class BasisRequest(BaseModel):
    hub: str
    contract_month: Optional[str] = None
    contract_year: Optional[int] = None

class BasisSpreadRequest(BaseModel):
    hub1: str
    hub2: str
    contract_month: str
    contract_year: int

# PJM Market Data Endpoints
@router.get("/pjm/lmp", response_model=Dict[str, Any])
async def get_pjm_lmp_data(
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    nodes: Optional[str] = Query(None),
    market_type: str = Query("real_time"),
    current_user: User = Depends(require_trader)
):
    """Get PJM LMP data for specified time range and nodes."""
    
    try:
        # Parse nodes if provided
        node_list = nodes.split(",") if nodes else None
        
        # Convert market type string to enum
        market_enum = PJMMarketType(market_type)
        
        async with PJMService() as service:
            lmp_data = await service.get_lmp_data(
                start_time=start_time,
                end_time=end_time,
                nodes=node_list,
                market_type=market_enum
            )
            
            # Convert to serializable format
            serialized_data = []
            for item in lmp_data:
                serialized_data.append({
                    "timestamp": item.timestamp.isoformat(),
                    "node_id": item.node_id,
                    "node_name": item.node_name,
                    "lmp": item.lmp,
                    "congestion": item.congestion,
                    "marginal_loss": item.marginal_loss,
                    "energy": item.energy,
                    "market_type": item.market_type.value,
                    "zone": item.zone,
                    "region": item.region
                })
            
            return {
                "success": True,
                "data": serialized_data,
                "count": len(serialized_data),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "market_type": market_type
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get PJM LMP data: {str(e)}")

@router.get("/pjm/ftr", response_model=Dict[str, Any])
async def get_pjm_ftr_data(
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    source_nodes: Optional[str] = Query(None),
    sink_nodes: Optional[str] = Query(None),
    current_user: User = Depends(require_trader)
):
    """Get PJM FTR data for specified time range and nodes."""
    
    try:
        # Parse node lists if provided
        source_list = source_nodes.split(",") if source_nodes else None
        sink_list = sink_nodes.split(",") if sink_nodes else None
        
        async with PJMService() as service:
            ftr_data = await service.get_ftr_data(
                start_time=start_time,
                end_time=end_time,
                source_nodes=source_list,
                sink_nodes=sink_list
            )
            
            # Convert to serializable format
            serialized_data = []
            for item in ftr_data:
                serialized_data.append({
                    "timestamp": item.timestamp.isoformat(),
                    "source_node": item.source_node,
                    "sink_node": item.sink_node,
                    "ftr_id": item.ftr_id,
                    "megawatt": item.megawatt,
                    "price": item.price,
                    "auction_type": item.auction_type,
                    "period": item.period,
                    "status": item.status
                })
            
            return {
                "success": True,
                "data": serialized_data,
                "count": len(serialized_data),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get PJM FTR data: {str(e)}")

@router.get("/pjm/schedule", response_model=Dict[str, Any])
async def get_pjm_schedule_data(
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    units: Optional[str] = Query(None),
    market_type: str = Query("day_ahead"),
    current_user: User = Depends(require_trader)
):
    """Get PJM scheduling data for specified time range and units."""
    
    try:
        # Parse units if provided
        unit_list = units.split(",") if units else None
        
        # Convert market type string to enum
        market_enum = PJMMarketType(market_type)
        
        async with PJMService() as service:
            schedule_data = await service.get_schedule_data(
                start_time=start_time,
                end_time=end_time,
                units=unit_list,
                market_type=market_enum
            )
            
            # Convert to serializable format
            serialized_data = []
            for item in schedule_data:
                serialized_data.append({
                    "timestamp": item.timestamp.isoformat(),
                    "unit_id": item.unit_id,
                    "unit_name": item.unit_name,
                    "megawatt": item.megawatt,
                    "schedule_type": item.schedule_type,
                    "market_type": item.market_type.value,
                    "zone": item.zone,
                    "fuel_type": item.fuel_type
                })
            
            return {
                "success": True,
                "data": serialized_data,
                "count": len(serialized_data),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "market_type": market_type
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get PJM schedule data: {str(e)}")

@router.get("/pjm/market-summary", response_model=Dict[str, Any])
async def get_pjm_market_summary(
    date: date = Query(...),
    current_user: User = Depends(require_trader)
):
    """Get daily PJM market summary for specified date."""
    
    try:
        async with PJMService() as service:
            summary = await service.get_market_summary(date)
            return {
                "success": True,
                "data": summary
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get PJM market summary: {str(e)}")

# REC Management Endpoints
@router.post("/rec/query", response_model=Dict[str, Any])
async def query_recs(
    request: RECQueryRequest,
    current_user: User = Depends(require_trader)
):
    """Query RECs based on specified criteria."""
    
    try:
        service = RECService()
        
        # Convert string parameters to enums
        registry = RECRegistry(request.registry) if request.registry else None
        status = RECStatus(request.status) if request.status else None
        fuel_type = RECFuelType(request.fuel_type) if request.fuel_type else None
        
        recs = await service.get_recs_by_owner(
            owner_id=request.owner_id,
            registry=registry,
            status=status,
            fuel_type=fuel_type,
            vintage_year=request.vintage_year
        )
        
        # Convert to serializable format
        serialized_recs = []
        for rec in recs:
            serialized_recs.append({
                "rec_id": rec.rec_id,
                "registry": rec.registry.value,
                "generator_id": rec.generator_id,
                "generator_name": rec.generator_name,
                "fuel_type": rec.fuel_type.value,
                "vintage": rec.vintage.value,
                "vintage_year": rec.vintage_year,
                "megawatt_hours": rec.megawatt_hours,
                "issue_date": rec.issue_date.isoformat(),
                "status": rec.status.value,
                "current_owner": rec.current_owner,
                "price": rec.price,
                "location": rec.location,
                "state": rec.state,
                "region": rec.region,
                "carbon_offset": rec.carbon_offset
            })
        
        return {
            "success": True,
            "data": serialized_recs,
            "count": len(serialized_recs),
            "owner_id": request.owner_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query RECs: {str(e)}")

@router.post("/rec/transfer", response_model=Dict[str, Any])
async def transfer_recs(
    request: RECTransferRequest,
    current_user: User = Depends(require_trader)
):
    """Transfer RECs between owners."""
    
    try:
        service = RECService()
        
        transaction = await service.transfer_recs(
            rec_ids=request.rec_ids,
            from_owner=request.from_owner,
            to_owner=request.to_owner,
            price_per_mwh=request.price_per_mwh,
            transaction_type=request.transaction_type
        )
        
        return {
            "success": True,
            "data": {
                "transaction_id": transaction.transaction_id,
                "rec_id": transaction.rec_id,
                "from_owner": transaction.from_owner,
                "to_owner": transaction.to_owner,
                "transaction_type": transaction.transaction_type,
                "megawatt_hours": transaction.megawatt_hours,
                "price_per_mwh": transaction.price_per_mwh,
                "total_value": transaction.total_value,
                "transaction_date": transaction.transaction_date.isoformat(),
                "status": transaction.status,
                "registry": transaction.registry.value
            },
            "message": "REC transfer completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transfer RECs: {str(e)}")

@router.post("/rec/retire", response_model=Dict[str, Any])
async def retire_recs(
    request: RECRetirementRequest,
    current_user: User = Depends(require_trader)
):
    """Retire RECs for compliance or voluntary purposes."""
    
    try:
        service = RECService()
        
        # Convert string to enum
        registry = RECRegistry(request.registry)
        
        retirement_data = await service.retire_recs(
            rec_ids=request.rec_ids,
            owner_id=request.owner_id,
            retirement_reason=request.retirement_reason,
            compliance_period=request.compliance_period,
            registry=registry
        )
        
        return {
            "success": True,
            "data": retirement_data,
            "message": "RECs retired successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retire RECs: {str(e)}")

@router.get("/rec/esg-metrics", response_model=Dict[str, Any])
async def get_rec_esg_metrics(
    owner_id: str = Query(...),
    period: str = Query("current_year"),
    current_user: User = Depends(require_trader)
):
    """Get ESG metrics based on REC holdings."""
    
    try:
        service = RECService()
        
        esg_metrics = await service.get_esg_metrics(
            owner_id=owner_id,
            period=period
        )
        
        return {
            "success": True,
            "data": esg_metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ESG metrics: {str(e)}")

# Henry Hub Futures & Basis Trading Endpoints
@router.get("/henry-hub/futures", response_model=Dict[str, Any])
async def get_henry_hub_futures(
    contract_month: Optional[str] = Query(None),
    contract_year: Optional[int] = Query(None),
    limit: int = Query(20),
    current_user: User = Depends(require_trader)
):
    """Get Henry Hub futures data."""
    
    try:
        async with HenryHubService() as service:
            futures_data = await service.get_henry_hub_futures(
                contract_month=contract_month,
                contract_year=contract_year,
                limit=limit
            )
            
            # Convert to serializable format
            serialized_data = []
            for item in futures_data:
                serialized_data.append({
                    "contract_month": item.contract_month,
                    "contract_year": item.contract_year,
                    "symbol": item.symbol,
                    "last_price": item.last_price,
                    "bid": item.bid,
                    "ask": item.ask,
                    "volume": item.volume,
                    "open_interest": item.open_interest,
                    "high": item.high,
                    "low": item.low,
                    "settlement": item.settlement,
                    "change": item.change,
                    "change_percent": item.change_percent,
                    "timestamp": item.timestamp.isoformat(),
                    "exchange": item.exchange
                })
            
            return {
                "success": True,
                "data": serialized_data,
                "count": len(serialized_data),
                "contract_month": contract_month,
                "contract_year": contract_year
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Henry Hub futures: {str(e)}")

@router.get("/henry-hub/basis", response_model=Dict[str, Any])
async def get_basis_data(
    hub: str = Query(...),
    contract_month: Optional[str] = Query(None),
    contract_year: Optional[int] = Query(None),
    current_user: User = Depends(require_trader)
):
    """Get basis trading data for a specific hub."""
    
    try:
        # Convert string to enum
        gas_hub = GasHub(hub)
        
        async with HenryHubService() as service:
            basis_data = await service.get_basis_data(
                hub=gas_hub,
                contract_month=contract_month,
                contract_year=contract_year
            )
            
            # Convert to serializable format
            serialized_data = []
            for item in basis_data:
                serialized_data.append({
                    "hub": item.hub.value,
                    "contract_month": item.contract_month,
                    "contract_year": item.contract_year,
                    "basis": item.basis,
                    "basis_type": item.basis_type.value,
                    "volume": item.volume,
                    "open_interest": item.open_interest,
                    "last_trade": item.last_trade,
                    "timestamp": item.timestamp.isoformat(),
                    "correlation": item.correlation
                })
            
            return {
                "success": True,
                "data": serialized_data,
                "count": len(serialized_data),
                "hub": hub,
                "contract_month": contract_month,
                "contract_year": contract_year
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get basis data: {str(e)}")

@router.post("/henry-hub/basis-spread", response_model=Dict[str, Any])
async def calculate_basis_spread(
    request: BasisSpreadRequest,
    current_user: User = Depends(require_trader)
):
    """Calculate basis spread between two hubs."""
    
    try:
        async with HenryHubService() as service:
            spread_data = await service.calculate_basis_spread(
                hub1=GasHub(request.hub1),
                hub2=GasHub(request.hub2),
                contract_month=request.contract_month,
                contract_year=request.contract_year
            )
            
            return {
                "success": True,
                "data": spread_data
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate basis spread: {str(e)}")

@router.get("/henry-hub/storage", response_model=Dict[str, Any])
async def get_storage_data(
    region: str = Query("total"),
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(require_trader)
):
    """Get natural gas storage data."""
    
    try:
        async with HenryHubService() as service:
            storage_data = await service.get_storage_data(
                region=region,
                start_date=start_date,
                end_date=end_date
            )
            
            # Convert to serializable format
            serialized_data = []
            for item in storage_data:
                serialized_data.append({
                    "report_date": item.report_date.isoformat(),
                    "working_gas": item.working_gas,
                    "total_gas": item.total_gas,
                    "net_change": item.net_change,
                    "year_ago": item.year_ago,
                    "five_year_avg": item.five_year_avg,
                    "five_year_range": item.five_year_range,
                    "region": item.region,
                    "timestamp": item.timestamp.isoformat()
                })
            
            return {
                "success": True,
                "data": serialized_data,
                "count": len(serialized_data),
                "region": region,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get storage data: {str(e)}")

@router.get("/henry-hub/pipeline-flows", response_model=Dict[str, Any])
async def get_pipeline_flows(
    pipeline: Optional[str] = Query(None),
    current_user: User = Depends(require_trader)
):
    """Get pipeline flow data."""
    
    try:
        async with HenryHubService() as service:
            flow_data = await service.get_pipeline_flows(pipeline=pipeline)
            
            # Convert to serializable format
            serialized_data = []
            for item in flow_data:
                serialized_data.append({
                    "pipeline": item.pipeline,
                    "receipt_point": item.receipt_point,
                    "delivery_point": item.delivery_point,
                    "flow_rate": item.flow_rate,
                    "capacity": item.capacity,
                    "utilization": item.utilization,
                    "timestamp": item.timestamp.isoformat(),
                    "direction": item.direction
                })
            
            return {
                "success": True,
                "data": serialized_data,
                "count": len(serialized_data),
                "pipeline": pipeline
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline flows: {str(e)}")

@router.get("/henry-hub/market-summary", response_model=Dict[str, Any])
async def get_henry_hub_market_summary(
    current_user: User = Depends(require_trader)
):
    """Get comprehensive Henry Hub market summary."""
    
    try:
        async with HenryHubService() as service:
            summary = await service.get_market_summary()
            
            return {
                "success": True,
                "data": summary
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get market summary: {str(e)}")

@router.get("/henry-hub/weather-correlation", response_model=Dict[str, Any])
async def get_weather_correlation(
    hub: str = Query(...),
    days: int = Query(30),
    current_user: User = Depends(require_trader)
):
    """Get weather correlation analysis for a hub."""
    
    try:
        gas_hub = GasHub(hub)
        
        async with HenryHubService() as service:
            correlation_data = await service.get_weather_correlation(
                hub=gas_hub,
                days=days
            )
            
            return {
                "success": True,
                "data": correlation_data
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather correlation: {str(e)}")

# Market Data Health Check
@router.get("/health", response_model=Dict[str, Any])
async def market_data_health_check(
    current_user: User = Depends(require_trader)
):
    """Health check for US market data services."""
    
    try:
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "services": {
                "pjm": "healthy",
                "rec": "healthy",
                "henry_hub": "healthy"
            },
            "endpoints": {
                "pjm_lmp": "/pjm/lmp",
                "pjm_ftr": "/pjm/ftr",
                "pjm_schedule": "/pjm/schedule",
                "rec_query": "/rec/query",
                "rec_transfer": "/rec/transfer",
                "henry_hub_futures": "/henry-hub/futures",
                "basis_data": "/henry-hub/basis",
                "storage_data": "/henry-hub/storage"
            },
            "status": "healthy"
        }
        
        return health_status
        
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "unhealthy",
            "error": str(e)
        } 