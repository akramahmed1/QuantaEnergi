"""
GraphQL schema for QuantaEnergi API using Strawberry
Provides alternative to REST API for complex queries and real-time data
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

import strawberry
from strawberry.types import Info
from strawberry.fastapi import GraphQLRouter

from app.schemas.base import (
    TradeStatus, TradeType, CommodityType, RiskLevel, 
    ComplianceRegion, UserRole, Currency
)


# GraphQL Types
@strawberry.type
class Trade:
    """GraphQL Trade type"""
    id: UUID
    trade_id: str
    trade_type: TradeType
    commodity_type: CommodityType
    quantity: Decimal
    price: Decimal
    currency: Currency
    counterparty: str
    trade_date: datetime
    settlement_date: datetime
    status: TradeStatus
    region: ComplianceRegion
    is_sharia_compliant: bool
    risk_level: RiskLevel
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]
    metadata: str  # JSON string representation


@strawberry.type
class MarketPrice:
    """GraphQL Market Price type"""
    commodity: CommodityType
    price: Decimal
    change: str
    change_percentage: Decimal
    volume: int
    source: str
    timestamp: datetime
    region: ComplianceRegion


@strawberry.type
class PortfolioPosition:
    """GraphQL Portfolio Position type"""
    commodity: CommodityType
    quantity: Decimal
    avg_price: Decimal
    current_price: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal
    weight: Decimal


@strawberry.type
class Portfolio:
    """GraphQL Portfolio type"""
    id: UUID
    name: str
    total_value: Decimal
    cash: Decimal
    invested: Decimal
    daily_change: Decimal
    daily_change_amount: Decimal
    monthly_change: Decimal
    yearly_change: Decimal
    total_return: Decimal
    positions: List[PortfolioPosition]
    allocation: str  # JSON string representation
    risk_metrics: str  # JSON string representation
    created_at: datetime
    updated_at: Optional[datetime]


@strawberry.type
class VaRCalculation:
    """GraphQL VaR Calculation type"""
    portfolio_id: UUID
    confidence_level: Decimal
    time_horizon: int
    var_value: Decimal
    expected_shortfall: Decimal
    calculation_method: str
    calculation_date: datetime


@strawberry.type
class TradingSignal:
    """GraphQL Trading Signal type"""
    id: int
    signal: str
    commodity: CommodityType
    confidence: Decimal
    price: Decimal
    target: Decimal
    stop_loss: Decimal
    timeframe: str
    source: str
    timestamp: datetime
    risk: RiskLevel
    volume: str
    trend: str
    esg_impact: str


@strawberry.type
class ESGMetrics:
    """GraphQL ESG Metrics type"""
    overall_esg_score: Decimal
    environmental_score: Decimal
    social_score: Decimal
    governance_score: Decimal
    carbon_offset: Decimal
    renewable_ratio: Decimal
    sustainability_score: Decimal
    climate_risk_score: Decimal
    social_impact_score: Decimal
    governance_quality: Decimal
    esg_trend: str
    esg_rank: str
    carbon_intensity: Decimal
    water_efficiency: Decimal
    waste_reduction: Decimal
    diversity_score: Decimal
    labor_rights: Decimal
    board_independence: Decimal
    executive_compensation: Decimal
    shareholder_rights: Decimal
    timestamp: datetime


@strawberry.type
class WeatherData:
    """GraphQL Weather Data type"""
    location: str  # JSON string representation
    temp: Decimal
    humidity: int
    description: str
    wind_speed: Decimal
    pressure: int
    visibility: int
    timestamp: datetime
    source: str


@strawberry.type
class RenewableEnergyData:
    """GraphQL Renewable Energy Data type"""
    wind: int
    solar: int
    hydro: int
    biomass: int
    geothermal: int
    total: int
    efficiency: Decimal
    carbon_savings: int
    timestamp: datetime


# Input Types
@strawberry.input
class TradeFilter:
    """Input filter for trade queries"""
    trade_type: Optional[TradeType] = None
    commodity_type: Optional[CommodityType] = None
    status: Optional[TradeStatus] = None
    region: Optional[ComplianceRegion] = None
    is_sharia_compliant: Optional[bool] = None
    counterparty: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


@strawberry.input
class PortfolioFilter:
    """Input filter for portfolio queries"""
    user_id: Optional[UUID] = None
    name: Optional[str] = None


@strawberry.input
class VaRCalculationInput:
    """Input for VaR calculation"""
    portfolio_id: UUID
    confidence_level: Decimal = strawberry.field(default=Decimal("0.95"))
    time_horizon: int = strawberry.field(default=1)
    calculation_method: str = strawberry.field(default="monte_carlo")


@strawberry.input
class TradingSignalFilter:
    """Input filter for trading signals"""
    commodity: Optional[CommodityType] = None
    confidence_min: Optional[Decimal] = None
    signal_type: Optional[str] = None
    risk_level: Optional[RiskLevel] = None


# Pagination Types
@strawberry.type
class PageInfo:
    """GraphQL pagination info"""
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str]
    end_cursor: Optional[str]


@strawberry.type
class TradeConnection:
    """GraphQL trade connection with pagination"""
    edges: List["TradeEdge"]
    page_info: PageInfo
    total_count: int


@strawberry.type
class TradeEdge:
    """GraphQL trade edge"""
    node: Trade
    cursor: str


# Resolvers
@strawberry.type
class Query:
    """GraphQL Query root type"""
    
    @strawberry.field
    async def trades(
        self,
        info: Info,
        filter: Optional[TradeFilter] = None,
        first: int = 20,
        after: Optional[str] = None
    ) -> TradeConnection:
        """
        Query trades with filtering and pagination
        
        Args:
            filter: Optional trade filter criteria
            first: Number of trades to return
            after: Cursor for pagination
            
        Returns:
            TradeConnection with paginated results
        """
        # This would be implemented with actual database queries
        # For now, returning mock data
        from app.services.trade_service import TradeService
        
        trade_service = TradeService()
        trades, total_count, has_next = await trade_service.get_trades_paginated(
            filter=filter,
            limit=first,
            offset=int(after) if after else 0
        )
        
        edges = [
            TradeEdge(
                node=Trade(
                    id=trade.id,
                    trade_id=trade.trade_id,
                    trade_type=trade.trade_type,
                    commodity_type=trade.commodity_type,
                    quantity=trade.quantity,
                    price=trade.price,
                    currency=trade.currency,
                    counterparty=trade.counterparty,
                    trade_date=trade.trade_date,
                    settlement_date=trade.settlement_date,
                    status=trade.status,
                    region=trade.region,
                    is_sharia_compliant=trade.is_sharia_compliant,
                    risk_level=trade.risk_level,
                    created_by=trade.created_by,
                    created_at=trade.created_at,
                    updated_at=trade.updated_at,
                    metadata=trade.metadata
                ),
                cursor=str(i)
            )
            for i, trade in enumerate(trades)
        ]
        
        page_info = PageInfo(
            has_next_page=has_next,
            has_previous_page=bool(after),
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None
        )
        
        return TradeConnection(
            edges=edges,
            page_info=page_info,
            total_count=total_count
        )
    
    @strawberry.field
    async def trade(self, info: Info, trade_id: str) -> Optional[Trade]:
        """Get a specific trade by ID"""
        from app.services.trade_service import TradeService
        
        trade_service = TradeService()
        trade = await trade_service.get_trade_by_id(trade_id)
        
        if not trade:
            return None
            
        return Trade(
            id=trade.id,
            trade_id=trade.trade_id,
            trade_type=trade.trade_type,
            commodity_type=trade.commodity_type,
            quantity=trade.quantity,
            price=trade.price,
            currency=trade.currency,
            counterparty=trade.counterparty,
            trade_date=trade.trade_date,
            settlement_date=trade.settlement_date,
            status=trade.status,
            region=trade.region,
            is_sharia_compliant=trade.is_sharia_compliant,
            risk_level=trade.risk_level,
            created_by=trade.created_by,
            created_at=trade.created_at,
            updated_at=trade.updated_at,
            metadata=trade.metadata
        )
    
    @strawberry.field
    async def portfolios(
        self,
        info: Info,
        filter: Optional[PortfolioFilter] = None
    ) -> List[Portfolio]:
        """Query portfolios with filtering"""
        from app.services.portfolio_service import PortfolioService
        
        portfolio_service = PortfolioService()
        portfolios = await portfolio_service.get_portfolios(filter=filter)
        
        return [
            Portfolio(
                id=portfolio.id,
                name=portfolio.name,
                total_value=portfolio.total_value,
                cash=portfolio.cash,
                invested=portfolio.invested,
                daily_change=portfolio.daily_change,
                daily_change_amount=portfolio.daily_change_amount,
                monthly_change=portfolio.monthly_change,
                yearly_change=portfolio.yearly_change,
                total_return=portfolio.total_return,
                positions=[
                    PortfolioPosition(
                        commodity=pos.commodity,
                        quantity=pos.quantity,
                        avg_price=pos.avg_price,
                        current_price=pos.current_price,
                        market_value=pos.market_value,
                        unrealized_pnl=pos.unrealized_pnl,
                        weight=pos.weight
                    )
                    for pos in portfolio.positions
                ],
                allocation=portfolio.allocation,
                risk_metrics=portfolio.risk_metrics,
                created_at=portfolio.created_at,
                updated_at=portfolio.updated_at
            )
            for portfolio in portfolios
        ]
    
    @strawberry.field
    async def market_prices(
        self,
        info: Info,
        region: Optional[ComplianceRegion] = None,
        commodities: Optional[List[CommodityType]] = None
    ) -> List[MarketPrice]:
        """Get current market prices"""
        from app.services.market_data_service import MarketDataService
        
        market_service = MarketDataService()
        prices = await market_service.get_market_prices(
            region=region,
            commodities=commodities
        )
        
        return [
            MarketPrice(
                commodity=price.commodity,
                price=price.price,
                change=price.change,
                change_percentage=price.change_percentage,
                volume=price.volume,
                source=price.source,
                timestamp=price.timestamp,
                region=price.region
            )
            for price in prices
        ]
    
    @strawberry.field
    async def trading_signals(
        self,
        info: Info,
        filter: Optional[TradingSignalFilter] = None,
        limit: int = 10
    ) -> List[TradingSignal]:
        """Get trading signals with filtering"""
        from app.services.trading_signals_service import TradingSignalsService
        
        signals_service = TradingSignalsService()
        signals = await signals_service.get_signals(
            filter=filter,
            limit=limit
        )
        
        return [
            TradingSignal(
                id=signal.id,
                signal=signal.signal,
                commodity=signal.commodity,
                confidence=signal.confidence,
                price=signal.price,
                target=signal.target,
                stop_loss=signal.stop_loss,
                timeframe=signal.timeframe,
                source=signal.source,
                timestamp=signal.timestamp,
                risk=signal.risk,
                volume=signal.volume,
                trend=signal.trend,
                esg_impact=signal.esg_impact
            )
            for signal in signals
        ]
    
    @strawberry.field
    async def esg_metrics(self, info: Info) -> ESGMetrics:
        """Get current ESG metrics"""
        from app.services.esg_service import ESGService
        
        esg_service = ESGService()
        metrics = await esg_service.get_current_metrics()
        
        return ESGMetrics(
            overall_esg_score=metrics.overall_esg_score,
            environmental_score=metrics.environmental_score,
            social_score=metrics.social_score,
            governance_score=metrics.governance_score,
            carbon_offset=metrics.carbon_offset,
            renewable_ratio=metrics.renewable_ratio,
            sustainability_score=metrics.sustainability_score,
            climate_risk_score=metrics.climate_risk_score,
            social_impact_score=metrics.social_impact_score,
            governance_quality=metrics.governance_quality,
            esg_trend=metrics.esg_trend,
            esg_rank=metrics.esg_rank,
            carbon_intensity=metrics.carbon_intensity,
            water_efficiency=metrics.water_efficiency,
            waste_reduction=metrics.waste_reduction,
            diversity_score=metrics.diversity_score,
            labor_rights=metrics.labor_rights,
            board_independence=metrics.board_independence,
            executive_compensation=metrics.executive_compensation,
            shareholder_rights=metrics.shareholder_rights,
            timestamp=metrics.timestamp
        )
    
    @strawberry.field
    async def weather_data(
        self,
        info: Info,
        lat: float = 33.44,
        lon: float = -94.04
    ) -> WeatherData:
        """Get current weather data"""
        from app.services.weather_service import WeatherService
        
        weather_service = WeatherService()
        weather = await weather_service.get_current_weather(lat, lon)
        
        return WeatherData(
            location=weather.location,
            temp=weather.temp,
            humidity=weather.humidity,
            description=weather.description,
            wind_speed=weather.wind_speed,
            pressure=weather.pressure,
            visibility=weather.visibility,
            timestamp=weather.timestamp,
            source=weather.source
        )
    
    @strawberry.field
    async def renewable_energy_data(self, info: Info) -> RenewableEnergyData:
        """Get renewable energy production data"""
        from app.services.renewable_energy_service import RenewableEnergyService
        
        energy_service = RenewableEnergyService()
        data = await energy_service.get_current_data()
        
        return RenewableEnergyData(
            wind=data.wind,
            solar=data.solar,
            hydro=data.hydro,
            biomass=data.biomass,
            geothermal=data.geothermal,
            total=data.total,
            efficiency=data.efficiency,
            carbon_savings=data.carbon_savings,
            timestamp=data.timestamp
        )


# Mutations
@strawberry.type
class Mutation:
    """GraphQL Mutation root type"""
    
    @strawberry.mutation
    async def calculate_var(
        self,
        info: Info,
        input: VaRCalculationInput
    ) -> VaRCalculation:
        """Calculate Value at Risk for a portfolio"""
        from app.services.risk_calculator_service import RiskCalculatorService
        
        risk_service = RiskCalculatorService()
        var_result = await risk_service.calculate_var(
            portfolio_id=input.portfolio_id,
            confidence_level=input.confidence_level,
            time_horizon=input.time_horizon,
            method=input.calculation_method
        )
        
        return VaRCalculation(
            portfolio_id=var_result.portfolio_id,
            confidence_level=var_result.confidence_level,
            time_horizon=var_result.time_horizon,
            var_value=var_result.var_value,
            expected_shortfall=var_result.expected_shortfall,
            calculation_method=var_result.calculation_method,
            calculation_date=var_result.calculation_date
        )
    
    @strawberry.mutation
    async def create_trade(
        self,
        info: Info,
        trade_data: str  # JSON string representation
    ) -> Trade:
        """Create a new trade"""
        from app.services.trade_service import TradeService
        
        trade_service = TradeService()
        trade = await trade_service.create_trade(trade_data)
        
        return Trade(
            id=trade.id,
            trade_id=trade.trade_id,
            trade_type=trade.trade_type,
            commodity_type=trade.commodity_type,
            quantity=trade.quantity,
            price=trade.price,
            currency=trade.currency,
            counterparty=trade.counterparty,
            trade_date=trade.trade_date,
            settlement_date=trade.settlement_date,
            status=trade.status,
            region=trade.region,
            is_sharia_compliant=trade.is_sharia_compliant,
            risk_level=trade.risk_level,
            created_by=trade.created_by,
            created_at=trade.created_at,
            updated_at=trade.updated_at,
            metadata=trade.metadata
        )


# Subscriptions
@strawberry.type
class Subscription:
    """GraphQL Subscription root type"""
    
    @strawberry.subscription
    async def trade_updates(
        self,
        info: Info,
        trade_id: Optional[str] = None
    ) -> Trade:
        """Subscribe to trade updates"""
        from app.services.websocket_service import WebSocketService
        
        websocket_service = WebSocketService()
        
        async for trade_update in websocket_service.subscribe_to_trade_updates(
            trade_id=trade_id
        ):
            yield Trade(
                id=trade_update.id,
                trade_id=trade_update.trade_id,
                trade_type=trade_update.trade_type,
                commodity_type=trade_update.commodity_type,
                quantity=trade_update.quantity,
                price=trade_update.price,
                currency=trade_update.currency,
                counterparty=trade_update.counterparty,
                trade_date=trade_update.trade_date,
                settlement_date=trade_update.settlement_date,
                status=trade_update.status,
                region=trade_update.region,
                is_sharia_compliant=trade_update.is_sharia_compliant,
                risk_level=trade_update.risk_level,
                created_by=trade_update.created_by,
                created_at=trade_update.created_at,
                updated_at=trade_update.updated_at,
                metadata=trade_update.metadata
            )
    
    @strawberry.subscription
    async def market_price_updates(
        self,
        info: Info,
        commodities: Optional[List[CommodityType]] = None
    ) -> MarketPrice:
        """Subscribe to market price updates"""
        from app.services.websocket_service import WebSocketService
        
        websocket_service = WebSocketService()
        
        async for price_update in websocket_service.subscribe_to_market_updates(
            commodities=commodities
        ):
            yield MarketPrice(
                commodity=price_update.commodity,
                price=price_update.price,
                change=price_update.change,
                change_percentage=price_update.change_percentage,
                volume=price_update.volume,
                source=price_update.source,
                timestamp=price_update.timestamp,
                region=price_update.region
            )


# Create GraphQL Schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)

# Create GraphQL Router for FastAPI
graphql_router = GraphQLRouter(schema, path="/graphql")
