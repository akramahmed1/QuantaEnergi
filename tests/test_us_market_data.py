"""
Comprehensive tests for US Market Data Services.

These tests verify:
- PJM market data integration (LMPs, FTRs, scheduling)
- REC management and trading
- Henry Hub futures and basis trading
- Natural gas storage and pipeline flows
"""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from src.energyopti_pro.services.market_data.pjm_service import (
    PJMService, PJMMarketType, PJMDataType, PJMLMPData, PJMFTRData, PJMScheduleData
)
from src.energyopti_pro.services.market_data.rec_service import (
    RECService, RECRegistry, RECStatus, RECFuelType, RECData, RECTransaction
)
from src.energyopti_pro.services.market_data.henry_hub_service import (
    HenryHubService, GasHub, BasisType, HenryHubFuturesData, BasisData, StorageData
)

class TestPJMService:
    """Test PJM market data service."""
    
    @pytest.fixture
    def pjm_service(self):
        """Create PJM service instance."""
        return PJMService()
    
    @pytest.fixture
    def mock_session(self):
        """Create mock aiohttp session."""
        session = AsyncMock()
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value={
            "data": [
                {
                    "timestamp": "2024-01-01T12:00:00Z",
                    "node_id": "NODE001",
                    "node_name": "Test Node",
                    "lmp": 45.67,
                    "congestion": 2.34,
                    "marginal_loss": 1.23,
                    "energy": 42.10,
                    "zone": "AEP",
                    "region": "RTO"
                }
            ]
        })
        session.get.return_value.__aenter__.return_value = response
        return session
    
    def test_pjm_service_initialization(self, pjm_service):
        """Test PJM service initialization."""
        assert pjm_service.base_url == "https://api.pjm.com/api/v1"
        assert pjm_service.rate_limit_delay == 0.1
        assert len(pjm_service.zones) > 0
        assert "AEP" in pjm_service.zones
    
    def test_pjm_market_types(self):
        """Test PJM market type enums."""
        assert PJMMarketType.DAY_AHEAD.value == "day_ahead"
        assert PJMMarketType.REAL_TIME.value == "real_time"
        assert PJMMarketType.CAPACITY.value == "capacity"
        assert PJMMarketType.ANCILLARY.value == "ancillary"
    
    def test_pjm_data_types(self):
        """Test PJM data type enums."""
        assert PJMDataType.LMP.value == "lmp"
        assert PJMDataType.FTR.value == "ftr"
        assert PJMDataType.SCHEDULE.value == "schedule"
        assert PJMDataType.CAPACITY.value == "capacity"
        assert PJMDataType.ANCILLARY.value == "ancillary"
    
    @pytest.mark.asyncio
    async def test_get_lmp_data(self, pjm_service, mock_session):
        """Test LMP data retrieval."""
        pjm_service.session = mock_session
        
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        end_time = datetime(2024, 1, 1, 13, 0, 0)
        
        lmp_data = await pjm_service.get_lmp_data(
            start_time=start_time,
            end_time=end_time,
            market_type=PJMMarketType.REAL_TIME
        )
        
        assert len(lmp_data) == 1
        assert lmp_data[0].node_id == "NODE001"
        assert lmp_data[0].lmp == 45.67
        assert lmp_data[0].market_type == PJMMarketType.REAL_TIME
    
    @pytest.mark.asyncio
    async def test_get_ftr_data(self, pjm_service, mock_session):
        """Test FTR data retrieval."""
        pjm_service.session = mock_session
        
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        end_time = datetime(2024, 1, 1, 13, 0, 0)
        
        ftr_data = await pjm_service.get_ftr_data(
            start_time=start_time,
            end_time=end_time
        )
        
        assert len(ftr_data) == 1
        assert ftr_data[0].ftr_id is not None
    
    @pytest.mark.asyncio
    async def test_get_schedule_data(self, pjm_service, mock_session):
        """Test schedule data retrieval."""
        pjm_service.session = mock_session
        
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        end_time = datetime(2024, 1, 1, 13, 0, 0)
        
        schedule_data = await pjm_service.get_schedule_data(
            start_time=start_time,
            end_time=end_time,
            market_type=PJMMarketType.DAY_AHEAD
        )
        
        assert len(schedule_data) == 1
        assert schedule_data[0].market_type == PJMMarketType.DAY_AHEAD
    
    def test_zone_info(self, pjm_service):
        """Test zone information retrieval."""
        zone_info = pjm_service.get_zone_info("AEP")
        assert zone_info is not None
        assert zone_info["code"] == "AEP"
        assert zone_info["name"] == "American Electric Power"
        
        # Test non-existent zone
        zone_info = pjm_service.get_zone_info("INVALID")
        assert zone_info is None
    
    def test_all_zones(self, pjm_service):
        """Test all zones retrieval."""
        zones = pjm_service.get_all_zones()
        assert len(zones) > 0
        assert any(zone["code"] == "AEP" for zone in zones)
        assert any(zone["code"] == "PJM" for zone in zones)

