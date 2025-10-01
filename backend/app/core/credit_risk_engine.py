"""
Advanced Credit Risk Engine for ETRM/CTRM Enterprise Application
Implements credit risk models including CVA, DVA, and counterparty risk
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from decimal import Decimal
from sqlalchemy.orm import Session
import json
from scipy import stats
from scipy.optimize import minimize

logger = logging.getLogger(__name__)

class CreditRating(Enum):
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    CCC = "CCC"
    CC = "CC"
    C = "C"
    D = "D"  # Default

class CreditRiskType(Enum):
    COUNTERPARTY_CREDIT_RISK = "counterparty_credit_risk"
    SOVEREIGN_CREDIT_RISK = "sovereign_credit_risk"
    CONCENTRATION_RISK = "concentration_risk"
    SETTLEMENT_RISK = "settlement_risk"
    PRE_SETTLEMENT_RISK = "pre_settlement_risk"

class CreditRiskModel(Enum):
    MERTON = "merton"
    KMV = "kmv"
    CREDIT_METRICS = "credit_metrics"
    CREDIT_PORTFOLIO_VIEW = "credit_portfolio_view"
    REDUCED_FORM = "reduced_form"
    STRUCTURAL = "structural"

@dataclass
class Counterparty:
    """Counterparty credit information"""
    counterparty_id: str
    name: str
    credit_rating: CreditRating
    probability_of_default: float
    loss_given_default: float
    exposure_at_default: float
    recovery_rate: float
    country: str
    sector: str
    credit_limit: float
    current_exposure: float = 0.0
    peak_exposure: float = 0.0
    expected_exposure: float = 0.0
    potential_future_exposure: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CreditExposure:
    """Credit exposure calculation"""
    counterparty_id: str
    exposure_type: CreditRiskType
    current_exposure: float
    peak_exposure: float
    expected_exposure: float
    potential_future_exposure: float
    exposure_currency: str
    calculation_date: datetime
    confidence_level: float = 0.95
    time_horizon: int = 1  # years
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CreditValuationAdjustment:
    """Credit Valuation Adjustment (CVA)"""
    counterparty_id: str
    cva_amount: float
    cva_currency: str
    calculation_method: str
    confidence_level: float
    time_horizon: int
    expected_exposure: float
    probability_of_default: float
    loss_given_default: float
    calculated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DebitValuationAdjustment:
    """Debit Valuation Adjustment (DVA)"""
    counterparty_id: str
    dva_amount: float
    dva_currency: str
    calculation_method: str
    confidence_level: float
    time_horizon: int
    expected_exposure: float
    own_probability_of_default: float
    own_loss_given_default: float
    calculated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CreditLimit:
    """Credit limit definition"""
    counterparty_id: str
    limit_amount: float
    limit_currency: str
    limit_type: str  # hard, soft, dynamic
    utilization: float
    available_limit: float
    breach_threshold: float = 0.8
    is_breached: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

class CreditRiskEngine:
    """Advanced credit risk engine with CVA/DVA calculations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.counterparties: Dict[str, Counterparty] = {}
        self.credit_exposures: Dict[str, CreditExposure] = {}
        self.cva_calculations: Dict[str, CreditValuationAdjustment] = {}
        self.dva_calculations: Dict[str, DebitValuationAdjustment] = {}
        self.credit_limits: Dict[str, CreditLimit] = {}
        
        # Credit risk parameters
        self.credit_risk_parameters = {
            "risk_free_rate": 0.02,
            "recovery_rate": 0.4,
            "correlation": 0.3,
            "volatility": 0.2,
            "time_horizon": 1.0
        }
        
        # Rating transition matrices
        self.rating_transition_matrix = self._initialize_rating_transition_matrix()
        
        # Initialize credit risk models
        self._initialize_credit_risk_models()
    
    def _initialize_rating_transition_matrix(self) -> np.ndarray:
        """Initialize rating transition matrix"""
        # Simplified transition matrix (in practice, this would be based on historical data)
        ratings = [CreditRating.AAA, CreditRating.AA, CreditRating.A, CreditRating.BBB, 
                  CreditRating.BB, CreditRating.B, CreditRating.CCC, CreditRating.D]
        
        n_ratings = len(ratings)
        transition_matrix = np.zeros((n_ratings, n_ratings))
        
        # Set transition probabilities (simplified)
        for i in range(n_ratings):
            for j in range(n_ratings):
                if i == j:
                    transition_matrix[i, j] = 0.9  # 90% probability of staying in same rating
                elif j == i + 1:
                    transition_matrix[i, j] = 0.05  # 5% probability of downgrade
                elif j == i - 1:
                    transition_matrix[i, j] = 0.03  # 3% probability of upgrade
                elif j == n_ratings - 1:  # Default
                    transition_matrix[i, j] = 0.02  # 2% probability of default
                else:
                    transition_matrix[i, j] = 0.0
        
        return transition_matrix
    
    def _initialize_credit_risk_models(self):
        """Initialize credit risk models"""
        self.credit_risk_models = {
            CreditRiskModel.MERTON: self._calculate_merton_model,
            CreditRiskModel.KMV: self._calculate_kmv_model,
            CreditRiskModel.CREDIT_METRICS: self._calculate_credit_metrics,
            CreditRiskModel.REDUCED_FORM: self._calculate_reduced_form_model,
            CreditRiskModel.STRUCTURAL: self._calculate_structural_model
        }
    
    def add_counterparty(self, counterparty: Counterparty) -> str:
        """Add counterparty to credit risk system"""
        self.counterparties[counterparty.counterparty_id] = counterparty
        logger.info(f"Counterparty added: {counterparty.counterparty_id}")
        return counterparty.counterparty_id
    
    def calculate_credit_exposure(self, 
                                 counterparty_id: str,
                                 trades: List[Dict[str, Any]],
                                 confidence_level: float = 0.95,
                                 time_horizon: int = 1) -> CreditExposure:
        """Calculate credit exposure for counterparty"""
        
        if counterparty_id not in self.counterparties:
            raise ValueError(f"Counterparty {counterparty_id} not found")
        
        # Calculate different types of exposure
        current_exposure = self._calculate_current_exposure(trades)
        peak_exposure = self._calculate_peak_exposure(trades)
        expected_exposure = self._calculate_expected_exposure(trades, time_horizon)
        potential_future_exposure = self._calculate_potential_future_exposure(trades, confidence_level, time_horizon)
        
        exposure = CreditExposure(
            counterparty_id=counterparty_id,
            exposure_type=CreditRiskType.COUNTERPARTY_CREDIT_RISK,
            current_exposure=current_exposure,
            peak_exposure=peak_exposure,
            expected_exposure=expected_exposure,
            potential_future_exposure=potential_future_exposure,
            exposure_currency="USD",
            calculation_date=datetime.utcnow(),
            confidence_level=confidence_level,
            time_horizon=time_horizon
        )
        
        # Store exposure
        exposure_id = f"CE_{counterparty_id}_{int(datetime.utcnow().timestamp())}"
        self.credit_exposures[exposure_id] = exposure
        
        # Update counterparty exposure
        self.counterparties[counterparty_id].current_exposure = current_exposure
        self.counterparties[counterparty_id].peak_exposure = peak_exposure
        self.counterparties[counterparty_id].expected_exposure = expected_exposure
        self.counterparties[counterparty_id].potential_future_exposure = potential_future_exposure
        
        return exposure
    
    def _calculate_current_exposure(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate current exposure"""
        # Current exposure is the sum of all positive mark-to-market values
        current_exposure = 0.0
        
        for trade in trades:
            mtm_value = trade.get('mark_to_market', 0)
            if mtm_value > 0:
                current_exposure += mtm_value
        
        return current_exposure
    
    def _calculate_peak_exposure(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate peak exposure"""
        # Peak exposure is the maximum exposure over time
        # For simplicity, we'll use a multiple of current exposure
        current_exposure = self._calculate_current_exposure(trades)
        return current_exposure * 1.5  # 50% buffer
    
    def _calculate_expected_exposure(self, trades: List[Dict[str, Any]], time_horizon: int) -> float:
        """Calculate expected exposure using Monte Carlo simulation"""
        # Simplified expected exposure calculation
        current_exposure = self._calculate_current_exposure(trades)
        
        # Expected exposure grows with time due to volatility
        volatility = self.credit_risk_parameters['volatility']
        time_factor = np.sqrt(time_horizon)
        
        expected_exposure = current_exposure * (1 + volatility * time_factor)
        return expected_exposure
    
    def _calculate_potential_future_exposure(self, 
                                           trades: List[Dict[str, Any]], 
                                           confidence_level: float, 
                                           time_horizon: int) -> float:
        """Calculate potential future exposure"""
        # PFE is the exposure at a given confidence level
        current_exposure = self._calculate_current_exposure(trades)
        volatility = self.credit_risk_parameters['volatility']
        time_factor = np.sqrt(time_horizon)
        
        # Calculate PFE using normal distribution
        z_score = stats.norm.ppf(confidence_level)
        pfe = current_exposure * (1 + volatility * time_factor * z_score)
        
        return max(0, pfe)  # PFE cannot be negative
    
    def calculate_cva(self, 
                     counterparty_id: str,
                     exposure: CreditExposure,
                     model: CreditRiskModel = CreditRiskModel.MERTON) -> CreditValuationAdjustment:
        """Calculate Credit Valuation Adjustment (CVA)"""
        
        if counterparty_id not in self.counterparties:
            raise ValueError(f"Counterparty {counterparty_id} not found")
        
        counterparty = self.counterparties[counterparty_id]
        
        # Get model calculation
        model_calculator = self.credit_risk_models.get(model)
        if not model_calculator:
            raise ValueError(f"Credit risk model {model} not implemented")
        
        # Calculate CVA using selected model
        cva_amount = model_calculator(counterparty, exposure)
        
        cva = CreditValuationAdjustment(
            counterparty_id=counterparty_id,
            cva_amount=cva_amount,
            cva_currency="USD",
            calculation_method=model.value,
            confidence_level=exposure.confidence_level,
            time_horizon=exposure.time_horizon,
            expected_exposure=exposure.expected_exposure,
            probability_of_default=counterparty.probability_of_default,
            loss_given_default=counterparty.loss_given_default,
            calculated_at=datetime.utcnow()
        )
        
        # Store CVA calculation
        cva_id = f"CVA_{counterparty_id}_{int(datetime.utcnow().timestamp())}"
        self.cva_calculations[cva_id] = cva
        
        return cva
    
    def calculate_dva(self, 
                     counterparty_id: str,
                     exposure: CreditExposure,
                     own_credit_rating: CreditRating = CreditRating.A,
                     model: CreditRiskModel = CreditRiskModel.MERTON) -> DebitValuationAdjustment:
        """Calculate Debit Valuation Adjustment (DVA)"""
        
        # Calculate own probability of default
        own_pd = self._get_probability_of_default(own_credit_rating)
        own_lgd = 1 - self.credit_risk_parameters['recovery_rate']
        
        # Calculate DVA (simplified)
        dva_amount = exposure.expected_exposure * own_pd * own_lgd
        
        dva = DebitValuationAdjustment(
            counterparty_id=counterparty_id,
            dva_amount=dva_amount,
            dva_currency="USD",
            calculation_method=model.value,
            confidence_level=exposure.confidence_level,
            time_horizon=exposure.time_horizon,
            expected_exposure=exposure.expected_exposure,
            own_probability_of_default=own_pd,
            own_loss_given_default=own_lgd,
            calculated_at=datetime.utcnow()
        )
        
        # Store DVA calculation
        dva_id = f"DVA_{counterparty_id}_{int(datetime.utcnow().timestamp())}"
        self.dva_calculations[dva_id] = dva
        
        return dva
    
    def _calculate_merton_model(self, counterparty: Counterparty, exposure: CreditExposure) -> float:
        """Calculate CVA using Merton structural model"""
        
        # Merton model parameters
        asset_value = 1000.0  # Simplified asset value
        debt_value = 500.0    # Simplified debt value
        volatility = 0.2      # Asset volatility
        risk_free_rate = self.credit_risk_parameters['risk_free_rate']
        time_to_maturity = exposure.time_horizon
        
        # Calculate distance to default
        d1 = (np.log(asset_value / debt_value) + (risk_free_rate + 0.5 * volatility**2) * time_to_maturity) / (volatility * np.sqrt(time_to_maturity))
        d2 = d1 - volatility * np.sqrt(time_to_maturity)
        
        # Calculate probability of default
        pd = 1 - stats.norm.cdf(d2)
        
        # Calculate CVA
        cva = exposure.expected_exposure * pd * counterparty.loss_given_default
        
        return cva
    
    def _calculate_kmv_model(self, counterparty: Counterparty, exposure: CreditExposure) -> float:
        """Calculate CVA using KMV model"""
        
        # KMV model is similar to Merton but with different parameters
        # For simplicity, we'll use a modified Merton approach
        cva = self._calculate_merton_model(counterparty, exposure)
        
        # Apply KMV-specific adjustments
        cva *= 1.1  # 10% adjustment for KMV model
        
        return cva
    
    def _calculate_credit_metrics(self, counterparty: Counterparty, exposure: CreditExposure) -> float:
        """Calculate CVA using CreditMetrics model"""
        
        # CreditMetrics uses rating migration and default probabilities
        rating_pd = counterparty.probability_of_default
        
        # Calculate CVA using rating-based PD
        cva = exposure.expected_exposure * rating_pd * counterparty.loss_given_default
        
        return cva
    
    def _calculate_reduced_form_model(self, counterparty: Counterparty, exposure: CreditExposure) -> float:
        """Calculate CVA using reduced form model"""
        
        # Reduced form model uses intensity-based default probabilities
        intensity = -np.log(1 - counterparty.probability_of_default) / exposure.time_horizon
        
        # Calculate CVA
        cva = exposure.expected_exposure * (1 - np.exp(-intensity * exposure.time_horizon)) * counterparty.loss_given_default
        
        return cva
    
    def _calculate_structural_model(self, counterparty: Counterparty, exposure: CreditExposure) -> float:
        """Calculate CVA using structural model"""
        
        # Structural model is similar to Merton but with different assumptions
        cva = self._calculate_merton_model(counterparty, exposure)
        
        # Apply structural model adjustments
        cva *= 0.95  # 5% adjustment for structural model
        
        return cva
    
    def _get_probability_of_default(self, rating: CreditRating) -> float:
        """Get probability of default for credit rating"""
        
        rating_pd = {
            CreditRating.AAA: 0.0001,
            CreditRating.AA: 0.0005,
            CreditRating.A: 0.001,
            CreditRating.BBB: 0.005,
            CreditRating.BB: 0.02,
            CreditRating.B: 0.05,
            CreditRating.CCC: 0.15,
            CreditRating.CC: 0.25,
            CreditRating.C: 0.35,
            CreditRating.D: 1.0
        }
        
        return rating_pd.get(rating, 0.01)
    
    def set_credit_limit(self, 
                        counterparty_id: str,
                        limit_amount: float,
                        limit_currency: str = "USD",
                        limit_type: str = "hard") -> str:
        """Set credit limit for counterparty"""
        
        if counterparty_id not in self.counterparties:
            raise ValueError(f"Counterparty {counterparty_id} not found")
        
        credit_limit = CreditLimit(
            counterparty_id=counterparty_id,
            limit_amount=limit_amount,
            limit_currency=limit_currency,
            limit_type=limit_type,
            utilization=0.0,
            available_limit=limit_amount
        )
        
        self.credit_limits[counterparty_id] = credit_limit
        logger.info(f"Credit limit set for {counterparty_id}: {limit_amount} {limit_currency}")
        
        return counterparty_id
    
    def check_credit_limit(self, counterparty_id: str, exposure_amount: float) -> Dict[str, Any]:
        """Check credit limit utilization"""
        
        if counterparty_id not in self.credit_limits:
            return {"status": "no_limit", "message": f"No credit limit set for {counterparty_id}"}
        
        credit_limit = self.credit_limits[counterparty_id]
        
        # Update utilization
        credit_limit.utilization = exposure_amount / credit_limit.limit_amount
        credit_limit.available_limit = credit_limit.limit_amount - exposure_amount
        credit_limit.is_breached = credit_limit.utilization > credit_limit.breach_threshold
        credit_limit.updated_at = datetime.utcnow()
        
        return {
            "counterparty_id": counterparty_id,
            "limit_amount": credit_limit.limit_amount,
            "current_exposure": exposure_amount,
            "utilization": credit_limit.utilization,
            "available_limit": credit_limit.available_limit,
            "is_breached": credit_limit.is_breached,
            "breach_threshold": credit_limit.breach_threshold,
            "status": "breached" if credit_limit.is_breached else "within_limit"
        }
    
    def calculate_portfolio_credit_risk(self, 
                                      counterparties: List[str],
                                      correlation_matrix: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Calculate portfolio-level credit risk"""
        
        if not counterparties:
            return {"message": "No counterparties provided"}
        
        # Get counterparty data
        portfolio_counterparties = [self.counterparties[cpid] for cpid in counterparties if cpid in self.counterparties]
        
        if not portfolio_counterparties:
            return {"message": "No valid counterparties found"}
        
        # Calculate portfolio metrics
        total_exposure = sum(cp.current_exposure for cp in portfolio_counterparties)
        total_expected_exposure = sum(cp.expected_exposure for cp in portfolio_counterparties)
        total_pfe = sum(cp.potential_future_exposure for cp in portfolio_counterparties)
        
        # Calculate portfolio CVA
        total_cva = sum(
            self.cva_calculations.get(f"CVA_{cp.counterparty_id}", CreditValuationAdjustment(
                counterparty_id=cp.counterparty_id,
                cva_amount=0,
                cva_currency="USD",
                calculation_method="portfolio",
                confidence_level=0.95,
                time_horizon=1,
                expected_exposure=cp.expected_exposure,
                probability_of_default=cp.probability_of_default,
                loss_given_default=cp.loss_given_default,
                calculated_at=datetime.utcnow()
            )).cva_amount
            for cp in portfolio_counterparties
        )
        
        # Calculate concentration risk
        exposure_weights = [cp.current_exposure / total_exposure for cp in portfolio_counterparties if total_exposure > 0]
        concentration_risk = sum(w**2 for w in exposure_weights) if exposure_weights else 0
        
        # Calculate diversification benefit
        diversification_benefit = 1 - concentration_risk
        
        return {
            "total_counterparties": len(portfolio_counterparties),
            "total_exposure": total_exposure,
            "total_expected_exposure": total_expected_exposure,
            "total_pfe": total_pfe,
            "total_cva": total_cva,
            "concentration_risk": concentration_risk,
            "diversification_benefit": diversification_benefit,
            "average_pd": np.mean([cp.probability_of_default for cp in portfolio_counterparties]),
            "average_lgd": np.mean([cp.loss_given_default for cp in portfolio_counterparties]),
            "counterparty_breakdown": [
                {
                    "counterparty_id": cp.counterparty_id,
                    "name": cp.name,
                    "credit_rating": cp.credit_rating.value,
                    "current_exposure": cp.current_exposure,
                    "probability_of_default": cp.probability_of_default,
                    "loss_given_default": cp.loss_given_default
                }
                for cp in portfolio_counterparties
            ]
        }
    
    def calculate_credit_risk_metrics(self, counterparty_id: str) -> Dict[str, Any]:
        """Calculate comprehensive credit risk metrics for counterparty"""
        
        if counterparty_id not in self.counterparties:
            return {"message": f"Counterparty {counterparty_id} not found"}
        
        counterparty = self.counterparties[counterparty_id]
        
        # Get credit limit information
        credit_limit_info = self.credit_limits.get(counterparty_id)
        
        # Get CVA information
        cva_info = None
        for cva_id, cva in self.cva_calculations.items():
            if cva.counterparty_id == counterparty_id:
                cva_info = cva
                break
        
        # Get DVA information
        dva_info = None
        for dva_id, dva in self.dva_calculations.items():
            if dva.counterparty_id == counterparty_id:
                dva_info = dva
                break
        
        return {
            "counterparty_id": counterparty_id,
            "name": counterparty.name,
            "credit_rating": counterparty.credit_rating.value,
            "probability_of_default": counterparty.probability_of_default,
            "loss_given_default": counterparty.loss_given_default,
            "recovery_rate": counterparty.recovery_rate,
            "current_exposure": counterparty.current_exposure,
            "peak_exposure": counterparty.peak_exposure,
            "expected_exposure": counterparty.expected_exposure,
            "potential_future_exposure": counterparty.potential_future_exposure,
            "credit_limit": {
                "limit_amount": credit_limit_info.limit_amount if credit_limit_info else None,
                "utilization": credit_limit_info.utilization if credit_limit_info else None,
                "available_limit": credit_limit_info.available_limit if credit_limit_info else None,
                "is_breached": credit_limit_info.is_breached if credit_limit_info else None
            },
            "cva": {
                "cva_amount": cva_info.cva_amount if cva_info else None,
                "calculation_method": cva_info.calculation_method if cva_info else None,
                "calculated_at": cva_info.calculated_at.isoformat() if cva_info else None
            },
            "dva": {
                "dva_amount": dva_info.dva_amount if dva_info else None,
                "calculation_method": dva_info.calculation_method if dva_info else None,
                "calculated_at": dva_info.calculated_at.isoformat() if dva_info else None
            },
            "risk_score": self._calculate_risk_score(counterparty),
            "country": counterparty.country,
            "sector": counterparty.sector
        }
    
    def _calculate_risk_score(self, counterparty: Counterparty) -> float:
        """Calculate overall risk score for counterparty"""
        
        # Risk score based on multiple factors
        pd_score = counterparty.probability_of_default * 100
        exposure_score = min(counterparty.current_exposure / 1000, 10)  # Cap at 10
        concentration_score = 5  # Placeholder for concentration risk
        
        # Weighted risk score
        risk_score = (pd_score * 0.4 + exposure_score * 0.3 + concentration_score * 0.3)
        
        return min(risk_score, 100)  # Cap at 100
    
    def get_credit_risk_summary(self) -> Dict[str, Any]:
        """Get credit risk system summary"""
        
        total_counterparties = len(self.counterparties)
        total_exposure = sum(cp.current_exposure for cp in self.counterparties.values())
        total_cva = sum(cva.cva_amount for cva in self.cva_calculations.values())
        total_dva = sum(dva.dva_amount for dva in self.dva_calculations.values())
        
        # Credit limit utilization
        credit_limits = list(self.credit_limits.values())
        breached_limits = len([cl for cl in credit_limits if cl.is_breached])
        
        # Rating distribution
        rating_distribution = {}
        for rating in CreditRating:
            rating_distribution[rating.value] = len([cp for cp in self.counterparties.values() if cp.credit_rating == rating])
        
        return {
            "total_counterparties": total_counterparties,
            "total_exposure": total_exposure,
            "total_cva": total_cva,
            "total_dva": total_dva,
            "net_cva": total_cva - total_dva,
            "credit_limits": {
                "total_limits": len(credit_limits),
                "breached_limits": breached_limits,
                "breach_rate": breached_limits / len(credit_limits) if credit_limits else 0
            },
            "rating_distribution": rating_distribution,
            "average_pd": np.mean([cp.probability_of_default for cp in self.counterparties.values()]),
            "average_lgd": np.mean([cp.loss_given_default for cp in self.counterparties.values()]),
            "total_calculations": {
                "cva_calculations": len(self.cva_calculations),
                "dva_calculations": len(self.dva_calculations),
                "exposure_calculations": len(self.credit_exposures)
            }
        }