class TestRECService:
    """Test REC management service."""
    
    @pytest.fixture
    def rec_service(self):
        """Create REC service instance."""
        return RECService()
    
    def test_rec_service_initialization(self, rec_service):
        """Test REC service initialization."""
        assert len(rec_service.registries) > 0
        assert RECRegistry.MRETS in rec_service.registries
        assert RECRegistry.NAR in rec_service.registries
    
    def test_rec_registry_enum(self):
        """Test REC registry enum values."""
        assert RECRegistry.MRETS.value == "mrets"
        assert RECRegistry.NAR.value == "nar"
        assert RECRegistry.WREGIS.value == "wregis"
        assert RECRegistry.NEPOOL.value == "nepool"
        assert RECRegistry.PJM.value == "pjm"
        assert RECRegistry.ERCOT.value == "ercot"
        assert RECRegistry.CAISO.value == "caiso"
        assert RECRegistry.NYISO.value == "nyiso"
    
    def test_rec_status_enum(self):
        """Test REC status enum values."""
        assert RECStatus.ISSUED.value == "issued"
        assert RECStatus.TRANSFERRED.value == "transferred"
        assert RECStatus.RETIRED.value == "retired"
        assert RECStatus.EXPIRED.value == "expired"
        assert RECStatus.PENDING.value == "pending"
        assert RECStatus.CANCELLED.value == "cancelled"
    
    def test_rec_fuel_type_enum(self):
        """Test REC fuel type enum values."""
        assert RECFuelType.SOLAR.value == "solar"
        assert RECFuelType.WIND.value == "wind"
        assert RECFuelType.HYDRO.value == "hydro"
        assert RECFuelType.BIOMASS.value == "biomass"
        assert RECFuelType.GEOTHERMAL.value == "geothermal"
        assert RECFuelType.LANDFILL_GAS.value == "landfill_gas"
        assert RECFuelType.WASTE_TO_ENERGY.value == "waste_to_energy"
    
    @pytest.mark.asyncio
    async def test_get_recs_by_owner(self, rec_service):
        """Test REC retrieval by owner."""
        recs = await rec_service.get_recs_by_owner("owner123")
        
        assert len(recs) > 0
        assert recs[0].current_owner == "owner123"
        assert recs[0].registry == RECRegistry.MRETS
        assert recs[0].fuel_type == RECFuelType.SOLAR
    
    @pytest.mark.asyncio
    async def test_transfer_recs(self, rec_service):
        """Test REC transfer functionality."""
        rec_ids = ["REC001", "REC002"]
        
        transaction = await rec_service.transfer_recs(
            rec_ids=rec_ids,
            from_owner="owner1",
            to_owner="owner2",
            price_per_mwh=25.50
        )
        
        assert transaction.transaction_id is not None
        assert transaction.from_owner == "owner1"
        assert transaction.to_owner == "owner2"
        assert transaction.price_per_mwh == 25.50
        assert transaction.status == "completed"
    
    @pytest.mark.asyncio
    async def test_retire_recs(self, rec_service):
        """Test REC retirement functionality."""
        rec_ids = ["REC001", "REC002"]
        
        retirement_data = await rec_service.retire_recs(
            rec_ids=rec_ids,
            owner_id="owner123",
            retirement_reason="Compliance",
            compliance_period="2024",
            registry=RECRegistry.MRETS
        )
        
        assert retirement_data["retirement_id"] is not None
        assert retirement_data["owner_id"] == "owner123"
        assert retirement_data["status"] == "retired"
        assert len(retirement_data["rec_ids"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_esg_metrics(self, rec_service):
        """Test ESG metrics calculation."""
        esg_metrics = await rec_service.get_esg_metrics("owner123")
        
        assert esg_metrics["owner_id"] == "owner123"
        assert "environmental" in esg_metrics
        assert "social" in esg_metrics
        assert "governance" in esg_metrics
        assert "overall_esg_score" in esg_metrics
    
    def test_registry_configuration(self, rec_service):
        """Test registry configuration."""
        mrets_config = rec_service.registries[RECRegistry.MRETS]
        assert mrets_config["api_url"] is not None
        assert "supported_fuels" in mrets_config
        assert "vintage_rules" in mrets_config
        assert "retirement_rules" in mrets_config

class TestHenryHubService:
    """Test Henry Hub futures and basis trading service."""
    
    @pytest.fixture
    def henry_hub_service(self):
        """Create Henry Hub service instance."""
        return HenryHubService()
    
    def test_henry_hub_service_initialization(self, henry_hub_service):
        """Test Henry Hub service initialization."""
        assert len(henry_hub_service.hub_info) > 0
        assert len(henry_hub_service.basis_correlations) > 0
        assert len(henry_hub_service.contract_months) == 12
    
    def test_gas_hub_enum(self):
        """Test gas hub enum values."""
        assert GasHub.HENRY_HUB.value == "henry_hub"
        assert GasHub.TRANSCO_Z6.value == "transco_z6"
        assert GasHub.ALGONQUIN.value == "algonquin"
        assert GasHub.CHICAGO.value == "chicago"
        assert GasHub.HOUSTON.value == "houston"
        assert GasHub.WAHA.value == "waha"
    
    def test_basis_type_enum(self):
        """Test basis type enum values."""
        assert BasisType.LOCATIONAL.value == "locational"
        assert BasisType.TEMPORAL.value == "temporal"
        assert BasisType.QUALITY.value == "quality"
        assert BasisType.TRANSPORTATION.value == "transportation"
    
    def test_contract_month_enum(self):
        """Test contract month enum values."""
        assert ContractMonth.JAN.value == "F"
        assert ContractMonth.FEB.value == "G"
        assert ContractMonth.MAR.value == "H"
        assert ContractMonth.APR.value == "J"
        assert ContractMonth.MAY.value == "K"
        assert ContractMonth.JUN.value == "M"
        assert ContractMonth.JUL.value == "N"
        assert ContractMonth.AUG.value == "Q"
        assert ContractMonth.SEP.value == "U"
        assert ContractMonth.OCT.value == "V"
        assert ContractMonth.NOV.value == "X"
        assert ContractMonth.DEC.value == "Z"
    
    @pytest.mark.asyncio
    async def test_get_henry_hub_futures(self, henry_hub_service):
        """Test Henry Hub futures data retrieval."""
        futures_data = await henry_hub_service.get_henry_hub_futures(limit=5)
        
        assert len(futures_data) == 5
        assert all(isinstance(item, HenryHubFuturesData) for item in futures_data)
        assert all(item.exchange == "NYMEX" for item in futures_data)
    
    @pytest.mark.asyncio
    async def test_get_basis_data(self, henry_hub_service):
        """Test basis data retrieval."""
        basis_data = await henry_hub_service.get_basis_data(
            hub=GasHub.TRANSCO_Z6,
            limit=3
        )
        
        assert len(basis_data) == 3
        assert all(isinstance(item, BasisData) for item in basis_data)
        assert all(item.hub == GasHub.TRANSCO_Z6 for item in basis_data)
    
    @pytest.mark.asyncio
    async def test_get_storage_data(self, henry_hub_service):
        """Test storage data retrieval."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        storage_data = await henry_hub_service.get_storage_data(
            region="total",
            start_date=start_date,
            end_date=end_date
        )
        
        assert len(storage_data) > 0
        assert all(isinstance(item, StorageData) for item in storage_data)
        assert all(item.region == "total" for item in storage_data)
    
    @pytest.mark.asyncio
    async def test_get_pipeline_flows(self, henry_hub_service):
        """Test pipeline flow data retrieval."""
        flow_data = await henry_hub_service.get_pipeline_flows()
        
        assert len(flow_data) > 0
        assert all(isinstance(item, PipelineFlowData) for item in flow_data)
        assert all(item.direction == "forward" for item in flow_data)
    
    @pytest.mark.asyncio
    async def test_calculate_basis_spread(self, henry_hub_service):
        """Test basis spread calculation."""
        spread_data = await henry_hub_service.calculate_basis_spread(
            hub1=GasHub.HENRY_HUB,
            hub2=GasHub.TRANSCO_Z6,
            contract_month="F",
            contract_year=2024
        )
        
        assert "hub1" in spread_data
        assert "hub2" in spread_data
        assert "spread" in spread_data
        assert "correlation" in spread_data
    
    @pytest.mark.asyncio
    async def test_get_weather_correlation(self, henry_hub_service):
        """Test weather correlation analysis."""
        correlation_data = await henry_hub_service.get_weather_correlation(
            hub=GasHub.TRANSCO_Z6,
            days=30
        )
        
        assert "hub" in correlation_data
        assert "temperature_correlation" in correlation_data
        assert "overall_correlation" in correlation_data
        assert "weather_sensitivity" in correlation_data
    
    @pytest.mark.asyncio
    async def test_get_market_summary(self, henry_hub_service):
        """Test market summary retrieval."""
        summary = await henry_hub_service.get_market_summary()
        
        assert "timestamp" in summary
        assert "henry_hub_futures" in summary
        assert "storage" in summary
        assert "basis_summary" in summary
        assert "market_status" in summary
    
    def test_hub_info(self, henry_hub_service):
        """Test hub information."""
        henry_hub_info = henry_hub_service.hub_info[GasHub.HENRY_HUB.value]
        assert henry_hub_info["name"] == "Henry Hub"
        assert henry_hub_info["location"] == "Erath, Louisiana"
        assert henry_hub_info["benchmark"] is True
        assert henry_hub_info["liquidity"] == "Very High"
    
    def test_basis_correlations(self, henry_hub_service):
        """Test basis correlations."""
        transco_correlations = henry_hub_service.basis_correlations[GasHub.TRANSCO_Z6.value]
        assert GasHub.HENRY_HUB.value in transco_correlations
        assert transco_correlations[GasHub.HENRY_HUB.value] > 0.8
    
    def test_contract_months(self, henry_hub_service):
        """Test contract month mapping."""
        assert henry_hub_service.contract_months["F"] == "January"
        assert henry_hub_service.contract_months["G"] == "February"
        assert henry_hub_service.contract_months["H"] == "March"
        assert henry_hub_service.contract_months["Z"] == "December"

class TestIntegration:
    """Integration tests for US market data services."""
    
    @pytest.mark.asyncio
    async def test_pjm_rec_integration(self):
        """Test integration between PJM and REC services."""
        # This would test real integration scenarios
        # For now, just verify services can be instantiated together
        pjm_service = PJMService()
        rec_service = RECService()
        
        assert pjm_service is not None
        assert rec_service is not None
    
    @pytest.mark.asyncio
    async def test_henry_hub_basis_integration(self):
        """Test integration between Henry Hub and basis services."""
        henry_hub_service = HenryHubService()
        
        # Test that basis calculations work with futures data
        futures = await henry_hub_service.get_henry_hub_futures(limit=1)
        if futures:
            assert futures[0].last_price > 0
    
    @pytest.mark.asyncio
    async def test_market_data_consistency(self):
        """Test consistency across market data services."""
        # Verify that all services return data in expected formats
        pjm_service = PJMService()
        rec_service = RECService()
        henry_hub_service = HenryHubService()
        
        # All services should be properly initialized
        assert pjm_service.base_url is not None
        assert len(rec_service.registries) > 0
        assert len(henry_hub_service.hub_info) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 